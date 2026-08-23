import React from 'react';
import { Clock, CheckCircle2, PlayCircle, BookOpen, Code, Brain } from 'lucide-react';

const DailyPlanCard = ({ dailyPlan }) => {
  if (!dailyPlan) return null;

  const getStepIcon = (step) => {
    switch (step) {
      case 1: return <Clock className="w-4 h-4 text-amber-400" />;
      case 2: return <BookOpen className="w-4 h-4 text-indigo-400" />;
      case 3: return <Code className="w-4 h-4 text-emerald-400" />;
      case 4: return <Brain className="w-4 h-4 text-purple-400" />;
      default: return <PlayCircle className="w-4 h-4 text-blue-400" />;
    }
  };

  return (
    <div className="bg-gradient-to-br from-slate-900 via-slate-900 to-indigo-950/40 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 font-bold text-sm">
            <Clock className="w-4 h-4" /> DAILY STUDY PLAN
          </div>
          <h3 className="text-xl font-black text-white mt-1">Today's Schedule</h3>
        </div>

        <div className="flex items-center gap-2">
          <span className="bg-indigo-950 text-indigo-300 border border-indigo-700/50 text-xs px-3 py-1.5 rounded-xl font-bold">
            ⏱️ {dailyPlan.hours_per_day} hrs ({dailyPlan.total_minutes} mins)
          </span>
        </div>
      </div>

      {dailyPlan.focus_topic && (
        <div className="bg-slate-800/50 border border-slate-700/60 p-3 rounded-xl flex items-center justify-between text-xs">
          <span className="text-slate-400">Current Priority Focus:</span>
          <span className="font-bold text-white bg-indigo-600/30 text-indigo-200 px-2.5 py-1 rounded-lg border border-indigo-500/40">
            🎯 {dailyPlan.focus_topic}
          </span>
        </div>
      )}

      <div className="space-y-3">
        {dailyPlan.schedule && dailyPlan.schedule.map((item) => (
          <div key={item.step} className="p-3.5 rounded-xl bg-slate-800/30 border border-slate-800 hover:border-slate-700 transition-colors flex items-start gap-3">
            <div className="p-2 rounded-lg bg-slate-800 border border-slate-700/60 mt-0.5">
              {getStepIcon(item.step)}
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-bold text-slate-200">{item.title}</h4>
                <span className="text-xs font-semibold text-indigo-400 bg-indigo-950/60 px-2 py-0.5 rounded border border-indigo-800/40">
                  {item.duration_mins} mins
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-1 leading-relaxed">{item.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DailyPlanCard;
