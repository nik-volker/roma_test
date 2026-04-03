import os
from flask_cors import CORS

# OpenAI и Flask конфиг
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL = "gpt-4o-mini"  # GPT-4.1 mini model
FLASK_ENV = os.getenv("FLASK_ENV", "development")


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
            }
        },
    )
