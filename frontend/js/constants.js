/**
 * constants.js - Константы и конфигурация
 */

export const SUPPORTED_LANGUAGES = ['en', 'ru'];

export const STORAGE_KEYS = {
    chatHistory: 'chatHistory',
    language: 'appLanguage'
};

export const UI_TEXT = {
    en: {
        pageTitle: 'AI Relationship Consultant | Thoughtful relationship support',
        brandEyebrow: 'AI relationship consultant',
        brandTitle: 'Relationship clarity, one message at a time',
        brandSubtitle: 'Reflect on difficult moments, get grounded questions, and receive practical techniques for your next step.',
        privacyBadge: 'Private in your browser',
        currentStateLabel: 'Current state',
        messageLabel: 'Your message',
        messagePlaceholder: 'Tell me what is happening in your relationship...',
        send: 'Send',
        sending: 'Sending...',
        clear: 'Clear',
        emptyMessageAlert: 'Please enter a message.',
        clearChatConfirm: 'Clear the entire chat history?',
        errorFallback: 'There was a problem reaching the server.',
        stateLabel: 'State',
        techniqueLabel: 'Technique',
        crisisState: 'Crisis support',
        unknownState: 'Thinking'
    },
    ru: {
        pageTitle: 'AI-консультант по отношениям | Поддержка в вопросах отношений',
        brandEyebrow: 'AI-консультант по отношениям',
        brandTitle: 'Больше ясности в отношениях, по одному сообщению за раз',
        brandSubtitle: 'Разберите сложную ситуацию, получите бережные уточняющие вопросы и практичные техники для следующего шага.',
        privacyBadge: 'Данные хранятся в браузере',
        currentStateLabel: 'Текущее состояние',
        messageLabel: 'Ваше сообщение',
        messagePlaceholder: 'Расскажите, что происходит в ваших отношениях...',
        send: 'Отправить',
        sending: 'Отправляю...',
        clear: 'Очистить',
        emptyMessageAlert: 'Введите сообщение.',
        clearChatConfirm: 'Очистить всю историю чата?',
        errorFallback: 'Не удалось связаться с сервером.',
        stateLabel: 'Состояние',
        techniqueLabel: 'Техника',
        crisisState: 'Кризисная поддержка',
        unknownState: 'Анализ'
    }
};

// API настройки
const IS_LOCAL = ['localhost', '127.0.0.1'].includes(window.location.hostname);
const DEFAULT_REMOTE_BACKEND = 'https://psycho-back.vercel.app';

export const API_CONFIG = {
    // Локально вызываем Flask на 5000, в проде сначала пробуем same-origin /api.
    base_url: IS_LOCAL ? 'http://localhost:5000' : '',
    // Если frontend задеплоен отдельно и /api отсутствует, используем отдельный backend.
    fallback_base_url: IS_LOCAL ? null : DEFAULT_REMOTE_BACKEND,
    endpoints: {
        health: '/api/health',
        chat: '/api/chat'
    }
};

export const STATE_LABELS = {
    en: {
        anxiety_in_relationship: 'Relationship anxiety',
        resentment_after_conflict: 'Resentment after conflict',
        distance_coldness: 'Distance and emotional coldness',
        lack_of_communication: 'Communication breakdown',
        trust_issues: 'Trust issues',
        loneliness_despite_relationship: 'Loneliness within the relationship',
        incompatibility_questions: 'Compatibility doubts',
        low_self_worth_in_context: 'Low self-worth in the relationship'
    },
    ru: {
        anxiety_in_relationship: 'Тревога в отношениях',
        resentment_after_conflict: 'Обида после конфликта',
        distance_coldness: 'Отдаление и холодность',
        lack_of_communication: 'Отсутствие общения',
        trust_issues: 'Проблемы с доверием',
        loneliness_despite_relationship: 'Одиночество в отношениях',
        incompatibility_questions: 'Сомнения в совместимости',
        low_self_worth_in_context: 'Низкая самооценка в отношениях'
    }
};

// Цвета по состояниям
export const STATE_COLORS = {
    anxiety_in_relationship: '#D67A61',
    resentment_after_conflict: '#C48763',
    distance_coldness: '#7F9C9B',
    lack_of_communication: '#86A8A1',
    trust_issues: '#B48E6B',
    loneliness_despite_relationship: '#7B8D77',
    incompatibility_questions: '#8D7C8F',
    low_self_worth_in_context: '#B67B7B'
};
