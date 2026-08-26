import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
    Mic, MicOff, Play, CheckCircle2, AlertCircle, Loader2, 
    StopCircle, RefreshCw, Volume2, Sparkles, TrendingUp, 
    Flame, Zap, Sprout, Award, ChevronRight, FileText, ArrowRight, RotateCcw, BookOpen
} from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import api from '../api/axios';

const MockInterview = () => {
    const navigate = useNavigate();

    // Setup form state
    const [targetRole, setTargetRole] = useState('Full Stack Developer');
    const [interviewType, setInterviewType] = useState('technical'); // technical, project, resume, mixed
    const [startingDifficulty, setStartingDifficulty] = useState('MEDIUM'); // EASY, MEDIUM, HARD
    const [questionCount, setQuestionCount] = useState(10);
    const [useResume, setUseResume] = useState(false);
    const [activeResume, setActiveResume] = useState(null);

    // Active session state
    const [status, setStatus] = useState('setup'); // 'setup', 'active', 'evaluating', 'finished'
    const [activeSession, setActiveSession] = useState(null);
    const [interviewId, setInterviewId] = useState(null);
    const [currentQuestion, setCurrentQuestion] = useState(null);
    const [currentStep, setCurrentStep] = useState(1);
    const [totalQuestions, setTotalQuestions] = useState(10);
    const [currentDifficulty, setCurrentDifficulty] = useState('MEDIUM');
    const [answerText, setAnswerText] = useState('');
    const [isRecording, setIsRecording] = useState(false);

    // Immediate feedback after single answer
    const [lastFeedback, setLastFeedback] = useState(null);
    const [loadingStage, setLoadingStage] = useState('');
    const [error, setError] = useState(null);

    // Final Report state
    const [report, setReport] = useState(null);

    const recognitionRef = useRef(null);

    // Check active resume & active existing session on load
    useEffect(() => {
        // Fetch active resume
        api.get('/resume/active')
            .then(res => {
                if (res.data && res.data.has_resume) {
                    setActiveResume(res.data);
                    setUseResume(true);
                }
            })
            .catch(() => {});

        // Fetch active interview session to allow resuming
        api.get('/interview/active')
            .then(res => {
                if (res.data && res.data.has_active) {
                    setActiveSession(res.data);
                }
            })
            .catch(() => {});

        // Speech recognition setup
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
                    setAnswerText(prev => prev + finalTranscript);
                }
            };

            rec.onerror = (err) => {
                console.error('Speech recognition error:', err);
                setIsRecording(false);
            };

            rec.onend = () => {
                setIsRecording(false);
            };

            recognitionRef.current = rec;
        }
    }, []);

    const speak = (text) => {
        if ('speechSynthesis' in window && text) {
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.0;
            window.speechSynthesis.speak(utterance);
        }
    };

    const toggleRecording = () => {
        if (!recognitionRef.current) {
            setError('Speech recognition is not supported in your browser.');
            return;
        }

        if (isRecording) {
            recognitionRef.current.stop();
            setIsRecording(false);
        } else {
            setError(null);
            recognitionRef.current.start();
            setIsRecording(true);
        }
    };

    const handleStartInterview = async () => {
        setError(null);
        setStatus('evaluating');
        setLoadingStage('Initializing Adaptive Mock Interview...');

        try {
            const res = await api.post('/interview/start', {
                target_role: targetRole,
                interview_type: useResume ? 'resume' : interviewType,
                difficulty: startingDifficulty,
                question_count: Number(questionCount),
                use_resume: useResume,
                resume_id: useResume ? activeResume?.resume_id : null
            });

            setInterviewId(res.data.interview_id);
            setCurrentQuestion({
                id: res.data.question_id,
                question: res.data.question,
                category: res.data.category,
                difficulty: res.data.difficulty,
                topic: res.data.topic,
                source: res.data.source
            });
            setCurrentDifficulty(res.data.difficulty || startingDifficulty);
            setCurrentStep(res.data.current_step || 1);
            setTotalQuestions(res.data.total_questions || questionCount);
            setAnswerText('');
            setLastFeedback(null);
            setStatus('active');
            speak(res.data.question);
        } catch (err) {
            console.error("Start interview error:", err);
            setError(err.response?.data?.detail || "Unable to start adaptive interview. Please try again.");
            setStatus('setup');
        }
    };

    const handleResumeActiveInterview = async () => {
        if (!activeSession) return;
        setError(null);
        setStatus('evaluating');
        setLoadingStage('Resuming interview session...');

        try {
            setInterviewId(activeSession.interview_id);
            setCurrentQuestion({
                id: activeSession.last_question?.id,
                question: activeSession.last_question?.question,
                category: activeSession.last_question?.category || "TECHNICAL",
                difficulty: activeSession.current_difficulty || "MEDIUM",
                topic: activeSession.last_question?.topic || activeSession.target_role,
                source: activeSession.last_question?.source
            });
            setCurrentDifficulty(activeSession.current_difficulty || "MEDIUM");
            setCurrentStep(activeSession.current_step || 1);
            setTotalQuestions(activeSession.total_questions || 10);
            setAnswerText('');
            setStatus('active');
            if (activeSession.last_question?.question) {
                speak(activeSession.last_question.question);
            }
        } catch (_ERR) {
            setError("Could not resume active session.");
            setStatus('setup');
        }
    };

    const handleSubmitAnswer = async () => {
        if (!answerText.trim() || answerText.trim().length < 4) {
            setError("Please provide a clearer answer before submitting.");
            return;
        }

        if (isRecording && recognitionRef.current) {
            recognitionRef.current.stop();
            setIsRecording(false);
        }

        setError(null);
        setStatus('evaluating');
        setLoadingStage('Evaluating your answer with Multi-Dimensional AI...');

        setTimeout(() => setLoadingStage('Analyzing technical understanding & communication...'), 1000);
        setTimeout(() => setLoadingStage('Determining performance level & adjusting difficulty...'), 2200);

        try {
            const isFinal = currentStep >= totalQuestions;
            const res = await api.post('/interview/answer', {
                interview_id: interviewId,
                current_question_id: currentQuestion?.id,
                answer: answerText,
                is_final: isFinal
            });

            setLastFeedback({
                eval_result: res.data.eval_result,
                difficulty_change: res.data.difficulty_change,
                old_difficulty: res.data.old_difficulty,
                new_difficulty: res.data.new_difficulty
            });

            if (res.data.is_complete) {
                setReport(res.data.report);
                setStatus('finished');
            } else {
                setCurrentQuestion({
                    id: res.data.next_question_id,
                    question: res.data.next_question,
                    category: res.data.next_category,
                    difficulty: res.data.next_difficulty,
                    topic: res.data.next_topic,
                    source: res.data.next_source,
                    is_followup: res.data.is_followup
                });
                setCurrentDifficulty(res.data.next_difficulty || currentDifficulty);
                setCurrentStep(res.data.current_step);
                setAnswerText('');
                setStatus('active');
                speak(res.data.next_question);
            }
        } catch (err) {
            console.error("Answer submission error:", err);
            setError(err.response?.data?.detail || "Failed to process answer. Please try again.");
            setStatus('active');
        }
    };

    const getDifficultyBadge = (diff) => {
        const d = (diff || "MEDIUM").toUpperCase();
        if (d === 'HARD') {
            return (
                <span className="bg-rose-950/70 text-rose-300 border border-rose-800 px-3 py-1 rounded-full text-xs font-black flex items-center gap-1">
                    <Flame className="w-3.5 h-3.5 text-rose-400" /> 🔥 HARD
                </span>
            );
        }
        if (d === 'EASY') {
            return (
                <span className="bg-emerald-950/70 text-emerald-300 border border-emerald-800 px-3 py-1 rounded-full text-xs font-black flex items-center gap-1">
                    <Sprout className="w-3.5 h-3.5 text-emerald-400" /> 🌱 EASY
                </span>
            );
        }
        return (
            <span className="bg-amber-950/70 text-amber-300 border border-amber-800 px-3 py-1 rounded-full text-xs font-black flex items-center gap-1">
                <Zap className="w-3.5 h-3.5 text-amber-400" /> ⚡ MEDIUM
            </span>
        );
    };

    return (
        <div className="flex-1 overflow-y-auto bg-slate-900 text-slate-100 p-6 md:p-12 relative">
            <div className="max-w-6xl mx-auto space-y-8">

                {/* Page Header */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-indigo-600/20 text-indigo-400 rounded-2xl border border-indigo-500/30">
                            <Mic className="w-8 h-8" />
                        </div>
                        <div>
                            <h1 className="text-3xl md:text-4xl font-black text-white tracking-tight">
                                AI Adaptive Interview
                            </h1>
                            <p className="text-slate-400 text-sm md:text-base mt-1 font-medium">
                                An interview that adapts to your performance.
                            </p>
                        </div>
                    </div>
                </div>

                {error && (
                    <div className="p-4 bg-rose-950/40 border border-rose-500/40 rounded-2xl text-xs text-rose-300 flex items-center gap-2 font-medium">
                        <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
                        <span>{error}</span>
                    </div>
                )}

                {/* SETUP STAGE */}
                {status === 'setup' && (
                    <div className="space-y-8 max-w-3xl mx-auto">
                        
                        {/* Resume Session Banner */}
                        {activeSession && (
                            <div className="bg-gradient-to-r from-amber-950/40 via-slate-900 to-slate-900 border border-amber-500/30 p-6 rounded-3xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-xl">
                                <div className="space-y-1">
                                    <span className="text-[10px] font-black uppercase tracking-wider bg-amber-500/20 text-amber-300 border border-amber-500/30 px-2.5 py-0.5 rounded-full">
                                        ⚡ Unfinished Session Found
                                    </span>
                                    <h3 className="text-lg font-bold text-white">
                                        {activeSession.target_role} ({activeSession.interview_type.toUpperCase()})
                                    </h3>
                                    <p className="text-xs text-slate-400">
                                        Stopped at Question {activeSession.current_step} of {activeSession.total_questions} • Current Difficulty: {activeSession.current_difficulty}
                                    </p>
                                </div>

                                <button
                                    onClick={handleResumeActiveInterview}
                                    className="px-5 py-2.5 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-xl text-xs flex items-center gap-2 shadow-lg shadow-amber-500/20 transition-all flex-shrink-0"
                                >
                                    <Play className="w-4 h-4 fill-current" />
                                    <span>Resume Interview</span>
                                </button>
                            </div>
                        )}

                        {/* Setup Form Container */}
                        <div className="bg-slate-800/80 border border-slate-700/80 rounded-3xl p-8 shadow-2xl space-y-6">
                            <div className="border-b border-slate-700/60 pb-4">
                                <h2 className="text-xl font-bold text-white">Configure Your Mock Interview</h2>
                                <p className="text-xs text-slate-400 mt-1">
                                    Our AI tutor will dynamically increase difficulty on strong answers and ask clarification questions on weak answers.
                                </p>
                            </div>

                            <div className="grid md:grid-cols-2 gap-6">
                                
                                {/* Target Role */}
                                <div className="space-y-2">
                                    <label className="text-xs font-bold uppercase tracking-wider text-slate-300">Target Role</label>
                                    <input 
                                        type="text"
                                        value={targetRole}
                                        onChange={(e) => setTargetRole(e.target.value)}
                                        placeholder="e.g. Full Stack Developer, Data Engineer"
                                        className="w-full bg-slate-950 border border-slate-700 rounded-2xl px-4 py-3 text-sm text-white focus:outline-none focus:border-indigo-500 font-medium"
                                    />
                                </div>

                                {/* Interview Type */}
                                <div className="space-y-2">
                                    <label className="text-xs font-bold uppercase tracking-wider text-slate-300">Interview Type</label>
                                    <select
                                        value={interviewType}
                                        onChange={(e) => setInterviewType(e.target.value)}
                                        className="w-full bg-slate-950 border border-slate-700 rounded-2xl px-4 py-3 text-sm text-white focus:outline-none focus:border-indigo-500 font-medium"
                                    >
                                        <option value="technical">Technical Interview</option>
                                        <option value="project">Project Architecture Interview</option>
                                        <option value="resume">Resume Intelligence Interview</option>
                                        <option value="mixed">Mixed (Technical + Project + Behavioral)</option>
                                    </select>
                                </div>

                                {/* Starting Difficulty */}
                                <div className="space-y-2">
                                    <label className="text-xs font-bold uppercase tracking-wider text-slate-300">Starting Difficulty</label>
                                    <div className="grid grid-cols-3 gap-2">
                                        {['EASY', 'MEDIUM', 'HARD'].map(d => (
                                            <button
                                                key={d}
                                                type="button"
                                                onClick={() => setStartingDifficulty(d)}
                                                className={`py-3 rounded-2xl text-xs font-bold transition-all border ${
                                                    startingDifficulty === d 
                                                        ? 'bg-indigo-600 border-indigo-500 text-white shadow-lg shadow-indigo-600/30'
                                                        : 'bg-slate-900 border-slate-700 text-slate-400 hover:text-white'
                                                }`}
                                            >
                                                {d}
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                {/* Question Count */}
                                <div className="space-y-2">
                                    <label className="text-xs font-bold uppercase tracking-wider text-slate-300">Number of Questions</label>
                                    <select
                                        value={questionCount}
                                        onChange={(e) => setQuestionCount(Number(e.target.value))}
                                        className="w-full bg-slate-950 border border-slate-700 rounded-2xl px-4 py-3 text-sm text-white focus:outline-none focus:border-indigo-500 font-medium"
                                    >
                                        <option value={5}>5 Questions (Quick Check)</option>
                                        <option value={10}>10 Questions (Standard Adaptive)</option>
                                        <option value={15}>15 Questions (Full Technical Loop)</option>
                                    </select>
                                </div>
                            </div>

                            {/* Resume Toggle Card */}
                            {activeResume && (
                                <div className="p-4 bg-indigo-950/40 border border-indigo-500/30 rounded-2xl flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <FileText className="w-5 h-5 text-indigo-400" />
                                        <div>
                                            <span className="text-xs font-bold text-white block">Use Active Resume Data</span>
                                            <span className="text-[10px] text-slate-400">{activeResume.file_name} ({activeResume.projects?.length || 0} projects)</span>
                                        </div>
                                    </div>
                                    <button
                                        type="button"
                                        onClick={() => setUseResume(!useResume)}
                                        className={`px-4 py-1.5 rounded-xl text-xs font-bold transition-all ${
                                            useResume
                                                ? 'bg-emerald-500 text-slate-950'
                                                : 'bg-slate-800 text-slate-400 hover:text-white border border-slate-700'
                                        }`}
                                    >
                                        {useResume ? '✓ Using Resume' : 'Use Resume'}
                                    </button>
                                </div>
                            )}

                            {/* Submit Button */}
                            <button
                                onClick={handleStartInterview}
                                className="w-full py-4 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-2xl shadow-xl shadow-indigo-600/30 transition-all text-sm flex items-center justify-center gap-2"
                            >
                                <Play className="w-4 h-4 fill-current" />
                                <span>Start Adaptive Interview</span>
                            </button>

                        </div>

                    </div>
                )}

                {/* LOADING OVERLAY */}
                {status === 'evaluating' && (
                    <div className="bg-slate-800/80 border border-slate-700/80 rounded-3xl p-12 text-center max-w-xl mx-auto space-y-6 shadow-2xl animate-pulse my-12">
                        <div className="w-16 h-16 bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 rounded-2xl flex items-center justify-center mx-auto shadow-lg">
                            <Loader2 className="w-8 h-8 animate-spin text-indigo-400" />
                        </div>
                        <div className="space-y-2">
                            <h3 className="text-xl font-bold text-white">AI Adaptive Engine</h3>
                            <p className="text-xs font-mono text-indigo-300 uppercase tracking-wider">{loadingStage}</p>
                        </div>
                    </div>
                )}

                {/* ACTIVE INTERVIEW SESSION */}
                {status === 'active' && currentQuestion && (
                    <div className="space-y-6 max-w-4xl mx-auto animate-in slide-in-from-right duration-300">
                        
                        {/* Immediate Feedback Banner from previous answer */}
                        {lastFeedback && (
                            <div className="bg-slate-800/90 border border-slate-700 p-5 rounded-3xl shadow-xl space-y-4">
                                <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-slate-700/60 pb-3 gap-2">
                                    <span className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                                        <Sparkles className="w-4 h-4 text-indigo-400" /> Answer Evaluation & Delivery
                                    </span>
                                    <div className="flex items-center gap-3">
                                        <span className="text-xs font-black text-indigo-400 font-mono">
                                            Technical: {lastFeedback.eval_result?.overall_score}%
                                        </span>
                                        {lastFeedback.communication_analysis && (
                                            <span className="text-xs font-black text-emerald-400 font-mono">
                                                Communication: {lastFeedback.communication_analysis?.communication_score}%
                                            </span>
                                        )}
                                        {lastFeedback.difficulty_change === 'INCREASED' && (
                                            <span className="bg-emerald-950 text-emerald-300 border border-emerald-800 px-2.5 py-0.5 rounded-full text-[10px] font-black">
                                                ✓ Technical Difficulty: {lastFeedback.new_difficulty}
                                            </span>
                                        )}
                                        {lastFeedback.difficulty_change === 'DECREASED' && (
                                            <span className="bg-rose-950 text-rose-300 border border-rose-800 px-2.5 py-0.5 rounded-full text-[10px] font-black">
                                                ↓ Technical Difficulty: {lastFeedback.new_difficulty}
                                            </span>
                                        )}
                                    </div>
                                </div>
                                <p className="text-xs text-slate-300 leading-relaxed font-medium">
                                    {lastFeedback.eval_result?.feedback}
                                </p>

                                {/* Communication Coach Compact Breakdown */}
                                {lastFeedback.communication_analysis && (
                                    <div className="pt-2 border-t border-slate-700/40 space-y-2">
                                        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                                            <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                                                <span className="text-[10px] text-slate-500 uppercase block font-bold">Clarity</span>
                                                <span className="font-bold text-white font-mono">{lastFeedback.communication_analysis.clarity_score}%</span>
                                            </div>
                                            <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                                                <span className="text-[10px] text-slate-500 uppercase block font-bold">Grammar</span>
                                                <span className="font-bold text-emerald-400 font-mono">{lastFeedback.communication_analysis.grammar_score}%</span>
                                            </div>
                                            <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                                                <span className="text-[10px] text-slate-500 uppercase block font-bold">Speaking Pace</span>
                                                <span className="font-bold text-indigo-300">{lastFeedback.communication_analysis.speaking_pace}</span>
                                            </div>
                                            <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                                                <span className="text-[10px] text-slate-500 uppercase block font-bold">Filler Words</span>
                                                <span className="font-bold text-amber-400 font-mono">{lastFeedback.communication_analysis.filler_word_count}</span>
                                            </div>
                                        </div>

                                        {lastFeedback.communication_analysis.grammar_improvements && lastFeedback.communication_analysis.grammar_improvements.length > 0 && (
                                            <div className="p-3 bg-indigo-950/40 border border-indigo-500/20 rounded-xl text-[11px]">
                                                <span className="font-bold text-indigo-400 block mb-1">Grammar Improvement Tip:</span>
                                                <span className="text-slate-400 line-through block">"{lastFeedback.communication_analysis.grammar_improvements[0].incorrect}"</span>
                                                <span className="text-emerald-300 font-bold block">✓ "{lastFeedback.communication_analysis.grammar_improvements[0].improved}"</span>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Top Bar: Progress & Difficulty */}
                        <div className="flex items-center justify-between bg-slate-800/80 p-4 rounded-2xl border border-slate-700/80">
                            <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                                Question {currentStep} of {totalQuestions}
                            </span>
                            <div className="flex items-center gap-3">
                                <span className="text-[10px] font-bold uppercase tracking-wider bg-indigo-950 text-indigo-300 px-2.5 py-1 rounded-full border border-indigo-800">
                                    {currentQuestion.category || "TECHNICAL"}
                                </span>
                                {getDifficultyBadge(currentDifficulty)}
                            </div>
                        </div>

                        {/* Question Card */}
                        <div className="bg-slate-800 p-8 rounded-3xl border border-slate-700 shadow-2xl relative space-y-3">
                            {currentQuestion.source && (
                                <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider flex items-center gap-1">
                                    <Sparkles className="w-3.5 h-3.5" /> Source: {currentQuestion.source}
                                </span>
                            )}
                            <p className="text-xl md:text-2xl font-bold text-white leading-relaxed">
                                "{currentQuestion.question}"
                            </p>
                        </div>

                        {/* Answer Box */}
                        <div className="space-y-3">
                            <div className="flex items-center justify-between">
                                <label className="text-xs font-bold uppercase tracking-wider text-slate-400">Your Answer</label>
                                <button
                                    onClick={toggleRecording}
                                    className={`px-3 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-all ${
                                        isRecording
                                            ? 'bg-rose-500/20 text-rose-400 border border-rose-500/50 animate-pulse'
                                            : 'bg-slate-800 text-slate-300 border border-slate-700 hover:text-white'
                                    }`}
                                >
                                    {isRecording ? <MicOff className="w-3.5 h-3.5" /> : <Mic className="w-3.5 h-3.5 text-indigo-400" />}
                                    {isRecording ? 'Stop Recording' : '🎤 Record Answer'}
                                </button>
                            </div>

                            <textarea
                                value={answerText}
                                onChange={(e) => setAnswerText(e.target.value)}
                                placeholder="Explain your approach, choices, and technical trade-offs..."
                                rows={6}
                                className="w-full bg-slate-950 border border-slate-700 rounded-2xl p-5 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 leading-relaxed resize-none text-sm font-medium"
                            />
                        </div>

                        {/* Submit Action */}
                        <button
                            onClick={handleSubmitAnswer}
                            disabled={!answerText.trim() || answerText.trim().length < 4}
                            className="w-full py-4 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-slate-600 text-white font-bold rounded-2xl shadow-xl flex items-center justify-center gap-2 transition-all text-sm"
                        >
                            <span>{currentStep >= totalQuestions ? 'Submit & Generate Final Report' : 'Submit Answer & Continue'}</span>
                            <ArrowRight className="w-4 h-4" />
                        </button>

                    </div>
                )}

                {/* FINAL ADAPTIVE REPORT */}
                {status === 'finished' && report && (
                    <div className="space-y-8 max-w-5xl mx-auto animate-in zoom-in-95 duration-300">
                        
                        {/* Report Header Banner */}
                        <div className="bg-gradient-to-r from-slate-900 via-indigo-950/60 to-slate-900 border border-slate-800 p-8 rounded-3xl flex flex-col md:flex-row items-center justify-between gap-6 shadow-2xl">
                            <div className="space-y-2 text-center md:text-left">
                                <div className="w-12 h-12 bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 rounded-2xl flex items-center justify-center mx-auto md:mx-0 shadow-lg">
                                    <Award className="w-7 h-7" />
                                </div>
                                <h2 className="text-3xl font-black text-white">AI Adaptive Interview Report</h2>
                                <p className="text-xs text-slate-400">
                                    Full analysis of your adaptive performance, difficulty scaling, and technical depth.
                                </p>
                            </div>

                            <div className="bg-slate-950/80 p-6 rounded-2xl border border-slate-800 text-center min-w-[140px]">
                                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block">Overall Score</span>
                                <span className="text-4xl font-black text-indigo-400 font-mono mt-1 block">
                                    {report.overall_score}%
                                </span>
                            </div>
                        </div>

                        {/* Metric Scores Grid */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <div className="bg-slate-800/80 p-5 rounded-2xl border border-slate-700/80 shadow-lg">
                                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Technical Accuracy</span>
                                <div className="text-2xl font-black text-white mt-1 font-mono">{report.technical_score}%</div>
                            </div>
                            <div className="bg-slate-800/80 p-5 rounded-2xl border border-slate-700/80 shadow-lg">
                                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Communication</span>
                                <div className="text-2xl font-black text-indigo-400 mt-1 font-mono">{report.communication_score}%</div>
                            </div>
                            <div className="bg-slate-800/80 p-5 rounded-2xl border border-slate-700/80 shadow-lg">
                                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Problem Solving</span>
                                <div className="text-2xl font-black text-emerald-400 mt-1 font-mono">{report.problem_solving_score}%</div>
                            </div>
                            <div className="bg-slate-800/80 p-5 rounded-2xl border border-slate-700/80 shadow-lg">
                                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Project Knowledge</span>
                                <div className="text-2xl font-black text-amber-400 mt-1 font-mono">{report.project_knowledge_score}%</div>
                            </div>
                        </div>

                        {/* DIFFICULTY PROGRESSION TIMELINE */}
                        <div className="bg-slate-800/90 border border-slate-700 p-6 rounded-3xl space-y-4 shadow-xl">
                            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                                <TrendingUp className="w-4 h-4 text-indigo-400" />
                                Adaptive Difficulty Progression
                            </h3>
                            <div className="flex items-center gap-2 overflow-x-auto pb-2">
                                {(report.progression || []).map((step, idx) => (
                                    <React.Fragment key={idx}>
                                        <div className="bg-slate-900 border border-slate-700 p-3 rounded-2xl text-center min-w-[100px] flex-shrink-0">
                                            <span className="text-[10px] text-slate-500 font-bold block uppercase">Q{step.question_number}</span>
                                            <span className={`text-xs font-black block my-1 ${
                                                step.difficulty === 'HARD' ? 'text-rose-400' : step.difficulty === 'EASY' ? 'text-emerald-400' : 'text-amber-400'
                                            }`}>
                                                {step.difficulty}
                                            </span>
                                            <span className="text-[10px] font-bold text-slate-300 font-mono block">{step.score}%</span>
                                        </div>
                                        {idx < (report.progression || []).length - 1 && (
                                            <ChevronRight className="w-4 h-4 text-slate-600 flex-shrink-0" />
                                        )}
                                    </React.Fragment>
                                ))}
                            </div>
                        </div>

                        {/* PERFORMANCE TREND GRAPH */}
                        <div className="bg-slate-800/90 border border-slate-700 p-6 rounded-3xl space-y-4 shadow-xl">
                            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
                                Performance Score Across Questions
                            </h3>
                            <div className="h-48 w-full pt-2">
                                <ResponsiveContainer width="100%" height="100%">
                                    <AreaChart data={(report.progression || []).map(p => ({ question: `Q${p.question_number}`, score: p.score }))}>
                                        <defs>
                                            <linearGradient id="scoreGrad" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.8}/>
                                                <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                                            </linearGradient>
                                        </defs>
                                        <XAxis dataKey="question" stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                                        <YAxis domain={[0, 100]} stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                                        <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', fontSize: '12px' }} />
                                        <Area type="monotone" dataKey="score" stroke="#6366f1" strokeWidth={3} fillOpacity={1} fill="url(#scoreGrad)" />
                                    </AreaChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        {/* Executive AI Insight */}
                        {report.ai_insight && (
                            <div className="bg-indigo-950/40 border border-indigo-500/30 p-6 rounded-3xl space-y-2">
                                <span className="text-xs font-bold uppercase tracking-wider text-indigo-400 flex items-center gap-1.5">
                                    <Sparkles className="w-4 h-4" /> AI Interview Insight
                                </span>
                                <p className="text-sm text-indigo-100 leading-relaxed font-medium">
                                    "{report.ai_insight}"
                                </p>
                            </div>
                        )}

                        {/* Strengths & Weaknesses */}
                        <div className="grid md:grid-cols-2 gap-6">
                            <div className="bg-slate-800/90 border border-slate-700 p-6 rounded-3xl space-y-3">
                                <span className="text-xs font-bold uppercase tracking-wider text-emerald-400 block">
                                    ✓ Identified Strengths
                                </span>
                                <ul className="space-y-2 text-xs text-slate-200 font-medium">
                                    {(report.strengths || []).map((s, idx) => (
                                        <li key={idx} className="flex items-start gap-2">
                                            <span className="text-emerald-400">•</span>
                                            <span>{s}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            <div className="bg-slate-800/90 border border-slate-700 p-6 rounded-3xl space-y-3">
                                <span className="text-xs font-bold uppercase tracking-wider text-rose-400 block">
                                    ⚠ Areas for Improvement
                                </span>
                                <ul className="space-y-2 text-xs text-slate-200 font-medium">
                                    {(report.weaknesses || []).map((w, idx) => (
                                        <li key={idx} className="flex items-start gap-2">
                                            <span className="text-rose-400">•</span>
                                            <span>{w}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>

                        {/* Next Action Navigation Buttons */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4">
                            <button
                                onClick={() => {
                                    setStatus('setup');
                                    setReport(null);
                                    setInterviewId(null);
                                    setCurrentQuestion(null);
                                }}
                                className="py-4 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-2xl text-xs flex items-center justify-center gap-2 shadow-lg transition-all"
                            >
                                <RotateCcw className="w-4 h-4" />
                                <span>Start New Adaptive Interview</span>
                            </button>

                            <button
                                onClick={() => navigate('/knowledge-gaps')}
                                className="py-4 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-bold rounded-2xl text-xs flex items-center justify-center gap-2 transition-all"
                            >
                                <AlertCircle className="w-4 h-4 text-amber-400" />
                                <span>View Knowledge Gaps</span>
                            </button>

                            <button
                                onClick={() => navigate('/revision')}
                                className="py-4 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-bold rounded-2xl text-xs flex items-center justify-center gap-2 transition-all"
                            >
                                <BookOpen className="w-4 h-4 text-indigo-400" />
                                <span>Practice Revision Hub</span>
                            </button>
                        </div>

                    </div>
                )}

            </div>
        </div>
    );
};

export default MockInterview;
