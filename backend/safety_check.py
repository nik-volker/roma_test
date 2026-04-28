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


FRAUD_FINANCIAL_PATTERNS = [
    # EN: requests to take a loan / borrow money for someone
    (
        r"\b(he|she|they|partner|husband|wife|boyfriend|girlfriend)\s+(asked|asks|wants|told|tells|is asking|is telling)\s+me\s+to\s+(take|get|apply\s+for|sign)\s+(a\s+)?(loan|credit|mortgage)\b",
        "request_to_take_loan",
    ),
    (
        r"\b(take|get|apply\s+for|sign)\s+(a\s+)?(loan|credit|mortgage)\s+for\s+(him|her|them|my\s+(partner|husband|wife|boyfriend|girlfriend))\b",
        "request_to_take_loan",
    ),
    (
        r"\b(he|she|they)\s+(asked|asks|wants|is asking)\s+me\s+to\s+(borrow|lend)\s+(money|cash)\b",
        "request_to_borrow_money",
    ),
    # EN: pressure to transfer money / send money urgently
    (
        r"\b(transfer|send|wire|give)\s+(him|her|them|me)\s+(money|cash|funds)\b",
        "money_transfer_pressure",
    ),
    (
        r"\b(urgent|urgently|right\s+now|immediately)\s+(needs|need)\s+(money|cash|funds)\b",
        "urgent_money_request",
    ),
    # EN: blackmail / extortion / threats for money / scam
    (r"\b(blackmail|blackmailing|blackmailed)\b", "blackmail"),
    (r"\b(extort|extorting|extortion|extorted)\b", "extortion"),
    (r"\b(scam|scammer|scammed|scamming)\b", "scam"),
    (
        r"\b(threatens|threatened|is threatening)\s+(me|to)\s+.*\b(money|leak|share|expose|publish|photos|videos)\b",
        "blackmail_threats",
    ),
    # EN: requests for codes / documents / passwords / banking data
    (
        r"\b(asks?|wants?|demanding|demanded|asked)\s+(me\s+)?(for\s+)?(my\s+)?(verification\s+code|sms\s+code|otp|one[-\s]?time\s+password|banking\s+password|card\s+pin|cvv|card\s+number|passport|id|documents)\b",
        "credential_or_document_request",
    ),
    (
        r"\b(send|share|give)\s+(him|her|them)\s+(my\s+)?(password|verification\s+code|sms\s+code|otp|card\s+pin|cvv|passport|documents)\b",
        "credential_or_document_request",
    ),
    # EN: prison / urgency / pity-based money pressure
    (
        r"\b(he|she|they|my\s+(partner|husband|wife|boyfriend|girlfriend))\s+(is\s+)?in\s+(prison|jail)\b.*\b(money|funds|loan|bail)\b",
        "prison_money_pressure",
    ),
    (
        r"\b(in\s+(prison|jail))\b.*\b(needs?|asks?|wants?)\s+(money|funds|loan)\b",
        "prison_money_pressure",
    ),

    # RU: просьбы взять кредит / занять деньги
    (
        r"\b(он|она|муж|жена|партнер|партнёр|парень|девушка)\s+(просит|просил|просила|хочет|требует|настаивает|заставляет)\s+(меня\s+)?(взять|оформить|подписать|получить)\s+(кредит|займ|заём|ипотеку|ссуду)\b",
        "request_to_take_loan",
    ),
    (
        r"\b(взять|оформить|подписать|получить)\s+(кредит|займ|заём|ипотеку|ссуду)\s+(для|на)\s+(него|неё|нее|них|мужа|жены|партнера|партнёра|парня|девушки)\b",
        "request_to_take_loan",
    ),
    (
        r"\b(он|она)\s+(просит|просил|просила|требует|хочет)\s+(меня\s+)?(занять|одолжить|взять\s+в\s+долг)\s+(деньги|денег|сумму)\b",
        "request_to_borrow_money",
    ),
    # RU: давление на перевод денег
    (
        r"\b(переведи|перевести|отправь|отправить|пришли|прислать|дай|отдай)\s+(ему|ей|им)\s+(деньги|денег|сумму|перевод)\b",
        "money_transfer_pressure",
    ),
    (
        r"\b(срочно|немедленно|прямо\s+сейчас)\s+(нужны|нужна|нужен|надо)\s+(деньги|денег|сумма|перевод)\b",
        "urgent_money_request",
    ),
    # RU: шантаж / вымогательство / мошенничество
    (r"\b(шантаж|шантажирует|шантажировал|шантажировала|шантажируют)\b", "blackmail"),
    (r"\b(вымогает|вымогательство|вымогал|вымогала|вымогают)\b", "extortion"),
    (r"\b(мошенник|мошенница|мошенничество|развод|разводит|кидала|кинул|кинула)\b", "scam"),
    (
        r"\b(угрожает|угрожал|угрожала)\s+.*\b(выложить|опубликовать|разослать|показать|слить)\s+.*\b(фото|видео|переписку|интим)\b",
        "blackmail_threats",
    ),
    # RU: требование кодов / документов / паролей
    (
        r"\b(просит|требует|хочет|просил|просила|требовал|требовала)\s+.*\b(код\s+из\s+смс|смс[-\s]?код|код\s+подтверждения|пароль\s+от|пин[-\s]?код|cvv|cvc|номер\s+карты|данные\s+карты|паспорт|документы)\b",
        "credential_or_document_request",
    ),
    (
        r"\b(отправь|отправить|пришли|прислать|дай|сообщи)\s+(ему|ей|им)\s+(код|пароль|пин|cvv|cvc|данные\s+карты|номер\s+карты|паспорт|документы)\b",
        "credential_or_document_request",
    ),
    # RU: тюрьма + деньги / срочность жалости
    (
        r"\b(он|она|муж|жена|партнер|партнёр|парень|девушка)\s+в\s+(тюрьме|сизо|колонии|зоне)\b.*\b(деньги|денег|кредит|залог|перевод)\b",
        "prison_money_pressure",
    ),
    (
        r"\bв\s+(тюрьме|сизо|колонии|зоне)\b.*\b(нужны|нужна|просит|просил|просила)\s+(деньги|денег|кредит|залог)\b",
        "prison_money_pressure",
    ),
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


def check_fraud_financial_pressure(message):
    """
    Проверяет признаки мошенничества, шантажа, финансового давления:
    просьбы взять кредит/занять/перевести деньги, требования кодов/документов,
    шантаж, вымогательство, scam, давление через тюрьму.
    Возвращает ('high', reason) или ('none', None).
    """
    if not message:
        return "none", None

    message_lower = message.lower()

    for pattern, reason in FRAUD_FINANCIAL_PATTERNS:
        if re.search(pattern, message_lower):
            logger.warning(f"FRAUD/FINANCIAL PRESSURE SAFETY CASE DETECTED: {reason}")
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
        "safety_category": "crisis",
        "show_technique": False,
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
            "safety_category": "abuse_violence",
            "show_technique": False,
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
        "safety_category": "abuse_violence",
        "show_technique": False,
        "needs_specialist_support": True,
    }


