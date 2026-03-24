/**
 * api.js - Работа с Flask API
 */
import { API_CONFIG } from './constants.js';

export class APIClient {
    constructor() {
        this.baseUrl = API_CONFIG.base_url;
    }

    async health() {
        try {
            const response = await fetch(`${this.baseUrl}${API_CONFIG.endpoints.health}`, {
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
            const response = await fetch(`${this.baseUrl}${API_CONFIG.endpoints.chat}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    history: history
                })
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            const data = await response.json();
            return data;

        } catch (error) {
            console.error('API error:', error);
            throw error;
        }
    }
}
