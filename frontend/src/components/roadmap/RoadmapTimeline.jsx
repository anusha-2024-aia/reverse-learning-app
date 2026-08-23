import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Lock, CheckCircle2, AlertTriangle, ArrowRight, Flame, 
  Clock, ShieldAlert, Award, ChevronRight, Layers, Sparkles 
} from 'lucide-react';

const RoadmapTimeline = ({ items = [] }) => {
  const navigate = useNavigate();

  if (!items || items.length === 0) {
    return (
      <div className="text-center p-12 bg-slate-800/40 rounded-2xl border border-slate-700/50">
        <p className="text-slate-400">No roadmap topics generated yet.</p>
      </div>
    );
  }

  const getStatusBadge = (status) => {
    switch (status) {
      case 'MASTERED':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-purple-900/60 text-purple-300 border border-purple-500/50 shadow-sm">
            <Award className="w-3.5 h-3.5 text-purple-400" /> MASTERED
          </span>
        );
      case 'STRONG':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-900/60 text-emerald-300 border border-emerald-500/50">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> STRONG
          </span>
        );
      case 'PRACTICE':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-indigo-900/60 text-indigo-300 border border-indigo-500/50">
            <Layers className="w-3.5 h-3.5 text-indigo-400" /> PRACTICE
          </span>
        );
      case 'REVIEW':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-900/60 text-amber-300 border border-amber-500/50">
            <Clock className="w-3.5 h-3.5 text-amber-400" /> REVIEW
          </span>
        );
      case 'WEAK':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-rose-950 text-rose-300 border border-rose-500 shadow-md animate-pulse">
            <AlertTriangle className="w-3.5 h-3.5 text-rose-400" /> CURRENT FOCUS 🔴
          </span>
        );
      case 'IN_PROGRESS':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-blue-900/60 text-blue-300 border border-blue-500/50">
            <Flame className="w-3.5 h-3.5 text-blue-400" /> IN PROGRESS
          </span>
        );
      case 'LOCKED':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-slate-800 text-slate-400 border border-slate-700">
            <Lock className="w-3.5 h-3.5 text-slate-500" /> LOCKED
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-slate-800 text-slate-300 border border-slate-700">
            NOT STARTED
          </span>
        );
    }
  };

  const getDifficultyColor = (diff) => {
    switch (diff) {
      case 'ADVANCED': return 'text-purple-400 bg-purple-950/40 border-purple-800/40';
      case 'INTERMEDIATE': return 'text-amber-400 bg-amber-950/40 border-amber-800/40';
      default: return 'text-emerald-400 bg-emerald-950/40 border-emerald-800/40';
    }
  };

  const handleStudyTopic = (topicName) => {
    navigate(`/study?topic=${encodeURIComponent(topicName)}`);
  };

  return (
    <div className="relative space-y-6">
      {/* Central Connector Line */}
      <div className="absolute left-6 top-8 bottom-8 w-0.5 bg-slate-700/60 -z-0"></div>

      {items.map((item, index) => {
        const isCurrentFocus = item.status === 'WEAK';
        const isLocked = item.status === 'LOCKED';
        const isMastered = item.status === 'MASTERED';

        return (
          <div key={item.id || index} className="relative flex gap-4 md:gap-6 items-start z-10 group">
            
            {/* Step Number Circle */}
            <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-sm border-2 shadow-lg transition-all flex-shrink-0 ${
              isCurrentFocus
                ? 'bg-rose-950 border-rose-500 text-rose-200 ring-4 ring-rose-500/20'
                : isMastered
                ? 'bg-purple-950 border-purple-500 text-purple-300'
                : isLocked
                ? 'bg-slate-900 border-slate-700 text-slate-500'
                : 'bg-slate-800 border-slate-600 text-slate-200 group-hover:border-indigo-500'
            }`}>
              {isMastered ? (
                <Award className="w-5 h-5 text-purple-400" />
              ) : isLocked ? (
                <Lock className="w-5 h-5 text-slate-500" />
              ) : (
                <span>{String(item.order_index).padStart(2, '0')}</span>
              )}
            </div>

            {/* Main Topic Card */}
            <div className={`flex-1 rounded-2xl border p-5 md:p-6 transition-all ${
              isCurrentFocus
                ? 'bg-slate-900/90 border-rose-500/80 shadow-xl shadow-rose-950/30 ring-1 ring-rose-500/30'
                : isMastered
                ? 'bg-slate-900/60 border-purple-500/30'
                : isLocked
                ? 'bg-slate-900/40 border-slate-800 opacity-75'
                : 'bg-slate-900/80 border-slate-800 hover:border-slate-700'
            }`}>

              {/* Card Header */}
              <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                <div className="flex items-center gap-3">
                  <span className="text-xs font-semibold uppercase tracking-wider text-indigo-400 bg-indigo-950/50 px-2.5 py-1 rounded-md border border-indigo-800/40">
                    {item.category || 'Engineering'}
                  </span>
                  <span className={`text-xs px-2.5 py-1 rounded-md font-semibold border ${getDifficultyColor(item.difficulty)}`}>
                    {item.difficulty}
                  </span>
                </div>

                <div className="flex items-center gap-3">
                  <span className="text-xs text-slate-400 flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-slate-500" /> ~{item.estimated_hours}h
                  </span>
                  {getStatusBadge(item.status)}
                </div>
              </div>

              {/* Title & Description */}
              <h3 className="text-lg font-bold text-white group-hover:text-indigo-300 transition-colors">
                {item.topic_name}
              </h3>
              {item.description && (
                <p className="text-sm text-slate-400 mt-1 line-clamp-2">{item.description}</p>
              )}

              {/* Mastery Progress Bar */}
              <div className="mt-4 space-y-1.5">
                <div className="flex justify-between text-xs font-medium">
                  <span className="text-slate-400">Demonstrated Mastery</span>
                  <span className={`font-bold ${
                    item.mastery_score >= 80 ? 'text-emerald-400' : (item.mastery_score >= 50 ? 'text-amber-400' : 'text-rose-400')
                  }`}>
                    {Math.round(item.mastery_score)}%
                  </span>
                </div>
                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div 
                    className={`h-full transition-all duration-500 ${
                      item.mastery_score >= 80 
                        ? 'bg-gradient-to-r from-emerald-500 to-teal-400' 
                        : (item.mastery_score >= 50 ? 'bg-gradient-to-r from-amber-500 to-indigo-400' : 'bg-gradient-to-r from-rose-500 to-amber-500')
                    }`}
                    style={{ width: `${Math.max(4, Math.min(100, item.mastery_score))}%` }}
                  ></div>
                </div>
              </div>

              {/* Reason / Explanation Callout */}
              {item.reason && (
                <div className={`mt-4 p-3 rounded-xl text-xs border flex items-start gap-2.5 ${
                  isCurrentFocus 
                    ? 'bg-rose-950/40 border-rose-800/40 text-rose-200' 
                    : 'bg-slate-800/50 border-slate-700/40 text-slate-300'
                }`}>
                  {isCurrentFocus ? (
                    <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0 mt-0.5" />
                  ) : (
                    <Sparkles className="w-4 h-4 text-indigo-400 flex-shrink-0 mt-0.5" />
                  )}
                  <div>
                    <span className="font-semibold block">{isCurrentFocus ? 'Why Focus Here:' : 'System Note:'}</span>
                    <span>{item.reason}</span>
                  </div>
                </div>
              )}

              {/* Prerequisites & Skills Gained Tags */}
              <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-slate-800/80 pt-4">
                <div className="flex flex-wrap gap-2 text-xs">
                  {item.prerequisites && item.prerequisites.length > 0 && (
                    <div className="flex items-center gap-1 text-slate-400">
                      <span className="font-medium text-slate-500">Prereqs:</span>
                      {item.prerequisites.map((p, pIdx) => (
                        <span key={pIdx} className="bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700">
                          {p}
                        </span>
                      ))}
                    </div>
                  )}

                  {item.skills_gained && item.skills_gained.length > 0 && (
                    <div className="flex items-center gap-1 text-slate-400">
                      <span className="font-medium text-slate-500">Skills:</span>
                      {item.skills_gained.slice(0, 3).map((sk, skIdx) => (
                        <span key={skIdx} className="bg-indigo-950/40 text-indigo-300 px-2 py-0.5 rounded border border-indigo-800/40">
                          {sk}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Action CTA Button */}
                {!isLocked ? (
                  <button
                    onClick={() => handleStudyTopic(item.topic_name)}
                    className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 transition-all shadow-md ${
                      isCurrentFocus
                        ? 'bg-rose-600 hover:bg-rose-500 text-white shadow-rose-600/30'
                        : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-indigo-600/20'
                    }`}
                  >
                    <span>{isCurrentFocus ? 'Start Focus Session' : 'Practice Topic'}</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                ) : (
                  <button
                    disabled
                    className="px-4 py-2 rounded-xl text-xs font-medium bg-slate-800 text-slate-500 border border-slate-700 flex items-center gap-2 cursor-not-allowed"
                  >
                    <Lock className="w-3.5 h-3.5" /> Complete Prerequisites
                  </button>
                )}
              </div>

            </div>
          </div>
        );
      })}
    </div>
  );
};

export default RoadmapTimeline;
