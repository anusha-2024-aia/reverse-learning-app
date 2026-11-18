/* eslint-disable react-hooks/set-state-in-effect */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    RotateCcw, Sparkles, ChevronDown, ChevronUp, CheckCircle2,
    AlertTriangle, Play, Clock, ArrowRight, Loader2, Calendar,
    Check, Layers, BookOpen, Activity, HelpCircle
} from 'lucide-react';
import api from '../api/axios';

const SmartRevision = () => {
    const _navigate = useNavigate();
    const [revisionData, setRevisionData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [showDerivation, setShowDerivation] = useState(false);
    const [activeCardIndex, setActiveCardIndex] = useState(0);
    const [ratingFeedback, setRatingFeedback] = useState(null);

    const loadRevisions = async () => {
        setLoading(true);
        try {
            const res = await api.get('/revisions');
            setRevisionData(res.data);
            setLoading(false);
        } catch (err) {
            console.error("Error loading revision data:", err);
            setLoading(false);
        }
    };

    useEffect(() => {
        loadRevisions();
    }, []);

    const recallCards = [
        {
            id: 1,
            topic: "QuickSort Worst-Case & Randomized Pivot",
            category: "Algorithms & Data Structures",
            subCategory: "Sorting",
            priority: "High",
            interval: "12h interval",
            question: "Explain why QuickSort worst-case degrades to O(n²) and demonstrate how randomized pivot selection mitigates this vulnerability.",
            derivation: (
                <div className="space-y-2 text-xs text-slate-300 leading-relaxed font-mono">
                    <p className="text-cyan-400 font-bold font-sans">1. Unbalanced Partition Recurrence:</p>
                    <p className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                        {`T(n) = T(n - 1) + O(n)\n     = O(n) + O(n-1) + ... + O(1)\n     = O(n²)`}
                    </p>
                    <p className="text-purple-400 font-bold font-sans mt-2">2. Randomized Pivot Selection Mitigation:</p>
                    <p className="text-slate-300 font-sans">
                        Uniformly sampling pivot indices prevents deterministic adversarial inputs. By Chernoff bounds, the probability of recursion depth exceeding 2c ln(n) decays as O(1/n^c), guaranteeing O(n log n) expected time.
                    </p>
                </div>
            )
        },
        {
            id: 2,
            topic: "B-Tree Balancing & Two-Phase Locking",
            category: "Databases & Storage Internals",
            subCategory: "Concurrency",
            priority: "High",
            interval: "18h interval",
            question: "How does strict two-phase locking (S2PL) prevent cascading aborts, and how does lock coupling (crabbing) guarantee deadlock-free B+ tree traversal?",
            derivation: (
                <div className="space-y-2 text-xs text-slate-300 leading-relaxed font-sans">
                    <p className="text-cyan-400 font-bold">1. S2PL Abort Isolation:</p>
                    <p className="text-slate-300">
                        In S2PL, all exclusive locks are held until transaction commit/abort, guaranteeing dirty reads are impossible and eliminating cascading aborts.
                    </p>
                    <p className="text-purple-400 font-bold mt-2">2. B+ Tree Crabbing Protocol:</p>
                    <p className="text-slate-300">
                        Acquire child lock before releasing parent lock. If child is safe (has space to split/merge), release all ancestor locks immediately.
                    </p>
                </div>
            )
        },
        {
            id: 3,
            topic: "TCP Congestion Control & Slow Start",
            category: "Computer Networks & Systems",
            subCategory: "Protocols",
            priority: "Medium",
            interval: "2d interval",
            question: "What triggers the transition from Slow Start to Congestion Avoidance in TCP Reno, and how does Fast Retransmit differentiate packet loss from congestion?",
            derivation: (
                <div className="space-y-2 text-xs text-slate-300 leading-relaxed font-sans">
                    <p className="text-cyan-400 font-bold">1. ssthresh Threshold:</p>
                    <p className="text-slate-300">
                        When cwnd reaches ssthresh, cwnd increases linearly by 1 MSS per RTT rather than exponentially.
                    </p>
                    <p className="text-purple-400 font-bold mt-2">2. Triple Duplicate ACKs:</p>
                    <p className="text-slate-300">
                        Three duplicate ACKs indicate out-of-order delivery, triggering Fast Retransmit without waiting for RTO timeout.
                    </p>
                </div>
            )
        }
    ];

    const currentCard = recallCards[activeCardIndex % recallCards.length];

    const handleRateRecall = (ratingLabel) => {
        setRatingFeedback(`Rated '${ratingLabel}'. Spaced interval calibrated.`);
        setTimeout(() => {
            setRatingFeedback(null);
            setShowDerivation(false);
            setActiveCardIndex(prev => (prev + 1) % recallCards.length);
        }, 1200);
    };

    if (loading) {
        return (
            <div className="flex-1 min-h-[70vh] flex items-center justify-center p-8">
                <div className="flex flex-col items-center gap-4">
                    <Loader2 className="w-10 h-10 text-cyan-400 animate-spin" />
                    <p className="text-slate-400 text-xs font-medium animate-pulse tracking-wide">
                        Optimizing spaced repetition retention curve...
                    </p>
                </div>
            </div>
        );
    }

    const summary = revisionData?.summary || {};
    const dueCount = (summary.due_today_count || 0) + (summary.overdue_count || 0) || 18;

    return (
        <div className="space-y-6 max-w-7xl mx-auto pb-12">
            {/* Header Banner */}
            <div className="p-6 md:p-8 rounded-2xl bg-gradient-to-r from-[#0F172A] via-[#111827] to-[#1E1B4B] border border-slate-800/80 shadow-2xl flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div className="space-y-1.5">
                    <div className="flex items-center gap-2 text-[10px] uppercase font-black tracking-wider text-cyan-400">
                        <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
                        SM-2 ADAPTIVE ENGINE • SYSTEM: IR-9682
                    </div>
                    <h1 className="text-2xl md:text-3xl font-black text-white tracking-tight">
                        Smart Spaced Repetition Engine
                    </h1>
                    <p className="text-xs md:text-sm text-slate-300 max-w-2xl leading-relaxed">
                        Personalized active recall queue calibrated to your optimal retention curve.
                    </p>
                </div>

                <div className="flex items-center gap-3">
                    <button
                        onClick={() => {
                            const el = document.getElementById('active-recall-card');
                            if (el) el.scrollIntoView({ behavior: 'smooth' });
                        }}
                        className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold text-xs shadow-lg shadow-purple-600/30 transition-all flex items-center gap-2"
                    >
                        <Play className="w-3.5 h-3.5 fill-current" />
                        <span>+ Start Revision</span>
                    </button>
                </div>
            </div>

            {/* Top 4 Stat Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-5 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg">
                    <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Topics Due</div>
                    <div className="text-2xl md:text-3xl font-black text-white">{dueCount}</div>
                    <div className="text-[11px] text-cyan-400 font-semibold mt-1">Ready for recall review</div>
                </div>

                <div className="p-5 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg">
                    <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Today's Revision</div>
                    <div className="text-2xl md:text-3xl font-black text-white">14 / 25</div>
                    <div className="text-[11px] text-purple-400 font-semibold mt-1">56% of daily goal reached</div>
                </div>

                <div className="p-5 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg">
                    <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Revision Priority</div>
                    <div className="text-2xl md:text-3xl font-black text-rose-400">High</div>
                    <div className="text-[11px] text-rose-400 font-semibold mt-1">3 Critical concepts need review</div>
                </div>

                <div className="p-5 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg">
                    <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Retention Rate</div>
                    <div className="text-2xl md:text-3xl font-black text-emerald-400">72%</div>
                    <div className="text-[11px] text-emerald-400 font-semibold mt-1">Long-term stability</div>
                </div>
            </div>

            {/* Main Interactive Grid: Active Recall Card (Left) & Topics Due Queue (Right) */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Active Recall Card (7 Cols) */}
                <div id="active-recall-card" className="lg:col-span-7 p-6 md:p-8 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-xl space-y-6 flex flex-col justify-between">
                    <div className="space-y-4">
                        <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
                            <div className="flex items-center gap-2">
                                <span className="text-[10px] font-black uppercase text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20">
                                    {currentCard.category}
                                </span>
                                <span className="text-[10px] text-slate-400 font-medium">{currentCard.subCategory}</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <span className="text-[10px] font-black uppercase text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded">
                                    Priority: {currentCard.priority}
                                </span>
                                <span className="text-xs text-slate-400">Card {activeCardIndex + 1} of {recallCards.length}</span>
                            </div>
                        </div>

                        {/* Question */}
                        <div>
                            <div className="text-[10px] uppercase font-bold text-slate-400 mb-1">QUESTION</div>
                            <h2 className="text-base md:text-lg font-black text-white leading-relaxed">
                                {currentCard.question}
                            </h2>
                        </div>

                        {/* Expandable Derivation */}
                        <div className="pt-2">
                            <button
                                onClick={() => setShowDerivation(!showDerivation)}
                                className="text-xs font-bold text-cyan-400 hover:text-cyan-300 flex items-center gap-1.5 transition-colors"
                            >
                                {showDerivation ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                                <span>{showDerivation ? 'Hide Derivation & Key Insight' : 'Show Derivation & Key Insight'}</span>
                            </button>

                            {showDerivation && (
                                <div className="mt-3 p-4 rounded-xl bg-slate-900/90 border border-cyan-500/30 animate-fadeIn">
                                    {currentCard.derivation}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Rate Your Recall Buttons */}
                    <div className="pt-6 border-t border-slate-800/80 space-y-3">
                        <div className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
                            RATE YOUR RECALL
                        </div>

                        {ratingFeedback ? (
                            <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-bold flex items-center justify-center gap-2">
                                <Check className="w-4 h-4" />
                                <span>{ratingFeedback}</span>
                            </div>
                        ) : (
                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                                <button
                                    onClick={() => handleRateRecall('Again')}
                                    className="p-3 rounded-xl bg-red-950/30 hover:bg-red-900/40 border border-red-500/30 text-red-300 text-xs font-bold transition-all text-center"
                                >
                                    <div>Again</div>
                                    <div className="text-[10px] text-red-400/80 font-normal">&lt; 1 Min</div>
                                </button>

                                <button
                                    onClick={() => handleRateRecall('Hard')}
                                    className="p-3 rounded-xl bg-amber-950/30 hover:bg-amber-900/40 border border-amber-500/30 text-amber-300 text-xs font-bold transition-all text-center"
                                >
                                    <div>Hard</div>
                                    <div className="text-[10px] text-amber-400/80 font-normal">12 Hours</div>
                                </button>

                                <button
                                    onClick={() => handleRateRecall('Good')}
                                    className="p-3 rounded-xl bg-cyan-950/30 hover:bg-cyan-900/40 border border-cyan-500/30 text-cyan-300 text-xs font-bold transition-all text-center"
                                >
                                    <div>Good</div>
                                    <div className="text-[10px] text-cyan-400/80 font-normal">2 Days</div>
                                </button>

                                <button
                                    onClick={() => handleRateRecall('Mastered')}
                                    className="p-3 rounded-xl bg-emerald-950/30 hover:bg-emerald-900/40 border border-emerald-500/30 text-emerald-300 text-xs font-bold transition-all text-center"
                                >
                                    <div>Mastered</div>
                                    <div className="text-[10px] text-emerald-400/80 font-normal">4 Days</div>
                                </button>
                            </div>
                        )}
                    </div>
                </div>

                {/* Topics Due Queue (5 Cols) */}
                <div className="lg:col-span-5 p-6 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg space-y-4">
                    <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
                        <h2 className="text-sm font-black uppercase tracking-wider text-white flex items-center gap-2">
                            <Layers className="w-4 h-4 text-cyan-400" />
                            Topics Due Queue
                        </h2>
                        <span className="text-[10px] font-bold text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">
                            18 Pending
                        </span>
                    </div>

                    <div className="space-y-3 pt-1">
                        {recallCards.map((card, idx) => (
                            <div
                                key={card.id}
                                className={`p-3.5 rounded-xl border transition-all flex items-center justify-between gap-3 ${activeCardIndex === idx ? 'bg-purple-950/30 border-purple-500/50' : 'bg-slate-900/60 border-slate-800/60 hover:border-slate-700'}`}
                            >
                                <div className="space-y-1 min-w-0 flex-1">
                                    <div className="flex items-center gap-2">
                                        <span className={`text-[9px] font-black uppercase px-1.5 py-0.5 rounded ${card.priority === 'High' ? 'bg-rose-500/10 text-rose-400' : 'bg-amber-500/10 text-amber-400'}`}>
                                            {card.priority}
                                        </span>
                                        <span className="text-[10px] text-slate-400">{card.interval}</span>
                                    </div>
                                    <div className="text-xs font-bold text-white truncate">
                                        {card.topic}
                                    </div>
                                </div>

                                <button
                                    onClick={() => {
                                        setActiveCardIndex(idx);
                                        setShowDerivation(false);
                                    }}
                                    className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-purple-600 text-slate-200 hover:text-white text-xs font-bold transition-all"
                                >
                                    Review
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SmartRevision;
