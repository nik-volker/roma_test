# 💭 AI Психолог (MVP)

Веб-приложение для поддержки в вопросах отношений. AI определяет состояние, задаёт уточняющие вопросы и рекомендует конкретные техники.

## 🎯 Возможности MVP

✅ **8 типов состояний**: тревога, обида, отдаление, отсутствие общения, проблемы с доверием, одиночество, сомнения совместимости, низкая самооценка  
✅ **Интеллектуальные ответы**: OpenAI GPT-4o mini  
✅ **Детекция кризиса**: Распознает суицидальные намерения и показывает кризисное сообщение  
✅ **История в браузере**: Все данные хранятся в localStorage, приватно  
✅ **Спокойный дизайн**: Успокаивающие цвета и простой UI  

---

## 🏗️ Архитектура

```
Браузер (localStorage)
    ↓ HTTPS POST /api/chat
Flask API (Python)
    ↓ OpenAI API call
GPT-4o mini
    ↓ JSON response
```

**Frontend:** HTML + CSS + Vanilla JS (Vercel Static)  
**Backend:** Flask (Python 3.9+) как Vercel Python Function  
**API:** OpenAI GPT-4o mini  

---

## 🚀 Локальный запуск

### 1. Backend

```bash
cd backend

# Установляем зависимости
pip install -r requirements.txt

# Устанавливаем OPENAI_API_KEY
export OPENAI_API_KEY="sk-..."  # Linux/Mac
# или
set OPENAI_API_KEY=sk-...  # Windows

# Запускаем сервер
python app.py
```

Сервер будет доступен на `http://localhost:5000`

Проверка:
```bash
curl http://localhost:5000/api/health
# Должен вернуть: {"status":"ok"}
```

### 2. Frontend

Локально можно открыть `frontend/index.html` в браузере или использовать простой HTTP сервер:

```bash
cd frontend

# Python 3
python -m http.server 8000

# или используй Live Server в VS Code
```

Откройте `http://localhost:8000` в браузере.

`base_url` переключается автоматически:
- локально: `http://localhost:5000`
- на Vercel: same-origin (`/api/*`)

---

## 📦 Развертывание (Vercel, единый проект)

1. Запушь репозиторий на GitHub.
2. В [Vercel](https://vercel.com/) создай `New Project` и выбери этот репозиторий.
3. В `Environment Variables` добавь:
   - `OPENAI_API_KEY` (обязательно)
   - `FLASK_ENV=production` (опционально)
   - `CORS_ORIGINS` (опционально, если используешь custom domains)
4. Нажми `Deploy`.

Маршрутизация настроена через `vercel.json`:
- `/api/*` → Flask функция (`api/index.py`)
- `/` и статические файлы → `frontend/*`

После деплоя:
1. Проверь `https://<your-project>.vercel.app/api/health`
2. Открой главную страницу и отправь тестовое сообщение в чат.

---

## 🧪 Тестирование

### Тест 1: Health check
```bash
curl http://localhost:5000/api/health
# → {"status":"ok"}
```

### Тест 2: Простое сообщение
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Мы не разговариваем 3 дня"}'

# → JSON с detected_state, suggested_technique и т.д.
```

### Тест 3: Кризис
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Я не хочу жить"}'

# → Должен вернуть кризисное сообщение
```

### Тест 4: UI
1. Открой фронтенд в браузере
2. Напиши сообщение
3. Проверь, что ответ появляется
4. Проверь, что состояние отображается выше
5. Проверь, что техника рекомендуется

---

## 📝 Структура файлов

```
ai-psycho/
├── frontend/
│   ├── index.html           # Главная страница
│   ├── css/style.css        # Стили
│   └── js/
│       ├── app.js           # Точка входа
│       ├── chat.js          # UI логика
│       ├── api.js           # API клиент
│       └── constants.js     # Конфиги
│
├── backend/
│   ├── app.py               # Flask приложение
│   ├── config.py            # Конфигурация
│   ├── routes.py            # API endpoints
│   ├── ai_service.py        # OpenAI интеграция
│   ├── prompts.py           # System prompt и техники
│   ├── state_detector.py    # Классификация состояний
│   ├── safety_check.py      # Детекция кризиса
│   ├── requirements.txt     # Зависимости
│   └── Procfile             # Для Render/Railway
│
├── api/
│   └── index.py             # Entrypoint для Vercel Python Function
├── vercel.json              # Роутинг Vercel (frontend + /api)
├── .env.example             # Список обязательных/опциональных env
├── requirements.txt         # Root requirements для Vercel
│
└── README.md                # Этот файл
```

---

## 🔑 Переменные окружения

### Backend

`OPENAI_API_KEY` - API ключ от OpenAI (обязателен)  
`FLASK_ENV` - `development` или `production` (опционально, по умолчанию `development`)
`CORS_ORIGINS` - доп. домены через запятую (опционально)

Пример смотри в `.env.example`.

---

## ✅ Pre-Deploy Checklist (Vercel)

- [x] Используются фиксированные patched-версии зависимостей.
- [x] Учитывается deploy target Vercel (`vercel.json`, `api/index.py`).
- [x] Нет top-level init внешнего OpenAI клиента (ленивая инициализация).
- [x] Обязательные env перечислены в `.env.example`.
- [x] Секреты только на сервере (ключ OpenAI не хранится во фронтенде).
- [ ] Prisma шаги не применимы для этого проекта (Prisma отсутствует).
- [ ] Upload/large file flow не применимы для этого проекта (файловый upload отсутствует).
- [x] Перед деплоем проверять env, routes и runtime endpoints (`/api/health`, `/api/chat`).

---

## ⚠️ Safety

- **Детекция кризиса**: Сообщения с ключевыми словами (убить, самоповреждение и т.д.) получают специальный кризисный ответ
- **Приватность**: Все данные хранятся в браузере, не отправляются на сервер между сеансами
- **Логирование**: Кризис-события логируются на сервере для мониторинга (без PII)

---

## 🐛 Troubleshooting

### "Cannot POST /api/chat"
- Убедись, что backend запущен (`python app.py`)
- Проверь, что `base_url` в `constants.js` правильный
- Посмотри консоль браузера (F12 → Console)

### "CORS error"
- Backend должен быть на другом порту (5000)
- Проверь, что `CORS` включён в `config.py`
- Убедись в `origins` списке есть твой фронтенд URL

### "OpenAI API error"
- Проверь, что `OPENAI_API_KEY` установлен
- Убедись, что у тебя есть кредиты на счёте OpenAI
- Проверь лог ошибки в консоли сервера

---

## 📚 Ссылки

- [OpenAI API Docs](https://platform.openai.com/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Render Docs](https://render.com/docs)
- [Railway Docs](https://docs.railway.app/)

---

## 📄 Лицензия

MIT

---

**Версия:** MVP 1.0  
**Дата:** 2026-03-24