"""Интеграция с OpenAI API"""

import json
import logging
from openai import OpenAI
from config import OPENAI_API_KEY, MODEL
from prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

client = OpenAI(api_key=OPENAI_API_KEY)


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
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, *messages],
            temperature=0.8,
            max_tokens=500,
        )

        # Извлекаем ответ
        assistant_response = response.choices[0].message.content
        logger.info(f"OpenAI response: {assistant_response[:100]}...")

        # Парсим JSON
        try:
            response_json = json.loads(assistant_response)
        except json.JSONDecodeError:
            logger.error(
                f"Failed to parse OpenAI response as JSON: {assistant_response}"
            )
            # Пытаемся найти JSON в ответе
            start_idx = assistant_response.find("{")
            end_idx = assistant_response.rfind("}") + 1
            if start_idx != -1 and end_idx > start_idx:
                try:
                    response_json = json.loads(assistant_response[start_idx:end_idx])
                except json.JSONDecodeError:
                    response_json = {
                        "message": assistant_response,
                        "detected_state": "unknown",
                        "suggested_technique": "Техника",
                        "technique_description": "Попробуй ещё раз",
                        "risk_level": "none",
                    }
            else:
                response_json = {
                    "message": assistant_response,
                    "detected_state": "unknown",
                    "suggested_technique": "Техника",
                    "technique_description": "Попробуй ещё раз",
                    "risk_level": "none",
                }

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
