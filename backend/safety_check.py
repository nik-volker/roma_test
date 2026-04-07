"""Детекция кризиса (суицид, самоповреждение)"""

import logging

logger = logging.getLogger(__name__)

CRISIS_KEYWORDS = [
    "убить себя",
    "покончить с собой",
    "свести счёты с жизнью",
    "не хочу жить",
    "давай мне яд",
    "пила таблетки",
    "режу себя",
    "self-harm",
    "self harm",
    "покончу с собой",
    "я не хочу жить",
    "нет смысла жить",
    "хочу умереть",
    "совсем надоело",
    "конец всему",
]


def check_crisis(message):
    """
    Проверяет, есть ли в сообщении признаки кризиса.
    Возвращает ('high', reason) или ('none', None)
    """
    if not message:
        return "none", None

    message_lower = message.lower()

    for keyword in CRISIS_KEYWORDS:
        if keyword in message_lower:
            logger.warning(f"CRISIS DETECTED: {keyword}")
            return "high", keyword

    return "none", None


def get_crisis_response(language="en"):
    """Возвращает кризисный ответ"""
    from prompts import get_crisis_message, normalize_language

    current_language = normalize_language(language)

    if current_language == "ru":
        suggested_technique = "Экстренная поддержка"
        technique_description = "Сразу обратись к живому специалисту или в экстренные службы."
    else:
        suggested_technique = "Emergency support"
        technique_description = "Contact a live professional, crisis line, or emergency services immediately."

    return {
        "message": get_crisis_message(current_language),
        "detected_state": "crisis",
        "suggested_technique": suggested_technique,
        "technique_description": technique_description,
        "risk_level": "high",
    }
