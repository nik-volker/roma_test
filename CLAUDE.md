# CLAUDE.md — заметки для Claude по проекту AI Relationship Consultant

Этот файл — рабочая инструкция для Claude. Читай его перед любыми действиями в репозитории и следуй правилам ниже.

---

## 1. Что это за проект

Веб-чат-консультант по отношениям. Один POST-эндпоинт `/api/chat` поверх OpenAI.
- БД нет.
- Авторизации нет.
- История чата хранится в `localStorage` браузера.
- На сервере есть только Flask-сессия с флагом `safety_mode` (cookie).

## 2. Стек

- **Backend:** Python 3.9+, Flask 3.0.3, flask-cors 5.0.0, OpenAI SDK 1.75.0 (модель `gpt-4.1`), python-dotenv, gunicorn.
- **Frontend:** чистый HTML + CSS + Vanilla JS (ES modules). Сборщика нет, `package.json` нет.
- **Хостинг:** Vercel (`@vercel/python` + `@vercel/static`). `backend/Procfile` — запасной вариант для Render/Railway.
- **Тесты:** `unittest` + смок-скрипты на `requests`.

## 3. Структура папок

- [api/index.py](api/index.py) — entrypoint Vercel-функции, добавляет `backend/` в `sys.path` и импортирует Flask `app`.
- [backend/](backend/) — Flask-приложение:
  - [app.py](backend/app.py) — фабрика приложения и обработчики ошибок.
  - [config.py](backend/config.py) — env, CORS, cookie-настройки.
  - [routes.py](backend/routes.py) — `/api/health` и `/api/chat`.
  - [ai_service.py](backend/ai_service.py) — интеграция с OpenAI.
  - [prompts.py](backend/prompts.py) — system prompt, i18n, техники.
  - [safety_check.py](backend/safety_check.py) — детекция кризиса, насилия, sticky safety-mode.
  - [state_detector.py](backend/state_detector.py) — валидация detected_state.
  - `test_*.py` — юнит и смок-тесты.
- [frontend/](frontend/) — статика:
  - [index.html](frontend/index.html), [css/style.css](frontend/css/style.css).
  - [js/app.js](frontend/js/app.js) — bootstrap, язык, отправка сообщений.
  - [js/chat.js](frontend/js/chat.js) — UI чата.
  - [js/api.js](frontend/js/api.js) — fetch + fallback URL.
  - [js/constants.js](frontend/js/constants.js) — i18n, цвета состояний, base URL.
- Корень: [vercel.json](vercel.json) — единственный live-конфиг деплоя; [requirements.txt](requirements.txt) — реэкспорт `backend/requirements.txt` для Vercel build.

## 4. Команды

### Запуск (dev)

- Backend: `cd backend && pip install -r requirements.txt && python app.py` → `http://localhost:5000`. Требует переменную `OPENAI_API_KEY`.
- Frontend: `cd frontend && python -m http.server 8000` → `http://localhost:8000`.

