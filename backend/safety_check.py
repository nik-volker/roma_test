"""Детекция кризиса и опасных safety-ситуаций."""

import logging
import re

logger = logging.getLogger(__name__)

CRISIS_KEYWORDS = [
    "i want to die",
    "i don't want to live",
    "i do not want to live",
    "kill myself",
    "end my life",
    "suicide",
    "self harm",
    "self-harm",
    "убить себя",
    "покончить с собой",
    "свести счёты с жизнью",
    "не хочу жить",
    "давай мне яд",
    "пила таблетки",
    "режу себя",
    "покончу с собой",
    "я не хочу жить",
    "нет смысла жить",
    "хочу умереть",
    "совсем надоело",
    "конец всему",
]


ABUSE_VIOLENCE_PATTERNS = [
    # EN: physical violence and threats
    (
        r"\b(husband|partner|boyfriend|girlfriend|he|she)\s+(hits|hit|beats|beat|punched|pushed)\s+me\b",
        "physical_violence",
    ),
    (
        r"\b(he|she)\s+(hit|beats|beat|punched|pushed|strangled|choked)\s+me\b",
        "physical_violence",
    ),
    (
        r"\b(i am|i'm|im)\s+afraid\s+of\s+(my\s+)?(partner|husband|wife|boyfriend|girlfriend|him|her)\b",
        "fear_for_safety",
    ),
    (r"\b(he|she)\s+(threatens|threatened|is threatening)\s+me\b", "threats"),
    (r"\b(not\s+safe|don't\s+feel\s+safe|do\s+not\s+feel\s+safe)\b", "fear_for_safety"),
    (
        r"\b(he|she)\s+(controls|is controlling)\s+(my\s+)?(phone|money|finances|movements|where\s+i\s+go)\b",
        "coercive_control",
    ),
    (
        r"\b(he|she)\s+(won't|will\s+not|doesn't|does\s+not)\s+let\s+me\s+leave\b",
        "restraining_or_isolation",
    ),
    (r"\b(he|she)\s+(forces|forced|is forcing)\s+me\b", "coercion"),
    # RU: физическое насилие, контроль, угрозы
    (
        r"\b(муж|партнер|парень|девушка|он|она)\s+меня\s+(бьет|бьёт|ударил|ударила|толкнул|толкнула|душил|душила)\b",
        "physical_violence",
    ),
    (
        r"\b(он|она)\s+меня\s+(бьет|бьёт|ударил|ударила|толкнул|толкнула|душил|душила)\b",
        "physical_violence",
    ),
    (
        r"\bя\s+боюсь\s+(мужа|партнера|партнёра|партнершу|партнёршу|его|ее|её|ее)\b",
        "fear_for_safety",
    ),
    (r"\b(он|она)\s+мне\s+угрожает\b", "threats"),
    (
        r"\b(не\s+чувствую\s+себя\s+в\s+безопасности|мне\s+не\s+безопасно)\b",
        "fear_for_safety",
    ),
    (
        r"\b(он|она)\s+контролирует\s+(меня|мой\s+телефон|деньги|мои\s+деньги|мои\s+передвижения|куда\s+я\s+хожу)\b",
        "coercive_control",
    ),
    (r"\b(он|она)\s+не\s+дает\s+уйти\b", "restraining_or_isolation"),
    (r"\b(он|она)\s+меня\s+заставляет\b", "coercion"),
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


def check_abuse_violence(message):
    """
    Проверяет, есть ли признаки насилия, угроз, coercive control,
    страха за безопасность и других red flags.
    Возвращает ('high', reason) или ('none', None)
    """
    if not message:
        return "none", None

    message_lower = message.lower()

    for pattern, reason in ABUSE_VIOLENCE_PATTERNS:
        if re.search(pattern, message_lower):
            logger.warning(f"ABUSE/VIOLENCE SAFETY CASE DETECTED: {reason}")
            return "high", reason

    return "none", None


def get_crisis_response(language="en"):
    """Возвращает кризисный ответ"""
    from prompts import get_crisis_message, normalize_language

    current_language = normalize_language(language)

    if current_language == "ru":
        suggested_technique = "Экстренная поддержка"
        technique_description = (
            "Сразу обратись к живому специалисту или в экстренные службы."
        )
    else:
        suggested_technique = "Emergency support"
        technique_description = "Contact a live professional, crisis line, or emergency services immediately."

    return {
        "message": get_crisis_message(current_language),
        "detected_state": "crisis",
        "suggested_technique": suggested_technique,
        "technique_description": technique_description,
        "risk_level": "high",
        "safety_mode": True,
        "needs_specialist_support": True,
    }


def get_abuse_violence_response(language="en"):
    """Возвращает safety-ответ при признаках насилия/угроз/абьюза."""
    from prompts import normalize_language

    current_language = normalize_language(language)

    if current_language == "ru":
        return {
            "message": (
                "Спасибо, что поделился этим. То, что ты описываешь, похоже на серьезный red flag и может быть опасной ситуацией, "
                "а не обычной ссорой. Твоя безопасность сейчас важнее всего. "
                "Пожалуйста, обратись за поддержкой к человеку, которому доверяешь, психологу или кризисной службе. "
                "Если есть риск немедленной опасности, сразу звони в экстренные службы."
            ),
            "detected_state": "safety_risk",
            "suggested_technique": "План безопасности",
            "technique_description": (
                "Определи безопасное место, подготовь контакты экстренной помощи и человека, которому можно написать или позвонить прямо сейчас."
            ),
            "risk_level": "high",
            "safety_mode": True,
            "needs_specialist_support": True,
        }

    return {
        "message": (
            "Thank you for sharing this. What you describe is a serious safety red flag and may be dangerous, not a normal relationship conflict. "
            "Your safety comes first. Please reach out to a trusted person, a mental health professional, or a crisis support service. "
            "If there is immediate danger, contact emergency services right now."
        ),
        "detected_state": "safety_risk",
        "suggested_technique": "Safety first plan",
        "technique_description": (
            "Identify a safe place, prepare emergency contacts, and contact a trusted person or crisis service now."
        ),
        "risk_level": "high",
        "safety_mode": True,
        "needs_specialist_support": True,
    }


def check_history_for_safety_flags(conversation_history):
    """
    Сканирует conversation_history на наличие прошлых red flags.
    Возвращает True, если хотя бы одно user-сообщение содержало
    crisis или abuse/violence триггер.
    """
    if not conversation_history:
        return False

    for entry in conversation_history:
        if entry.get("role") != "user":
            continue
        content = entry.get("content", "")
        crisis_level, _ = check_crisis(content)
        if crisis_level == "high":
            return True
        abuse_level, _ = check_abuse_violence(content)
        if abuse_level == "high":
            return True

    return False


def get_safety_mode_followup_response(language="en"):
    """Возвращает ответ, когда safety-mode уже активен для текущей сессии."""
    from prompts import normalize_language

    current_language = normalize_language(language)

    if current_language == "ru":
        return {
            "message": (
                "Сейчас важно не рассматривать это как обычный конфликт. "
                "Похоже, вопрос связан с безопасностью. "
                "Давай сфокусируемся на твоей защите и поддержке: обратись к человеку, которому доверяешь, "
                "к психологу или в кризисную службу. Если есть риск немедленной опасности, звони в экстренные службы."
            ),
            "detected_state": "safety_risk",
            "suggested_technique": "Поддержка и безопасность",
            "technique_description": (
                "Сделай один безопасный шаг прямо сейчас: свяжись с trusted person, специалистом или службой поддержки."
            ),
            "risk_level": "high",
            "safety_mode": True,
            "needs_specialist_support": True,
        }

    return {
        "message": (
            "This should not be treated as a normal relationship conflict. "
            "It still looks like a safety-focused situation. "
            "Let us keep the focus on your protection and support: contact a trusted person, a mental health professional, "
            "or a crisis support service. If there is immediate danger, call emergency services now."
        ),
        "detected_state": "safety_risk",
        "suggested_technique": "Safety and support step",
        "technique_description": (
            "Take one concrete safety step now: contact a trusted person, a professional, or a support service."
        ),
        "risk_level": "high",
        "safety_mode": True,
        "needs_specialist_support": True,
    }
