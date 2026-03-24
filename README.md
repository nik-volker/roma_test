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

**Frontend:** HTML + CSS + Vanilla JS (GitHub Pages)  
**Backend:** Flask (Python 3.9+) на Render или Railway  
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

**Важно:** Обновите `base_url` в `frontend/js/constants.js` на `http://localhost:5000` для локального тестирования.

---

## 📦 Развертывание

### Backend (выбери один)

#### Вариант 1: Render

1. Сделай форк репо на GitHub
2. На [render.com](https://render.com/):
   - Создай новый Web Service
   - Укажи git-репо
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
   - Добавь env переменную `OPENAI_API_KEY`
3. После деплоя получишь URL, например: `https://ai-psycho-backend.onrender.com`

#### Вариант 2: Railway

1. На [railway.app](https://railway.app/):
   - Создай новый проект
   - Connect repo
   - Railway автоматически обнаружит `Procfile`
   - Добавь env переменную `OPENAI_API_KEY`

**Копируй URL бэкенда** (например: `https://ai-psycho-backend.onrender.com`)

### Frontend (GitHub Pages)

1. Обнови `base_url` в `frontend/js/constants.js`:
   ```javascript
   base_url: 'https://ai-psycho-backend.onrender.com'
   ```

2. На GitHub:
   - Создай репо `username.github.io` (если его нет) или используй существующий
   - Загрузи содержимое `frontend/` в корень или в папку `/docs`
   - Включи GitHub Pages в настройках репо
   - Откройся по `https://username.github.io/` (или `/ai-psycho/` если в подпапке)

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
└── README.md                # Этот файл
```

---

## 🔑 Переменные окружения

### Backend

`OPENAI_API_KEY` - API ключ от OpenAI (обязателен)  
`FLASK_ENV` - `development` или `production` (опционально, по умолчанию `development`)

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