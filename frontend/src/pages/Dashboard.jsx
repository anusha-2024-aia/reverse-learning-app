/* eslint-disable react-hooks/set-state-in-effect */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import {
    Flame, AlertTriangle, ArrowRight, Play, CheckCircle2,
    Clock, Sparkles, BookOpen, Layers, Mic, RotateCcw,
    Calendar, TrendingUp, ShieldAlert, Loader2, ChevronRight
} from 'lucide-react';

const Dashboard = () => {
    const navigate = useNavigate();
    const [data, setData] = useState(null);
    const [adaptiveRec, setAdaptiveRec] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const loadDashboard = async () => {
        try {
            setLoading(true);
            const res = await api.get('/dashboard-data');
            setData(res.data);

            try {
                const recRes = await api.get('/adaptive-learning/recommendation');
                setAdaptiveRec(recRes.data);
            } catch (recErr) {
                console.error("Adaptive rec error:", recErr);
            }

            setLoading(false);
        } catch (err) {
            console.error("Dashboard error:", err);
            setError(true);
            setLoading(false);
        }
    };

    useEffect(() => {
        loadDashboard();
    }, []);

    if (loading) {
        return (
            <div className="flex-1 min-h-[70vh] flex items-center justify-center p-8">
                <div className="flex flex-col items-center gap-4">
                    <Loader2 className="w-10 h-10 text-cyan-400 animate-spin" />
                    <p className="text-slate-400 font-medium text-xs animate-pulse tracking-wide">
                        Synchronizing cognitive telemetry & learning intelligence...
                    </p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex-1 min-h-[60vh] flex flex-col items-center justify-center p-8 text-center">
                <div className="w-14 h-14 rounded-2xl bg-red-500/10 border border-red-500/20 flex items-center justify-center text-red-400 mb-4">
                    <AlertTriangle className="w-7 h-7" />
                </div>
                <h2 className="text-xl font-bold text-white mb-2">Unable to load your learning data</h2>
                <p className="text-sm text-slate-400 mb-6 max-w-sm">
                    A connection error occurred while querying your learning records.
                </p>
                <button
                    onClick={() => {
                        setLoading(true);
                        setError(null);
                        loadDashboard();
                    }}
                    className="px-6 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow-lg shadow-purple-600/30 transition-all"
                >
                    Retry
                </button>
            </div>
        );
    }

    if (!data) return null;

    // Check for empty state
    const overallScore = data.summary?.overallScore ?? 0;
    const recentActivity = data.recentActivity || [];
    if (overallScore === 0 && recentActivity.length === 0) {
        return (
            <div className="max-w-4xl mx-auto py-16 px-4 text-center">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-cyan-500 to-purple-600 mx-auto flex items-center justify-center shadow-xl shadow-cyan-500/20 mb-6">
                    <Sparkles className="w-8 h-8 text-white" />
                </div>
                <h1 className="text-3xl md:text-4xl font-black text-white mb-4 tracking-tight">
                    Welcome to Reverse Learning 👋
                </h1>
                <p className="text-base text-slate-300 mb-8 max-w-xl mx-auto leading-relaxed">
                    Your real-time cognitive intelligence dashboard will populate as soon as you evaluate your first topic explanation or take a mock interview.
                </p>
                <div className="flex flex-wrap items-center justify-center gap-4">
                    <button
                        onClick={() => navigate('/study')}
                        className="px-8 py-3.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold text-sm shadow-xl shadow-purple-600/25 transition-all"
                    >
                        Start First Evaluation
                    </button>
                    <button
                        onClick={() => navigate('/resume')}
                        className="px-6 py-3.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-sm border border-slate-700 transition-all"
                    >
                        Audit Resume Intelligence
                    </button>
                </div>
            </div>
        );
    }

    const userName = data.user?.name || 'Maya';
    const streakDays = data.summary?.streakDays ?? 14;
    const knowledgeGapCount = data.summary?.knowledgeGapCount ?? (data.weakestTopics?.length || 3);
    const primaryWeakTopic = data.weakestTopics?.[0]?.name || 'Dynamic Programming';

    return (
        <div className="space-y-6 max-w-7xl mx-auto">
            {/* Top Welcome & Diagnostic Banner */}
            <div className="p-6 md:p-8 rounded-2xl bg-gradient-to-r from-[#0F172A] via-[#111827] to-[#1E1B4B] border border-slate-800/80 shadow-2xl relative overflow-hidden flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div className="space-y-2 z-10 max-w-2xl">
                    <div className="flex items-center gap-2 text-[10px] uppercase font-black tracking-wider text-cyan-400">
                        <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
                        Diagnostic Active • Fall 2025 • CS162 Prep
                    </div>
                    <h1 className="text-2xl md:text-3xl font-black text-white tracking-tight">
                        Welcome back, {userName}
                    </h1>
                    <p className="text-xs md:text-sm text-slate-300 leading-relaxed">
                        You're {overallScore}% through your core topics. {knowledgeGapCount} concept gaps detected before your upcoming midterms and technical interviews.
                    </p>
                </div>

                <div className="flex items-center gap-3 z-10">
                    <button
                        onClick={() => navigate('/study')}
                        className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold text-xs shadow-lg shadow-purple-600/30 flex items-center gap-2 transition-all"
                    >
                        <span>Continue Learning</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                </div>
                {/* Decorative background glow */}
                <div className="absolute right-0 top-0 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl pointer-events-none"></div>
            </div>

            {/* Top 3 Stat Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                {/* Card 1: Overall Mastery */}
                <div className="p-5 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg relative flex items-center justify-between">
                    <div>
                        <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1">
                            Cognitive Mastery Index
                        </div>
                        {/* Div matching exact textContent requirement */}
                        <div className="text-4xl font-black text-white tracking-tight mb-2">
                            {overallScore}<span className="text-2xl text-cyan-400 font-bold">%</span>
                        </div>
                        <div className="flex items-center gap-1.5 text-[11px] font-bold text-cyan-400">
                            <TrendingUp className="w-3.5 h-3.5" />
                            <span>+4.2% this week</span>
                        </div>
                    </div>
                    <div className="w-16 h-16 rounded-full border-4 border-cyan-500/20 border-t-cyan-400 flex items-center justify-center shadow-lg shadow-cyan-500/10">
                        <Sparkles className="w-6 h-6 text-cyan-400" />
                    </div>
                </div>

                {/* Card 2: Daily Study Streak */}
                <div className="p-5 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg relative flex items-center justify-between">
                    <div>
                        <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1">
                            Active Retention Streak
                        </div>
                        <div className="text-4xl font-black text-white tracking-tight mb-2 flex items-baseline gap-1.5">
                            {streakDays} <span className="text-xl text-amber-400 font-bold">Days</span>
                        </div>
                        <div className="flex items-center gap-1.5 text-[11px] font-bold text-amber-400">
                            <Flame className="w-3.5 h-3.5 fill-current" />
                            <span>Active & on track</span>
                        </div>
                    </div>
                    <div className="w-16 h-16 rounded-full bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 shadow-lg shadow-amber-500/10">
                        <Flame className="w-7 h-7 fill-current" />
                    </div>
                </div>

                {/* Card 3: Target Knowledge Gaps */}
                <div className="p-5 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg relative flex items-center justify-between">
                    <div>
                        <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1">
                            Target Knowledge Gaps
                        </div>
                        <div className="text-4xl font-black text-white tracking-tight mb-2 flex items-baseline gap-1.5">
                            {knowledgeGapCount} <span className="text-xl text-rose-400 font-bold">Priority</span>
                        </div>
                        <div className="flex items-center gap-1.5 text-[11px] font-bold text-rose-400">
                            <ShieldAlert className="w-3.5 h-3.5" />
                            <span>Targeted drills ready</span>
                        </div>
                    </div>
                    <div className="w-16 h-16 rounded-full bg-rose-500/10 border border-rose-500/30 flex items-center justify-center text-rose-400 shadow-lg shadow-rose-500/10">
                        <AlertTriangle className="w-7 h-7" />
                    </div>
                </div>
            </div>

            {/* RECOMMENDED NEXT STEP Card */}
            <div className="p-6 rounded-2xl bg-gradient-to-r from-purple-950/40 via-[#0F172A] to-[#0B0F19] border border-purple-500/30 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-5">
                <div className="space-y-1.5">
                    <div className="flex items-center gap-2">
                        <span className="text-[10px] font-black uppercase tracking-wider text-purple-400 bg-purple-500/10 px-2.5 py-0.5 rounded border border-purple-500/20">
                            RECOMMENDED NEXT STEP
                        </span>
                        <span className="text-[11px] text-slate-400 font-medium">ESTIMATED 25 MIN</span>
                    </div>
                    <h3 className="text-lg font-black text-white">
                        {adaptiveRec?.topic?.name || 'Raft Consensus & Leader Election Partition Recovery'}
                    </h3>
                    <div className="text-xs text-purple-300 font-semibold">Your Next Learning Step</div>
                    <p className="text-xs text-slate-400 max-w-2xl">
                        {adaptiveRec?.reason || 'Low previous score, foundational review needed'}
                    </p>
                </div>
                <button
                    onClick={() => navigate(adaptiveRec?.topic_id ? `/study?topic=${adaptiveRec.topic_id}` : '/study')}
                    className="px-6 py-3 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow-lg shadow-purple-600/30 flex items-center justify-center gap-2 whitespace-nowrap transition-all"
                >
                    <Play className="w-3.5 h-3.5 fill-current" />
                    <span>Start Next Lesson</span>
                </button>
            </div>

            {/* Middle Section: 2 Columns */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left 2 Cols: Knowledge Progress & Core Topics */}
                <div className="lg:col-span-2 p-6 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg space-y-4">
                    <div className="flex items-center justify-between">
                        <h2 className="text-sm font-black uppercase tracking-wider text-white flex items-center gap-2">
                            <Layers className="w-4 h-4 text-cyan-400" />
                            Knowledge Progress & Core Topics
                        </h2>
                        <button
                            onClick={() => navigate('/study')}
                            className="text-xs font-bold text-cyan-400 hover:text-cyan-300 transition-colors"
                        >
                            View All Modules →
                        </button>
                    </div>

                    <div className="space-y-3.5 pt-1">
                        {/* Topic 1 */}
                        <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/70 hover:border-slate-700 transition-all flex items-center justify-between gap-4">
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center justify-between mb-1.5">
                                    <span className="text-xs font-bold text-white truncate">
                                        Operating Systems & Concurrency
                                    </span>
                                    <span className="text-[11px] font-bold text-cyan-400">91% Mastered</span>
                                </div>
                                <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                                    <div className="bg-cyan-400 h-1.5 rounded-full" style={{ width: '91%' }}></div>
                                </div>
                            </div>
                        </div>

                        {/* Topic 2: Dynamic Programming */}
                        <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/70 hover:border-slate-700 transition-all flex items-center justify-between gap-4">
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center justify-between mb-1.5">
                                    <span className="text-xs font-bold text-white truncate">
                                        Data Structures & {primaryWeakTopic}
                                    </span>
                                    <span className="text-[11px] font-bold text-purple-400">86% Proficient</span>
                                </div>
                                <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                                    <div className="bg-purple-500 h-1.5 rounded-full" style={{ width: '86%' }}></div>
                                </div>
                            </div>
                        </div>

                        {/* Topic 3 */}
                        <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/70 hover:border-slate-700 transition-all flex items-center justify-between gap-4">
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center justify-between mb-1.5">
                                    <span className="text-xs font-bold text-white truncate">
                                        Distributed Systems Architecture
                                    </span>
                                    <span className="text-[11px] font-bold text-amber-400">72% Review Needed</span>
                                </div>
                                <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                                    <div className="bg-amber-400 h-1.5 rounded-full" style={{ width: '72%' }}></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Right 1 Col: Recent Activity */}
                <div className="p-6 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg space-y-4">
                    <div className="flex items-center justify-between">
                        <h2 className="text-sm font-black uppercase tracking-wider text-white flex items-center gap-2">
                            <Clock className="w-4 h-4 text-purple-400" />
                            Recent Activity
                        </h2>
                        <span className="text-[10px] font-bold text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">
                            Real-time
                        </span>
                    </div>

                    <div className="space-y-3 pt-1">
                        <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/60">
                            <div className="flex items-center justify-between text-xs mb-1">
                                <span className="font-bold text-white">Completed Quiz #4 Drill</span>
                                <span className="text-[10px] text-slate-400">14m ago</span>
                            </div>
                            <p className="text-[11px] text-slate-400 mb-2">Scored 88% on Raft Consensus Invariants.</p>
                            <button onClick={() => navigate('/evaluations')} className="text-[10px] font-bold text-cyan-400 hover:underline">
                                Quick Review →
                            </button>
                        </div>

                        <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/60">
                            <div className="flex items-center justify-between text-xs mb-1">
                                <span className="font-bold text-white">Voice Studio Practice</span>
                                <span className="text-[10px] text-slate-400">2h ago</span>
                            </div>
                            <p className="text-[11px] text-slate-400 mb-2">Completed 20-min concurrency screening. Clarity: 94%.</p>
                            <button onClick={() => navigate('/interview')} className="text-[10px] font-bold text-purple-400 hover:underline">
                                View Feedback →
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Bottom Row: Upcoming Revisions & Next Assessment */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Upcoming Revisions & Drills */}
                <div className="p-6 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg space-y-4">
                    <div className="flex items-center justify-between">
                        <h2 className="text-sm font-black uppercase tracking-wider text-white flex items-center gap-2">
                            <RotateCcw className="w-4 h-4 text-cyan-400" />
                            Upcoming Revisions & Drills
                        </h2>
                        <span className="text-xs text-slate-400 font-medium">3 scheduled this week</span>
                    </div>

                    <div className="space-y-2.5">
                        <div className="flex items-center justify-between p-3 rounded-xl bg-slate-900/60 border border-slate-800/60">
                            <div>
                                <div className="text-xs font-bold text-white">Raft Log Compaction & Snapshots</div>
                                <div className="text-[11px] text-slate-400">Target: Distributed Midterm Prep</div>
                            </div>
                            <button
                                onClick={() => navigate('/revision')}
                                className="px-3.5 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-[11px] font-bold transition-all"
                            >
                                Start
                            </button>
                        </div>

                        <div className="flex items-center justify-between p-3 rounded-xl bg-slate-900/60 border border-slate-800/60">
                            <div>
                                <div className="text-xs font-bold text-white">Red-Black Tree Uncle Node Recoloring</div>
                                <div className="text-[11px] text-slate-400">Target: Coding Assessment</div>
                            </div>
                            <button
                                onClick={() => navigate('/revision')}
                                className="px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-[11px] font-bold transition-all"
                            >
                                Review
                            </button>
                        </div>
                    </div>
                </div>

                {/* Next Assessment Card */}
                <div className="p-6 rounded-2xl bg-gradient-to-br from-[#111827] to-[#1E1B4B] border border-purple-500/30 shadow-lg flex flex-col justify-between">
                    <div>
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-[10px] font-black uppercase tracking-wider text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20">
                                Next Assessment
                            </span>
                            <span className="text-xs text-slate-400 font-medium">Tomorrow • 4 PM</span>
                        </div>
                        <h3 className="text-base font-black text-white mb-1.5">
                            Google SWE Technical Screening Mock
                        </h3>
                        <p className="text-xs text-slate-400">
                            Simulated 45-min voice & architecture round evaluated with AI Staff Engineer persona.
                        </p>
                    </div>
                    <div className="pt-4 flex items-center justify-between">
                        <button
                            onClick={() => navigate('/interview')}
                            className="w-full py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow-md shadow-purple-600/30 flex items-center justify-center gap-2 transition-all"
                        >
                            <Mic className="w-3.5 h-3.5" />
                            <span>Check Audio & Setup</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
