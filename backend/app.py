"""Flask приложение - точка входа"""

import logging
import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла ДО импорта других модулей
load_dotenv()

from flask import Flask, jsonify
from config import setup_cors, FLASK_ENV, SECRET_KEY
from routes import api

# Конфигурация логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_app():
    """Создание и конфигурация Flask приложения"""
    app = Flask(__name__)

    # Конфигурация
    app.config["ENV"] = FLASK_ENV
    app.config["JSON_AS_ASCII"] = False  # Поддержка кириллицы в JSON
    app.config["SECRET_KEY"] = SECRET_KEY

    # CORS
    setup_cors(app)

    # Регистрация blueprints
    app.register_blueprint(api)

    logger.info(f"Flask app created (ENV={FLASK_ENV})")

    return app


app = create_app()


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    logger.info("Starting Flask server on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
