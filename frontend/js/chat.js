/**
 * chat.js - UI логика чата
 */
import { STATES, STATE_COLORS } from './constants.js';

export class ChatUI {
    constructor() {
        this.chatContainer = document.getElementById('chat-container');
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        this.stateIndicator = document.getElementById('state-indicator');
        this.techniqueBox = document.getElementById('technique-box');
    }

    addMessage(text, sender = 'user') {
        const messageEl = document.createElement('div');
        messageEl.className = `message message-${sender}`;
        messageEl.innerHTML = `<p>${this.escapeHtml(text)}</p>`;
        this.chatContainer.appendChild(messageEl);
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }

    addAIResponse(response) {
        const state = response?.detected_state || 'unknown';
        const stateLabel = STATES[state] || state;
        const stateColor = STATE_COLORS[state] || '#999';
        const aiMessage = response?.message || 'Я рядом. Расскажи чуть подробнее, что происходит.';
        const suggestedTechnique = response?.suggested_technique || 'Техника';
        const techniqueDescription = response?.technique_description || 'Попробуй ещё раз';

        // Основное сообщение
        const messageEl = document.createElement('div');
        messageEl.className = 'message message-ai';
        messageEl.innerHTML = `<p>${this.escapeHtml(aiMessage)}</p>`;
        this.chatContainer.appendChild(messageEl);

        // Блок с состоянием и техникой
        const infoEl = document.createElement('div');
        infoEl.className = 'ai-info-block';
        infoEl.innerHTML = `
            <div class="state-tag" style="background-color: ${stateColor}">
                <strong>Состояние:</strong> ${this.escapeHtml(stateLabel)}
            </div>
            <div class="technique-suggestion">
                <strong>💡 Техника:</strong> <em>${this.escapeHtml(suggestedTechnique)}</em><br>
                <span class="technique-desc">${this.escapeHtml(techniqueDescription)}</span>
            </div>
        `;
        this.chatContainer.appendChild(infoEl);

        // Обновляем индикатор вверху
        if (state !== 'unknown' && state !== 'crisis') {
            this.updateStateIndicator(state, stateLabel, stateColor);
        } else if (state === 'crisis') {
            this.updateStateIndicator(state, '⚠️ КРИЗИС', '#FF3333');
        }

        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }

    updateStateIndicator(state, label, color) {
        this.stateIndicator.innerHTML = `
            <span style="background-color: ${color}; padding: 5px 10px; border-radius: 5px; color: white;">
                ${this.escapeHtml(label)}
            </span>
        `;
    }

    clearInput() {
        this.messageInput.value = '';
        this.messageInput.focus();
    }

    disableSending(disabled = true) {
        this.sendButton.disabled = disabled;
        if (disabled) {
            this.sendButton.textContent = 'Отправляю...';
        } else {
            this.sendButton.textContent = 'Отправить';
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    getChatHistory() {
        /**
         * Извлекает историю чата из DOM.
         * Формирует массив сообщений для отправки на сервер.
         */
        const messages = [];
        const messageElements = this.chatContainer.querySelectorAll('.message');

        messageElements.forEach(el => {
            const text = el.innerText.trim();
            if (text) {
                if (el.classList.contains('message-user')) {
                    messages.push({ role: 'user', content: text });
                } else if (el.classList.contains('message-ai')) {
                    messages.push({ role: 'assistant', content: text });
                }
            }
        });

        return messages;
    }

    showError(errorText) {
        const errorEl = document.createElement('div');
        errorEl.className = 'message message-error';
        errorEl.innerHTML = `<p>❌ ${this.escapeHtml(errorText)}</p>`;
        this.chatContainer.appendChild(errorEl);
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }

    clearChat() {
        this.chatContainer.innerHTML = '';
        this.stateIndicator.innerHTML = '';
        localStorage.removeItem('chatHistory');
    }
}
