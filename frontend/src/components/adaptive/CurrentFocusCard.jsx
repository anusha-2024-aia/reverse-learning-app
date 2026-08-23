import React from 'react';
import { useNavigate } from 'react-router-dom';

const actionIcons = {
  LEARN: '📘',
  REVIEW: '🔄',
  EXPLAIN: '🎙️',
  PRACTICE: '✍️',
  RETAKE: '🔁',
  MOVE_FORWARD: '⏩',
};

const CurrentFocusCard = ({ recommendation }) => {
  const navigate = useNavigate();

  if (!recommendation) {
    return (
      <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-xl">
        <h3 className="text-xl font-bold text-slate-100 mb-2">🎯 Your Next Learning Step</h3>
        <p className="text-slate-400">Your adaptive learning path isn't ready yet.</p>
        <button
          onClick={() => navigate('/study')}
          className="mt-4 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 rounded text-white font-medium transition-colors"
        >
          Start First Evaluation
        </button>
      </div>
    );
  }

  const { topic_id, action_type, reason, target_concept, difficulty, topic } = recommendation;
  
  // Safe extraction of topic name (assuming API returns populated topic object if possible, or we rely on just knowing it's a recommendation for a topic)
  // For now, if topic isn't joined, we might just display "Topic" and load it elsewhere, but ideally the API sends it.
  // Actually, we need to ensure the backend sends the topic name or we fetch it. We will handle whatever is passed.

  const handleStart = async () => {
    // Determine where to navigate based on action type
    if (action_type === 'EXPLAIN') {
      navigate(`/study?topic=${topic_id}`);
    } else {
      // General fallback to study room for now
      navigate(`/study?topic=${topic_id}&mode=${action_type.toLowerCase()}`);
    }
  };

  return (
    <div className="bg-gradient-to-br from-slate-800 to-indigo-900/40 rounded-xl p-6 border border-indigo-500/30 shadow-xl relative overflow-hidden">
      <div className="absolute top-0 right-0 p-4 opacity-10 text-6xl">
        {actionIcons[action_type] || '🎯'}
      </div>
      
      <div className="flex items-center gap-2 mb-4">
        <span className="text-2xl">{actionIcons[action_type] || '🎯'}</span>
        <h3 className="text-xl font-bold text-slate-100">Your Next Learning Step</h3>
      </div>

      <div className="mb-6">
        <div className="text-sm font-semibold text-indigo-400 uppercase tracking-wider mb-1">
          {action_type}
        </div>
        <h4 className="text-2xl font-black text-white mb-2">
          {topic?.name || "Topic"}
        </h4>
        {target_concept && (
          <div className="inline-block px-3 py-1 bg-red-500/20 text-red-300 border border-red-500/30 rounded-full text-sm font-medium mb-3">
            Focus: {target_concept}
          </div>
        )}
      </div>

      <div className="space-y-4 mb-6">
        <div>
          <h5 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-1">Why this topic?</h5>
          <p className="text-slate-300 bg-slate-900/50 p-3 rounded border border-slate-700/50">
            {reason || "Based on your recent performance, this is the optimal next step."}
          </p>
        </div>

        <div className="flex gap-4">
          <div className="flex flex-col">
             <span className="text-xs text-slate-400 uppercase">Difficulty</span>
             <span className="text-sm font-medium text-slate-200">{difficulty}</span>
          </div>
          <div className="flex flex-col">
             <span className="text-xs text-slate-400 uppercase">Priority</span>
             <span className="text-sm font-medium text-amber-400">High</span>
          </div>
        </div>
      </div>

      <button
        onClick={handleStart}
        className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-white font-bold transition-all shadow-lg shadow-indigo-600/20 active:scale-[0.98]"
      >
        Start Adaptive {action_type === 'EXPLAIN' ? 'Explanation' : 'Practice'}
      </button>
    </div>
  );
};

export default CurrentFocusCard;
