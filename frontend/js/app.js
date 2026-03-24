/**
 * app.js - Главная логика приложения
 */
import { APIClient } from './api.js';
import { ChatUI } from './chat.js';

class App {
    constructor() {
        this.api = new APIClient();
        this.chat = new ChatUI();
        this.init();
    }

    async init() {
        console.log('Initalizing app...');

        // Проверяем, доступен ли сервер
        const isHealthy = await this.api.health();
        if (!isHealthy) {
            console.warn('Backend is not available. Using local mode or will try later.');
        }

        // Загружаем сохранённую историю из localStorage
        this.loadChatHistory();

        // Обработчики событий
        this.chat.sendButton.addEventListener('click', () => this.sendMessage());
        this.chat.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Кнопка "Очистить чат"
        const clearButton = document.getElementById('clear-button');
        if (clearButton) {
            clearButton.addEventListener('click', () => {
                if (confirm('Вы уверены? История чата будет удалена.')) {
                    this.chat.clearChat();
                }
            });
        }

        console.log('App initialized');
    }

    async sendMessage() {
        const message = this.chat.messageInput.value.trim();

        if (!message) {
            alert('Напишите сообщение');
            return;
        }

        // Отправляем сообщение в UI
        this.chat.addMessage(message, 'user');
        this.chat.clearInput();
        this.chat.disableSending(true);

        try {
            // Получаем историю для отправки серверу
            const history = this.chat.getChatHistory();

            // Отправляем на API
            const response = await this.api.sendMessage(message, history);

            // Добавляем ответ в UI
            this.chat.addAIResponse(response);

            // Сохраняем историю в localStorage
            this.saveChatHistory();

        } catch (error) {
            console.error('Error:', error);
            this.chat.showError(error.message || 'Ошибка при обращении к серверу');
        } finally {
            this.chat.disableSending(false);
            this.chat.messageInput.focus();
        }
    }

    saveChatHistory() {
        const messages = [];
        document.querySelectorAll('.message').forEach(el => {
            const text = el.innerText.trim();
            if (text) {
                if (el.classList.contains('message-user')) {
                    messages.push({ role: 'user', text });
                } else if (el.classList.contains('message-ai')) {
                    messages.push({ role: 'assistant', text });
                }
            }
        });
        localStorage.setItem('chatHistory', JSON.stringify(messages));
    }

    loadChatHistory() {
        const saved = localStorage.getItem('chatHistory');
        if (saved) {
            try {
                const messages = JSON.parse(saved);
                messages.forEach(msg => {
                    this.chat.addMessage(msg.text, msg.role);
                });
            } catch (e) {
                console.error('Failed to load chat history:', e);
            }
        }
    }
}

// Инициализируем когда DOM готов
document.addEventListener('DOMContentLoaded', () => {
    new App();
});
