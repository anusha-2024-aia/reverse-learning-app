import React, { useState, useEffect } from 'react';
import { X, Target, Sparkles, Send, Loader2, CheckCircle2, TrendingUp, AlertTriangle, ArrowRight, BookOpen, Mic, MicOff, Type, Headphones } from 'lucide-react';
import api from '../../api/axios';

const RevisionSessionModal = ({ topicItem, onClose, onRevisionComplete }) => {
    const [step, setStep] = useState(1); // 1: Briefing, 2: Explanation, 3: Complete Summary
    const [briefing, setBriefing] = useState(null);
    const [explanation, setExplanation] = useState('');
    const [learningMode, setLearningMode] = useState('technical');
    const [isLoading, setIsLoading] = useState(false);
    const [isBriefingLoading, setIsBriefingLoading] = useState(true);
    const [completionData, setCompletionData] = useState(null);
    const [error, setError] = useState(null);

    // Voice evaluation mode
    const [evaluationMode, setEvaluationMode] = useState('text-to-text');
    const [isRecording, setIsRecording] = useState(false);
    const [recognition, setRecognition] = useState(null);

    const evalModes = [
        { id: 'text-to-text', label: 'Text', icon: Type },
        { id: 'voice-to-text', label: 'Voice-to-Text', icon: Mic },
        { id: 'voice-to-voice', label: 'Voice-to-Voice', icon: Headphones }
    ];

    // Load briefing
    useEffect(() => {
        if (!topicItem) return;
        setIsBriefingLoading(true);
        api.post(`/revisions/${topicItem.topic_id}/start`)
            .then(res => {
                setBriefing(res.data);
                setIsBriefingLoading(false);
            })
            .catch(err => {
                console.error("Error loading revision briefing", err);
                setIsBriefingLoading(false);
            });
    }, [topicItem]);

    // Speech Recognition setup
    useEffect(() => {
        if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const rec = new SpeechRecognition();
            rec.continuous = true;
            rec.interimResults = true;
            rec.lang = 'en-US';

            rec.onresult = (event) => {
                let finalTranscript = '';
                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript + ' ';
                    }
                }
                if (finalTranscript) {
                    setExplanation(prev => prev + finalTranscript);
                }
            };

            rec.onerror = (event) => {
                console.error('Speech recognition error', event.error);
                setIsRecording(false);
            };

            rec.onend = () => {
                setIsRecording(false);
            };

            setRecognition(rec);
        }
    }, []);

    const toggleRecording = () => {
        if (!recognition) {
            setError('Speech recognition is not supported in your browser.');
            return;
        }

        if (isRecording) {
            recognition.stop();
            setIsRecording(false);
        } else {
            setError(null);
            recognition.start();
            setIsRecording(true);
        }
    };

    const handleSubmitRevision = async () => {
        if (!explanation.trim() || explanation.trim().length < 5) return;
        
        setIsLoading(true);
        setError(null);

        try {
            const res = await api.post(`/revisions/${topicItem.topic_id}/complete`, {
                explanation,
                learning_mode: learningMode
            });
            
            setCompletionData(res.data);
            setStep(3);

            if (evaluationMode === 'voice-to-voice' && res.data.ai_insight) {
                window.speechSynthesis.cancel();
                const utterance = new SpeechSynthesisUtterance(res.data.ai_insight);
                window.speechSynthesis.speak(utterance);
            }
        } catch (err) {
            console.error("Error completing revision:", err);
            setError(err.response?.data?.detail || 'Failed to submit revision. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    if (!topicItem) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-200">
            <div className="bg-slate-900 border border-slate-700 rounded-3xl w-full max-w-2xl overflow-hidden shadow-2xl relative flex flex-col max-h-[90vh]">
                
                {/* Header */}
                <div className="p-6 bg-slate-800/80 border-b border-slate-700 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="p-2.5 bg-indigo-600/20 text-indigo-400 rounded-xl border border-indigo-500/30">
                            <BookOpen className="w-6 h-6" />
                        </div>
                        <div>
                            <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-400">
                                Revision Session
                            </span>
                            <h2 className="text-xl font-black text-white">
                                {topicItem.topic_name}
                            </h2>
                        </div>
                    </div>
                    <button 
                        onClick={onClose}
                        className="p-2 text-slate-400 hover:text-white rounded-full hover:bg-slate-800 transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Content Body */}
                <div className="p-6 overflow-y-auto flex-1 space-y-6">
                    
                    {/* STEP 1: BRIEFING */}
                    {step === 1 && (
                        <div className="space-y-6 animate-in slide-in-from-right duration-300">
                            {isBriefingLoading ? (
                                <div className="py-12 flex flex-col items-center justify-center gap-3 text-slate-400">
                                    <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
                                    <span>Preparing revision briefing...</span>
                                </div>
                            ) : (
                                <>
                                    {/* Stats grid */}
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="bg-slate-800 p-4 rounded-2xl border border-slate-700">
                                            <span className="text-xs font-semibold text-slate-400 uppercase">Current Mastery</span>
                                            <div className="text-3xl font-black text-white mt-1 font-mono">
                                                {briefing?.current_mastery || Math.round(topicItem.mastery_score)}%
                                            </div>
                                        </div>
                                        <div className="bg-slate-800 p-4 rounded-2xl border border-slate-700">
                                            <span className="text-xs font-semibold text-slate-400 uppercase">Status</span>
                                            <div className="text-lg font-bold text-indigo-400 mt-1 capitalize">
                                                {topicItem.status.toLowerCase()}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Target Focus Concept */}
                                    {briefing?.focus_concept && (
                                        <div className="bg-rose-950/40 border border-rose-500/40 rounded-2xl p-4 text-rose-200">
                                            <div className="flex items-center gap-2 text-rose-400 font-bold text-xs uppercase tracking-wider mb-1">
                                                <AlertTriangle className="w-4 h-4" /> Focus Concept (Knowledge Gap)
                                            </div>
                                            <p className="text-sm font-medium text-rose-100">
                                                {briefing.focus_concept}
                                            </p>
                                        </div>
                                    )}

                                    {/* Goal */}
                                    <div className="bg-indigo-950/40 border border-indigo-500/30 rounded-2xl p-5 text-indigo-200">
                                        <div className="flex items-center gap-2 text-indigo-400 font-bold text-xs uppercase tracking-wider mb-2">
                                            <Target className="w-4 h-4" /> Revision Goal
                                        </div>
                                        <p className="text-sm leading-relaxed text-indigo-100 font-medium">
                                            {briefing?.revision_goal || `Understand ${topicItem.topic_name} and explain it clearly in your own words.`}
                                        </p>
                                    </div>

                                    <button
                                        onClick={() => setStep(2)}
                                        className="w-full py-4 px-6 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-2xl shadow-lg shadow-indigo-600/30 flex items-center justify-center gap-2 transition-all text-base"
                                    >
                                        <span>Begin Explanation</span>
                                        <ArrowRight className="w-5 h-5" />
                                    </button>
                                </>
                            )}
                        </div>
                    )}

                    {/* STEP 2: EXPLANATION INPUT */}
                    {step === 2 && (
                        <div className="space-y-6 animate-in slide-in-from-right duration-300">
                            <div className="flex items-center justify-between bg-slate-800 p-3 rounded-xl border border-slate-700">
                                <span className="text-xs font-bold uppercase text-slate-400">Mode</span>
                                <div className="flex gap-2">
                                    {evalModes.map((m) => (
                                        <button
                                            key={m.id}
                                            onClick={() => setEvaluationMode(m.id)}
                                            className={`px-3 py-1 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-all ${
                                                evaluationMode === m.id
                                                    ? 'bg-indigo-600 text-white shadow'
                                                    : 'bg-slate-900 text-slate-400 hover:text-slate-200'
                                            }`}
                                        >
                                            <m.icon className="w-3.5 h-3.5" />
                                            {m.label}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div className="relative">
                                <div className="flex items-center justify-between mb-2">
                                    <label className="text-xs font-bold uppercase text-slate-400">
                                        Explain {topicItem.topic_name}
                                    </label>
                                    {(evaluationMode === 'voice-to-text' || evaluationMode === 'voice-to-voice') && (
                                        <button
                                            onClick={toggleRecording}
                                            className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold transition-all ${
                                                isRecording
                                                    ? 'bg-rose-500/20 text-rose-400 border border-rose-500/50 animate-pulse'
                                                    : 'bg-slate-800 text-slate-300 hover:bg-slate-700 border border-slate-700'
                                            }`}
                                        >
                                            {isRecording ? <MicOff className="w-3.5 h-3.5" /> : <Mic className="w-3.5 h-3.5" />}
                                            {isRecording ? 'Stop Recording' : 'Start Voice Input'}
                                        </button>
                                    )}
                                </div>
                                <textarea
                                    value={explanation}
                                    onChange={(e) => setExplanation(e.target.value)}
                                    placeholder={`Explain ${topicItem.topic_name} in detail... Focus on accuracy, core concepts, and practical examples.`}
                                    rows={8}
                                    className="w-full bg-slate-950 border border-slate-700 rounded-2xl p-4 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors leading-relaxed resize-none"
                                ></textarea>
                            </div>

                            {error && (
                                <div className="p-4 bg-rose-950/40 border border-rose-500/40 rounded-xl text-xs text-rose-300 flex items-center gap-2">
                                    <AlertTriangle className="w-4 h-4 text-rose-400" />
                                    <span>{error}</span>
                                </div>
                            )}

                            <div className="flex gap-3">
                                <button
                                    onClick={() => setStep(1)}
                                    className="px-5 py-3.5 bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold rounded-2xl text-sm transition-colors"
                                >
                                    Back
                                </button>
                                <button
                                    onClick={handleSubmitRevision}
                                    disabled={isLoading || explanation.trim().length < 5}
                                    className="flex-1 py-3.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-slate-600 text-white font-bold rounded-2xl shadow-lg flex items-center justify-center gap-2 transition-all text-sm"
                                >
                                    {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                                    {isLoading ? 'Evaluating Revision...' : 'Submit Revision'}
                                </button>
                            </div>
                        </div>
                    )}

                    {/* STEP 3: REVISION COMPLETE SUMMARY */}
                    {step === 3 && completionData && (
                        <div className="space-y-6 animate-in zoom-in-95 duration-300 text-center py-2">
                            
                            <div className="w-16 h-16 bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 rounded-full flex items-center justify-center mx-auto shadow-lg shadow-emerald-500/10">
                                <CheckCircle2 className="w-10 h-10" />
                            </div>

                            <div>
                                <h3 className="text-2xl font-black text-white">
                                    Revision Complete 🎉
                                </h3>
                                <p className="text-sm text-slate-400 mt-1">
                                    {completionData.topic_name}
                                </p>
                            </div>

                            {/* Scores comparison card */}
                            <div className="grid grid-cols-3 gap-3 bg-slate-950 p-4 rounded-2xl border border-slate-800">
                                <div className="p-2">
                                    <span className="block text-[10px] uppercase font-bold text-slate-500">Previous</span>
                                    <span className="text-xl font-black text-slate-400 font-mono">
                                        {completionData.previous_mastery}%
                                    </span>
                                </div>
                                <div className="p-2 border-x border-slate-800">
                                    <span className="block text-[10px] uppercase font-bold text-slate-500">New Mastery</span>
                                    <span className="text-2xl font-black text-emerald-400 font-mono">
                                        {completionData.new_mastery}%
                                    </span>
                                </div>
                                <div className="p-2">
                                    <span className="block text-[10px] uppercase font-bold text-slate-500">Improvement</span>
                                    <span className={`text-xl font-black font-mono ${completionData.improvement >= 0 ? 'text-indigo-400' : 'text-rose-400'}`}>
                                        {completionData.improvement_formatted}
                                    </span>
                                </div>
                            </div>

                            {/* Next Revision info badge */}
                            <div className="bg-indigo-950/40 border border-indigo-500/30 rounded-2xl p-4 flex items-center justify-between text-left">
                                <div>
                                    <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-400">Next Revision Scheduled</span>
                                    <div className="text-base font-bold text-white mt-0.5">
                                        {completionData.next_revision_formatted}
                                    </div>
                                </div>
                                <Sparkles className="w-6 h-6 text-indigo-400" />
                            </div>

                            {/* AI Insight */}
                            {completionData.ai_insight && (
                                <div className="bg-slate-800/80 border border-slate-700 rounded-2xl p-4 text-left">
                                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
                                        💡 AI Insight
                                    </span>
                                    <p className="text-xs text-slate-200 leading-relaxed italic">
                                        "{completionData.ai_insight}"
                                    </p>
                                </div>
                            )}

                            <button
                                onClick={() => {
                                    if (onRevisionComplete) onRevisionComplete();
                                    onClose();
                                }}
                                className="w-full py-4 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-2xl shadow-lg shadow-indigo-600/30 transition-all text-sm"
                            >
                                Back to Revision Schedule
                            </button>
                        </div>
                    )}

                </div>
            </div>
        </div>
    );
};

export default RevisionSessionModal;
