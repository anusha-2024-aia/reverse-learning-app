import React from 'react';
import { Calendar, AlertTriangle, Play, CheckCircle2, Clock, RotateCcw, TrendingUp } from 'lucide-react';

const RevisionCard = ({ item, onStartRevision }) => {
    const isOverdue = item.status === 'OVERDUE';
    const isDueToday = item.status === 'DUE';
    const isTomorrow = item.days_until_due === 1;

    let badgeBg = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
    let statusLabel = `In ${item.days_until_due} Days`;

    if (isOverdue) {
        badgeBg = 'bg-rose-500/20 text-rose-400 border-rose-500/40 animate-pulse';
        statusLabel = 'OVERDUE';
    } else if (isDueToday) {
        badgeBg = 'bg-amber-500/20 text-amber-300 border-amber-500/40';
        statusLabel = 'Due Today';
    } else if (isTomorrow) {
        badgeBg = 'bg-yellow-500/15 text-yellow-300 border-yellow-500/30';
        statusLabel = 'Tomorrow';
    }

    const mastery = Math.round(item.mastery_score);
    let masteryColor = 'bg-rose-500';
    if (mastery >= 80) masteryColor = 'bg-emerald-500';
    else if (mastery >= 60) masteryColor = 'bg-amber-500';

    return (
        <div className={`bg-slate-800/90 border rounded-2xl p-6 shadow-xl hover:border-indigo-500/50 transition-all duration-300 relative flex flex-col justify-between overflow-hidden backdrop-blur-sm ${isOverdue ? 'border-rose-500/30' : isDueToday ? 'border-amber-500/30' : 'border-slate-700'}`}>
            
            {/* Top Bar */}
            <div>
                <div className="flex items-start justify-between gap-3 mb-3">
                    <div>
                        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-700">
                            {item.category || 'Topic'}
                        </span>
                        <h3 className="text-xl font-bold text-white mt-1 tracking-tight">
                            {item.topic_name}
                        </h3>
                    </div>
                    <span className={`text-xs font-black uppercase px-2.5 py-1 rounded-full border flex items-center gap-1.5 ${badgeBg}`}>
                        {isOverdue && <AlertTriangle className="w-3.5 h-3.5" />}
                        {isDueToday && <Clock className="w-3.5 h-3.5" />}
                        {!isOverdue && !isDueToday && <Calendar className="w-3.5 h-3.5" />}
                        {statusLabel}
                    </span>
                </div>

                {/* Mastery Progress Bar */}
                <div className="mb-4 bg-slate-900/80 p-3 rounded-xl border border-slate-700/60">
                    <div className="flex justify-between items-center text-xs font-semibold mb-1.5">
                        <span className="text-slate-400">Current Mastery</span>
                        <span className="text-white font-mono font-bold text-sm">{mastery}%</span>
                    </div>
                    <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden p-0.5 border border-slate-700">
                        <div 
                            className={`h-full rounded-full transition-all duration-500 ${masteryColor}`}
                            style={{ width: `${Math.max(5, mastery)}%` }}
                        ></div>
                    </div>
                </div>

                {/* Knowledge Gap Override Alert Box */}
                {item.has_knowledge_gap && item.knowledge_gap && (
                    <div className="mb-4 bg-rose-950/40 border border-rose-500/40 rounded-xl p-3 text-xs text-rose-200 flex items-start gap-2.5">
                        <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0 mt-0.5" />
                        <div>
                            <span className="font-bold text-rose-300 block uppercase tracking-wider text-[10px]">
                                ⚠ Focus Area (Knowledge Gap)
                            </span>
                            <p className="mt-0.5 text-rose-200 leading-relaxed font-medium">
                                {item.knowledge_gap}
                            </p>
                        </div>
                    </div>
                )}

                {/* Meta details */}
                <div className="grid grid-cols-2 gap-2 text-xs text-slate-400 mb-4 bg-slate-900/40 p-3 rounded-xl border border-slate-800">
                    <div>
                        <span className="block text-[10px] text-slate-500 font-semibold uppercase">Last Reviewed</span>
                        <span className="text-slate-200 font-medium">
                            {item.last_reviewed_at ? new Date(item.last_reviewed_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) : 'Not yet'}
                        </span>
                    </div>
                    <div>
                        <span className="block text-[10px] text-slate-500 font-semibold uppercase">Review Count</span>
                        <span className="text-slate-200 font-medium">
                            {item.review_count || 1} {item.review_count === 1 ? 'session' : 'sessions'}
                        </span>
                    </div>
                </div>
            </div>

            {/* Action Button */}
            <button
                onClick={() => onStartRevision(item)}
                className={`w-full py-3 px-4 rounded-xl font-bold text-sm flex items-center justify-center gap-2 transition-all shadow-lg ${
                    isOverdue || isDueToday
                        ? 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-indigo-600/30'
                        : 'bg-slate-700 hover:bg-slate-600 text-slate-200'
                }`}
            >
                <Play className="w-4 h-4 fill-current" />
                {isOverdue || isDueToday ? 'Start Revision' : 'Review Topic'}
            </button>
        </div>
    );
};

export default RevisionCard;
