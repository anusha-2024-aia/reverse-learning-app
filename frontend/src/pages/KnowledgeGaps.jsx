import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    AlertTriangle, CheckCircle2, TrendingUp, TrendingDown,
    ArrowRight, Loader2, Sparkles, Filter, ShieldAlert,
    Activity, Play, BookOpen, Layers, RefreshCw, BarChart2, Target
} from 'lucide-react';
import api from '../api/axios';
import { AuthContext } from '../context/AuthContext';

const KnowledgeGaps = () => {
    const navigate = useNavigate();
    const { user } = useContext(AuthContext) || {};
    const [gaps, setGaps] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('ALL');

    useEffect(() => {
        api.get('/knowledge-gaps')
            .then(res => {
                setGaps(res.data.gaps || []);
                setLoading(false);
            })
            .catch(err => {
                console.error("Error loading knowledge gaps:", err);
                setLoading(false);
            });
    }, []);

    const isDemo = user?.email === 'maya.lin@berkeley.edu';
    const isNewUser = !isDemo && gaps.length === 0;

    const filteredGaps = filter === 'ALL'
        ? gaps
        : gaps.filter(g => g.severity?.toUpperCase() === filter);

    const filterOptions = ['ALL', 'CRITICAL', 'HIGH', 'MODERATE', 'LOW'];

    if (loading) {
        return (
            <div className="flex-1 min-h-[70vh] flex items-center justify-center p-8">
                <div className="flex flex-col items-center gap-4">
                    <Loader2 className="w-10 h-10 text-cyan-400 animate-spin" />
                    <p className="text-slate-400 text-xs font-medium animate-pulse tracking-wide">
                        Calculating cognitive gap diagnostics...
                    </p>
                </div>
            </div>
        );
    }

    if (isNewUser) {
        return (
            <div className="space-y-8 max-w-5xl mx-auto pb-16">
                {/* Header Banner */}
                <div className="p-6 md:p-8 rounded-2xl bg-gradient-to-r from-[#0F172A] via-[#111827] to-[#1E1B4B] border border-slate-800/80 shadow-2xl flex flex-col md:flex-row md:items-center justify-between gap-6">
                    <div className="space-y-1.5">
                        <div className="flex items-center gap-2 text-[10px] uppercase font-black tracking-wider text-cyan-400">
                            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
                            DIAGNOSTIC & GAP ANALYSIS • Telemetry Standby
                        </div>
                        <h1 className="text-2xl md:text-3xl font-black text-white tracking-tight">
                            Knowledge Diagnostic & Readiness
                        </h1>
                        <p className="text-xs md:text-sm text-slate-300 max-w-xl">
                            Continuous algorithmic detection of technical concept blindspots and cognitive weaknesses across systems and engineering curricula.
                        </p>
                    </div>

                    <div className="flex items-center gap-3">
                        <button
                            onClick={() => navigate('/study')}
                            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold text-xs shadow-lg shadow-purple-600/30 transition-all flex items-center gap-2"
                        >
                            <Play className="w-3.5 h-3.5 fill-current" />
                            <span>Start First Diagnostic →</span>
                        </button>
                    </div>
                </div>

                {/* Empty State Hero Box */}
                <div className="p-8 md:p-12 rounded-3xl bg-[#0B0F19] border border-slate-800/80 shadow-2xl text-center space-y-4">
                    <div className="w-16 h-16 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center mx-auto shadow-lg">
                        <ShieldAlert className="w-8 h-8" />
                    </div>
                    <h2 className="text-xl md:text-2xl font-black text-white">
                        No Knowledge Gaps Detected Yet
                    </h2>
                    <p className="text-xs md:text-sm text-slate-400 max-w-lg mx-auto leading-relaxed">
                        You have not completed any topic explanations or diagnostic evaluations yet. As you answer active recall drills, our diagnostic engine will detect misconception patterns and prioritize concepts that need remediation.
                    </p>
                    <div className="pt-2">
                        <button
                            onClick={() => navigate('/study')}
                            className="px-6 py-3 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow-lg shadow-purple-600/30 transition-all inline-flex items-center gap-2"
                        >
                            <span>Explore Topics & Start Diagnostic</span>
                            <ArrowRight className="w-4 h-4" />
                        </button>
                    </div>
                </div>

                {/* Informational Guidance Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                    <div className="p-5 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg space-y-2">
                        <div className="w-8 h-8 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400 mb-1">
                            <Target className="w-4 h-4" />
                        </div>
                        <h3 className="text-xs font-bold text-white uppercase tracking-wider">Concept Graph Mapping</h3>
                        <p className="text-xs text-slate-400 leading-relaxed">
                            Maps topic prerequisite chains to ensure foundational understanding before advancing to higher complexity tiers.
                        </p>
                    </div>

                    <div className="p-5 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg space-y-2">
                        <div className="w-8 h-8 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 mb-1">
                            <Activity className="w-4 h-4" />
                        </div>
                        <h3 className="text-xs font-bold text-white uppercase tracking-wider">Dynamic Severity Ratings</h3>
                        <p className="text-xs text-slate-400 leading-relaxed">
                            Flags declining topic trends as Critical, High, or Moderate priority based on score consistency and elapsed decay intervals.
                        </p>
                    </div>

                    <div className="p-5 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg space-y-2">
                        <div className="w-8 h-8 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 mb-1">
                            <CheckCircle2 className="w-4 h-4" />
                        </div>
                        <h3 className="text-xs font-bold text-white uppercase tracking-wider">Targeted Remediations</h3>
                        <p className="text-xs text-slate-400 leading-relaxed">
                            Generates targeted 10-15 minute focused active recall drills directly addressing your diagnosed gaps.
                        </p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6 max-w-7xl mx-auto pb-12">
            {/* Header Banner */}
            <div className="p-6 md:p-8 rounded-2xl bg-gradient-to-r from-[#0F172A] via-[#111827] to-[#1E1B4B] border border-slate-800/80 shadow-2xl flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div className="space-y-1.5">
                    <div className="flex items-center gap-2 text-[10px] uppercase font-black tracking-wider text-cyan-400">
                        <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
                        DIAGNOSTIC & GAP ANALYSIS • CS 162: Systems & OS
                    </div>
                    <h1 className="text-2xl md:text-3xl font-black text-white tracking-tight">
                        Knowledge Diagnostic & Readiness
                    </h1>
                    <p className="text-xs md:text-sm text-slate-300 max-w-2xl leading-relaxed">
                        Comprehensive skill breakdown across core concepts. Target identified cognitive gaps to prepare for upcoming exams.
                    </p>
                </div>

                <div className="flex items-center gap-3">
                    <div className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-purple-950/40 border border-purple-500/30 text-purple-300 text-xs font-black">
                        <Sparkles className="w-4 h-4 text-purple-400" />
                        <span>78% Readiness (Target: 85%)</span>
                    </div>
                    <button
                        onClick={() => navigate('/study')}
                        className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold text-xs shadow-lg shadow-purple-600/30 transition-all flex items-center gap-2"
                    >
                        <span>+ Improve Weak Areas</span>
                    </button>
                </div>
            </div>

            {/* Top 2 Cards: Strong Topics & Needs Review */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Strong Topics */}
                <div className="p-6 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg space-y-4">
                    <div className="flex items-center justify-between">
                        <h2 className="text-sm font-black uppercase tracking-wider text-white flex items-center gap-2">
                            <CheckCircle2 className="w-4 h-4 text-cyan-400" />
                            Strong Topics
                        </h2>
                        <span className="text-[10px] font-bold text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">
                            Above 80% Benchmark
                        </span>
                    </div>

                    <div className="space-y-3 pt-1">
                        <div>
                            <div className="flex items-center justify-between text-xs mb-1">
                                <span className="font-bold text-white">Physical Memory Allocators</span>
                                <span className="font-black text-cyan-400">93%</span>
                            </div>
                            <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                                <div className="bg-cyan-400 h-1.5 rounded-full" style={{ width: '93%' }}></div>
                            </div>
                        </div>

                        <div>
                            <div className="flex items-center justify-between text-xs mb-1">
                                <span className="font-bold text-white">Concurrency & Mutex Locks</span>
                                <span className="font-black text-cyan-400">88%</span>
                            </div>
                            <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                                <div className="bg-cyan-400 h-1.5 rounded-full" style={{ width: '88%' }}></div>
                            </div>
                        </div>

                        <div>
                            <div className="flex items-center justify-between text-xs mb-1">
                                <span className="font-bold text-white">File Systems & Inodes</span>
                                <span className="font-black text-cyan-400">82%</span>
                            </div>
                            <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                                <div className="bg-cyan-400 h-1.5 rounded-full" style={{ width: '82%' }}></div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Needs Review */}
                <div className="p-6 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg space-y-4">
                    <div className="flex items-center justify-between">
                        <h2 className="text-sm font-black uppercase tracking-wider text-white flex items-center gap-2">
                            <AlertTriangle className="w-4 h-4 text-rose-400" />
                            Needs Review
                        </h2>
                        <span className="text-[10px] font-bold text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/20">
                            Immediate Remediation
                        </span>
                    </div>

                    <div className="space-y-3 pt-1">
                        <div>
                            <div className="flex items-center justify-between text-xs mb-1">
                                <span className="font-bold text-white">Virtual Memory Paging & TLB</span>
                                <span className="font-black text-rose-400">54%</span>
                            </div>
                            <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                                <div className="bg-rose-500 h-1.5 rounded-full" style={{ width: '54%' }}></div>
                            </div>
                        </div>

                        <div>
                            <div className="flex items-center justify-between text-xs mb-1">
                                <span className="font-bold text-white">Deadlock Avoidance (Banker's Algorithm)</span>
                                <span className="font-black text-rose-400">58%</span>
                            </div>
                            <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                                <div className="bg-rose-500 h-1.5 rounded-full" style={{ width: '58%' }}></div>
                            </div>
                        </div>

                        <div>
                            <div className="flex items-center justify-between text-xs mb-1">
                                <span className="font-bold text-white">Distributed Consensus & Raft</span>
                                <span className="font-black text-amber-400">63%</span>
                            </div>
                            <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                                <div className="bg-amber-400 h-1.5 rounded-full" style={{ width: '63%' }}></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Category Proficiency Breakdown: 4 Circular Indicators */}
            <div className="p-6 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg space-y-4">
                <div className="flex items-center justify-between">
                    <h2 className="text-sm font-black uppercase tracking-wider text-white flex items-center gap-2">
                        <Activity className="w-4 h-4 text-cyan-400" />
                        Category Proficiency Breakdown
                    </h2>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center pt-2">
                    <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/70 flex flex-col items-center">
                        <div className="w-16 h-16 rounded-full border-4 border-cyan-500/20 border-t-cyan-400 flex items-center justify-center text-sm font-black text-white mb-2">
                            91%
                        </div>
                        <div className="text-xs font-bold text-white">Memory Subsystem</div>
                        <div className="text-[10px] text-cyan-400 font-bold uppercase mt-0.5">Mastered</div>
                    </div>

                    <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/70 flex flex-col items-center">
                        <div className="w-16 h-16 rounded-full border-4 border-indigo-500/20 border-t-indigo-400 flex items-center justify-center text-sm font-black text-white mb-2">
                            84%
                        </div>
                        <div className="text-xs font-bold text-white">Threads & Locks</div>
                        <div className="text-[10px] text-indigo-400 font-bold uppercase mt-0.5">Proficient</div>
                    </div>

                    <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/70 flex flex-col items-center">
                        <div className="w-16 h-16 rounded-full border-4 border-purple-500/20 border-t-purple-400 flex items-center justify-center text-sm font-black text-white mb-2">
                            68%
                        </div>
                        <div className="text-xs font-bold text-white">Distributed Systems</div>
                        <div className="text-[10px] text-purple-400 font-bold uppercase mt-0.5">Developing</div>
                    </div>

                    <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/70 flex flex-col items-center">
                        <div className="w-16 h-16 rounded-full border-4 border-rose-500/20 border-t-rose-400 flex items-center justify-center text-sm font-black text-white mb-2">
                            54%
                        </div>
                        <div className="text-xs font-bold text-white">Virtual Memory</div>
                        <div className="text-[10px] text-rose-400 font-bold uppercase mt-0.5">Needs Focus</div>
                    </div>
                </div>
            </div>

            {/* Identified Knowledge Gaps Section */}
            <div className="p-6 md:p-8 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-2xl space-y-6">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
                    <div>
                        <h2 className="text-base font-black text-white uppercase tracking-wider flex items-center gap-2">
                            <ShieldAlert className="w-4 h-4 text-rose-400" />
                            Identified Knowledge Gaps
                        </h2>
                        <p className="text-xs text-slate-400 mt-1">
                            Discovered through incorrect quiz explanations, low recall rates, and interview rubric evaluations.
                        </p>
                    </div>

                    {/* Filter buttons matching test expectations */}
                    <div className="flex flex-wrap gap-1.5 bg-slate-900 p-1 rounded-xl border border-slate-800">
                        {filterOptions.map(opt => (
                            <button
                                key={opt}
                                onClick={() => setFilter(opt)}
                                className={`px-3 py-1 rounded-lg text-xs font-black uppercase transition-all ${filter === opt ? 'bg-cyan-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'}`}
                            >
                                {opt === 'ALL' ? 'ALL GAPS' : opt}
                            </button>
                        ))}
                    </div>
                </div>

                {filteredGaps.length === 0 ? (
                    <div className="py-12 text-center text-slate-400 text-xs">
                        No knowledge gaps detected for filter '{filter}'.
                    </div>
                ) : (
                    <div className="space-y-4">
                        {filteredGaps.map((gap, index) => {
                            const isCritical = gap.severity?.toUpperCase() === 'CRITICAL';
                            const score = gap.mastery_score ?? gap.recent_score ?? 0;

                            return (
                                <div
                                    key={gap.topic_id || index}
                                    className="p-5 rounded-xl bg-slate-900/60 border border-slate-800/80 hover:border-slate-700 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4"
                                >
                                    <div className="space-y-1.5 flex-1 min-w-0">
                                        <div className="flex items-center gap-2.5">
                                            <span className={`text-[10px] font-black uppercase px-2 py-0.5 rounded border ${isCritical ? 'bg-rose-500/10 border-rose-500/30 text-rose-400' : 'bg-amber-500/10 border-amber-500/30 text-amber-400'}`}>
                                                {gap.severity || 'CRITICAL'}
                                            </span>
                                            <h3 className="text-sm font-black text-white truncate">
                                                {gap.topic_name}
                                            </h3>
                                        </div>

                                        <p className="text-xs text-slate-400 leading-relaxed max-w-3xl">
                                            {gap.recommendation || "Review core concept fundamentals and re-attempt explanation."}
                                        </p>

                                        <div className="flex items-center gap-4 text-[11px] text-slate-400 pt-0.5">
                                            <span className="font-semibold text-slate-300">
                                                Mastery: <span className="text-white font-bold">{score}%</span>
                                            </span>
                                            <span>•</span>
                                            <span>Trend: <span className="font-bold text-slate-300">{gap.trend || 'STABLE'}</span></span>
                                            <span>•</span>
                                            <span>Drill: 12 min drill</span>
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-3">
                                        <button
                                            onClick={() => navigate(`/study?topic=${gap.topic_id}`)}
                                            className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow-md shadow-purple-600/30 flex items-center gap-1.5 whitespace-nowrap transition-all"
                                        >
                                            <Play className="w-3 h-3 fill-current" />
                                            <span>Practice Topic</span>
                                        </button>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>

            {/* Recommended Next Topics Section */}
            <div className="p-6 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg space-y-4">
                <div className="flex items-center justify-between">
                    <h2 className="text-sm font-black uppercase tracking-wider text-white flex items-center gap-2">
                        <BookOpen className="w-4 h-4 text-cyan-400" />
                        Recommended Next Topics
                    </h2>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-[10px] font-black uppercase text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/20">
                                    Hard
                                </span>
                                <span className="text-[10px] text-slate-400">15 min</span>
                            </div>
                            <h3 className="text-xs font-bold text-white mb-1">Multi-Level Paging Walkthroughs</h3>
                            <p className="text-[11px] text-slate-400">Calculate page offsets and translate 32-bit & 64-bit virtual addresses step-by-step.</p>
                        </div>
                        <button onClick={() => navigate('/study')} className="mt-4 text-xs font-bold text-cyan-400 hover:text-cyan-300 text-left">
                            Start Practice →
                        </button>
                    </div>

                    <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-[10px] font-black uppercase text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20">
                                    Medium
                                </span>
                                <span className="text-[10px] text-slate-400">20 min</span>
                            </div>
                            <h3 className="text-xs font-bold text-white mb-1">Distributed Consensus (Raft Quorums)</h3>
                            <p className="text-[11px] text-slate-400">Understand split votes, heartbeat intervals, and commit indexes during network partitions.</p>
                        </div>
                        <button onClick={() => navigate('/study')} className="mt-4 text-xs font-bold text-purple-400 hover:text-purple-300 text-left">
                            Start Practice →
                        </button>
                    </div>

                    <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-[10px] font-black uppercase text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                                    Easy
                                </span>
                                <span className="text-[10px] text-slate-400">10 min</span>
                            </div>
                            <h3 className="text-xs font-bold text-white mb-1">Condition Variables & Spurious Wakeups</h3>
                            <p className="text-[11px] text-slate-400">Reinforce why while-loops are required over if-checks when calling wait().</p>
                        </div>
                        <button onClick={() => navigate('/study')} className="mt-4 text-xs font-bold text-emerald-400 hover:text-emerald-300 text-left">
                            Start Practice →
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default KnowledgeGaps;
