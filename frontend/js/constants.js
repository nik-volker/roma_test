/**
 * constants.js - Константы и конфигурация
 */

// API настройки
export const API_CONFIG = {
    // Локально
    base_url: 'http://localhost:5000',

    // Production (GitHub Pages)
    // base_url: 'https://ai-psycho-backend.onrender.com', // или Railway
    endpoints: {
        health: '/api/health',
        chat: '/api/chat'
    }
};

// Состояния
export const STATES = {
    anxiety_in_relationship: 'Тревога в отношениях',
    resentment_after_conflict: 'Обида после конфликта',
    distance_coldness: 'Отдаление и холодность',
    lack_of_communication: 'Отсутствие общения',
    trust_issues: 'Проблемы с доверием',
    loneliness_despite_relationship: 'Одиночество при наличии отношений',
    incompatibility_questions: 'Сомнения совместимости',
    low_self_worth_in_context: 'Низкая самооценка в контексте отношений'
};

// Цвета по состояниям
export const STATE_COLORS = {
    anxiety_in_relationship: '#FF6B6B',
    resentment_after_conflict: '#FFA94D',
    distance_coldness: '#4ECDC4',
    lack_of_communication: '#95E1D3',
    trust_issues: '#FFD93D',
    loneliness_despite_relationship: '#6BCB77',
    incompatibility_questions: '#9B59B6',
    low_self_worth_in_context: '#E8958E'
};
