"""Детекция состояния на основе ответа AI"""


def extract_detected_state(ai_response_json):
    """
    Извлекает detected_state из JSON ответа от OpenAI.
    Если поле отсутствует, возвращает 'unknown'.
    """
    try:
        state = ai_response_json.get("detected_state", "unknown")
        # Проверяем, что это одно из допустимых состояний
        valid_states = [
            "anxiety_in_relationship",
            "resentment_after_conflict",
            "distance_coldness",
            "lack_of_communication",
            "trust_issues",
            "loneliness_despite_relationship",
            "incompatibility_questions",
            "low_self_worth_in_context",
            "unknown",
        ]
        if state in valid_states:
            return state
        return "unknown"
    except Exception:
        return "unknown"
