/**
 * app.js - Главная логика приложения
 */
import { APIClient } from './api.js';
import { ChatUI } from './chat.js';
import { STATE_LABELS, STORAGE_KEYS, SUPPORTED_LANGUAGES, UI_TEXT } from './constants.js';

class App {
    constructor() {
        this.api = new APIClient();
        this.language = this.getInitialLanguage();
        this.chat = new ChatUI({
            language: this.language,
            translations: UI_TEXT,
            stateLabels: STATE_LABELS
        });
        this.init();
    }

    async init() {
        console.log('Initalizing app...');

        this.applyLanguage();

        const isHealthy = await this.api.health();
        if (!isHealthy) {
            console.warn('Backend is not available. Using local mode or will try later.');
        }

        this.loadChatHistory();
        this.syncHeroVisibility();

        this.chat.sendButton.addEventListener('click', () => this.sendMessage());
        this.chat.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        const langSelect = document.getElementById('lang-select');
        if (langSelect) {
            langSelect.addEventListener('change', (event) => {
                this.setLanguage(event.target.value);
            });
        }

        const clearButton = document.getElementById('clear-button');
        if (clearButton) {
            clearButton.addEventListener('click', () => {
                if (window.confirm(this.t('clearChatConfirm'))) {
                    this.chat.clearChat();
                    localStorage.removeItem(STORAGE_KEYS.chatHistory);
                    this.syncHeroVisibility();
                }
            });
        }

        console.log('App initialized');
    }

    getInitialLanguage() {
        const savedLanguage = localStorage.getItem(STORAGE_KEYS.language);

        if (SUPPORTED_LANGUAGES.includes(savedLanguage)) {
            return savedLanguage;
        }

        return 'en';
    }

    t(key) {
        return UI_TEXT[this.language]?.[key] || key;
    }

    setLanguage(language) {
        if (!SUPPORTED_LANGUAGES.includes(language) || language === this.language) {
            return;
        }

        this.language = language;
        localStorage.setItem(STORAGE_KEYS.language, language);
        this.applyLanguage();
    }

    applyLanguage() {
        document.documentElement.lang = this.language;
        document.title = this.t('pageTitle');

        document.querySelectorAll('[data-i18n]').forEach((element) => {
            const key = element.dataset.i18n;
            element.textContent = this.t(key);
        });

        this.chat.messageInput.placeholder = this.t('messagePlaceholder');
        this.chat.sendButton.textContent = this.t('send');
        document.getElementById('clear-button').textContent = this.t('clear');

        const langSelect = document.getElementById('lang-select');
        if (langSelect) {
            langSelect.value = this.language;
        }

        this.chat.setLanguage(this.language);
    }

    async sendMessage() {
        const message = this.chat.messageInput.value.trim();

        if (!message) {
            window.alert(this.t('emptyMessageAlert'));
            return;
        }

        this.chat.addMessage(message, 'user');
        this.syncHeroVisibility();
        this.chat.clearInput();
        this.chat.disableSending(true);

        try {
            const history = this.chat.getChatHistory();

            const response = await this.api.sendMessage(message, history);

            this.chat.addAIResponse(response);

            this.saveChatHistory();

        } catch (error) {
            console.error('Error:', error);
            this.chat.showError(error.message || this.t('errorFallback'));
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
        localStorage.setItem(STORAGE_KEYS.chatHistory, JSON.stringify(messages));
    }

    loadChatHistory() {
        const saved = localStorage.getItem(STORAGE_KEYS.chatHistory);
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

    syncHeroVisibility() {
        const appShell = document.querySelector('.app-shell');
        if (!appShell) {
            return;
        }

        const hasMessages = document.querySelectorAll('#chat-container .message').length > 0;
        appShell.classList.toggle('has-chat-history', hasMessages);
    }
}

// Инициализируем когда DOM готов
document.addEventListener('DOMContentLoaded', () => {
    new App();
});
