import React from 'react';
import { TrendingUp, TrendingDown, Clock, Award } from 'lucide-react';

const dimensionLabels = {
  technical_score: 'Technical Accuracy',
  concept_score: 'Concept Understanding',
  completeness_score: 'Completeness',
  examples_score: 'Examples',
  relevance_score: 'Relevance',
  communication_score: 'Communication',
  grammar_score: 'Grammar',
  vocabulary_score: 'Vocabulary'
};

const TopicTimeline = ({ topicData }) => {
  if (!topicData || !topicData.history || topicData.history.length === 0) {
    return (
      <div className="bg-slate-900/50 p-6 rounded-xl border border-slate-800 text-center text-slate-400">
        No evaluation attempts found for this topic yet.
      </div>
    );
  }

  const { topic_name, total_attempts, first_score, latest_score, total_improvement, history } = topicData;

  return (
    <div className="bg-slate-800 rounded-2xl p-6 border border-slate-700 shadow-xl space-y-6">
      {/* Header stats */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-4 border-b border-slate-700">
        <div>
          <h3 className="text-xl font-black text-white">{topic_name} — Attempt History</h3>
          <p className="text-xs text-slate-400 mt-1">Tracking longitudinal progress across {total_attempts} attempts</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-700 text-xs">
            <span className="text-slate-400">First:</span> <span className="font-mono font-bold text-slate-200">{first_score}%</span>
          </div>
          <div className="bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-700 text-xs">
            <span className="text-slate-400">Latest:</span> <span className="font-mono font-bold text-indigo-400">{latest_score}%</span>
          </div>
          <div className={`px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1 border ${
            total_improvement >= 0 
              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' 
              : 'bg-red-500/10 text-red-400 border-red-500/30'
          }`}>
            {total_improvement >= 0 ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
            {total_improvement >= 0 ? `+${total_improvement}` : total_improvement} pts
          </div>
        </div>
      </div>

      {/* Visual Timeline */}
      <div className="relative pl-6 border-l-2 border-slate-700 space-y-6">
        {history.map((attempt) => {
          const delta = attempt.attempt > 1 ? attempt.overall_score - history[attempt.attempt - 2].overall_score : 0;
          return (
            <div key={attempt.id} className="relative group">
              {/* Dot */}
              <div className="absolute -left-[31px] top-1.5 w-4 h-4 rounded-full bg-slate-900 border-2 border-indigo-500 group-hover:bg-indigo-500 transition-colors" />

              <div className="bg-slate-900/80 rounded-xl p-4 border border-slate-700/70 hover:border-indigo-500/50 transition-all">
                <div className="flex justify-between items-center mb-2">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-100 text-sm">Attempt #{attempt.attempt}</span>
                    {attempt.attempt > 1 && (
                      <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                        delta >= 0 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'
                      }`}>
                        {delta >= 0 ? `+${delta}` : delta} pts
                      </span>
                    )}
                  </div>
                  <span className="text-[11px] text-slate-500 flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {new Date(attempt.created_at).toLocaleDateString()}
                  </span>
                </div>

                <div className="flex items-baseline gap-2 mb-3">
                  <span className="text-3xl font-black text-white">{attempt.overall_score}%</span>
                </div>

                {attempt.ai_insight && (
                  <p className="text-xs text-indigo-300 bg-indigo-950/30 p-2.5 rounded border border-indigo-500/20 mb-3">
                    "{attempt.ai_insight}"
                  </p>
                )}

                {/* Grid of dimensions for this attempt */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-slate-800">
                  {Object.entries(dimensionLabels).map(([key, label]) => (
                    <div key={key} className="bg-slate-800/60 p-2 rounded text-left">
                      <div className="text-[10px] text-slate-400 font-medium truncate">{label}</div>
                      <div className="text-xs font-mono font-bold text-slate-200">{attempt[key]}%</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default TopicTimeline;
