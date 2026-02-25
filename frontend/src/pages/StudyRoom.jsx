import React, { useState } from 'react';
import { BookOpen, Send, Loader2, BrainCircuit, Layers, Target, Code, MessageCircle } from 'lucide-react';
import { evaluateExplanationStream } from '../services/api';
import FeedbackCard from '../components/FeedbackCard';
import SyllabusTracker from '../components/SyllabusTracker';

const StudyRoom = () => {
    const [topic, setTopic] = useState('Core Foundations');
    const [explanation, setExplanation] = useState('');
    const [learningMode, setLearningMode] = useState('technical');
    const [isLoading, setIsLoading] = useState(false);
    const [evaluation, setEvaluation] = useState(null);
    const [thinkingText, setThinkingText] = useState('');
    const [error, setError] = useState(null);

    const modes = [
        { id: 'general', label: 'General Knowledge', icon: Target, description: 'Core concepts & analogies' },
        { id: 'technical', label: 'Technical & DSA', icon: Code, description: 'Complexity & logic' },
        { id: 'fluency', label: 'English Fluency', icon: MessageCircle, description: 'Tone & vocabulary' }
    ];

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!topic || !explanation) return;

        setIsLoading(true);
        setError(null);
        setEvaluation(null);
        setThinkingText('');

        try {
            const rawOutput = await evaluateExplanationStream(topic, explanation, learningMode, (fullText) => {
                if (fullText.includes('<thinking>')) {
                    const startTag = '<thinking>';
                    const endTag = '</thinking>';
                    const startIndex = fullText.indexOf(startTag) + startTag.length;
                    const endIndex = fullText.indexOf(endTag);

                    let thinking;
                    if (endIndex !== -1) {
                        thinking = fullText.substring(startIndex, endIndex).trim();
                    } else {
                        thinking = fullText.substring(startIndex).trim();
                    }
                    setThinkingText(thinking);
                }
            });

            if (rawOutput.includes('<json>')) {
                const jsonStr = rawOutput.split('<json>')[1].split('</json>')[0].trim();
                try {
                    const result = JSON.parse(jsonStr);
                    setEvaluation(result);
                } catch (_err) {
                    console.error("JSON parse error:", _err);
                    setError('Failed to parse the evaluation data. Please try again.');
                }
            } else {
                const firstBrace = rawOutput.indexOf('{');
                const lastBrace = rawOutput.lastIndexOf('}');
                if (firstBrace !== -1 && lastBrace !== -1 && lastBrace > firstBrace) {
                    try {
                        const jsonStr = rawOutput.substring(firstBrace, lastBrace + 1);
                        setEvaluation(JSON.parse(jsonStr));
                    } catch (_e) {
                        setError('Failed to extract valid feedback from the AI.');
                    }
                } else {
                    setError('The AI did not return a valid evaluation format.');
                }
            }
        } catch (err) {
            setError('Failed to get evaluation. Please ensure the backend is running.');
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    const handleRetry = () => {
        setExplanation('');
        setEvaluation(null);
        setThinkingText('');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handleNewTopic = () => {
        setTopic('');
        setExplanation('');
        setEvaluation(null);
        setThinkingText('');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handleTopicSelect = (selectedTopicName) => {
        setTopic(selectedTopicName);
        const inputElement = document.getElementById('topic');
        if (inputElement) {
            inputElement.focus();
            inputElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    };

    return (
        <div className="min-h-screen bg-slate-50 py-12 px-4 sm:px-6 lg:px-8 transition-colors duration-500 font-sans">
            <div className="max-w-4xl mx-auto">
                <div className="text-center mb-10">
                    <div className="inline-flex items-center gap-2 px-3 py-1 bg-indigo-50 text-indigo-600 rounded-full text-[10px] font-black uppercase tracking-widest mb-4 border border-indigo-100 shadow-sm">
                        <Sparkles className="w-3 h-3" />
                        AI Learning Co-Pilot
                    </div>
                    <h1 className="text-5xl font-black text-slate-900 mb-4 tracking-tighter">
                        Reverse Learning
                    </h1>
                    <p className="text-lg text-slate-500 font-medium">
                        The ultimate way to master complex topics through active teaching.
                    </p>
                </div>

                {/* 1. Syllabus Roadmap - Now Interactive */}
                <SyllabusTracker currentTopic={topic} onSelectTopic={handleTopicSelect} />

                {/* 2. Main Input Section */}
                <div className="bg-white rounded-3xl shadow-xl shadow-slate-200/50 p-10 mb-10 border border-slate-200 relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-50/50 rounded-full -mr-16 -mt-16 blur-3xl"></div>

                    <form onSubmit={handleSubmit} className="space-y-8 relative z-10">
                        {/* Learning Mode Selector */}
                        <div className="space-y-4">
                            <div className="flex items-center gap-2 mb-2">
                                <Layers className="w-4 h-4 text-indigo-500" />
                                <label className="text-xs font-black text-slate-400 uppercase tracking-widest">
                                    Learning Context
                                </label>
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                                {modes.map((mode) => (
                                    <button
                                        key={mode.id}
                                        type="button"
                                        onClick={() => setLearningMode(mode.id)}
                                        className={`flex flex-col items-center p-4 rounded-2xl border-2 transition-all duration-300 text-left group
                                            ${learningMode === mode.id
                                                ? 'bg-indigo-600 border-indigo-600 text-white shadow-lg shadow-indigo-100 scale-[1.02]'
                                                : 'bg-white border-slate-100 text-slate-400 hover:border-slate-200 hover:bg-slate-50 hover:scale-[1.01]'}`}
                                    >
                                        <mode.icon className={`w-5 h-5 mb-2 transition-colors ${learningMode === mode.id ? 'text-white' : 'text-indigo-400 group-hover:text-indigo-600'}`} />
                                        <span className="text-xs font-black uppercase tracking-tight mb-1">{mode.label}</span>
                                        <span className={`text-[10px] text-center leading-tight transition-colors ${learningMode === mode.id ? 'text-indigo-100' : 'text-slate-400'}`}>
                                            {mode.description}
                                        </span>
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div className="grid grid-cols-1 gap-8">
                            <div>
                                <label htmlFor="topic" className="block text-xs font-black text-slate-400 uppercase tracking-widest mb-3">
                                    Target Concept
                                </label>
                                <input
                                    id="topic"
                                    type="text"
                                    value={topic}
                                    onChange={(e) => setTopic(e.target.value)}
                                    placeholder="e.g., Dijkstra's Algorithm, Inflation, Photosynthesis"
                                    className="w-full px-6 py-4 rounded-2xl bg-slate-50 border border-slate-200 focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 focus:bg-white transition-all text-slate-900 font-bold placeholder:text-slate-300 shadow-inner"
                                    required
                                />
                            </div>

                            <div>
                                <label htmlFor="explanation" className="block text-xs font-black text-slate-400 uppercase tracking-widest mb-3">
                                    Your Explanation
                                </label>
                                <textarea
                                    id="explanation"
                                    rows={8}
                                    value={explanation}
                                    onChange={(e) => setExplanation(e.target.value)}
                                    placeholder="Explain the concept as if you were teaching it to a curious student..."
                                    className="w-full px-6 py-4 rounded-2xl bg-slate-50 border border-slate-200 focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 focus:bg-white transition-all text-slate-900 font-medium placeholder:text-slate-300 shadow-inner leading-relaxed"
                                    required
                                />
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={isLoading || !topic || !explanation}
                            className="w-full flex items-center justify-center gap-3 bg-slate-900 hover:bg-black text-white font-black py-4 px-8 rounded-2xl transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-xl shadow-slate-900/20 active:scale-[0.98]"
                        >
                            {isLoading ? (
                                <>
                                    <Loader2 className="animate-spin w-5 h-5" />
                                    AI is deep in thought...
                                </>
                            ) : (
                                <>
                                    <Send className="w-5 h-5" />
                                    ANALYZE EXPLANATION
                                </>
                            )}
                        </button>
                    </form>

                    {error && (
                        <div className="mt-6 p-4 bg-rose-50 text-rose-700 rounded-xl border border-rose-100 flex items-center gap-3 font-bold text-sm">
                            <div className="w-2 h-2 rounded-full bg-rose-500 animate-pulse"></div>
                            {error}
                        </div>
                    )}
                </div>

                {thinkingText && !evaluation && (
                    <div className="mb-10 animate-in fade-in slide-in-from-bottom-8 duration-700">
                        <div className="bg-white border border-slate-200 rounded-3xl p-8 shadow-xl shadow-indigo-100/20 relative overflow-hidden">
                            <div className="absolute top-0 left-0 w-1 h-full bg-indigo-500"></div>
                            <div className="flex items-center gap-3 mb-6">
                                <div className="p-2 bg-indigo-50 text-indigo-600 rounded-xl">
                                    <BrainCircuit className="w-6 h-6 animate-pulse" />
                                </div>
                                <div>
                                    <h2 className="text-sm font-black text-slate-800 uppercase tracking-widest">AI Cognition Phase</h2>
                                    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-tight">Processing pedagogical nuances</p>
                                </div>
                            </div>
                            <div className="text-slate-600 italic font-medium leading-relaxed whitespace-pre-wrap pl-4 border-l-2 border-slate-100">
                                {thinkingText}
                                {isLoading && <span className="inline-block w-2 h-4 ml-1 bg-indigo-500 animate-pulse" />}
                            </div>
                        </div>
                    </div>
                )}

                <FeedbackCard
                    evaluation={evaluation}
                    isLoading={isLoading}
                    onRetry={handleRetry}
                    onNewTopic={handleNewTopic}
                />
            </div>
        </div>
    );
};

const Sparkles = ({ className }) => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className={className}>
        <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z" />
        <path d="M5 3v4" />
        <path d="M19 17v4" />
        <path d="M3 5h4" />
        <path d="M17 19h4" />
    </svg>
);

export default StudyRoom;
