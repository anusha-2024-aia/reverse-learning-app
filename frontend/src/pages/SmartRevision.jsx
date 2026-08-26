/* eslint-disable react-hooks/set-state-in-effect */
import React, { useState, useEffect } from 'react';
import { RotateCcw, AlertTriangle, Calendar, Clock, CheckCircle2, Loader2, RefreshCw, BookOpen, TrendingUp, Sparkles } from 'lucide-react';
import api from '../api/axios';
import RevisionCard from '../components/revision/RevisionCard';
import RevisionSessionModal from '../components/revision/RevisionSessionModal';

const SmartRevision = () => {
    const [revisionData, setRevisionData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedItemForRevision, setSelectedItemForRevision] = useState(null);
    const [activeTab, setActiveTab] = useState('all'); // all, due, upcoming, history

    const loadRevisions = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await api.get('/revisions');
            setRevisionData(res.data);
            setLoading(false);
        } catch (err) {
            console.error("Error loading revision schedule:", err);
            setError("We couldn't load your revision schedule.");
            setLoading(false);
        }
    };

    useEffect(() => {
        loadRevisions();
    }, []);

    const dueToday = revisionData?.due_today || [];
    const overdue = revisionData?.overdue || [];
    const tomorrow = revisionData?.tomorrow || [];
    const upcoming = revisionData?.upcoming || [];
    const groupedUpcoming = revisionData?.grouped_upcoming || {};
    const history = revisionData?.history || [];
    const summary = revisionData?.summary || { due_today_count: 0, overdue_count: 0, tomorrow_count: 0, upcoming_count: 0 };

    const totalActionNeeded = (summary.due_today_count || 0) + (summary.overdue_count || 0);

    return (
        <div className="flex-1 overflow-y-auto bg-slate-900 text-slate-100 p-6 md:p-12 relative">
            <div className="max-w-7xl mx-auto space-y-8">

                {/* Page Header */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
                    <div>
                        <div className="flex items-center gap-3">
                            <div className="p-3 bg-indigo-600/20 text-indigo-400 rounded-2xl border border-indigo-500/30">
                                <RotateCcw className="w-8 h-8 animate-spin-slow" />
                            </div>
                            <div>
                                <h1 className="text-3xl md:text-4xl font-black text-white tracking-tight">
                                    Smart Revision
                                </h1>
                                <p className="text-slate-400 text-sm md:text-base mt-1 font-medium">
                                    Review the right topics at the right time.
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="flex items-center gap-3">
                        <button
                            onClick={loadRevisions}
                            className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-bold transition-all border border-slate-700 flex items-center gap-2"
                        >
                            <RefreshCw className="w-4 h-4" />
                            <span>Refresh</span>
                        </button>
                    </div>
                </div>

                {/* Metric Summary Bar */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div className="bg-slate-800/80 p-5 rounded-2xl border border-slate-700/80 shadow-lg">
                        <span className="text-xs font-bold text-rose-400 uppercase tracking-wider block">Overdue</span>
                        <div className="text-3xl font-black text-white mt-1 font-mono">{summary.overdue_count}</div>
                        <span className="text-[11px] text-slate-400 mt-1 block">Needs immediate review</span>
                    </div>

                    <div className="bg-slate-800/80 p-5 rounded-2xl border border-slate-700/80 shadow-lg">
                        <span className="text-xs font-bold text-amber-400 uppercase tracking-wider block">Due Today</span>
                        <div className="text-3xl font-black text-white mt-1 font-mono">{summary.due_today_count}</div>
                        <span className="text-[11px] text-slate-400 mt-1 block">Ready for today</span>
                    </div>

                    <div className="bg-slate-800/80 p-5 rounded-2xl border border-slate-700/80 shadow-lg">
                        <span className="text-xs font-bold text-yellow-300 uppercase tracking-wider block">Tomorrow</span>
                        <div className="text-3xl font-black text-white mt-1 font-mono">{summary.tomorrow_count}</div>
                        <span className="text-[11px] text-slate-400 mt-1 block">Scheduled tomorrow</span>
                    </div>

                    <div className="bg-slate-800/80 p-5 rounded-2xl border border-slate-700/80 shadow-lg">
                        <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider block">Upcoming</span>
                        <div className="text-3xl font-black text-white mt-1 font-mono">{summary.upcoming_count}</div>
                        <span className="text-[11px] text-slate-400 mt-1 block">Scheduled in future</span>
                    </div>
                </div>

                {/* Filter Navigation Tabs */}
                <div className="flex gap-2 border-b border-slate-800 pb-2 overflow-x-auto">
                    <button
                        onClick={() => setActiveTab('all')}
                        className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                            activeTab === 'all'
                                ? 'bg-indigo-600 text-white shadow-md'
                                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                        }`}
                    >
                        All Schedules ({summary.total_scheduled || 0})
                    </button>
                    <button
                        onClick={() => setActiveTab('due')}
                        className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
                            activeTab === 'due'
                                ? 'bg-amber-600 text-white shadow-md'
                                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                        }`}
                    >
                        Due & Overdue ({totalActionNeeded})
                    </button>
                    <button
                        onClick={() => setActiveTab('upcoming')}
                        className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                            activeTab === 'upcoming'
                                ? 'bg-indigo-600 text-white shadow-md'
                                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                        }`}
                    >
                        Upcoming ({summary.upcoming_count})
                    </button>
                    <button
                        onClick={() => setActiveTab('history')}
                        className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                            activeTab === 'history'
                                ? 'bg-indigo-600 text-white shadow-md'
                                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                        }`}
                    >
                        Revision History ({history.length})
                    </button>
                </div>

                {/* LOADING STATE */}
                {loading && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 py-12">
                        {[1, 2, 3, 4, 5, 6].map(i => (
                            <div key={i} className="bg-slate-800/50 border border-slate-700/50 rounded-2xl p-6 h-64 animate-pulse">
                                <div className="h-4 bg-slate-700 rounded w-1/3 mb-4"></div>
                                <div className="h-6 bg-slate-700 rounded w-2/3 mb-6"></div>
                                <div className="h-12 bg-slate-700/60 rounded mb-4"></div>
                                <div className="h-10 bg-slate-700/80 rounded mt-auto"></div>
                            </div>
                        ))}
                    </div>
                )}

                {/* ERROR STATE */}
                {error && !loading && (
                    <div className="bg-slate-800 border border-rose-500/30 rounded-2xl p-12 text-center max-w-xl mx-auto space-y-4 shadow-2xl">
                        <AlertTriangle className="w-12 h-12 text-rose-400 mx-auto" />
                        <h3 className="text-xl font-bold text-white">{error}</h3>
                        <p className="text-sm text-slate-400">
                            Check your connection and try again. Your existing learning data is safe.
                        </p>
                        <button
                            onClick={loadRevisions}
                            className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl text-sm transition-colors shadow-lg"
                        >
                            Try Again
                        </button>
                    </div>
                )}

                {/* EMPTY STATE */}
                {!loading && !error && (summary.total_scheduled === 0 || (activeTab === 'due' && totalActionNeeded === 0)) && (
                    <div className="bg-slate-800/40 border border-slate-800 rounded-3xl p-12 text-center max-w-2xl mx-auto space-y-4 my-8">
                        <div className="w-16 h-16 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded-full flex items-center justify-center mx-auto">
                            <CheckCircle2 className="w-10 h-10" />
                        </div>
                        <h2 className="text-2xl font-black text-white">🎉 You're all caught up!</h2>
                        <p className="text-slate-300 text-sm max-w-md mx-auto leading-relaxed">
                            No topics need revision right now. Keep learning new topics and the system will automatically schedule your next revisions based on your comprehension.
                        </p>
                        <div className="pt-2">
                            <button
                                onClick={() => window.location.href = '/study'}
                                className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl text-xs uppercase tracking-wider transition-all shadow-lg shadow-indigo-600/30"
                            >
                                Learn New Topic
                            </button>
                        </div>
                    </div>
                )}

                {/* CONTENT SECTIONS */}
                {!loading && !error && (
                    <div className="space-y-12">
                        
                        {/* REVISION HISTORY TAB */}
                        {activeTab === 'history' ? (
                            <div className="space-y-6">
                                <h2 className="text-2xl font-black text-white flex items-center gap-2">
                                    <BookOpen className="w-6 h-6 text-indigo-400" />
                                    Revision History & Progression
                                </h2>
                                
                                {history.length === 0 ? (
                                    <div className="p-8 text-center bg-slate-800/40 rounded-2xl text-slate-400">
                                        No revision history logged yet. Complete evaluations to see your progress trends!
                                    </div>
                                ) : (
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        {history.map((hItem) => (
                                            <div key={hItem.topic_id} className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-6 space-y-3">
                                                <div className="flex justify-between items-start">
                                                    <div>
                                                        <h3 className="text-lg font-bold text-white">{hItem.topic_name}</h3>
                                                        <span className="text-xs text-slate-400">{hItem.total_attempts} attempts logged</span>
                                                    </div>
                                                    <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${hItem.improvement >= 0 ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-rose-500/20 text-rose-300'}`}>
                                                        {hItem.improvement >= 0 ? `+${hItem.improvement}%` : `${hItem.improvement}%`}
                                                    </span>
                                                </div>

                                                <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 text-xs font-mono text-indigo-300 flex items-center justify-between">
                                                    <span>Progression:</span>
                                                    <span className="font-bold">{hItem.scores_progression}</span>
                                                </div>

                                                <div className="text-xs text-slate-400 flex justify-between pt-1">
                                                    <span>Next Review: <strong className="text-slate-200">{hItem.next_review_formatted}</strong></span>
                                                    <span>Latest: <strong className="text-emerald-400">{hItem.latest_score}%</strong></span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        ) : (
                            <>
                                {/* SECTION 1: OVERDUE */}
                                {(activeTab === 'all' || activeTab === 'due') && overdue.length > 0 && (
                                    <section className="space-y-4">
                                        <div className="flex items-center gap-2 text-rose-400 font-bold text-xl">
                                            <AlertTriangle className="w-5 h-5 animate-bounce" />
                                            <h2>🔴 Overdue ({overdue.length})</h2>
                                        </div>
                                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                            {overdue.map(item => (
                                                <RevisionCard 
                                                    key={item.id} 
                                                    item={item} 
                                                    onStartRevision={(item) => setSelectedItemForRevision(item)} 
                                                />
                                            ))}
                                        </div>
                                    </section>
                                )}

                                {/* SECTION 2: DUE TODAY */}
                                {(activeTab === 'all' || activeTab === 'due') && dueToday.length > 0 && (
                                    <section className="space-y-4">
                                        <div className="flex items-center gap-2 text-amber-300 font-bold text-xl">
                                            <Clock className="w-5 h-5" />
                                            <h2>🔴 Due Today ({dueToday.length})</h2>
                                        </div>
                                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                            {dueToday.map(item => (
                                                <RevisionCard 
                                                    key={item.id} 
                                                    item={item} 
                                                    onStartRevision={(item) => setSelectedItemForRevision(item)} 
                                                />
                                            ))}
                                        </div>
                                    </section>
                                )}

                                {/* SECTION 3: TOMORROW */}
                                {(activeTab === 'all' || activeTab === 'upcoming') && tomorrow.length > 0 && (
                                    <section className="space-y-4">
                                        <div className="flex items-center gap-2 text-yellow-300 font-bold text-xl">
                                            <Calendar className="w-5 h-5" />
                                            <h2>🟡 Tomorrow ({tomorrow.length})</h2>
                                        </div>
                                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                            {tomorrow.map(item => (
                                                <RevisionCard 
                                                    key={item.id} 
                                                    item={item} 
                                                    onStartRevision={(item) => setSelectedItemForRevision(item)} 
                                                />
                                            ))}
                                        </div>
                                    </section>
                                )}

                                {/* SECTION 4: UPCOMING */}
                                {(activeTab === 'all' || activeTab === 'upcoming') && upcoming.length > 0 && (
                                    <section className="space-y-6">
                                        <div className="flex items-center gap-2 text-emerald-400 font-bold text-xl">
                                            <Calendar className="w-5 h-5" />
                                            <h2>🟢 Upcoming Revisions</h2>
                                        </div>

                                        {Object.entries(groupedUpcoming).map(([groupLabel, groupItems]) => (
                                            <div key={groupLabel} className="space-y-3">
                                                <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-400 bg-slate-800/60 inline-block px-3 py-1 rounded-full border border-slate-700">
                                                    {groupLabel}
                                                </h3>
                                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                                    {groupItems.map(item => (
                                                        <RevisionCard 
                                                            key={item.id} 
                                                            item={item} 
                                                            onStartRevision={(item) => setSelectedItemForRevision(item)} 
                                                        />
                                                    ))}
                                                </div>
                                            </div>
                                        ))}
                                    </section>
                                )}
                            </>
                        )}
                    </div>
                )}

                {/* INTERACTIVE REVISION MODAL */}
                {selectedItemForRevision && (
                    <RevisionSessionModal 
                        topicItem={selectedItemForRevision}
                        onClose={() => setSelectedItemForRevision(null)}
                        onRevisionComplete={loadRevisions}
                    />
                )}

            </div>
        </div>
    );
};

export default SmartRevision;
