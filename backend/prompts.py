import re


SUPPORTED_LANGUAGES = {"en", "ru"}


def normalize_language(language):
    if isinstance(language, str) and language.lower() in SUPPORTED_LANGUAGES:
        return language.lower()
    return "en"


def detect_explicit_response_language(message):
    """Detect explicit requests like 'reply in Russian/English' inside user text."""
    if not isinstance(message, str):
        return None

    text = message.lower()

    russian_request_patterns = [
        r"(reply|respond|answer|write)\s+(in\s+)?russian",
        r"(отвечай|ответь|пиши|напиши)\s+на\s+русском",
        r"на\s+русском\s+(языке)?",
    ]
    english_request_patterns = [
        r"(reply|respond|answer|write)\s+(in\s+)?english",
        r"(отвечай|ответь|пиши|напиши)\s+на\s+английском",
        r"на\s+английском\s+(языке)?",
    ]

    for pattern in russian_request_patterns:
        if re.search(pattern, text):
            return "ru"

    for pattern in english_request_patterns:
        if re.search(pattern, text):
            return "en"

    return None


def detect_user_language(message, fallback="en"):
    """Heuristic language detection: Cyrillic -> RU, Latin -> EN."""
    if not isinstance(message, str) or not message.strip():
        return normalize_language(fallback)

    text = message.strip()
    cyrillic_count = len(re.findall(r"[А-Яа-яЁё]", text))
    latin_count = len(re.findall(r"[A-Za-z]", text))

    if cyrillic_count > latin_count:
        return "ru"
    if latin_count > cyrillic_count:
        return "en"

    return normalize_language(fallback)


def infer_response_language(message, fallback="en"):
    """Prefer explicit language request, otherwise infer from message content."""
    explicit = detect_explicit_response_language(message)
    if explicit:
        return explicit

    return detect_user_language(message, fallback=fallback)


BASE_SYSTEM_PROMPT = """You are an AI relationship consultant focused on interpersonal relationships.

YOUR ROLE:
- Help the user understand feelings, patterns, and relationship situations more clearly.
- Ask 2-4 focused follow-up questions when more context is needed.
- Identify the user's relationship state from the allowed state list.
- Suggest one concrete technique or exercise that fits the situation.

DO NOT:
- Do not diagnose mental health conditions.
- Do not manipulate or pressure the user toward a decision.
- Do not take sides in a conflict.
- Do not give clinical or medical advice.
- If the user appears to be in crisis (suicidal ideation or self-harm), clearly note it in the JSON so the dedicated safety layer can handle it.
- If there are signs of violence, threats, coercive control, fear for safety, sexual coercion, strangulation, being physically hit/pushed, or being prevented from leaving:
    - treat this as a serious safety red flag,
    - set "risk_level" to "high",
    - prioritize safety-focused guidance,
    - do not frame this as a normal communication conflict,
    - do not suggest "just talk calmly" or "listen more to partner" as the main approach.

ALLOWED detected_state VALUES:
1. anxiety_in_relationship
2. resentment_after_conflict
3. distance_coldness
4. lack_of_communication
5. trust_issues
6. loneliness_despite_relationship
7. incompatibility_questions
8. low_self_worth_in_context
9. unknown

RESPONSE FORMAT:
Always return valid JSON only:
{
    "message": "An empathic response plus 2-4 clarifying questions when useful",
    "detected_state": "one of the allowed values above or 'unknown'",
    "suggested_technique": "Technique name",
    "technique_description": "Short practical instruction",
    "risk_level": "none" or "high"
}

TECHNIQUE EXAMPLES:
- anxiety_in_relationship: "Box breathing"
- resentment_after_conflict: "Perspective reframing"
- distance_coldness: "Micro-moments of connection"
- lack_of_communication: "Active listening"
- trust_issues: "Trust journal"
- loneliness_despite_relationship: "Unsent letter"
- incompatibility_questions: "Values alignment check"
- low_self_worth_in_context: "Grounded self-affirmations"

Keep the tone warm, steady, and practical. You are an AI relationship consultant, not a psychologist."""


LANGUAGE_PROMPT_ADDONS = {
    "en": """LANGUAGE LAYER:
- Respond in English by default.
- If the user explicitly asks for another response language, follow that request.""",
    "ru": """ЯЗЫКОВАЯ НАДСТРОЙКА:
- Отвечай по-русски по умолчанию.
- Если пользователь явно просит другой язык ответа, следуй этой просьбе.""",
}


def get_system_prompt(language="en"):
    current_language = normalize_language(language)
    return f"{BASE_SYSTEM_PROMPT}\n\n" f"{LANGUAGE_PROMPT_ADDONS[current_language]}"


CRISIS_MESSAGES = {
    "en": """I am glad you told me this.

It sounds like you may be in a crisis right now. I cannot provide crisis support, but you should contact immediate human help now.

Please reach out to:
- Local emergency services right away
- A crisis hotline in your country
- A trusted person who can stay with you or contact help

If you are in immediate danger, call emergency services now.""",
    "ru": """Спасибо, что написал об этом.

Похоже, сейчас рядом с тобой может быть кризисная ситуация. Я не могу оказывать кризисную помощь, но тебе важно срочно обратиться к людям, которые могут помочь прямо сейчас.

Пожалуйста, обратись:
- В экстренные службы или скорую помощь
- На горячую линию кризисной помощи
- К близкому человеку, который сможет быть рядом и помочь обратиться за поддержкой

Если есть непосредственная опасность, звони в экстренные службы прямо сейчас.""",
}


def get_crisis_message(language="en"):
    return CRISIS_MESSAGES[normalize_language(language)]


TECHNIQUES = {
    "anxiety_in_relationship": {
        "name": "Box Breathing",
        "description": "Inhale for 4, hold for 4, exhale for 4, pause for 4. Repeat 5 times to calm the nervous system.",
    },
    "resentment_after_conflict": {
        "name": "Perspective Reframing",
        "description": "Ask yourself what remains valuable in the other person and what context may have shaped the conflict. Write the answers down.",
    },
    "distance_coldness": {
        "name": "Micro-Moments of Connection",
        "description": "Start with one small action: a warm smile, a gentle touch, or a sincere compliment.",
    },
    "lack_of_communication": {
        "name": "Active Listening",
        "description": "Repeat back what you heard and ask whether you understood correctly. It lowers defensiveness and builds clarity.",
    },
    "trust_issues": {
        "name": "Trust Journal",
        "description": "Write down 2-3 moments each day when reliability, honesty, or consistency showed up.",
    },
    "loneliness_despite_relationship": {
        "name": "Unsent Letter",
        "description": "Write a letter about your feelings without sending it immediately. It helps surface what you actually need.",
    },
    "incompatibility_questions": {
        "name": "Values Alignment Check",
        "description": "List the 5 qualities that matter most to you in a relationship, then compare them with what is happening in reality.",
    },
    "low_self_worth_in_context": {
        "name": "Grounded Self-Affirmations",
        "description": "Repeat a few believable affirmations each morning, such as 'I deserve respect' and 'My needs matter too'.",
    },
}
