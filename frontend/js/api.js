/**
 * api.js - Работа с Flask API
 */
import { API_CONFIG } from './constants.js';

export class APIClient {
    constructor() {
        this.baseUrls = [API_CONFIG.base_url, API_CONFIG.fallback_base_url]
            .filter(Boolean)
            .filter((url, idx, arr) => arr.indexOf(url) === idx);
        this.activeBaseUrl = this.baseUrls[0] || '';
    }

    buildUrl(baseUrl, endpoint) {
        return `${baseUrl}${endpoint}`;
    }

    async requestWithFallback(endpoint, options = {}) {
        let lastError = null;

        for (const baseUrl of this.baseUrls) {
            const url = this.buildUrl(baseUrl, endpoint);

            try {
                const response = await fetch(url, options);

                if (response.ok) {
                    this.activeBaseUrl = baseUrl;
                    return response;
                }

                // Для 404 на same-origin пробуем следующий backend.
                if (response.status === 404) {
                    lastError = new Error(`Server error: ${response.status}`);
                    continue;
                }

                throw new Error(`Server error: ${response.status}`);
            } catch (error) {
                lastError = error;
            }
        }

        throw lastError || new Error('API request failed');
    }

    async health() {
        try {
            const response = await this.requestWithFallback(API_CONFIG.endpoints.health, {
                method: 'GET'
            });
            return response.ok;
        } catch (error) {
            console.error('Health check failed:', error);
            return false;
        }
    }

    async sendMessage(message, history = []) {
        try {
            const response = await this.requestWithFallback(API_CONFIG.endpoints.chat, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    history: history
                })
            });

            const data = await response.json();
            return data;

        } catch (error) {
            console.error('API error:', error);
            throw error;
        }
    }
}
