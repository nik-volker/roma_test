"""Интеграция с OpenAI API"""

import json
import logging
import re
from openai import OpenAI
from config import OPENAI_API_KEY, MODEL
from prompts import SYSTEM_PROMPT

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


def call_openai(user_message, conversation_history=None):
    """
    Отправляет сообщение в OpenAI и получает ответ в формате JSON.

    Args:
        user_message: сообщение пользователя
        conversation_history: история разговора (список {"role": "user/assistant", "content": "..."})

    Returns:
        dict с полями: message, detected_state, suggested_technique, technique_description, risk_level
    """
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY is not set")
        return {
            "message": "Ошибка: API ключ не установлен",
            "detected_state": "unknown",
            "suggested_technique": "Error",
            "technique_description": "Проверьте конфигурацию",
            "risk_level": "none",
        }

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
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, *messages],
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
            response_json = {
                "message": assistant_response,
                "detected_state": "unknown",
                "suggested_technique": "Техника",
                "technique_description": "Попробуй ещё раз",
                "risk_level": "none",
            }

        # Защита от частично заполненного JSON
        response_json.setdefault(
            "message", "Я рядом. Расскажи чуть подробнее, что происходит."
        )
        response_json.setdefault("detected_state", "unknown")
        response_json.setdefault("suggested_technique", "Техника")
        response_json.setdefault("technique_description", "Попробуй ещё раз")
        response_json.setdefault("risk_level", "none")

        return response_json

    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return {
            "message": f"Ошибка при обращении к AI: {str(e)}",
            "detected_state": "unknown",
            "suggested_technique": "Error",
            "technique_description": "Попробуйте позже",
            "risk_level": "none",
        }
