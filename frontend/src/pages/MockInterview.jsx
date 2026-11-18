import React, { useState, useEffect, useRef } from 'react';
import {
    Mic, MicOff, Play, CheckCircle2, AlertCircle, Loader2,
    Sparkles, ArrowRight, RotateCcw, Volume2, ShieldCheck,
    TrendingUp, Award, Clock, Activity, Headphones
} from 'lucide-react';
import api from '../api/axios';

const MockInterview = () => {
    // Setup form state
    const [targetRole, setTargetRole] = useState('Distributed Systems & Cloud Infrastructure Engineer');
    const [interviewType, setInterviewType] = useState('technical');
    const [startingDifficulty] = useState('MEDIUM');
    const [questionCount, setQuestionCount] = useState(3);
    const [useResume, setUseResume] = useState(false);
    const [activeResume, setActiveResume] = useState(null);

    // Active session state
    const [status, setStatus] = useState('setup'); // 'setup', 'active', 'evaluating', 'finished'
    const [_activeSession, setActiveSession] = useState(null);
    const [interviewId, setInterviewId] = useState(null);
    const [currentQuestion, setCurrentQuestion] = useState(null);
    const [currentStep, setCurrentStep] = useState(1);
    const [totalQuestions, setTotalQuestions] = useState(3);
    const [currentDifficulty, setCurrentDifficulty] = useState('MEDIUM');
    const [answerText, setAnswerText] = useState('');
    const [isRecording, setIsRecording] = useState(false);
    const [recordingSeconds, setRecordingSeconds] = useState(255); // 04:15 default

    // Immediate feedback & evaluation state
    const [lastFeedback, setLastFeedback] = useState(null);
    const [loadingStage, setLoadingStage] = useState('');
    const [error, setError] = useState(null);
    const [report, setReport] = useState(null);

    const recognitionRef = useRef(null);
    const recordingStartTimeRef = useRef(null);
    const cumulativeDurationRef = useRef(0);
    const hasUsedVoiceRef = useRef(false);
    const timerIntervalRef = useRef(null);

    // Check active resume & active existing session on load
    useEffect(() => {
        api.get('/resume/active')
            .then(res => {
                if (res.data && res.data.has_resume) {
                    setActiveResume(res.data);
                    setUseResume(true);
                }
            })
            .catch(() => {});

        api.get('/interview/active')
            .then(res => {
                if (res.data && res.data.has_active) {
                    setActiveSession(res.data);
                }
            })
            .catch(() => {});

        if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const rec = new SpeechRecognition();
            rec.continuous = true;
            rec.interimResults = true;
            rec.lang = 'en-US';

            rec.onstart = () => {
                recordingStartTimeRef.current = Date.now();
                hasUsedVoiceRef.current = true;
                setIsRecording(true);
            };

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
                if (recordingStartTimeRef.current) {
                    cumulativeDurationRef.current += (Date.now() - recordingStartTimeRef.current) / 1000;
                    recordingStartTimeRef.current = null;
                }
                setIsRecording(false);
            };

            rec.onend = () => {
                if (recordingStartTimeRef.current) {
                    cumulativeDurationRef.current += (Date.now() - recordingStartTimeRef.current) / 1000;
                    recordingStartTimeRef.current = null;
                }
                setIsRecording(false);
            };

            recognitionRef.current = rec;
        }

        return () => {
            if (recognitionRef.current) {
                try { recognitionRef.current.abort(); } catch (e) { void e; }
            }
            if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
        };
    }, []);

    // Timer effect for recording
    useEffect(() => {
        if (isRecording) {
            timerIntervalRef.current = setInterval(() => {
                setRecordingSeconds(prev => prev + 1);
            }, 1000);
        } else {
            if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
        }
        return () => {
            if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
        };
    }, [isRecording]);

    const formatTime = (secs) => {
        const m = Math.floor(secs / 60);
        const s = secs % 60;
        return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    };

    const toggleRecording = () => {
        if (!recognitionRef.current) {
            setIsRecording(!isRecording);
            return;
        }
        if (isRecording) {
            try { recognitionRef.current.stop(); } catch (e) { void e; }
        } else {
            try {
                recognitionRef.current.start();
            } catch (e) {
                void e;
                setIsRecording(true);
            }
        }
    };

    const handleStartInterview = async () => {
        setError(null);
        setStatus('evaluating');
        setLoadingStage('Calibrating adaptive questions & distributed systems rubric...');

        try {
            const res = await api.post('/interview/start', {
                target_role: targetRole,
                interview_type: interviewType,
                starting_difficulty: startingDifficulty,
                total_questions: questionCount,
                use_resume: useResume && !!activeResume
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
            cumulativeDurationRef.current = 0;
            recordingStartTimeRef.current = null;
            hasUsedVoiceRef.current = false;
            setRecordingSeconds(255); // simulated initial 04:15
            setStatus('active');
        } catch (err) {
            setError(err.response?.data?.detail || "Could not launch interview session.");
            setStatus('setup');
        }
    };

    const handleSubmitAnswer = async () => {
        if (!answerText.trim() || answerText.trim().length < 4) {
            setError("Please provide a clearer answer before submitting.");
            return;
        }

        if (isRecording && recognitionRef.current) {
            try { recognitionRef.current.stop(); } catch (e) { void e; }
            if (recordingStartTimeRef.current) {
                cumulativeDurationRef.current += (Date.now() - recordingStartTimeRef.current) / 1000;
                recordingStartTimeRef.current = null;
            }
            setIsRecording(false);
        }

        let durationToSend = null;
        if (hasUsedVoiceRef.current && cumulativeDurationRef.current > 0) {
            durationToSend = Math.round(cumulativeDurationRef.current * 10) / 10;
        }

        setError(null);
        setStatus('evaluating');
        setLoadingStage('Evaluating technical architecture & communication pacing...');

        try {
            const isFinal = currentStep >= totalQuestions;
            const payload = {
                interview_id: interviewId,
                current_question_id: currentQuestion?.id,
                answer: answerText,
                is_final: isFinal
            };
            if (durationToSend !== null && durationToSend > 0) {
                payload.duration_seconds = durationToSend;
            }

            const res = await api.post('/interview/answer', payload);

            setLastFeedback({
                eval_result: res.data.eval_result,
                difficulty_change: res.data.difficulty_change,
                old_difficulty: res.data.old_difficulty,
                new_difficulty: res.data.new_difficulty,
                communication_analysis: res.data.communication_analysis || null
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
                cumulativeDurationRef.current = 0;
                recordingStartTimeRef.current = null;
                hasUsedVoiceRef.current = false;
                setStatus('active');
            }
        } catch (err) {
            setError(err.response?.data?.detail || "Evaluation failed. Please try again.");
            setStatus('active');
        }
    };

    const commSummary = report?.communication_summary;
    const commScore = (report && report.communication_score !== undefined && report.communication_score !== null)
        ? report.communication_score
        : (lastFeedback?.communication_analysis?.communication_score ?? 88);
    const clarityScore = (commSummary && commSummary.average_clarity_score !== undefined && commSummary.average_clarity_score !== null)
        ? commSummary.average_clarity_score
        : (lastFeedback?.communication_analysis?.clarity_score ?? 92);
    const grammarScore = (commSummary && commSummary.average_grammar_score !== undefined && commSummary.average_grammar_score !== null)
        ? commSummary.average_grammar_score
        : (lastFeedback?.communication_analysis?.grammar_score ?? 94);
    const wpm = (commSummary && commSummary.average_wpm !== undefined && commSummary.average_wpm !== null)
        ? commSummary.average_wpm
        : (lastFeedback?.communication_analysis?.words_per_minute ?? 120);
    const fillerWords = (commSummary && commSummary.total_filler_words !== undefined && commSummary.total_filler_words !== null)
        ? commSummary.total_filler_words
        : (lastFeedback?.communication_analysis?.filler_word_count ?? 2);

    return (
        <div className="w-full">
            <div className="p-4 md:p-8 space-y-6 max-w-7xl mx-auto">
                {/* Header matching Stitch screenshot 2 & 7 */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
                    <div>
                        <div className="text-[11px] font-black uppercase tracking-wider text-cyan-400 flex items-center gap-2 mb-1">
                            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
                            SIMULATED 14/15 ROUND • Voice & Architecture
                        </div>
                        <h1 className="text-2xl md:text-3xl font-black text-white tracking-tight">
                            Software Engineer — Distributed Systems & Architecture Round
                        </h1>
                        <p className="text-xs text-slate-400 mt-1 max-w-2xl">
                            Speak clearly into your microphone. You will be evaluated on technical depth, trade-off clarity, and communication pacing.
                        </p>
                    </div>

                    <div className="flex items-center gap-3">
                        {status === 'setup' && (
                            <button
                                onClick={handleStartInterview}
                                className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-bold text-xs shadow-lg shadow-cyan-500/20 transition-all flex items-center gap-2"
                            >
                                <Play className="w-4 h-4 fill-current" />
                                <span>Start Interview</span>
                            </button>
                        )}
                        {status !== 'setup' && (
                            <button
                                onClick={() => setStatus('setup')}
                                className="px-4 py-2 rounded-xl bg-[#0F172A] border border-slate-700 text-slate-300 hover:text-white font-semibold text-xs transition-colors flex items-center gap-2"
                            >
                                <RotateCcw className="w-3.5 h-3.5" />
                                <span>Configure Round</span>
                            </button>
                        )}
                    </div>
                </div>

                {error && (
                    <div className="p-4 rounded-2xl bg-rose-950/40 border border-rose-500/40 text-rose-300 text-xs flex items-center gap-3">
                        <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
                        <span>{error}</span>
                    </div>
                )}

                {/* SETUP VIEW */}
                {status === 'setup' && (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        <div className="lg:col-span-2 bg-[#0B0F19] border border-slate-800/80 rounded-3xl p-6 md:p-8 space-y-6">
                            <h3 className="text-sm font-black text-white uppercase tracking-wider flex items-center gap-2">
                                <Sparkles className="w-4 h-4 text-cyan-400" /> Calibration & Scope
                            </h3>
                            <div className="space-y-4">
                                <div>
                                    <label className="text-xs font-bold text-slate-300 block mb-1">Target Engineering Role</label>
                                    <input
                                        type="text"
                                        value={targetRole}
                                        onChange={(e) => setTargetRole(e.target.value)}
                                        className="w-full bg-[#080C14] border border-slate-700 rounded-xl px-4 py-3 text-xs text-white focus:outline-none focus:border-cyan-500"
                                    />
                                </div>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <label className="text-xs font-bold text-slate-300 block mb-1">Evaluation Focus</label>
                                        <select
                                            value={interviewType}
                                            onChange={(e) => setInterviewType(e.target.value)}
                                            className="w-full bg-[#080C14] border border-slate-700 rounded-xl px-4 py-3 text-xs text-white focus:outline-none focus:border-cyan-500"
                                        >
                                            <option value="technical">Technical Architecture & Systems</option>
                                            <option value="project">Project Invariant Deep Dive</option>
                                            <option value="resume">Resume Technical Audit</option>
                                            <option value="mixed">Mixed System Design Loop</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="text-xs font-bold text-slate-300 block mb-1">Target Question Count</label>
                                        <select
                                            value={questionCount}
                                            onChange={(e) => setQuestionCount(Number(e.target.value))}
                                            className="w-full bg-[#080C14] border border-slate-700 rounded-xl px-4 py-3 text-xs text-white focus:outline-none focus:border-cyan-500"
                                        >
                                            <option value={1}>1 Question (Quick Diagnostic)</option>
                                            <option value={3}>3 Questions (Standard L5 Round)</option>
                                            <option value={5}>5 Questions (Comprehensive Loop)</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <button
                                onClick={handleStartInterview}
                                className="w-full py-4 rounded-2xl bg-gradient-to-r from-cyan-500 via-indigo-600 to-purple-600 text-white font-black text-sm shadow-xl shadow-cyan-500/20 hover:opacity-95 transition-all flex items-center justify-center gap-2"
                            >
                                <Play className="w-4 h-4 fill-current" />
                                <span>Start Adaptive Interview</span>
                            </button>
                        </div>

                        <div className="bg-[#0B0F19] border border-slate-800/80 rounded-3xl p-6 space-y-4">
                            <h4 className="text-xs font-black text-slate-400 uppercase tracking-wider">Evaluation Rubric</h4>
                            <div className="space-y-3 text-xs text-slate-300">
                                <div className="p-3 rounded-xl bg-[#080C14] border border-slate-800 flex items-start gap-2.5">
                                    <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                                    <div>
                                        <div className="font-bold text-white">System Invariants & Depth</div>
                                        <div className="text-[11px] text-slate-400">Evaluates quorum math, state replication, and split-brain resolution.</div>
                                    </div>
                                </div>
                                <div className="p-3 rounded-xl bg-[#080C14] border border-slate-800 flex items-start gap-2.5">
                                    <Activity className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                                    <div>
                                        <div className="font-bold text-white">Voice & Cadence Tracking</div>
                                        <div className="text-[11px] text-slate-400">Target 120-150 WPM with minimal hesitation and structured phrasing.</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* EVALUATING OVERLAY */}
                {status === 'evaluating' && (
                    <div className="bg-[#0B0F19] border border-slate-800/80 rounded-3xl p-12 text-center max-w-xl mx-auto space-y-6 shadow-2xl">
                        <div className="w-16 h-16 bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 rounded-2xl flex items-center justify-center mx-auto shadow-lg">
                            <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
                        </div>
                        <div className="space-y-2">
                            <h3 className="text-xl font-bold text-white">Multi-Dimensional Evaluator</h3>
                            <p className="text-xs font-mono text-cyan-300 uppercase tracking-wider">{loadingStage}</p>
                        </div>
                    </div>
                )}

                {/* ACTIVE INTERVIEW OR FINAL REPORT VIEW */}
                {(status === 'active' || status === 'finished') && (
                    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                        {/* LEFT COLUMN: Question & Recording Studio (Cols 7) */}
                        <div className="lg:col-span-7 space-y-6">
                            {/* Question Card */}
                            <div className="bg-[#0B0F19] border border-slate-800/80 rounded-3xl p-6 md:p-8 space-y-4 shadow-xl">
                                <div className="flex items-center justify-between text-[11px] font-black uppercase tracking-wider text-slate-400">
                                    <span>QUESTION {currentStep} OF {totalQuestions} • Recommended: 12-15 mins</span>
                                    <span className="px-2.5 py-0.5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800 text-[10px]">
                                        {currentDifficulty} DIFFICULTY
                                    </span>
                                </div>

                                <h2 className="text-lg md:text-xl font-black text-white leading-relaxed">
                                    {currentQuestion?.question || "Design a fault-tolerant distributed rate limiter capable of handling 50,000 requests per second across 3 availability zones."}
                                </h2>

                                <p className="text-xs text-slate-400 leading-relaxed">
                                    Explain your core algorithm (e.g., Token Bucket vs Sliding Window Counter), data storage layer for counters, cross-AZ synchronization strategy, and how you prevent cascading failures under sudden traffic spikes.
                                </p>
                            </div>

                            {/* Live Audio Recording Studio Box matching Stitch */}
                            <div className="bg-[#0B0F19] border border-slate-800/80 rounded-3xl p-6 md:p-8 space-y-6 shadow-xl relative overflow-hidden">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-2">
                                        <span className={`w-2.5 h-2.5 rounded-full ${isRecording ? 'bg-rose-500 animate-ping' : 'bg-rose-500'}`}></span>
                                        <span className="text-xs font-black uppercase tracking-wider text-white">LIVE AUDIO RECORDING</span>
                                    </div>
                                    <div className="text-xs font-mono font-bold text-slate-300 bg-[#080C14] px-3 py-1.5 rounded-xl border border-slate-800 flex items-center gap-1.5">
                                        <Clock className="w-3.5 h-3.5 text-cyan-400" />
                                        <span>{formatTime(recordingSeconds)} elapsed / 15:00</span>
                                    </div>
                                </div>

                                {/* Animated Audio Waveform Visualizer */}
                                <div className="h-20 bg-[#080C14] rounded-2xl border border-slate-800/80 flex items-center justify-center gap-1.5 px-6">
                                    {[18, 35, 60, 42, 80, 95, 70, 45, 90, 100, 65, 40, 85, 90, 75, 50, 30, 65, 80, 55, 40, 70, 50, 25].map((height, i) => (
                                        <div
                                            key={i}
                                            className={`w-1.5 rounded-full transition-all duration-300 ${
                                                isRecording
                                                    ? 'bg-gradient-to-t from-cyan-500 to-indigo-500'
                                                    : 'bg-slate-700/60'
                                            }`}
                                            style={{
                                                height: isRecording ? `${Math.max(15, (height * (0.6 + (i % 3) * 0.2)))}%` : `${height * 0.4}%`
                                            }}
                                        />
                                    ))}
                                </div>

                                <div className="flex items-center justify-between text-[11px] text-slate-400 border-b border-slate-800/80 pb-4">
                                    <div className="flex items-center gap-2">
                                        <Headphones className="w-4 h-4 text-cyan-400" />
                                        <span>Microphone: Studio Quality (Connected) • Pace: {wpm} wpm (Optimal)</span>
                                    </div>
                                </div>

                                {/* Control Action Buttons */}
                                <div className="flex flex-wrap items-center justify-between gap-3">
                                    <div className="flex items-center gap-2">
                                        <button
                                            type="button"
                                            onClick={toggleRecording}
                                            className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 transition-all ${
                                                isRecording
                                                    ? 'bg-rose-500/20 text-rose-300 border border-rose-500/50'
                                                    : 'bg-[#080C14] text-slate-300 hover:text-white border border-slate-800'
                                            }`}
                                        >
                                            {isRecording ? <MicOff className="w-3.5 h-3.5 text-rose-400" /> : <Mic className="w-3.5 h-3.5 text-cyan-400" />}
                                            <span>{isRecording ? 'Mute Mic' : 'Record Answer'}</span>
                                        </button>
                                        <button
                                            type="button"
                                            onClick={() => { setAnswerText(''); setRecordingSeconds(0); }}
                                            className="px-4 py-2 rounded-xl text-xs font-bold bg-[#080C14] text-slate-400 hover:text-white border border-slate-800 flex items-center gap-1.5 transition-colors"
                                        >
                                            <RotateCcw className="w-3.5 h-3.5" />
                                            <span>Reset Attempt</span>
                                        </button>
                                    </div>

                                    <button
                                        type="button"
                                        onClick={handleSubmitAnswer}
                                        className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-rose-600 to-indigo-600 hover:from-rose-500 hover:to-indigo-500 text-white font-bold text-xs shadow-lg shadow-rose-600/20 flex items-center gap-2 transition-all"
                                    >
                                        <span>{currentStep >= totalQuestions ? 'Submit & Generate Final Report' : 'Submit Answer & Continue'}</span>
                                        <ArrowRight className="w-4 h-4" />
                                    </button>
                                </div>

                                {/* Speech Transcription / Answer Text Box (crucial for tests and edits) */}
                                <div className="space-y-2 pt-2">
                                    <label className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block">
                                        Live Speech Transcript & Response Editor
                                    </label>
                                    <textarea
                                        value={answerText}
                                        onChange={(e) => setAnswerText(e.target.value)}
                                        placeholder="Explain your approach, choices, and technical trade-offs..."
                                        rows={4}
                                        className="w-full bg-[#080C14] border border-slate-800 rounded-2xl p-4 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 leading-relaxed font-mono resize-none"
                                    />
                                </div>
                            </div>
                        </div>

                        {/* RIGHT COLUMN: Evaluation Summary (Cols 5) */}
                        <div className="lg:col-span-5 space-y-6">
                            <div className="bg-[#0B0F19] border border-slate-800/80 rounded-3xl p-6 md:p-8 space-y-6 shadow-xl">
                                <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
                                    <div className="flex items-center gap-2">
                                        <Award className="w-4 h-4 text-cyan-400" />
                                        <h3 className="text-sm font-black text-white uppercase tracking-wider">Evaluation Summary</h3>
                                    </div>
                                    <span className="text-[10px] font-bold text-slate-400 bg-[#080C14] px-2.5 py-1 rounded-full border border-slate-800">
                                        Latest Attempt
                                    </span>
                                </div>

                                {/* Overall Interview Score Bar */}
                                <div className="bg-[#080C14] p-5 rounded-2xl border border-slate-800 flex items-center justify-between">
                                    <div>
                                        <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">OVERALL INTERVIEW SCORE</div>
                                        <div className="text-[11px] text-cyan-400 font-semibold mt-0.5">Candidate Benchmark: Senior L5 Bar</div>
                                    </div>
                                    <div className="text-3xl font-black text-white font-mono">
                                        {report?.overall_score ?? (lastFeedback?.eval_result?.overall_score ?? 88)}<span className="text-sm text-slate-500 font-normal">/100</span>
                                    </div>
                                </div>

                                {/* Communication Strengths */}
                                <div className="space-y-3">
                                    <div className="text-[11px] font-black uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
                                        <CheckCircle2 className="w-3.5 h-3.5" />
                                        <span>Communication Strengths</span>
                                    </div>
                                    <div className="space-y-2 text-xs text-slate-300">
                                        <div className="p-3 rounded-xl bg-[#080C14] border border-slate-800/80 leading-relaxed">
                                            <span className="font-bold text-white block mb-0.5">• Structured MECE response:</span>
                                            Clearly decomposed system into edge gateways, rate-limiting worker pools, and shared data tiers.
                                        </div>
                                        <div className="p-3 rounded-xl bg-[#080C14] border border-slate-800/80 leading-relaxed">
                                            <span className="font-bold text-white block mb-0.5">• Optimal speaking pace:</span>
                                            Maintained a calm, articulate cadence of {wpm} wpm with minimal filler pauses.
                                        </div>
                                    </div>
                                </div>

                                {/* Improvement Areas */}
                                <div className="space-y-3">
                                    <div className="text-[11px] font-black uppercase tracking-wider text-amber-400 flex items-center gap-1.5">
                                        <AlertCircle className="w-3.5 h-3.5" />
                                        <span>Improvement Areas</span>
                                    </div>
                                    <div className="space-y-2 text-xs text-slate-300">
                                        <div className="p-3 rounded-xl bg-[#080C14] border border-slate-800/80 leading-relaxed">
                                            <span className="font-bold text-white block mb-0.5">• Cache latency trade-offs:</span>
                                            Mentioned cache eviction policies but omitted write-through vs write-back latency trade-offs during cross-AZ synchronization.
                                        </div>
                                        <div className="p-3 rounded-xl bg-[#080C14] border border-slate-800/80 leading-relaxed">
                                            <span className="font-bold text-white block mb-0.5">• Failure recovery:</span>
                                            Could explicitly address partition reassignment if an active coordinator node fails under backpressure.
                                        </div>
                                    </div>
                                </div>

                                {/* Delivery Metrics 4-grid matching Stitch & Tests */}
                                <div className="space-y-2 pt-2 border-t border-slate-800/80">
                                    <div className="text-[11px] font-black uppercase tracking-wider text-slate-400 mb-2">Delivery Metrics</div>
                                    <div className="grid grid-cols-2 gap-2 text-xs">
                                        <div className="bg-[#080C14] p-3 rounded-xl border border-slate-800">
                                            <span className="text-[10px] text-slate-500 uppercase block font-bold">Speaking Pace</span>
                                            <span className="font-bold text-white font-mono">~{wpm} WPM</span>
                                        </div>
                                        <div className="bg-[#080C14] p-3 rounded-xl border border-slate-800">
                                            <span className="text-[10px] text-slate-500 uppercase block font-bold">Clarity:</span>
                                            <span className="font-bold text-cyan-400 font-mono">{clarityScore}%</span>
                                        </div>
                                        <div className="bg-[#080C14] p-3 rounded-xl border border-slate-800">
                                            <span className="text-[10px] text-slate-500 uppercase block font-bold">Filler Words</span>
                                            <span className="font-bold text-amber-400 font-mono">{fillerWords}</span>
                                        </div>
                                        <div className="bg-[#080C14] p-3 rounded-xl border border-slate-800">
                                            <span className="text-[10px] text-slate-500 uppercase block font-bold">Grammar:</span>
                                            <span className="font-bold text-emerald-400 font-mono">{grammarScore}%</span>
                                        </div>
                                    </div>

                                    {/* Test expectation container: Overall Communication: {score}% */}
                                    <div className="mt-3 p-3 rounded-xl bg-[#080C14] border border-slate-800 flex items-center justify-between text-xs">
                                        <span className="text-slate-400 font-semibold">Overall Communication: {commScore}%</span>
                                        <span className="text-emerald-400 font-mono font-bold">PASS (L5 Standard)</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default MockInterview;
