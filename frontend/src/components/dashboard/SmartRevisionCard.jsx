import React from 'react';
import { useNavigate } from 'react-router-dom';
import { RotateCcw, AlertTriangle, ArrowRight, CheckCircle2, Clock } from 'lucide-react';

const SmartRevisionCard = ({ revisionSummary }) => {
    const navigate = useNavigate();

    if (!revisionSummary) return null;

    const summary = revisionSummary.summary || { due_today_count: 0, overdue_count: 0, tomorrow_count: 0 };
    const dueToday = revisionSummary.due_today || [];
    const overdue = revisionSummary.overdue || [];
    const tomorrow = revisionSummary.tomorrow || [];
    const upcoming = revisionSummary.upcoming || [];

    const urgentItems = [...overdue, ...dueToday].slice(0, 3);
    const nextUpcoming = tomorrow[0] || upcoming[0];

    const totalActionCount = (summary.due_today_count || 0) + (summary.overdue_count || 0);

    return (
        <div className="bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl relative overflow-hidden flex flex-col justify-between mb-8">
            <div>
                {/* Header */}
                <div className="flex items-center justify-between gap-4 mb-4">
                    <div className="flex items-center gap-2.5 text-white font-bold text-lg">
                        <div className="p-2 bg-indigo-600/20 text-indigo-400 rounded-xl border border-indigo-500/30">
                            <RotateCcw className="w-5 h-5" />
                        </div>
                        <span>Smart Revision</span>
                    </div>

                    <span className={`text-xs font-black uppercase px-2.5 py-1 rounded-full border ${
                        totalActionCount > 0 
                            ? 'bg-rose-500/20 text-rose-300 border-rose-500/30 animate-pulse'
                            : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
                    }`}>
                        {totalActionCount > 0 ? `${totalActionCount} topics due` : 'All caught up 🎉'}
                    </span>
                </div>

                {/* Due Topics list */}
                {urgentItems.length > 0 ? (
                    <div className="space-y-2 mb-4">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
                            Topics Needing Review:
                        </span>
                        {urgentItems.map(item => (
                            <div key={item.id} className="flex items-center justify-between bg-slate-900/90 px-3.5 py-2.5 rounded-xl border border-slate-800 text-xs">
                                <div className="flex items-center gap-2 font-medium text-slate-200">
                                    <span className="text-rose-400 font-bold">🔴</span>
                                    <span>{item.topic_name}</span>
                                    {item.has_knowledge_gap && (
                                        <span className="text-[9px] bg-rose-950 text-rose-300 px-1.5 py-0.5 rounded border border-rose-800">
                                            Gap
                                        </span>
                                    )}
                                </div>
                                <span className="font-mono font-bold text-slate-300 bg-slate-800 px-2 py-0.5 rounded">
                                    {Math.round(item.mastery_score)}%
                                </span>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="p-4 bg-slate-900/60 rounded-xl border border-slate-800 text-xs text-slate-400 mb-4 flex items-center gap-2">
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                        <span>No revisions due today. The system will notify you when it's time to review.</span>
                    </div>
                )}

                {/* Next Revision preview */}
                {nextUpcoming && (
                    <div className="text-xs text-indigo-300 pt-1 border-t border-slate-800 flex items-center justify-between mb-4">
                        <span className="text-slate-400">Next Revision:</span>
                        <span className="font-semibold text-white">
                            {nextUpcoming.topic_name} — {nextUpcoming.days_until_due === 1 ? 'Tomorrow' : `In ${nextUpcoming.days_until_due} days`}
                        </span>
                    </div>
                )}
            </div>

            {/* Action button */}
            <button
                onClick={() => navigate('/revision')}
                className="w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl text-xs flex items-center justify-center gap-2 transition-all shadow-lg shadow-indigo-600/30"
            >
                <span>Review Now</span>
                <ArrowRight className="w-4 h-4" />
            </button>
        </div>
    );
};

export default SmartRevisionCard;
