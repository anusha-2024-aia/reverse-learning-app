/* eslint-disable react-hooks/set-state-in-effect */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Video, Users, Clock, Play, Pause, Square, Volume2, VolumeX,
    Sparkles, MessageSquare, Send, CheckCircle2, Coffee, Flame,
    ChevronDown, ShieldCheck, BookOpen, Layers, Terminal, AlertCircle, ArrowLeft
} from 'lucide-react';
import api from '../api/axios';

const VirtualStudyRoom = () => {
    const navigate = useNavigate();
    const [secondsLeft, setSecondsLeft] = useState(1827); // 30m 27s
    const [isRunning, setIsRunning] = useState(false);
    const [isMuted, setIsMuted] = useState(false);
    const [ambience, setAmbience] = useState("Ambient Rain (45kHz)");
    const [sessionLogged, setSessionLogged] = useState(false);
    const [cheers, setCheers] = useState({ plusOne: 14, focus: 28, coffee: 9 });

    // Room TA Synapse AI state
    const [taMessages, setTaMessages] = useState([
        { sender: 'Synapse TA', time: '14m ago', text: 'Hint for Pod: Remember that in Raft, a leader never commits log entries from previous terms by counting replicas; it must commit an entry from its current term.' }
    ]);
    const [taInput, setTaInput] = useState('');

    useEffect(() => {
        let interval = null;
        if (isRunning && secondsLeft > 0) {
            interval = setInterval(() => {
                setSecondsLeft(prev => prev - 1);
            }, 1000);
        } else if (secondsLeft === 0) {
            setIsRunning(false);
        }
        return () => clearInterval(interval);
    }, [isRunning, secondsLeft]);

    const formatTime = (secs) => {
        const m = Math.floor(secs / 60);
        const s = secs % 60;
        return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    };

    const handleEndSession = async () => {
        setIsRunning(false);
        try {
            await api.post('/sessions/live-focus', {
                topic_name: "Distributed Systems: Raft Consensus",
                duration_minutes: 25,
                objective: "Review Raft consensus invariants & solve 2 dynamic programming problems"
            });
            setSessionLogged(true);
            setTimeout(() => setSessionLogged(false), 4000);
        } catch (err) {
            console.error("Failed to log focus session:", err);
        }
    };

    const handleSendTaMessage = () => {
        if (!taInput.trim()) return;
        const newMsg = { sender: 'You', time: 'Just now', text: taInput.trim() };
        setTaMessages(prev => [...prev, newMsg]);
        setTaInput('');

        setTimeout(() => {
            setTaMessages(prev => [
                ...prev,
                {
                    sender: 'Synapse TA',
                    time: 'Just now',
                    text: 'Affirmative. State transitions are verified. Continue deep work sprint without context switching.'
                }
            ]);
        }, 1200);
    };

    return (
        <div className="space-y-6 max-w-7xl mx-auto pb-12">
            {/* Header Banner */}
            <div className="p-6 md:p-8 rounded-2xl bg-gradient-to-r from-[#0F172A] via-[#111827] to-[#1E1B4B] border border-slate-800/80 shadow-2xl flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div className="space-y-1.5">
                    <div className="flex items-center gap-2 text-[10px] uppercase font-black tracking-wider text-cyan-400">
                        <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
                        LIVE • 4 PEERS ACTIVE • Cyan Lab #01: Pomodoro Mode
                    </div>
                    <h1 className="text-2xl md:text-3xl font-black text-white tracking-tight">
                        Distributed Systems & Algorithms Focus Lab
                    </h1>
                    <p className="text-xs md:text-sm text-slate-300 max-w-2xl leading-relaxed">
                        Shared deep work room for MIT 6.824 & algorithmic problem solving — Fall 2025.
                    </p>
                </div>

                <div className="flex flex-wrap items-center gap-3">
                    <button
                        onClick={() => navigate('/')}
                        className="px-3.5 py-2 rounded-xl bg-slate-900/80 hover:bg-slate-800 text-slate-300 hover:text-white font-bold text-xs border border-slate-700 flex items-center gap-1.5 transition-colors"
                    >
                        <ArrowLeft className="w-3.5 h-3.5" />
                        <span>Dashboard</span>
                    </button>
                    {/* Ambience audio dropdown */}
                    <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300">
                        <select
                            value={ambience}
                            onChange={(e) => setAmbience(e.target.value)}
                            className="bg-transparent text-xs text-slate-200 focus:outline-none cursor-pointer"
                        >
                            <option value="Ambient Rain (45kHz)" className="bg-slate-900">Ambient Rain (45kHz)</option>
                            <option value="White Noise Generator" className="bg-slate-900">White Noise Generator</option>
                            <option value="Deep Focus Lo-Fi" className="bg-slate-900">Deep Focus Lo-Fi</option>
                            <option value="Silent Lab Mode" className="bg-slate-900">Silent Lab Mode</option>
                        </select>
                        <button onClick={() => setIsMuted(!isMuted)} className="text-slate-400 hover:text-white">
                            {isMuted ? <VolumeX className="w-4 h-4 text-red-400" /> : <Volume2 className="w-4 h-4 text-cyan-400" />}
                        </button>
                    </div>
                </div>
            </div>

            {/* Pomodoro Timer Box */}
            <div className="p-6 md:p-8 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-2xl flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div className="flex items-center gap-6">
                    <div className="w-20 h-20 rounded-2xl bg-gradient-to-tr from-cyan-500/20 to-purple-600/20 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shadow-lg">
                        <Clock className="w-9 h-9" />
                    </div>
                    <div>
                        <div className="text-4xl md:text-5xl font-black text-white font-mono tracking-tight">
                            {formatTime(secondsLeft)} <span className="text-sm font-sans uppercase tracking-widest text-cyan-400 font-bold">REMAINING</span>
                        </div>
                        <div className="text-xs text-slate-400 mt-1">
                            Sprint 2 of 4 (10m Break in complete) • <span className="text-slate-300 font-semibold">Pomodoro Sprint 2 of 4: Deep Work Block</span>
                        </div>
                    </div>
                </div>

                <div className="flex flex-wrap items-center gap-3">
                    <button
                        onClick={() => setIsRunning(!isRunning)}
                        className={`px-6 py-2.5 rounded-xl font-bold text-xs shadow-lg transition-all flex items-center gap-2 ${isRunning ? 'bg-amber-600 hover:bg-amber-500 text-white' : 'bg-purple-600 hover:bg-purple-500 text-white shadow-purple-600/30'}`}
                    >
                        {isRunning ? <Pause className="w-3.5 h-3.5 fill-current" /> : <Play className="w-3.5 h-3.5 fill-current" />}
                        <span>{isRunning ? 'Pause Sprint' : 'Start Sprint'}</span>
                    </button>

                    <button
                        onClick={() => setSecondsLeft(600)}
                        className="px-4 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 font-bold text-xs border border-slate-700 transition-colors"
                    >
                        Break
                    </button>

                    <button
                        onClick={handleEndSession}
                        className="px-4 py-2.5 rounded-xl bg-red-950/40 hover:bg-red-900/50 text-red-300 font-bold text-xs border border-red-500/30 transition-colors flex items-center gap-1.5"
                    >
                        <Square className="w-3 h-3 fill-current" />
                        <span>End Session</span>
                    </button>
                </div>
            </div>

            {sessionLogged && (
                <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-bold flex items-center justify-between animate-fadeIn">
                    <div className="flex items-center gap-2">
                        <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                        <span>Focus session successfully logged to your learning history!</span>
                    </div>
                    <button onClick={() => navigate('/')} className="underline text-emerald-300 font-bold hover:text-white transition-colors">
                        Return to Dashboard →
                    </button>
                </div>
            )}

            {/* Objective Banner */}
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                    <span className="text-[10px] font-black uppercase text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20">
                        COLLECTIVE SESSION OBJECTIVE
                    </span>
                    <span className="text-white font-semibold">
                        Review Raft consensus invariants & solve 2 dynamic programming problems
                    </span>
                </div>
                <span className="text-slate-400 hidden sm:inline">Target: 2 Problems Completed</span>
            </div>

            {/* Middle Grid: Participants + Notes (Left 8 Cols) and TA Chat (Right 4 Cols) */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                <div className="lg:col-span-8 space-y-6">
                    {/* Study Room Participants (4 in Silent Deep Focus) */}
                    <div className="p-6 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg space-y-4">
                        <div className="flex items-center justify-between">
                            <h2 className="text-sm font-black uppercase tracking-wider text-white flex items-center gap-2">
                                <Users className="w-4 h-4 text-cyan-400" />
                                Study Room Participants (4 in Silent Deep Focus)
                            </h2>
                        </div>

                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center gap-3">
                                <div className="w-8 h-8 rounded-full bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center font-bold text-xs text-cyan-300">
                                    ML
                                </div>
                                <div className="min-w-0 flex-1">
                                    <div className="text-xs font-bold text-white truncate">Maya Lin</div>
                                    <div className="text-[10px] text-emerald-400 flex items-center gap-1">
                                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                                        In Deep Work
                                    </div>
                                </div>
                            </div>

                            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center gap-3">
                                <div className="w-8 h-8 rounded-full bg-purple-500/20 border border-purple-500/40 flex items-center justify-center font-bold text-xs text-purple-300">
                                    AC
                                </div>
                                <div className="min-w-0 flex-1">
                                    <div className="text-xs font-bold text-white truncate">Alex Chen</div>
                                    <div className="text-[10px] text-cyan-400">Pomodoro 32m</div>
                                </div>
                            </div>

                            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center gap-3">
                                <div className="w-8 h-8 rounded-full bg-indigo-500/20 border border-indigo-500/40 flex items-center justify-center font-bold text-xs text-indigo-300">
                                    SK
                                </div>
                                <div className="min-w-0 flex-1">
                                    <div className="text-xs font-bold text-white truncate">Sara Kim</div>
                                    <div className="text-[10px] text-purple-400">Pomodoro 28m</div>
                                </div>
                            </div>

                            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center gap-3">
                                <div className="w-8 h-8 rounded-full bg-amber-500/20 border border-amber-500/40 flex items-center justify-center font-bold text-xs text-amber-300">
                                    DP
                                </div>
                                <div className="min-w-0 flex-1">
                                    <div className="text-xs font-bold text-white truncate">David Park</div>
                                    <div className="text-[10px] text-amber-400">Timer Sync</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Shared Notes • Raft & DP Synthesis */}
                    <div className="p-6 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg space-y-3">
                        <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
                            <h2 className="text-sm font-black uppercase tracking-wider text-white flex items-center gap-2">
                                <BookOpen className="w-4 h-4 text-purple-400" />
                                Shared Notes • Raft & DP Synthesis
                            </h2>
                            <span className="text-[10px] text-slate-400">Auto-saved 2s ago</span>
                        </div>

                        <div className="p-4 rounded-xl bg-[#070B12] border border-slate-800 text-xs font-mono text-slate-300 leading-relaxed space-y-3">
                            <div>
                                <span className="text-cyan-400 font-bold font-sans">### 1. Raft Election Safety & Log Matching Invariant</span>
                                <p className="text-slate-400 mt-1">
                                    - Election Safety: At most one leader can be elected in a given term.<br/>
                                    - Log Matching Property: If two logs contain an entry with the same index and term, then the logs are identical in all entries up through the given index.
                                </p>
                            </div>

                            <div>
                                <span className="text-purple-400 font-bold font-sans">### 2. Levenshtein Distance (DP #42 Optimization)</span>
                                <p className="text-slate-400 mt-1">
                                    - State Definition: dp[i][j] = minimum edits to convert s1[0..i] to s2[0..j].<br/>
                                    - Space Optimization: Only current row and previous row are needed. Allocating dp[2][len] reduces memory to O(min(M, N)).
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Right Column: Room TA & Silent Accountability (4 Cols) */}
                <div className="lg:col-span-4 space-y-6">
                    {/* Room TA - Synapse AI */}
                    <div className="p-6 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg space-y-4">
                        <div className="flex items-center justify-between">
                            <h2 className="text-sm font-black uppercase tracking-wider text-white flex items-center gap-2">
                                <Sparkles className="w-4 h-4 text-cyan-400" />
                                Room TA — Synapse AI
                            </h2>
                            <span className="text-[10px] text-slate-400">MIT 6.824</span>
                        </div>
                        <p className="text-[11px] text-slate-400">
                            Ask questions silently without disrupting peer focus flow.
                        </p>

                        <div className="space-y-2.5 max-h-56 overflow-y-auto pr-1">
                            {taMessages.map((msg, idx) => (
                                <div key={idx} className={`p-3 rounded-xl text-xs ${msg.sender === 'You' ? 'bg-purple-950/30 border border-purple-500/30 text-purple-200' : 'bg-slate-900/70 border border-slate-800 text-slate-300'}`}>
                                    <div className="flex items-center justify-between text-[10px] font-bold text-slate-400 mb-1">
                                        <span>{msg.sender}</span>
                                        <span>{msg.time}</span>
                                    </div>
                                    <p className="leading-relaxed">{msg.text}</p>
                                </div>
                            ))}
                        </div>

                        <div className="relative pt-1">
                            <input
                                type="text"
                                value={taInput}
                                onChange={(e) => setTaInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleSendTaMessage()}
                                placeholder="Ask TA privately..."
                                className="w-full pl-3 pr-10 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                            />
                            <button
                                onClick={handleSendTaMessage}
                                className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 text-cyan-400 hover:text-white"
                            >
                                <Send className="w-3.5 h-3.5" />
                            </button>
                        </div>
                    </div>

                    {/* Silent Accountability */}
                    <div className="p-6 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg space-y-4">
                        <div className="flex items-center justify-between">
                            <h2 className="text-sm font-black uppercase tracking-wider text-white">
                                Silent Accountability
                            </h2>
                        </div>

                        <div className="space-y-2 text-xs text-slate-400">
                            <p>• Alex Chen finished 25-min Pomodoro session</p>
                            <p>• Sara Kim shared MIT 6.824 Lab 2 notes</p>
                        </div>

                        <div className="pt-2 flex items-center justify-between gap-2">
                            <button
                                onClick={() => setCheers(c => ({ ...c, plusOne: c.plusOne + 1 }))}
                                className="flex-1 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs font-bold text-cyan-300 transition-colors"
                            >
                                +1 ({cheers.plusOne})
                            </button>
                            <button
                                onClick={() => setCheers(c => ({ ...c, focus: c.focus + 1 }))}
                                className="flex-1 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs font-bold text-purple-300 transition-colors"
                            >
                                Focus ({cheers.focus})
                            </button>
                            <button
                                onClick={() => setCheers(c => ({ ...c, coffee: c.coffee + 1 }))}
                                className="flex-1 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs font-bold text-amber-300 transition-colors"
                            >
                                Coffee ({cheers.coffee})
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default VirtualStudyRoom;
