import os
from flask_cors import CORS

# OpenAI и Flask конфиг
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL = "gpt-4.1"  # GPT-4.1 model
FLASK_ENV = os.getenv("FLASK_ENV", "development")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-safety-session-key")


def get_session_cookie_settings():
    """Настройки cookie-сессии с учетом cross-domain deploy."""
    is_production = FLASK_ENV == "production"

    samesite = os.getenv(
        "SESSION_COOKIE_SAMESITE",
        "None" if is_production else "Lax",
    )
    secure_raw = os.getenv(
        "SESSION_COOKIE_SECURE",
        "true" if is_production else "false",
    )
    secure = secure_raw.strip().lower() in {"1", "true", "yes", "on"}

    return {
        "SESSION_COOKIE_SAMESITE": samesite,
        "SESSION_COOKIE_SECURE": secure,
        "SESSION_COOKIE_HTTPONLY": True,
    }


def setup_cors(app):
    """Настройка CORS для фронтенда"""
    extra_origins = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "").split(",")
        if origin.strip()
    ]

    allowed_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        r"https://.*\.vercel\.app",
        *extra_origins,
    ]

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": allowed_origins,
                "methods": ["GET", "POST"],
                "allow_headers": ["Content-Type"],
                "supports_credentials": True,
            }
        },
    )
