import React from 'react';
import { useNavigate } from 'react-router-dom';

const stateColors = {
  NOT_STARTED: 'bg-slate-700 text-slate-300 border-slate-600',
  LEARNING: 'bg-blue-900/30 text-blue-300 border-blue-500/30',
  CRITICAL: 'bg-red-900/40 text-red-300 border-red-500/40',
  WEAK: 'bg-orange-900/40 text-orange-300 border-orange-500/40',
  DEVELOPING: 'bg-amber-900/30 text-amber-300 border-amber-500/30',
  PRACTICE: 'bg-indigo-900/30 text-indigo-300 border-indigo-500/30',
  STRONG: 'bg-emerald-900/30 text-emerald-300 border-emerald-500/30',
  MASTERED: 'bg-cyan-900/30 text-cyan-300 border-cyan-500/30'
};

const trendIcons = {
  IMPROVING: '↗️',
  DECLINING: '↘️',
  STABLE: '➡️'
};

const TopicProgressCard = ({ topic }) => {
  const navigate = useNavigate();

  const { 
    topic_id,
    topic_name, 
    mastery_score, 
    state, 
    action_type, 
    difficulty, 
    trend, 
    target_concept, 
    reason 
  } = topic;

  const barWidth = `${Math.max(0, Math.min(100, mastery_score))}%`;

  const handleStart = () => {
    if (action_type === 'EXPLAIN') {
      navigate(`/study?topic=${topic_id}`);
    } else {
      navigate(`/study?topic=${topic_id}&mode=${action_type.toLowerCase()}`);
    }
  };
  
  return (
    <div 
      className="bg-slate-800 rounded-lg p-5 border border-slate-700 hover:border-indigo-500 transition-all flex flex-col md:flex-row gap-6 items-start md:items-center cursor-pointer hover:shadow-lg hover:shadow-indigo-500/10"
      onClick={handleStart}
    >
      <div className="flex-1 w-full">
        <div className="flex justify-between items-start mb-2">
          <h4 className="text-lg font-bold text-slate-100 group-hover:text-indigo-300 transition-colors">{topic_name}</h4>
          <span className={`text-xs px-2 py-1 rounded border font-medium ${stateColors[state] || stateColors.NOT_STARTED}`}>
            {state}
          </span>
        </div>
        
        <div className="flex items-center gap-4 text-sm text-slate-400 mb-3">
          <div className="flex items-center gap-1">
            <span className="text-white font-mono">{Math.round(mastery_score)}%</span> Mastery
          </div>
          {trend && trend !== "STABLE" && (
            <div className="flex items-center gap-1">
              <span>{trendIcons[trend]}</span> <span className="text-xs">{trend}</span>
            </div>
          )}
          <div className="flex items-center gap-1 text-xs px-1.5 py-0.5 bg-slate-700 rounded text-slate-300">
            {difficulty}
          </div>
        </div>

        <div className="h-2 w-full bg-slate-900 rounded-full overflow-hidden">
          <div 
            className={`h-full rounded-full transition-all duration-1000 ${
              mastery_score >= 80 ? 'bg-emerald-500' :
              mastery_score >= 60 ? 'bg-indigo-500' :
              mastery_score > 0 ? 'bg-orange-500' : 'bg-slate-600'
            }`}
            style={{ width: barWidth }}
          />
        </div>
      </div>

      <div className="w-full md:w-64 bg-slate-900/50 rounded p-4 border border-slate-700/50 flex-shrink-0 flex flex-col justify-between h-full">
        <div>
          <div className="text-xs text-slate-500 uppercase font-semibold mb-1">Recommended Action</div>
          <div className="font-bold text-indigo-400 mb-2">{action_type}</div>
          {target_concept && (
            <div className="text-xs text-red-300 bg-red-900/20 inline-block px-2 py-1 rounded border border-red-500/20 mb-2">
              Focus: {target_concept}
            </div>
          )}
          <div className="text-xs text-slate-400 line-clamp-2 mb-3" title={reason}>
            {reason}
          </div>
        </div>
        <button className="w-full py-1.5 bg-slate-700 hover:bg-indigo-600 rounded text-xs font-medium text-white transition-colors mt-auto">
          Start {action_type}
        </button>
      </div>
    </div>
  );
};

export default TopicProgressCard;
