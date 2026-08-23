import React from 'react';
import { RefreshCw, Award, ArrowUpRight, ArrowDownRight, Clock, Sparkles, AlertTriangle } from 'lucide-react';

const RoadmapHistory = ({ history = [] }) => {
  if (!history || history.length === 0) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 text-center">
        <p className="text-sm text-slate-500">No roadmap adaptations logged yet.</p>
        <p className="text-xs text-slate-600 mt-1">Changes occur automatically as you complete evaluations.</p>
      </div>
    );
  }

  const getChangeIcon = (type) => {
    switch (type) {
      case 'REORDERED':
        return <RefreshCw className="w-4 h-4 text-indigo-400" />;
      case 'STATUS_CHANGED':
        return <Award className="w-4 h-4 text-emerald-400" />;
      case 'ROLE_CHANGED':
        return <Sparkles className="w-4 h-4 text-purple-400" />;
      default:
        return <Clock className="w-4 h-4 text-slate-400" />;
    }
  };

  const formatDate = (isoString) => {
    if (!isoString) return '';
    try {
      const d = new Date(isoString);
      return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch {
      return '';
    }
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2 text-slate-200 font-bold text-base">
          <RefreshCw className="w-5 h-5 text-indigo-400" />
          <span>Roadmap Changes</span>
        </div>
        <span className="text-xs text-slate-500 font-semibold uppercase">{history.length} logged</span>
      </div>

      <div className="space-y-3 max-h-96 overflow-y-auto pr-1 custom-scrollbar">
        {history.map((change, idx) => (
          <div key={change.id || idx} className="p-3.5 rounded-xl bg-slate-800/40 border border-slate-700/50 space-y-1.5 hover:bg-slate-800/70 transition-colors">
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-2 font-bold text-slate-200">
                {getChangeIcon(change.change_type)}
                <span>{change.topic_name || 'Roadmap'}</span>
              </div>
              <span className="text-[10px] text-slate-500">{formatDate(change.created_at)}</span>
            </div>

            {change.reason && (
              <p className="text-xs text-slate-300 leading-relaxed font-normal">
                {change.reason}
              </p>
            )}

            {change.old_position && change.new_position && (
              <div className="flex items-center gap-1.5 text-[11px] text-indigo-300 pt-1 font-medium">
                <span>Position Shift:</span>
                <span className="bg-slate-800 px-2 py-0.5 rounded text-slate-400">#{change.old_position}</span>
                <span>→</span>
                <span className="bg-indigo-950 text-indigo-300 px-2 py-0.5 rounded font-bold border border-indigo-800/40">#{change.new_position}</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default RoadmapHistory;
