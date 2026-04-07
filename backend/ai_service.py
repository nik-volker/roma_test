"""Интеграция с OpenAI API"""

import json
import logging
import re
from openai import OpenAI
from config import OPENAI_API_KEY, MODEL
from prompts import get_system_prompt, normalize_language

logger = logging.getLogger(__name__)

_openai_client = None


def _extract_json_payload(raw_text):
    """Best-effort JSON extraction from model output."""
    if not isinstance(raw_text, str):
        return None

    text = raw_text.strip()

    # Частый кейс: модель оборачивает JSON в markdown-кодблок.
    text = re.sub(r"^```(?:json)?\\s*", "", text)
    text = re.sub(r"\\s*```$", "", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    start_idx = text.find("{")
    end_idx = text.rfind("}") + 1
    if start_idx != -1 and end_idx > start_idx:
        try:
            return json.loads(text[start_idx:end_idx])
        except json.JSONDecodeError:
            return None

    return None


def get_openai_client():
    """Lazily initialize OpenAI client to avoid top-level external client init."""
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(api_key=OPENAI_API_KEY)
    return _openai_client


def _default_response(language, message=None, technique=None, description=None):
    current_language = normalize_language(language)

    defaults = {
        "en": {
            "message": "I am here with you. Tell me a little more about what is happening.",
            "technique": "Grounding pause",
            "description": "Take one slow breath, then describe the situation in one short sentence.",
        },
        "ru": {
            "message": "Я рядом. Расскажи чуть подробнее, что сейчас происходит.",
            "technique": "Пауза на опору",
            "description": "Сделай один медленный вдох и опиши ситуацию одной короткой фразой.",
        },
    }

    localized = defaults[current_language]

    return {
        "message": message or localized["message"],
        "detected_state": "unknown",
        "suggested_technique": technique or localized["technique"],
        "technique_description": description or localized["description"],
        "risk_level": "none",
    }


def call_openai(user_message, conversation_history=None, language="en"):
    """
    Отправляет сообщение в OpenAI и получает ответ в формате JSON.

    Args:
        user_message: сообщение пользователя
        conversation_history: история разговора (список {"role": "user/assistant", "content": "..."})

    Returns:
        dict с полями: message, detected_state, suggested_technique, technique_description, risk_level
    """
    current_language = normalize_language(language)

    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY is not set")
        if current_language == "ru":
            return _default_response(
                current_language,
                message="Ошибка: API ключ не установлен.",
                technique="Проверка конфигурации",
                description="Проверь настройки backend и переменную OPENAI_API_KEY.",
            )
        return _default_response(
            current_language,
            message="Error: API key is not configured.",
            technique="Configuration check",
            description="Verify the backend configuration and OPENAI_API_KEY.",
        )

    try:
        # Подготавливаем history
        if conversation_history is None:
            conversation_history = []

        # Добавляем новое сообщение
        messages = conversation_history + [{"role": "user", "content": user_message}]

        # Вызываем OpenAI
        client = get_openai_client()
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": get_system_prompt(current_language)}, *messages],
            temperature=0.8,
            max_tokens=500,
            response_format={"type": "json_object"},
        )

        # Извлекаем ответ
        assistant_response = response.choices[0].message.content
        logger.info(f"OpenAI response: {assistant_response[:100]}...")

        # Парсим JSON
        response_json = _extract_json_payload(assistant_response)
        if response_json is None:
            logger.error(
                f"Failed to parse OpenAI response as JSON: {assistant_response}"
            )
            response_json = _default_response(
                current_language,
                message=assistant_response,
            )

        defaults = _default_response(current_language)
        for key, value in defaults.items():
            response_json.setdefault(key, value)

        return response_json

    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        if current_language == "ru":
            return _default_response(
                current_language,
                message=f"Ошибка при обращении к AI: {str(e)}",
                technique="Повторить позже",
                description="Попробуйте ещё раз немного позже.",
            )
        return _default_response(
            current_language,
            message=f"Error while contacting the AI service: {str(e)}",
            technique="Try again later",
            description="Please try sending the message again in a moment.",
        )
