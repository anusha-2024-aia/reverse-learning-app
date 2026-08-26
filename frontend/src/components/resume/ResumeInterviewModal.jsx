import React, { useState, useEffect } from 'react';
import { X, Send, Loader2, Award, CheckCircle2, AlertTriangle, Sparkles, ArrowRight, Mic, MicOff, Type, Headphones } from 'lucide-react';
import api from '../../api/axios';

const ResumeInterviewModal = ({ resumeId, initialQuestions: _INITIAL_QUESTIONS = [], onClose, onComplete }) => {
    const [step, setStep] = useState('interview'); // 'interview', 'evaluating', 'report'
    const [interviewId, setInterviewId] = useState(null);
    const [currentQuestion, setCurrentQuestion] = useState(null);
    const [currentStepIndex, setCurrentStepIndex] = useState(1);
    const [maxSteps, setMaxSteps] = useState(5);
    const [answer, setAnswer] = useState('');
    const [qaHistory, setQaHistory] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [report, setReport] = useState(null);

    // Voice evaluation state
    const [evaluationMode, setEvaluationMode] = useState('text-to-text');
    const [isRecording, setIsRecording] = useState(false);
    const [recognition, setRecognition] = useState(null);

    const evalModes = [
        { id: 'text-to-text', label: 'Text', icon: Type },
        { id: 'voice-to-text', label: 'Voice-to-Text', icon: Mic },
        { id: 'voice-to-voice', label: 'Voice-to-Voice', icon: Headphones }
    ];

    // Initialize interview session
    useEffect(() => {
        setIsLoading(true);
        api.post('/resume/interview/start', { resume_id: resumeId })
            .then(res => {
                setInterviewId(res.data.interview_id);
                setCurrentQuestion({
                    id: res.data.question_id,
                    question: res.data.question,
                    category: res.data.category,
                    difficulty: res.data.difficulty,
                    target: res.data.target
                });
                setMaxSteps(res.data.total_questions || 5);
                setIsLoading(false);
            })
            .catch(err => {
                console.error("Error starting resume interview:", err);
                setError(err.response?.data?.detail || "Could not start interview.");
                setIsLoading(false);
            });
    }, [resumeId]);

    // Speech recognition setup
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
                    setAnswer(prev => prev + finalTranscript);
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

    const handleNextAnswer = async () => {
        if (!answer.trim() || answer.trim().length < 5) return;

        setIsLoading(true);
        setError(null);

        const newHistory = [...qaHistory, { question: currentQuestion.question, answer }];
        setQaHistory(newHistory);

        const isFinal = newHistory.length >= maxSteps;

        try {
            const res = await api.post('/resume/interview/answer', {
                interview_id: interviewId,
                answer: answer,
                is_final: isFinal,
                qa_history: newHistory
            });

            if (res.data.is_complete) {
                setReport(res.data.report);
                setStep('report');
                if (onComplete) onComplete();
            } else {
                setCurrentQuestion({
                    question: res.data.follow_up_question,
                    category: "Follow-up",
                    difficulty: "Medium",
                    target: currentQuestion.target
                });
                setCurrentStepIndex(newHistory.length + 1);
                setAnswer('');
            }
        } catch (err) {
            console.error("Error submitting interview answer:", err);
            setError(err.response?.data?.detail || "Failed to process answer. Please try again.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-200">
            <div className="bg-slate-900 border border-slate-700 rounded-3xl w-full max-w-2xl overflow-hidden shadow-2xl relative flex flex-col max-h-[90vh]">
                
                {/* Header */}
                <div className="p-6 bg-slate-800/80 border-b border-slate-700 flex items-center justify-between">
                    <div>
                        <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-400">
                            Resume Mock Interview
                        </span>
                        <h2 className="text-xl font-black text-white">
                            Personalized Interview Session
                        </h2>
                    </div>
                    <button 
                        onClick={onClose}
                        className="p-2 text-slate-400 hover:text-white rounded-full hover:bg-slate-800 transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 overflow-y-auto flex-1 space-y-6">

                    {/* INTERVIEW IN PROGRESS */}
                    {step === 'interview' && (
                        <div className="space-y-6 animate-in slide-in-from-right duration-300">
                            
                            {/* Step & Category badges */}
                            <div className="flex items-center justify-between">
                                <span className="text-xs font-bold uppercase tracking-wider text-slate-400 bg-slate-800 px-3 py-1 rounded-full border border-slate-700">
                                    Question {currentStepIndex} of {maxSteps}
                                </span>
                                {currentQuestion && (
                                    <div className="flex gap-2">
                                        <span className="text-[10px] font-bold uppercase tracking-wider bg-indigo-950 text-indigo-300 px-2.5 py-0.5 rounded border border-indigo-800">
                                            {currentQuestion.category}
                                        </span>
                                        <span className="text-[10px] font-bold uppercase tracking-wider bg-slate-800 text-slate-300 px-2.5 py-0.5 rounded border border-slate-700">
                                            {currentQuestion.difficulty}
                                        </span>
                                    </div>
                                )}
                            </div>

                            {/* Target project indicator */}
                            {currentQuestion?.target && (
                                <div className="text-xs font-semibold text-indigo-300 bg-indigo-950/40 p-2.5 rounded-xl border border-indigo-500/20 flex items-center gap-2">
                                    <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                                    <span>Target Project / Skill: <strong>{currentQuestion.target}</strong></span>
                                </div>
                            )}

                            {/* Question display */}
                            <div className="bg-slate-800 p-6 rounded-2xl border border-slate-700 shadow-inner">
                                <p className="text-lg font-bold text-white leading-relaxed">
                                    "{currentQuestion?.question}"
                                </p>
                            </div>

                            {/* Input mode selector */}
                            <div className="flex items-center justify-between">
                                <label className="text-xs font-bold uppercase text-slate-400">Your Answer</label>
                                <div className="flex gap-2">
                                    {evalModes.map((m) => (
                                        <button
                                            key={m.id}
                                            onClick={() => setEvaluationMode(m.id)}
                                            className={`px-2.5 py-1 rounded-lg text-[11px] font-bold flex items-center gap-1 transition-all ${
                                                evaluationMode === m.id
                                                    ? 'bg-indigo-600 text-white'
                                                    : 'bg-slate-800 text-slate-400'
                                            }`}
                                        >
                                            <m.icon className="w-3 h-3" />
                                            {m.label}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Textarea */}
                            <div className="relative">
                                {(evaluationMode === 'voice-to-text' || evaluationMode === 'voice-to-voice') && (
                                    <button
                                        onClick={toggleRecording}
                                        className={`mb-2 flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold transition-all ${
                                            isRecording
                                                ? 'bg-rose-500/20 text-rose-400 border border-rose-500/50 animate-pulse'
                                                : 'bg-slate-800 text-slate-300 border border-slate-700'
                                        }`}
                                    >
                                        {isRecording ? <MicOff className="w-3.5 h-3.5" /> : <Mic className="w-3.5 h-3.5" />}
                                        {isRecording ? 'Stop Recording' : 'Start Voice Input'}
                                    </button>
                                )}
                                <textarea
                                    value={answer}
                                    onChange={(e) => setAnswer(e.target.value)}
                                    placeholder="Explain your approach, choices, and implementation details based on your resume experience..."
                                    rows={6}
                                    className="w-full bg-slate-950 border border-slate-700 rounded-2xl p-4 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 leading-relaxed resize-none text-sm"
                                ></textarea>
                            </div>

                            {error && (
                                <div className="p-3 bg-rose-950/40 border border-rose-500/40 rounded-xl text-xs text-rose-300 flex items-center gap-2">
                                    <AlertTriangle className="w-4 h-4 text-rose-400" />
                                    <span>{error}</span>
                                </div>
                            )}

                            <button
                                onClick={handleNextAnswer}
                                disabled={isLoading || answer.trim().length < 5}
                                className="w-full py-4 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-slate-600 text-white font-bold rounded-2xl shadow-lg flex items-center justify-center gap-2 transition-all text-sm"
                            >
                                {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                                {isLoading ? 'Processing Answer...' : currentStepIndex >= maxSteps ? 'Submit & Generate Report' : 'Submit Answer & Continue'}
                            </button>
                        </div>
                    )}

                    {/* FINAL REPORT */}
                    {step === 'report' && report && (
                        <div className="space-y-6 animate-in zoom-in-95 duration-300 py-2">
                            <div className="text-center">
                                <div className="w-16 h-16 bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 rounded-full flex items-center justify-center mx-auto mb-3 shadow-lg">
                                    <Award className="w-10 h-10" />
                                </div>
                                <h3 className="text-2xl font-black text-white">
                                    Resume Interview Report
                                </h3>
                                <p className="text-xs text-slate-400 mt-1">
                                    Performance evaluation based on your resume & responses
                                </p>
                            </div>

                            {/* Scores Grid */}
                            <div className="grid grid-cols-3 gap-3 bg-slate-950 p-4 rounded-2xl border border-slate-800 text-center">
                                <div className="p-2">
                                    <span className="block text-[10px] uppercase font-bold text-slate-500">Overall</span>
                                    <span className="text-2xl font-black text-indigo-400 font-mono">
                                        {report.overall_score}%
                                    </span>
                                </div>
                                <div className="p-2 border-x border-slate-800">
                                    <span className="block text-[10px] uppercase font-bold text-slate-500">Project Knowledge</span>
                                    <span className="text-2xl font-black text-emerald-400 font-mono">
                                        {report.project_knowledge_score}%
                                    </span>
                                </div>
                                <div className="p-2">
                                    <span className="block text-[10px] uppercase font-bold text-slate-500">Resume Match</span>
                                    <span className="text-2xl font-black text-amber-400 font-mono">
                                        {report.resume_understanding_score}%
                                    </span>
                                </div>
                            </div>

                            {/* Strengths & Weaknesses */}
                            <div className="grid md:grid-cols-2 gap-4">
                                <div className="bg-slate-800 p-4 rounded-2xl border border-slate-700 text-xs">
                                    <span className="font-bold text-emerald-400 block uppercase tracking-wider mb-2">
                                        ✓ Key Strengths
                                    </span>
                                    <ul className="space-y-1 text-slate-200">
                                        {(report.strengths || []).map((s, idx) => (
                                            <li key={idx}>• {s}</li>
                                        ))}
                                    </ul>
                                </div>

                                <div className="bg-slate-800 p-4 rounded-2xl border border-slate-700 text-xs">
                                    <span className="font-bold text-rose-400 block uppercase tracking-wider mb-2">
                                        ⚠ Areas to Improve
                                    </span>
                                    <ul className="space-y-1 text-slate-200">
                                        {(report.weaknesses || []).map((w, idx) => (
                                            <li key={idx}>• {w}</li>
                                        ))}
                                    </ul>
                                </div>
                            </div>

                            {/* Recommended Prep */}
                            {report.recommended_preparation && report.recommended_preparation.length > 0 && (
                                <div className="bg-indigo-950/40 border border-indigo-500/30 rounded-2xl p-4 text-xs text-indigo-200">
                                    <span className="font-bold uppercase tracking-wider text-indigo-400 block mb-1">
                                        🎯 Recommended Next Preparation
                                    </span>
                                    <ul className="space-y-1 text-indigo-100">
                                        {report.recommended_preparation.map((prep, idx) => (
                                            <li key={idx}>• {prep}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            <button
                                onClick={onClose}
                                className="w-full py-4 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-2xl shadow-lg shadow-indigo-600/30 text-sm transition-all"
                            >
                                Return to Resume Intelligence Hub
                            </button>
                        </div>
                    )}

                </div>
            </div>
        </div>
    );
};

export default ResumeInterviewModal;
