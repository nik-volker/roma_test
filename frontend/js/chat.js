/**
 * chat.js - UI логика чата
 */
import { STATE_COLORS } from './constants.js';

export class ChatUI {
    constructor({ language = 'en', translations = {}, stateLabels = {} } = {}) {
        this.chatContainer = document.getElementById('chat-container');
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        this.stateIndicator = document.getElementById('state-indicator');
        this.stateIndicatorWrapper = document.querySelector('.state-indicator-wrapper');
        this.translations = translations;
        this.stateLabels = stateLabels;
        this.currentLanguage = language;
        this.currentStateMeta = null;
        this.syncStateIndicatorVisibility();
    }

    setLanguage(language) {
        this.currentLanguage = language;
        this.disableSending(this.sendButton.disabled);

        if (this.currentStateMeta) {
            const { state, color } = this.currentStateMeta;
            this.updateStateIndicator(state, this.getStateLabel(state), color);
        }
    }

    translate(key) {
        return this.translations?.[this.currentLanguage]?.[key] || key;
    }

    getStateLabel(state) {
        return this.stateLabels?.[this.currentLanguage]?.[state] || state;
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
        const hasKnownState = Object.prototype.hasOwnProperty.call(this.stateLabels?.[this.currentLanguage] || {}, state);
        const showState = state !== 'unknown' && state !== 'crisis' && hasKnownState;
        const stateLabel = this.getStateLabel(state);
        const stateColor = STATE_COLORS[state] || '#999';
        const aiMessage = response?.message || this.translate('errorFallback');
        const rawTechnique = response?.suggested_technique;
        const invalidTechniques = ['none', 'null', 'unknown', 'undefined', ''];
        const hasTechnique = rawTechnique && !invalidTechniques.includes(rawTechnique.toLowerCase().trim());
        const suggestedTechnique = hasTechnique ? rawTechnique : null;
        const techniqueDescription = hasTechnique ? (response?.technique_description || '') : null;

        const messageEl = document.createElement('div');
        messageEl.className = 'message message-ai';
        messageEl.innerHTML = `<p>${this.escapeHtml(aiMessage)}</p>`;
        this.chatContainer.appendChild(messageEl);

        const infoEl = document.createElement('div');
        infoEl.className = 'ai-info-block';
        infoEl.innerHTML = `
            ${showState ? `
            <div class="state-tag" style="background-color: ${stateColor}">
                <strong>${this.escapeHtml(this.translate('stateLabel'))}:</strong> ${this.escapeHtml(stateLabel)}
            </div>
            ` : ''}
            ${hasTechnique ? `
            <div class="technique-suggestion">
                <strong>${this.escapeHtml(this.translate('techniqueLabel'))}:</strong> <em>${this.escapeHtml(suggestedTechnique)}</em><br>
                <span class="technique-desc">${this.escapeHtml(techniqueDescription)}</span>
            </div>
            ` : ''}
        `;
        this.chatContainer.appendChild(infoEl);

        if (state !== 'unknown' && state !== 'crisis') {
            this.updateStateIndicator(state, stateLabel, stateColor);
        } else if (state === 'crisis') {
            this.updateStateIndicator(state, this.translate('crisisState'), '#B94A48');
        }

        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }

    updateStateIndicator(state, label, color) {
        this.currentStateMeta = { state, color };
        this.stateIndicator.innerHTML = `
            <span class="state-indicator-pill" style="background-color: ${color};">
                ${this.escapeHtml(label)}
            </span>
        `;
        this.syncStateIndicatorVisibility();
    }

    syncStateIndicatorVisibility() {
        if (!this.stateIndicatorWrapper) {
            return;
        }

        const hasVisibleState = Boolean(this.currentStateMeta);
        this.stateIndicatorWrapper.classList.toggle('is-hidden', !hasVisibleState);
    }

    clearInput() {
        this.messageInput.value = '';
        this.messageInput.focus();
    }

    disableSending(disabled = true) {
        this.sendButton.disabled = disabled;
        if (disabled) {
            this.sendButton.textContent = this.translate('sending');
        } else {
            this.sendButton.textContent = this.translate('send');
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
        errorEl.innerHTML = `<p>${this.escapeHtml(errorText)}</p>`;
        this.chatContainer.appendChild(errorEl);
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }

    clearChat() {
        this.chatContainer.innerHTML = '';
        this.stateIndicator.innerHTML = '';
        this.currentStateMeta = null;
        this.syncStateIndicatorVisibility();
    }
}
