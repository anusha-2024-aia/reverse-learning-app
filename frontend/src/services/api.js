import axios from 'axios';

const API_BASE_URL = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api`;

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

api.interceptors.request.use(
    (config) => {
        const token = sessionStorage.getItem('token') || localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Study Session / Topics
export const evaluateExplanation = async (topic, explanation, mode = 'general') => {
    const response = await api.post('/evaluate', { topic, explanation, learning_mode: mode });
    return response.data;
};

// Adaptive Engine
export const getWeakTopics = async () => {
    const response = await api.get('/recommendations/weak-topics');
    return response.data;
};

export const getStrongTopics = async () => {
    const response = await api.get('/recommendations/strong-topics');
    return response.data;
};

// Roadmap
export const generateRoadmap = async () => {
    const response = await api.post('/roadmap/generate');
    return response.data;
};

export const getMyRoadmap = async () => {
    const response = await api.get('/roadmap/mine');
    return response.data;
};

// Interviews & Resumes
export const uploadResume = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/interview/resume/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
};

export const startInterview = async (targetRole, difficulty, interviewType, resumeId) => {
    const formData = new FormData();
    formData.append('target_role', targetRole);
    formData.append('difficulty', difficulty);
    formData.append('interview_type', interviewType);
    if (resumeId) formData.append('resume_id', resumeId);
    
    const response = await api.post('/interview/start', formData);
    return response.data;
};

export const answerInterviewQuestion = async (interviewId, questionId, answer, isFinal) => {
    const response = await api.post('/interview/answer', {
        interview_id: interviewId,
        current_question_id: questionId,
        answer,
        is_final: isFinal
    });
    return response.data;
};

export const getInterviewHistory = async () => {
    const response = await api.get('/interview/history');
    return response.data;
};

// Analytics & Dashboard
export const getDashboardAnalytics = async () => {
    const response = await api.get('/analytics/dashboard');
    return response.data;
};

export default api;