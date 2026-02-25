import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const evaluateExplanation = async (topic, explanation, mode = 'general') => {
    try {
        const response = await api.post('/evaluate', {
            topic,
            explanation,
            learning_mode: mode
        });
        return response.data;
    } catch (error) {
        console.error('Error evaluating explanation:', error);
        throw error;
    }
};

export const evaluateExplanationStream = async (topic, explanation, mode, onChunk) => {
    try {
        const response = await fetch(`${API_BASE_URL}/evaluate-stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ topic, explanation, learning_mode: mode }),
        });

        if (!response.ok) throw new Error('Network response was not ok');

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullText = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            fullText += chunk;
            onChunk(fullText);
        }

        return fullText;
    } catch (error) {
        console.error('Error in streaming evaluation:', error);
        throw error;
    }
};

export default api;
