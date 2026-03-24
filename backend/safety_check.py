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


def get_crisis_response():
    """Возвращает кризисный ответ"""
    from prompts import CRISIS_MESSAGE

    return {
        "message": CRISIS_MESSAGE,
        "detected_state": "crisis",
        "suggested_technique": "Emergency",
        "technique_description": "Обратись к специалисту",
        "risk_level": "high",
    }