`base_url` фронта переключается автоматически в [frontend/js/constants.js:60](frontend/js/constants.js#L60): локально — `http://localhost:5000`, в проде — same-origin с фоллбеком на `https://psycho-back.vercel.app`.

### Сборка

Сборки как таковой нет: фронт — статичный, бэк — Flask-функция, Vercel собирает оба билда сам по [vercel.json](vercel.json). Линтеров и форматтеров не настроено — самостоятельно их не вводить.

### Проверка

- Health: `curl http://localhost:5000/api/health` → `{"status":"ok"}`.
- Юнит-тесты safety:
  ```
  cd backend && python -m unittest test_safety_checks test_safety_session_mode
  ```
- Смок API (требует запущенный backend): `python backend/test_api.py`.
- Смок фронт + бэк (требует оба сервера): `python test_frontend.py`.
- Production-запуск под Procfile: из папки `backend` команда `gunicorn app:app`.

## 5. Конфиг и env

- Файлы примеров: [.env.example](.env.example), [backend/.env.example](backend/.env.example).
- Обязательно: `OPENAI_API_KEY`.
- В проде обязательно задавать `SECRET_KEY` — дефолт `"dev-safety-session-key"` в [backend/config.py:8](backend/config.py#L8) небезопасен.
- `FLASK_ENV`, `CORS_ORIGINS`, `SESSION_COOKIE_SAMESITE`, `SESSION_COOKIE_SECURE` — опциональны.
- Реальные `.env` лежат в `.gitignore` и в коммиты не попадают.

## 6. Правила работы с кодом

1. **Сначала план, потом изменения.** Перед любой нетривиальной правкой описывай план: какие файлы, какие функции, какой ожидаемый эффект, какие риски. Дождись подтверждения от пользователя — и только потом редактируй.
2. **Никаких больших изменений без согласования.** Рефакторинг, переименование модулей, смена архитектуры, обновления зависимостей, перенос логики между файлами, массовая замена конвенций — только после явного «да». Когда сомневаешься, считай изменение «большим».
3. **Не удаляй файлы без разрешения.** Это касается исходников, тестов, конфигов, `.env*`, скриптов, документации, бэкапов. Если что-то выглядит лишним — спроси, а не удаляй.
4. **Не меняй env-переменные без согласования.** Не редактируй реальные `.env` файлы. Файлы `.env.example` можно менять только после согласования, если задача требует добавить или изменить переменные окружения. Не добавляй новые переменные и не убирай существующие без подтверждения. Не подставляй значения секретов в код или коммиты.
5. **После изменений запускай доступные проверки.** Минимум: `python -m unittest test_safety_checks test_safety_session_mode` из `backend/`. Если правил backend — прогоняй `backend/test_api.py` (с поднятым сервером). Если правил фронт или интеграцию — `test_frontend.py`. Результат сообщай в ответе. Если проверку невозможно запустить из-за отсутствия сервера, ключей, зависимостей или окружения, явно сообщи причину и укажи, какую проверку нужно выполнить вручную.
6. **Точечные правки.** Не добавляй фичи, абстракции, обработку ошибок и комментарии «на будущее» сверх того, что требует задача.
7. **Не вводи новые инструменты молча.** Никаких линтеров, форматтеров, сборщиков, package-менеджеров, ORM, миграционных систем, фреймворков без согласования.
8. **Безопасность.** Не отключай safety-проверки, не ослабляй CORS, не убирай `SESSION_COOKIE_SECURE/HTTPONLY`, не логируй PII или содержимое чатов.
9. **Не выдумывай информацию о проекте.** Если информации о проекте нет в файлах репозитория, не выдумывай. Сначала проверь файлы, затем задай уточняющий вопрос.
10. **Маленькие логические блоки.** Делай изменения маленькими логическими блоками. Не смешивай исправление бага, рефакторинг и улучшение UX в одной правке без согласования.

## 7. Критические зоны — особая осторожность

- **Safety-логика.** [backend/safety_check.py](backend/safety_check.py) (`CRISIS_KEYWORDS`, `ABUSE_VIOLENCE_PATTERNS`) и порядок проверок в [backend/routes.py](backend/routes.py) (crisis → abuse → sticky safety_mode → обычный flow). Любая правка требует прогона `test_safety_checks.py` и `test_safety_session_mode.py`.
- **System prompt.** [backend/prompts.py](backend/prompts.py) — длинный, регулирует границы темы, фрод, абьюз, гендерные формы, обращение «ты/вы». Правки только точечные.
- **Sticky safety-mode.** Реализован двумя путями (cookie + скан истории) — оба нужны для cross-origin без кук, не выпиливать.
- **Модель OpenAI.** Захардкожена в [backend/config.py:6](backend/config.py#L6). Менять только по явной просьбе.
- **CORS и cookie.** В [backend/config.py](backend/config.py) `supports_credentials=True` и regex `https://.*\.vercel\.app`. Менять с пониманием последствий.

## 8. Чего в проекте нет (не выдумывать)

- БД, миграций, ORM.
- Авторизации, rate-limiting, биллинга.
- Сборщика фронта, `package.json`, тайпчекинга.
- Фичефлагов, A/B-тестов.
- CI/CD-конфига в репозитории (деплой делает Vercel по push).

## 9. Чек-лист перед сдачей правки

- [ ] План был согласован (для нетривиальных правок).
- [ ] Не удалены файлы без разрешения.
- [ ] `.env*` не тронуты.
- [ ] Прогнаны юнит-тесты safety.
- [ ] При правках в backend — прогнан `backend/test_api.py` (если применимо).
- [ ] При правках во frontend — открыта страница в браузере, проверены golden path и кризисный сценарий.
- [ ] В ответе пользователю указано, что именно изменилось и какие проверки выполнены.

## 10. Формат ответа пользователю

- Отвечай кратко и по делу.
- Для задач по коду используй структуру:
  1. Что нашел.
  2. План.
  3. Какие файлы будут затронуты.
  4. Риски.
  5. Какие проверки выполнить.
- Не используй длинные вступления.
