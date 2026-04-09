"""API маршруты"""

import logging
from flask import Blueprint, request, jsonify, session
from ai_service import call_openai
from safety_check import (
    check_crisis,
    check_abuse_violence,
    check_history_for_safety_flags,
    get_crisis_response,
    get_abuse_violence_response,
    get_safety_mode_followup_response,
)
from prompts import infer_response_language

logger = logging.getLogger(__name__)

api = Blueprint("api", __name__, url_prefix="/api")


@api.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"}), 200


@api.route("/chat", methods=["POST"])
def chat():
    """
    Endpoint для чата.

    Ожидает:
    {
        "message": "текст сообщения",
        "history": [{"role": "user", "content": "..."}, ...],  # опционально
        "language": "en" | "ru"  # опционально, сохраняется для обратной совместимости
    }

    Возвращает:
    {
        "message": "ответ AI",
        "detected_state": "anxiety_in_relationship",
        "suggested_technique": "Box breathing",
        "technique_description": "...",
        "risk_level": "none" или "high"
    }
    """
    try:
        data = request.get_json(silent=True)

        if not data or "message" not in data:
            return jsonify({"error": "Missing 'message' field"}), 400

        user_message = data.get("message", "").strip()
        conversation_history = data.get("history", [])
        # Язык интерфейса не должен управлять ответом модели.
        # Язык ответа определяется текстом пользователя и его явными просьбами.
        language = infer_response_language(user_message)

        if not user_message:
            return jsonify({"error": "Empty message"}), 400

        # Если history пустая или почти пустая, считаем это новой сессией диалога.
        if len(conversation_history) <= 1:
            session.pop("safety_mode", None)

        # 1. Проверяем суицидальный/кризисный риск
        risk_level, crisis_keyword = check_crisis(user_message)

        if risk_level == "high":
            logger.warning(f"Crisis detected: {crisis_keyword}")
            session["safety_mode"] = True
            return jsonify(get_crisis_response(language=language)), 200

        # 2. Проверяем признаки насилия/угроз/абьюза до обычного flow
        abuse_risk, abuse_reason = check_abuse_violence(user_message)
        if abuse_risk == "high":
            logger.warning(f"Abuse/violence safety case detected: {abuse_reason}")
            session["safety_mode"] = True
            return jsonify(get_abuse_violence_response(language=language)), 200

        # 3. Если safety-mode уже активирован в этой сессии, не возвращаемся в обычный flow.
        #    Проверяем session cookie И историю (на случай потери cookie).
        if session.get("safety_mode") or check_history_for_safety_flags(
            conversation_history
        ):
            session["safety_mode"] = True
            logger.info(
                "Session safety_mode is active, returning safety follow-up response"
            )
            return jsonify(get_safety_mode_followup_response(language=language)), 200

        ai_response = call_openai(user_message, conversation_history, language=language)

        logger.info(
            f"Chat response: detected_state={ai_response.get('detected_state')}"
        )

        return jsonify(ai_response), 200

    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500
