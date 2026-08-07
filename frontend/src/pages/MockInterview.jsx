import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Play, CheckCircle2, AlertCircle, Loader2, StopCircle, RefreshCcw, Volume2 } from 'lucide-react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, ResponsiveContainer } from 'recharts';
import api from '../api/axios';

const MockInterview = () => {
    const [file, setFile] = useState(null);
    const [extractedNotes, setExtractedNotes] = useState('');
    const [durationMinutes, setDurationMinutes] = useState(5);
    const [status, setStatus] = useState('setup'); // setup, active, loading, finished
    
    const [interviewTranscript, setInterviewTranscript] = useState([]);
    const [currentQuestion, setCurrentQuestion] = useState('');
    const [currentAnswer, setCurrentAnswer] = useState('');
    
    const [isRecording, setIsRecording] = useState(false);
    const [error, setError] = useState(null);
    const [evaluation, setEvaluation] = useState(null);
    const [timeLeft, setTimeLeft] = useState(0);
    
    const recognitionRef = useRef(null);
    const timerRef = useRef(null);

    // Initialize Speech Recognition
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
                    setCurrentAnswer(prev => prev + finalTranscript);
                }
            };

            rec.onerror = (event) => {
                console.error('Speech recognition error', event.error);
                setIsRecording(false);
                setError('Microphone error: ' + event.error);
            };

            rec.onend = () => {
                setIsRecording(false);
            };

            recognitionRef.current = rec;
        }
    }, []);

    const speak = (text) => {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        window.speechSynthesis.speak(utterance);
    };

    const startInterview = async () => {
        if (!file) {
            setError("Please upload a file to study from.");
            return;
        }
        
        setError(null);
        setStatus('loading');
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const res = await api.post('/interview/start', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            
            setExtractedNotes(res.data.extracted_text);
            setCurrentQuestion(res.data.question);
            setInterviewTranscript([]);
            setStatus('active');
            setTimeLeft(durationMinutes * 60);
            
            // Start Timer
            timerRef.current = setInterval(() => {
                setTimeLeft(prev => {
                    if (prev <= 1) {
                        clearInterval(timerRef.current);
                        endInterview(true);
                        return 0;
                    }
                    return prev - 1;
                });
            }, 1000);
            
            speak(res.data.question);
            
        } catch (err) {
            setError("Failed to start interview. Try again.");
            setStatus('setup');
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

    const submitAnswer = async () => {
        if (!currentAnswer.trim() || isRecording) return;
        
        const newTranscript = [...interviewTranscript, { question: currentQuestion, answer: currentAnswer }];
        setInterviewTranscript(newTranscript);
        setCurrentAnswer('');
        setStatus('loading');
        
        try {
            const res = await api.post('/interview/answer', {
                notes: extractedNotes,
                previous_qa: newTranscript,
                is_final: false
            });
            
            setCurrentQuestion(res.data.next_question);
            speak(res.data.next_question);
            setStatus('active');
            
        } catch (err) {
            setError("Failed to process answer.");
            setStatus('active');
        }
    };

    const endInterview = async (auto = false) => {
        clearInterval(timerRef.current);
        window.speechSynthesis.cancel();
        if (isRecording) recognitionRef.current.stop();
        
        let finalTranscript = [...interviewTranscript];
        if (currentAnswer.trim() && !auto) {
             finalTranscript.push({ question: currentQuestion, answer: currentAnswer });
             setInterviewTranscript(finalTranscript);
        }
        
        setStatus('loading');
        try {
            const res = await api.post('/interview/answer', {
                notes: extractedNotes,
                previous_qa: finalTranscript,
                is_final: true
            });
            
            setEvaluation(res.data.evaluation);
            setStatus('finished');
            
            if (res.data.evaluation?.summary) {
                speak("Interview finished. " + res.data.evaluation.summary);
            }
        } catch (err) {
            setError("Failed to generate final evaluation.");
            setStatus('active');
        }
    };
    
    const formatTime = (seconds) => {
        const m = Math.floor(seconds / 60).toString().padStart(2, '0');
        const s = (seconds % 60).toString().padStart(2, '0');
        return `${m}:${s}`;
    };

    return (
        <div className="p-8 max-w-4xl mx-auto w-full pb-20">
            <h1 className="text-4xl font-black mb-8 flex items-center gap-3">
                <Mic className="w-8 h-8 text-indigo-400" />
                Mock Interview Studio
            </h1>

            {error && (
                <div className="mb-6 p-4 bg-red-900/30 border border-red-500/30 rounded-lg flex items-center gap-2 text-red-400">
                    <AlertCircle className="w-5 h-5" /> {error}
                </div>
            )}

            {status === 'setup' && (
                <div className="bg-slate-800 p-8 rounded-2xl border border-slate-700 shadow-lg animate-in fade-in slide-in-from-bottom-4">
                    <h2 className="text-2xl font-bold text-white mb-4">Prepare for Interview</h2>
                    <p className="text-slate-400 mb-6">Upload your study notes (TXT, PDF, DOCX) below. Our AI Tutor will read them and conduct a personalized voice-to-voice mock interview to test your knowledge.</p>
                    
                    <label className="block text-sm font-bold text-slate-300 mb-2">Upload Notes</label>
                    <div className="flex items-center justify-center w-full mb-6">
                        <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-slate-700 border-dashed rounded-xl cursor-pointer bg-slate-900 hover:bg-slate-800 hover:border-indigo-500 transition-colors">
                            <div className="flex flex-col items-center justify-center pt-5 pb-6">
                                <svg className="w-8 h-8 mb-4 text-indigo-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 16">
                                    <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"/>
                                </svg>
                                <p className="mb-2 text-sm text-slate-300"><span className="font-semibold">Click to upload</span> or drag and drop</p>
                                <p className="text-xs text-slate-500">PDF, DOCX, or TXT</p>
                            </div>
                            <input 
                                type="file" 
                                className="hidden" 
                                accept=".txt,.pdf,.docx"
                                onChange={(e) => setFile(e.target.files[0])}
                            />
                        </label>
                    </div>
                    {file && (
                        <div className="mb-6 p-3 bg-indigo-900/20 border border-indigo-500/30 rounded-lg text-indigo-300 text-sm flex items-center justify-between">
                            <span>Selected: {file.name}</span>
                            <button onClick={() => setFile(null)} className="text-red-400 hover:text-red-300 text-xs">Remove</button>
                        </div>
                    )}

                    <label className="block text-sm font-bold text-slate-300 mb-2">Interview Duration</label>
                    <select 
                        value={durationMinutes}
                        onChange={(e) => setDurationMinutes(Number(e.target.value))}
                        className="w-full bg-slate-900 border border-slate-700 rounded-lg py-3 px-4 text-white focus:outline-none focus:border-indigo-500 mb-8"
                    >
                        <option value={2}>2 Minutes (Quick Check)</option>
                        <option value={5}>5 Minutes (Standard)</option>
                        <option value={10}>10 Minutes (Deep Dive)</option>
                        <option value={30}>30 Minutes (Comprehensive)</option>
                        <option value={60}>60 Minutes (Full Length)</option>
                    </select>

                    <button 
                        onClick={startInterview}
                        disabled={!file}
                        className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-700 disabled:text-slate-500 text-white py-4 rounded-xl font-bold flex items-center justify-center gap-2 transition-all shadow-lg hover:shadow-indigo-500/25"
                    >
                        <Play className="w-5 h-5" /> Start Mock Interview
                    </button>
                </div>
            )}

            {(status === 'active' || status === 'loading') && !evaluation && (
                <div className="space-y-6 animate-in slide-in-from-bottom-4">
                    <div className="flex justify-between items-center bg-slate-800 p-4 rounded-xl border border-slate-700">
                        <div className="flex items-center gap-3">
                            <div className="w-3 h-3 rounded-full bg-red-500 animate-pulse"></div>
                            <span className="font-bold text-slate-200">Interview in Progress</span>
                        </div>
                        <div className="text-xl font-mono text-indigo-400 font-bold">
                            {formatTime(timeLeft)}
                        </div>
                    </div>

                    <div className="bg-indigo-900/20 border border-indigo-500/30 p-8 rounded-2xl relative">
                        <Volume2 className="absolute top-4 right-4 w-6 h-6 text-indigo-500/50" />
                        <h3 className="text-sm font-bold text-indigo-400 uppercase tracking-wider mb-4">Tutor Asks:</h3>
                        <p className="text-2xl text-white font-medium leading-relaxed">
                            {currentQuestion || "Preparing your first question..."}
                        </p>
                    </div>

                    <div className="bg-slate-800 p-6 rounded-2xl border border-slate-700 shadow-lg">
                        <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4 flex justify-between items-center">
                            Your Answer
                            <button 
                                onClick={toggleRecording}
                                disabled={status === 'loading'}
                                className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-bold transition-all ${isRecording ? 'bg-red-500 text-white animate-pulse shadow-lg shadow-red-500/30' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}`}
                            >
                                {isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                                {isRecording ? 'Stop Recording' : 'Start Recording'}
                            </button>
                        </h3>
                        
                        <div className="min-h-[120px] bg-slate-900 p-4 rounded-xl text-slate-200 mb-6 border border-slate-700">
                            {currentAnswer || <span className="text-slate-600 italic">Click the microphone and start speaking...</span>}
                        </div>

                        <div className="flex gap-4">
                            <button 
                                onClick={submitAnswer}
                                disabled={!currentAnswer.trim() || isRecording || status === 'loading'}
                                className="flex-1 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-700 disabled:opacity-50 text-white py-3 rounded-xl font-bold flex items-center justify-center gap-2 transition-all"
                            >
                                {status === 'loading' ? <Loader2 className="w-5 h-5 animate-spin" /> : <CheckCircle2 className="w-5 h-5" />}
                                Submit Answer
                            </button>
                            <button 
                                onClick={() => endInterview(false)}
                                disabled={status === 'loading'}
                                className="px-6 bg-red-900/50 hover:bg-red-900 text-red-200 border border-red-500/30 disabled:opacity-50 py-3 rounded-xl font-bold flex items-center justify-center gap-2 transition-all"
                            >
                                <StopCircle className="w-5 h-5" /> End Early
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {status === 'finished' && evaluation && (
                <div className="space-y-6 animate-in slide-in-from-bottom-8 duration-700">
                    <div className="bg-slate-800 rounded-3xl border border-slate-700 shadow-2xl p-8">
                        <div className="flex justify-between items-start mb-8">
                            <div>
                                <h2 className="text-3xl font-black text-white mb-2">Final Evaluation</h2>
                                <p className="text-slate-400">Here is how you performed in your mock interview.</p>
                            </div>
                            <div className="flex items-center justify-center w-24 h-24 rounded-full border-4 shadow-lg shrink-0" 
                                style={{
                                    borderColor: evaluation.overall_score >= 8 ? '#10b981' : evaluation.overall_score >= 5 ? '#f59e0b' : '#ef4444',
                                    background: 'rgba(15, 23, 42, 0.5)'
                                }}>
                                <div className="text-center">
                                    <span className="text-3xl font-black text-white">{evaluation.overall_score || 0}</span>
                                    <span className="text-sm text-slate-400 block -mt-1">/ 10</span>
                                </div>
                            </div>
                        </div>

                        <div className="mb-8">
                            <h3 className="text-lg font-bold text-slate-300 mb-2 border-b border-slate-700 pb-2">Summary</h3>
                            <p className="text-slate-200 text-lg leading-relaxed">{evaluation.summary}</p>
                        </div>
                        
                        <div className="mb-8 bg-slate-900 rounded-2xl border border-slate-700 p-6 flex flex-col md:flex-row items-center">
                            <div className="w-full md:w-1/2 h-64">
                                <ResponsiveContainer width="100%" height="100%">
                                    <RadarChart cx="50%" cy="50%" outerRadius="80%" data={[
                                        { subject: 'Technical', A: evaluation.technical_score || 0, fullMark: 10 },
                                        { subject: 'Grammar', A: evaluation.grammar_score || 0, fullMark: 10 },
                                        { subject: 'Confidence', A: evaluation.confidence_score || 0, fullMark: 10 },
                                        { subject: 'Communication', A: evaluation.communication_score || 0, fullMark: 10 }
                                    ]}>
                                        <PolarGrid stroke="#334155" />
                                        <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                                        <Radar name="Score" dataKey="A" stroke="#6366f1" fill="#818cf8" fillOpacity={0.5} />
                                    </RadarChart>
                                </ResponsiveContainer>
                            </div>
                            <div className="w-full md:w-1/2 mt-6 md:mt-0 md:pl-8 space-y-4">
                                <h3 className="text-lg font-bold text-slate-300">Score Breakdown</h3>
                                <div className="space-y-2">
                                    <div className="flex justify-between items-center bg-slate-800 p-3 rounded-lg">
                                        <span className="text-slate-400">Technical Depth</span>
                                        <span className="text-white font-bold">{evaluation.technical_score || 0}/10</span>
                                    </div>
                                    <div className="flex justify-between items-center bg-slate-800 p-3 rounded-lg">
                                        <span className="text-slate-400">Grammar & Clarity</span>
                                        <span className="text-white font-bold">{evaluation.grammar_score || 0}/10</span>
                                    </div>
                                    <div className="flex justify-between items-center bg-slate-800 p-3 rounded-lg">
                                        <span className="text-slate-400">Communication Flow</span>
                                        <span className="text-white font-bold">{evaluation.communication_score || 0}/10</span>
                                    </div>
                                    <div className="flex justify-between items-center bg-slate-800 p-3 rounded-lg">
                                        <span className="text-slate-400">Speaking Confidence</span>
                                        <span className="text-white font-bold">{evaluation.confidence_score || 0}/10</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="mb-8 bg-indigo-900/20 p-6 rounded-xl border border-indigo-500/20">
                            <h3 className="text-sm font-bold text-indigo-400 uppercase tracking-wider mb-2">Technical Feedback</h3>
                            <p className="text-slate-300 leading-relaxed">{evaluation.technical_feedback}</p>
                        </div>
                        
                        {evaluation.filler_words_used && (
                            <div className="mb-8 bg-purple-900/10 p-6 rounded-xl border border-purple-500/20">
                                <h3 className="text-sm font-bold text-purple-400 uppercase tracking-wider mb-2">Confidence & Soft Skills</h3>
                                <p className="text-slate-300 leading-relaxed">{evaluation.filler_words_used}</p>
                            </div>
                        )}

                        <div className="grid md:grid-cols-2 gap-6 mb-8">
                            {evaluation.strengths && evaluation.strengths.length > 0 && (
                                <div className="bg-slate-900 rounded-xl p-6 border border-slate-700">
                                    <h3 className="text-sm font-bold text-green-400 uppercase tracking-wider mb-4">Strengths</h3>
                                    <ul className="space-y-3">
                                        {evaluation.strengths.map((item, i) => (
                                            <li key={i} className="flex gap-2 text-sm">
                                                <span className="text-green-500 shrink-0 mt-0.5">✓</span>
                                                <span className="text-slate-300">{item}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {evaluation.areas_for_improvement && evaluation.areas_for_improvement.length > 0 && (
                                <div className="bg-slate-900 rounded-xl p-6 border border-slate-700">
                                    <h3 className="text-sm font-bold text-orange-400 uppercase tracking-wider mb-4">Needs Improvement</h3>
                                    <ul className="space-y-3">
                                        {evaluation.areas_for_improvement.map((item, i) => (
                                            <li key={i} className="flex gap-2 text-sm">
                                                <span className="text-orange-500 shrink-0 mt-0.5">↑</span>
                                                <span className="text-slate-300">{item}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>

                        {evaluation.grammar_issues && evaluation.grammar_issues.length > 0 && (
                            <div className="mb-8 bg-red-900/10 p-6 rounded-xl border border-red-500/20">
                                <h3 className="text-sm font-bold text-red-400 uppercase tracking-wider mb-4">Grammar & Clarity Issues</h3>
                                <ul className="space-y-3">
                                    {evaluation.grammar_issues.map((issue, i) => (
                                        <li key={i} className="flex gap-2 text-sm">
                                            <span className="text-red-500 shrink-0 mt-0.5">•</span>
                                            <span className="text-slate-300">{issue}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        <div className="pt-6 border-t border-slate-700">
                            <button 
                                onClick={() => {
                                    setStatus('setup');
                                    setEvaluation(null);
                                    setInterviewTranscript([]);
                                    setCurrentQuestion('');
                                    setCurrentAnswer('');
                                    setFile(null);
                                    setExtractedNotes('');
                                }}
                                className="w-full bg-slate-700 hover:bg-slate-600 text-white py-4 rounded-xl font-bold flex items-center justify-center gap-2 transition-all"
                            >
                                <RefreshCcw className="w-5 h-5" /> Start New Interview
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default MockInterview;