def check_history_for_safety_flags(conversation_history):
    """
    Сканирует conversation_history на наличие прошлых red flags.
    Возвращает True, если хотя бы одно user-сообщение содержало
    crisis, abuse/violence или fraud/financial-pressure триггер.
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
        fraud_level, _ = check_fraud_financial_pressure(content)
        if fraud_level == "high":
            return True

    return False


def get_fraud_financial_response(language="en", reason=None):
    """Safety-ответ при fraud / blackmail / financial pressure."""
    from prompts import normalize_language

    current_language = normalize_language(language)

    if current_language == "ru":
        return {
            "message": (
                "Спасибо, что поделился этим. То, что ты описываешь, похоже на серьезный red flag: "
                "это может быть давление, шантаж, вымогательство, мошенничество или финансовая манипуляция, "
                "а не обычный конфликт в отношениях. Сделай паузу и не принимай решений под давлением. "
                "Не переводи деньги, не бери кредит, не передавай документы, пароли, коды из СМС или банковские данные. "
                "Обратись к человеку, которому доверяешь, в банк, в службу поддержки или в полицию, "
                "если ситуация выглядит опасной."
            ),
            "detected_state": "safety_risk",
            "suggested_technique": "Пауза и защита",
            "technique_description": (
                "Не принимай решений сейчас. Не переводи деньги и не передавай данные. "
                "Свяжись с доверенным человеком, банком или службой поддержки."
            ),
            "risk_level": "high",
            "safety_mode": True,
            "safety_category": "fraud_blackmail_financial_pressure",
            "show_technique": False,
            "needs_specialist_support": True,
        }

    return {
        "message": (
            "Thank you for sharing this. What you describe sounds like a serious red flag: "
            "this can be pressure, blackmail, extortion, a scam, or financial manipulation, "
            "not a normal relationship conflict. Pause and do not make decisions under pressure. "
            "Do not transfer money, do not take a loan, and do not share documents, passwords, "
            "verification codes, or banking data. Reach out to a trusted person, your bank, "
            "platform support, or the police if the situation looks dangerous."
        ),
        "detected_state": "safety_risk",
        "suggested_technique": "Pause and protect",
        "technique_description": (
            "Do not decide now. Do not transfer money or share personal data. "
            "Contact a trusted person, your bank, or a support service."
        ),
        "risk_level": "high",
        "safety_mode": True,
        "safety_category": "fraud_blackmail_financial_pressure",
        "show_technique": False,
        "needs_specialist_support": True,
    }


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
            "safety_category": "safety_followup",
            "show_technique": False,
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
        "safety_category": "safety_followup",
        "show_technique": False,
        "needs_specialist_support": True,
    }
