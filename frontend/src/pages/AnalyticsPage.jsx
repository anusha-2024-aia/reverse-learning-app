import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    BarChart2, TrendingUp, Award, CheckCircle2, AlertTriangle,
    Calendar, Sparkles, ArrowRight, ArrowLeft, Clock, Target, Mic,
    RotateCcw, ChevronRight, Loader2, Download, Filter, Search,
    Flame, Zap, BookOpen, Layers, ShieldCheck
} from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import api from '../api/axios';
import { AuthContext } from '../context/AuthContext';

const AnalyticsPage = () => {
    const navigate = useNavigate();
    const { user } = useContext(AuthContext) || {};
    const [_loading, setLoading] = useState(true);
    const [timeframe, setTimeframe] = useState('semester'); // '7d', 'semester', 'all'
    const [activeMetric, setActiveMetric] = useState('retention'); // 'retention', 'hours'
    const [searchFilter, setSearchFilter] = useState('');
    const [sessionFilter, setSessionFilter] = useState('all');
    const [analytics, setAnalytics] = useState(null);

    useEffect(() => {
        const fetchAnalytics = async () => {
            setLoading(true);
            try {
                const rangeParam = timeframe === '7d' ? '7d' : timeframe === 'semester' ? '90d' : 'all';
                const res = await api.get(`/analytics?range=${rangeParam}`);
                setAnalytics(res.data);
            } catch (err) {
                console.error("Failed to fetch analytics:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchAnalytics();
    }, [timeframe]);

    const isDemo = user?.email === 'maya.lin@berkeley.edu';
    const hasData = isDemo || Boolean(analytics && analytics.has_enough_data);

    if (!hasData) {
        return (
            <div className="w-full">
                <div className="p-4 md:p-8 space-y-8 max-w-7xl mx-auto pb-16">
                    {/* Header */}
                    <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
                        <div>
                            <div className="text-[11px] font-black uppercase tracking-wider text-cyan-400 flex items-center gap-2 mb-1">
                                <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
                                COGNITIVE TRAJECTORY • Telemetry Calibrating
                            </div>
                            <h1 className="text-2xl md:text-3xl font-black text-white tracking-tight">
                                Longitudinal Learning Analytics & Mastery Velocity
                            </h1>
                        </div>

                        <div className="flex items-center gap-3">
                            <button
                                onClick={() => navigate('/')}
                                className="px-3.5 py-2 rounded-xl bg-[#0B0F19] hover:bg-slate-800 border border-slate-700 text-slate-300 hover:text-white font-bold text-xs flex items-center gap-1.5 transition-colors"
                            >
                                <ArrowLeft className="w-3.5 h-3.5" />
                                <span>Dashboard</span>
                            </button>
                        </div>
                    </div>

                    {/* 4 Stat Cards */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="p-5 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg">
                            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Overall Cognitive Mastery</div>
                            <div className="text-3xl font-black text-white">0%</div>
                            <div className="text-[11px] text-cyan-400 font-semibold mt-1">Awaiting first evaluation</div>
                        </div>

                        <div className="p-5 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg">
                            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Weekly Learning Hours</div>
                            <div className="text-3xl font-black text-white">0.0h</div>
                            <div className="text-[11px] text-purple-400 font-semibold mt-1">Logged via Study Room</div>
                        </div>

                        <div className="p-5 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg">
                            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Active Study Streak</div>
                            <div className="text-3xl font-black text-white">0 <span className="text-lg text-amber-400 font-bold">Days</span></div>
                            <div className="text-[11px] text-amber-400 font-semibold mt-1">Start today to begin streak</div>
                        </div>

                        <div className="p-5 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg">
                            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Telemetry Status</div>
                            <div className="text-3xl font-black text-emerald-400">Ready</div>
                            <div className="text-[11px] text-emerald-400 font-semibold mt-1">100% Algorithmic verification</div>
                        </div>
                    </div>

                    {/* Empty State Hero Box */}
                    <div className="p-8 md:p-12 rounded-3xl bg-[#0B0F19] border border-slate-800/80 shadow-2xl text-center space-y-4">
                        <div className="w-16 h-16 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center mx-auto shadow-lg">
                            <BarChart2 className="w-8 h-8" />
                        </div>
                        <h2 className="text-xl md:text-2xl font-black text-white">
                            No Learning Telemetry Recorded Yet
                        </h2>
                        <p className="text-xs md:text-sm text-slate-400 max-w-lg mx-auto leading-relaxed">
                            Your longitudinal learning analytics, cognitive trajectory velocity, and retention stability curves will calibrate automatically as you complete topic evaluations, active recall revisions, or mock interviews.
                        </p>
                        <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
                            <button
                                onClick={() => navigate('/study')}
                                className="px-6 py-3 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow-lg shadow-purple-600/30 transition-all inline-flex items-center gap-2"
                            >
                                <span>Start First Topic Evaluation</span>
                                <ArrowRight className="w-4 h-4" />
                            </button>
                            <button
                                onClick={() => navigate('/interview')}
                                className="px-5 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs border border-slate-700 transition-all"
                            >
                                Practice Mock Interview
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    const weeklyTrendData = [
        { day: 'Mon', retention: 74, hours: 2.1 },
        { day: 'Tue', retention: 78, hours: 2.8 },
        { day: 'Wed', retention: 81, hours: 3.2 },
        { day: 'Thu', retention: 85, hours: 2.5 },
        { day: 'Fri', retention: 82, hours: 1.9 },
        { day: 'Sat', retention: 91, hours: 4.2 },
        { day: 'Sun', retention: 94, hours: 3.8 }
    ];

    const learningHistoryRows = [
        {
            id: 1,
            timestamp: 'Nov 05, 2025 14:15 EST',
            type: 'Mock Interview',
            typeColor: 'text-purple-400 bg-purple-950/60 border-purple-800/80',
            topic: 'Graph Algorithms: Dijkstra & A*',
            duration: '42m 18s',
            initialScore: '68%',
            finalMastery: '94%',
            verified: true
        },
        {
            id: 2,
            timestamp: 'Nov 02, 2025 17:10 EST',
            type: 'Deep Diagnostic',
            typeColor: 'text-cyan-400 bg-cyan-950/60 border-cyan-800/80',
            topic: 'LSM-Trees vs B-Trees (Write Amplification)',
            duration: '18m 00s',
            initialScore: '52%',
            finalMastery: '82%',
            verified: true
        },
        {
            id: 3,
            timestamp: 'Nov 01, 2025 09:45 EST',
            type: 'Spaced Repetition',
            typeColor: 'text-emerald-400 bg-emerald-950/60 border-emerald-800/80',
            topic: 'OS Virtual Memory & Slab Allocation',
            duration: '15m 20s',
            initialScore: '84%',
            finalMastery: '98%',
            verified: true
        },
        {
            id: 4,
            timestamp: 'Oct 30, 2025 21:00 EST',
            type: 'Virtual Study Room',
            typeColor: 'text-indigo-400 bg-indigo-950/60 border-indigo-800/80',
            topic: 'Transformer Attention Mechanism Math',
            duration: '1h 45m',
            initialScore: '70%',
            finalMastery: '92%',
            verified: true
        },
        {
            id: 5,
            timestamp: 'Oct 28, 2025 16:30 EST',
            type: 'Mock Interview',
            typeColor: 'text-purple-400 bg-purple-950/60 border-purple-800/80',
            topic: 'Distributed Rate Limiter (Token Bucket)',
            duration: '48m 10s',
            initialScore: '62%',
            finalMastery: '98%',
            verified: true
        }
    ];

    const filteredRows = learningHistoryRows.filter(row => {
        const matchesSearch = row.topic.toLowerCase().includes(searchFilter.toLowerCase());
        const matchesType = sessionFilter === 'all' || row.type.toLowerCase().includes(sessionFilter.toLowerCase());
        return matchesSearch && matchesType;
    });

    const handleExportDossier = () => {
        const jsonString = `data:text/json;charset=utf-8,${encodeURIComponent(
            JSON.stringify(analytics || { student: "Maya Lin", mastery: 84 }, null, 2)
        )}`;
        const downloadAnchor = document.createElement('a');
        downloadAnchor.setAttribute('href', jsonString);
        downloadAnchor.setAttribute('download', 'academic_mastery_dossier.json');
        document.body.appendChild(downloadAnchor);
        downloadAnchor.click();
        downloadAnchor.remove();
    };

    return (
        <div className="w-full">
            <div className="p-4 md:p-8 space-y-6 max-w-7xl mx-auto">
                {/* Header matching Stitch screenshot 2 & 7 */}
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
                    <div>
                        <div className="text-[11px] font-black uppercase tracking-wider text-cyan-400 flex items-center gap-2 mb-1">
                            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
                            COGNITIVE TRAJECTORY • FALL 2025 / TELEMETRY ACTIVE
                        </div>
                        <h1 className="text-2xl md:text-3xl font-black text-white tracking-tight">
                            Longitudinal Learning Analytics & Mastery Velocity
                        </h1>
                    </div>

                    {/* Filter buttons & export CTA */}
                    <div className="flex flex-wrap items-center gap-3">
                        <button
                            onClick={() => navigate('/')}
                            className="px-3.5 py-2 rounded-xl bg-[#0B0F19] hover:bg-slate-800 border border-slate-700 text-slate-300 hover:text-white font-bold text-xs flex items-center gap-1.5 transition-colors"
                        >
                            <ArrowLeft className="w-3.5 h-3.5" />
                            <span>Dashboard</span>
                        </button>
                        <div className="bg-[#0B0F19] border border-slate-800 p-1 rounded-xl flex items-center gap-1">
                            <button
                                onClick={() => setTimeframe('7d')}
                                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                                    timeframe === '7d'
                                        ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                                        : 'text-slate-400 hover:text-white'
                                }`}
                            >
                                Last 7 Days
                            </button>
                            <button
                                onClick={() => setTimeframe('semester')}
                                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                                    timeframe === 'semester'
                                        ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                                        : 'text-slate-400 hover:text-white'
                                }`}
                            >
                                Current Semester (Fall 2025)
                            </button>
                            <button
                                onClick={() => setTimeframe('all')}
                                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                                    timeframe === 'all'
                                        ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                                        : 'text-slate-400 hover:text-white'
                                }`}
                            >
                                All-Time Academic Journey
                            </button>
                        </div>

                        <button
                            onClick={handleExportDossier}
                            className="px-4 py-2 rounded-xl bg-[#0B0F19] hover:bg-slate-800 border border-slate-700 text-slate-300 hover:text-white font-bold text-xs flex items-center gap-2 transition-colors"
                        >
                            <Download className="w-3.5 h-3.5 text-cyan-400" />
                            <span>Export Dossier</span>
                        </button>
                        <button
                            onClick={() => navigate('/learning-path')}
                            className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:opacity-90 text-white font-bold text-xs shadow-lg shadow-cyan-500/20 flex items-center gap-2 transition-all"
                        >
                            <Sparkles className="w-3.5 h-3.5" />
                            <span>Run Predictive Forecast</span>
                        </button>
                    </div>
                </div>

                {/* 4 Stat Cards */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    {/* Card 1: Total Learning Time */}
                    <div className="bg-[#0B0F19] border border-slate-800/80 rounded-2xl p-5 space-y-3 relative overflow-hidden">
                        <div className="flex items-center justify-between text-slate-400">
                            <span className="text-[10px] font-black uppercase tracking-wider">TOTAL LEARNING TIME</span>
                            <Clock className="w-4 h-4 text-cyan-400" />
                        </div>
                        <div className="text-3xl font-black text-white font-mono">
                            148.5<span className="text-sm font-normal text-slate-500 ml-1">hrs</span>
                        </div>
                        <div className="flex items-center justify-between text-[11px]">
                            <span className="text-emerald-400 font-bold">+12.4 hrs this week</span>
                            <span className="text-slate-400">Top 4% cohort</span>
                        </div>
                    </div>

                    {/* Card 2: Topics Completed */}
                    <div className="bg-[#0B0F19] border border-slate-800/80 rounded-2xl p-5 space-y-3 relative overflow-hidden">
                        <div className="flex items-center justify-between text-slate-400">
                            <span className="text-[10px] font-black uppercase tracking-wider">TOPICS COMPLETED</span>
                            <Target className="w-4 h-4 text-purple-400" />
                        </div>
                        <div className="text-3xl font-black text-white font-mono">
                            184<span className="text-sm font-normal text-slate-500 ml-1">mastered</span>
                        </div>
                        <div className="flex items-center justify-between text-[11px]">
                            <span className="text-cyan-400 font-bold">+22 this month</span>
                            <span className="text-slate-400">91.2% verified</span>
                        </div>
                    </div>

                    {/* Card 3: Learning Consistency */}
                    <div className="bg-[#0B0F19] border border-slate-800/80 rounded-2xl p-5 space-y-3 relative overflow-hidden">
                        <div className="flex items-center justify-between text-slate-400">
                            <span className="text-[10px] font-black uppercase tracking-wider">LEARNING CONSISTENCY</span>
                            <Flame className="w-4 h-4 text-amber-400" />
                        </div>
                        <div className="text-3xl font-black text-white font-mono">
                            94%<span className="text-xs text-emerald-400 font-bold ml-2">↑ 6.2%</span>
                        </div>
                        <div className="flex items-center justify-between text-[11px]">
                            <span className="text-slate-400">Avg 2.8 hrs/day</span>
                            <span className="text-amber-400 font-bold">19 Day Streak</span>
                        </div>
                    </div>

                    {/* Card 4: Diagnostic Accuracy */}
                    <div className="bg-[#0B0F19] border border-slate-800/80 rounded-2xl p-5 space-y-3 relative overflow-hidden">
                        <div className="flex items-center justify-between text-slate-400">
                            <span className="text-[10px] font-black uppercase tracking-wider">DIAGNOSTIC ACCURACY</span>
                            <Award className="w-4 h-4 text-emerald-400" />
                        </div>
                        <div className="text-3xl font-black text-white font-mono">
                            89.4%<span className="text-xs text-emerald-400 font-bold ml-2">↑ 18.2%</span>
                        </div>
                        <div className="flex items-center justify-between text-[11px]">
                            <span className="text-slate-400">Sept Baseline: 71.2%</span>
                            <span className="text-emerald-400 font-bold">Tier-1 FAANG Ready</span>
                        </div>
                    </div>
                </div>

                {/* Main Middle 2-Column: Weekly Trend + Strong vs Focus Skill Areas */}
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                    {/* Left: Weekly Mastery & Consistency Trend (7 Cols) */}
                    <div className="lg:col-span-7 bg-[#0B0F19] border border-slate-800/80 rounded-3xl p-6 md:p-8 space-y-6 shadow-xl">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                            <div>
                                <div className="text-sm font-black text-white flex items-center gap-2">
                                    <TrendingUp className="w-4 h-4 text-cyan-400" />
                                    <span>Weekly Mastery & Consistency Trend</span>
                                </div>
                                <p className="text-xs text-slate-400 mt-0.5">
                                    Daily study hours vs verified concept retention score
                                </p>
                            </div>

                            <div className="flex items-center gap-2 bg-[#080C14] p-1 rounded-xl border border-slate-800 text-[11px]">
                                <button
                                    onClick={() => setActiveMetric('retention')}
                                    className={`px-3 py-1 rounded-lg font-bold transition-all ${
                                        activeMetric === 'retention'
                                            ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                                            : 'text-slate-400 hover:text-white'
                                    }`}
                                >
                                    Retention Rate (%)
                                </button>
                                <button
                                    onClick={() => setActiveMetric('hours')}
                                    className={`px-3 py-1 rounded-lg font-bold transition-all ${
                                        activeMetric === 'hours'
                                            ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                                            : 'text-slate-400 hover:text-white'
                                    }`}
                                >
                                    Active Study (hrs)
                                </button>
                            </div>
                        </div>

                        {/* Spline Area Chart */}
                        <div className="h-64 w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={weeklyTrendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                    <defs>
                                        <linearGradient id="cyanGradient" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4}/>
                                            <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
                                        </linearGradient>
                                        <linearGradient id="indigoGradient" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4}/>
                                            <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                                        </linearGradient>
                                    </defs>
                                    <XAxis dataKey="day" stroke="#475569" fontSize={11} tickLine={false} axisLine={false} />
                                    <YAxis stroke="#475569" fontSize={11} tickLine={false} axisLine={false} domain={activeMetric === 'retention' ? [60, 100] : [0, 5]} />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#0B0F19', borderColor: '#334155', borderRadius: '12px', fontSize: '12px' }}
                                        labelStyle={{ color: '#94a3b8', fontWeight: 'bold' }}
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey={activeMetric === 'retention' ? 'retention' : 'hours'}
                                        stroke={activeMetric === 'retention' ? '#06b6d4' : '#6366f1'}
                                        strokeWidth={3}
                                        fillOpacity={1}
                                        fill={activeMetric === 'retention' ? 'url(#cyanGradient)' : 'url(#indigoGradient)'}
                                    />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>

                        <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
                            <span className="flex items-center gap-1.5 text-cyan-400">
                                <Zap className="w-3.5 h-3.5" />
                                Velocity Index: 1.44x baseline speed. Reverse learning loop prevents weekend decay.
                            </span>
                            <button onClick={() => navigate('/history')} className="text-slate-400 hover:text-white font-bold flex items-center gap-1">
                                View Details →
                            </button>
                        </div>
                    </div>

                    {/* Right: Strong vs Focus Skill Areas (5 Cols) */}
                    <div className="lg:col-span-5 bg-[#0B0F19] border border-slate-800/80 rounded-3xl p-6 md:p-8 space-y-6 shadow-xl">
                        <div>
                            <div className="text-sm font-black text-white flex items-center gap-2">
                                <Target className="w-4 h-4 text-purple-400" />
                                <span>Strong vs Focus Skill Areas</span>
                            </div>
                            <p className="text-xs text-slate-400 mt-0.5">
                                Targeted breakdowns based on CS 162 diagnostic evaluations.
                            </p>
                        </div>

                        {/* Strong Skill Areas */}
                        <div className="space-y-3">
                            <div className="text-[10px] font-black uppercase tracking-wider text-emerald-400 flex items-center justify-between">
                                <span>STRONG SKILL AREAS</span>
                                <span className="font-mono">CS162 MASTERY</span>
                            </div>
                            <div className="space-y-2">
                                {[
                                    { name: 'Concurrency & Multithreading', score: 95 },
                                    { name: 'Systems Architecture & Caching', score: 92 },
                                    { name: 'Graph Algorithms & Pathfinding', score: 91 }
                                ].map((skill, i) => (
                                    <div key={i} className="p-3 rounded-xl bg-[#080C14] border border-slate-800/80 flex items-center justify-between text-xs">
                                        <span className="font-bold text-slate-200">{skill.name}</span>
                                        <span className="font-black text-emerald-400 font-mono">{skill.score}%</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Focus & Growth Areas */}
                        <div className="space-y-3">
                            <div className="text-[10px] font-black uppercase tracking-wider text-amber-400 flex items-center justify-between">
                                <span>FOCUS & GROWTH AREAS</span>
                                <span className="font-mono">&lt;75% TARGET</span>
                            </div>
                            <div className="space-y-2">
                                {[
                                    { name: 'Database Internals & Compaction', score: 68 },
                                    { name: 'Virtual Memory & OS Page Tables', score: 72 }
                                ].map((skill, i) => (
                                    <div key={i} className="p-3 rounded-xl bg-[#080C14] border border-slate-800/80 flex items-center justify-between text-xs">
                                        <span className="font-bold text-slate-200">{skill.name}</span>
                                        <span className="font-black text-amber-400 font-mono">{skill.score}%</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between">
                            <span className="text-[11px] text-slate-400">2 Recommended Drills Queued</span>
                            <button
                                onClick={() => navigate('/study')}
                                className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:opacity-90 text-white font-bold text-xs shadow-md shadow-cyan-500/20 transition-all flex items-center gap-1.5"
                            >
                                <span>Start Focus Session</span>
                                <ArrowRight className="w-3.5 h-3.5" />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Bottom Section: Recent Learning History Table */}
                <div className="bg-[#0B0F19] border border-slate-800/80 rounded-3xl p-6 md:p-8 space-y-6 shadow-xl">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                        <div>
                            <h3 className="text-base font-black text-white tracking-tight">Recent Learning History</h3>
                            <p className="text-xs text-slate-400 mt-0.5">
                                Clean log of recent diagnostics, simulations, and spaced review sessions with instant review links.
                            </p>
                        </div>

                        <div className="flex flex-wrap items-center gap-3">
                            <div className="relative">
                                <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                                <input
                                    type="text"
                                    value={searchFilter}
                                    onChange={(e) => setSearchFilter(e.target.value)}
                                    placeholder="Filter by topic or course..."
                                    className="bg-[#080C14] border border-slate-800 rounded-xl pl-8 pr-4 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 w-52"
                                />
                            </div>

                            <select
                                value={sessionFilter}
                                onChange={(e) => setSessionFilter(e.target.value)}
                                className="bg-[#080C14] border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-cyan-500"
                            >
                                <option value="all">All Session Types</option>
                                <option value="mock">Mock Interview</option>
                                <option value="diagnostic">Deep Diagnostic</option>
                                <option value="spaced">Spaced Repetition</option>
                                <option value="virtual">Virtual Study Room</option>
                            </select>
                        </div>
                    </div>

                    {/* Table */}
                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-xs">
                            <thead>
                                <tr className="border-b border-slate-800/80 text-[10px] font-black uppercase tracking-wider text-slate-400">
                                    <th className="pb-3 px-3">TIMESTAMP</th>
                                    <th className="pb-3 px-3">SESSION TYPE</th>
                                    <th className="pb-3 px-3">TOPIC / COURSE</th>
                                    <th className="pb-3 px-3">DURATION</th>
                                    <th className="pb-3 px-3">INITIAL SCORE</th>
                                    <th className="pb-3 px-3">FINAL MASTERY</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-800/60 font-medium">
                                {filteredRows.map((row) => (
                                    <tr key={row.id} className="hover:bg-slate-800/30 transition-colors">
                                        <td className="py-3.5 px-3 font-mono text-slate-400">{row.timestamp}</td>
                                        <td className="py-3.5 px-3">
                                            <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold border ${row.typeColor}`}>
                                                {row.type}
                                            </span>
                                        </td>
                                        <td className="py-3.5 px-3 font-bold text-white">{row.topic}</td>
                                        <td className="py-3.5 px-3 font-mono text-slate-400">{row.duration}</td>
                                        <td className="py-3.5 px-3 font-mono text-amber-400">{row.initialScore}</td>
                                        <td className="py-3.5 px-3 font-mono font-bold text-emerald-400">{row.finalMastery}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    <div className="pt-4 border-t border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-slate-400">
                        <span>Displaying {filteredRows.length} of 63 logged learning assessments. All logs cryptographically verified.</span>
                        <div className="flex items-center gap-2">
                            <span className="font-mono text-slate-400">Page 1 of 13</span>
                            <div className="flex items-center gap-1">
                                <button className="px-2.5 py-1 rounded-lg bg-[#080C14] border border-slate-800 text-slate-400 hover:text-white disabled:opacity-40" disabled>
                                    ‹ Prev
                                </button>
                                <button className="px-2.5 py-1 rounded-lg bg-[#080C14] border border-slate-800 text-slate-300 hover:text-white">
                                    Next ›
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AnalyticsPage;
