import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Compass, 
  BrainCircuit, 
  RotateCcw, 
  Bot, 
  FileText, 
  Mic, 
  ArrowRight, 
  Sparkles,
  CheckCircle2
} from 'lucide-react';

const ConnectedStudentPipeline = ({ roadmapSummary, revisionSummary, resumeSummary, adaptiveRec }) => {
  const navigate = useNavigate();

  // Determine current priority step based on user status
  const getActiveStepIndex = () => {
    if (!roadmapSummary || roadmapSummary.progress === 0) return 0; // Step 1: Set Roadmap
    const dueCount = (revisionSummary?.summary?.due_today_count || 0) + (revisionSummary?.summary?.overdue_count || 0);
    if (dueCount > 0) return 2; // Step 3: Revision due
    if (!resumeSummary?.has_resume) return 4; // Step 5: Upload resume
    return 1; // Default to Step 2: Explanation
  };

  const activeStepIdx = getActiveStepIndex();

  const steps = [
    {
      stepNum: '01',
      title: 'Target Roadmap',
      icon: Compass,
      path: '/learning-path',
      badge: roadmapSummary?.target_role ? `🎯 ${roadmapSummary.target_role}` : 'Set Goal',
      metric: roadmapSummary ? `${roadmapSummary.progress}% Complete` : '0% Started',
      desc: 'Define your target role & daily study timeline',
      btnText: 'View Roadmap',
      color: 'from-blue-600/20 to-indigo-600/20 border-blue-500/40 text-blue-400'
    },
    {
      stepNum: '02',
      title: 'Concept Explanation',
      icon: BrainCircuit,
      path: '/syllabi',
      badge: adaptiveRec?.action_type || 'Feynman Technique',
      metric: adaptiveRec?.topic?.name ? `Focus: ${adaptiveRec.topic.name}` : 'Explain & Teach AI',
      desc: 'Teach concepts in your own words for 4D AI evaluation',
      btnText: 'Explain Concept',
      color: 'from-indigo-600/20 to-violet-600/20 border-indigo-500/40 text-indigo-400'
    },
    {
      stepNum: '03',
      title: 'Spaced Revision',
      icon: RotateCcw,
      path: '/revision',
      badge: (revisionSummary?.summary?.due_today_count || 0) > 0 
        ? `${revisionSummary.summary.due_today_count} Due Today` 
        : 'All Caught Up',
      metric: (revisionSummary?.summary?.overdue_count || 0) > 0 
        ? `${revisionSummary.summary.overdue_count} Overdue` 
        : 'Ebbinghaus Curve Active',
      desc: 'Retain knowledge before memory retention fades',
      btnText: 'Review Now',
      color: 'from-violet-600/20 to-purple-600/20 border-violet-500/40 text-violet-400'
    },
    {
      stepNum: '04',
      title: 'AI Mock Interview',
      icon: Bot,
      path: '/mock-interview',
      badge: 'Adaptive Probes',
      metric: 'Technical & Behavioral',
      desc: 'Practice under real-time adaptive interview pressure',
      btnText: 'Start Interview',
      color: 'from-purple-600/20 to-fuchsia-600/20 border-purple-500/40 text-purple-400'
    },
    {
      stepNum: '05',
      title: 'Resume Intelligence',
      icon: FileText,
      path: '/resume-intelligence',
      badge: resumeSummary?.has_resume ? '✓ Resume Analyzed' : 'Upload Resume',
      metric: resumeSummary?.has_resume ? `${resumeSummary.questions_count || 0} Custom Qs` : 'ATS Gap Analysis',
      desc: 'Match target ATS job skills & project-specific questions',
      btnText: 'Resume Hub',
      color: 'from-fuchsia-600/20 to-pink-600/20 border-fuchsia-500/40 text-fuchsia-400'
    },
    {
      stepNum: '06',
      title: 'Communication Coach',
      icon: Mic,
      path: '/communication-coach',
      badge: 'Voice Analytics',
      metric: 'WPM, Fillers & Pitch',
      desc: 'Master speech pace, reduce filler words & boost confidence',
      btnText: 'Practice Speech',
      color: 'from-emerald-600/20 to-teal-600/20 border-emerald-500/40 text-emerald-400'
    }
  ];

  return (
    <div className="bg-slate-900/90 border border-indigo-500/30 rounded-3xl p-6 md:p-8 mb-10 shadow-2xl relative overflow-hidden backdrop-blur-xl">
      {/* Background Subtle Gradient Glow */}
      <div className="absolute -top-24 -right-24 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header Banner */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-8 pb-6 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2.5 mb-1">
            <span className="bg-indigo-600/20 border border-indigo-500/40 text-indigo-300 text-xs font-black uppercase tracking-wider px-3 py-1 rounded-full flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-indigo-400 animate-spin" />
              Connected Student Learning Pipeline
            </span>
          </div>
          <h2 className="text-2xl md:text-3xl font-black text-white tracking-tight">
            Follow Your Step-by-Step Mastery Path 🚀
          </h2>
          <p className="text-slate-400 text-sm mt-1">
            Each box connects to the next step in your journey for maximum concept retention and interview readiness.
          </p>
        </div>

        {/* Legend Indicator */}
        <div className="flex items-center gap-3 bg-slate-800/80 border border-slate-700 px-4 py-2 rounded-xl text-xs text-slate-300">
          <span className="flex items-center gap-1.5 font-bold">
            <span className="w-2.5 h-2.5 rounded-full bg-indigo-500 animate-pulse" /> Current Focus
          </span>
          <span className="text-slate-600">|</span>
          <span>6 Connected Steps</span>
        </div>
      </div>

      {/* Connected Steps Pipeline Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 relative">
        {steps.map((step, idx) => {
          const StepIcon = step.icon;
          const isActive = idx === activeStepIdx;
          const isNext = idx === (activeStepIdx + 1) % steps.length;

          return (
            <div key={step.stepNum} className="relative group flex flex-col justify-between">
              
              {/* Connector Arrow for LG/XL screens */}
              {idx < steps.length - 1 && (
                <div className="hidden xl:block absolute -right-3 top-1/2 -translate-y-1/2 z-20 pointer-events-none">
                  <div className="w-6 h-6 rounded-full bg-slate-800 border border-slate-700 text-slate-400 flex items-center justify-center shadow-lg group-hover:border-indigo-500 group-hover:text-indigo-400 transition-all">
                    <ArrowRight className="w-3.5 h-3.5" />
                  </div>
                </div>
              )}

              {/* Box Card */}
              <div 
                onClick={() => navigate(step.path)}
                className={`cursor-pointer rounded-2xl p-5 border transition-all duration-300 flex flex-col justify-between h-full relative overflow-hidden bg-slate-800/80 hover:bg-slate-800 ${
                  isActive 
                    ? 'border-indigo-500 ring-2 ring-indigo-500/50 shadow-xl shadow-indigo-500/20 bg-gradient-to-b from-slate-800 to-indigo-950/40' 
                    : 'border-slate-800 hover:border-slate-700 hover:shadow-lg'
                }`}
              >
                {/* Active Indicator Pin */}
                {isActive && (
                  <div className="absolute top-2 right-2 bg-indigo-500 text-white text-[9px] font-black uppercase px-2 py-0.5 rounded-full tracking-wider flex items-center gap-1 shadow-md animate-bounce">
                    <span>NEXT STEP</span>
                  </div>
                )}

                <div>
                  {/* Top Step Badge & Icon */}
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-[11px] font-black tracking-widest text-slate-500 group-hover:text-slate-400">
                      STEP {step.stepNum}
                    </span>
                    <div className={`p-2.5 rounded-xl border bg-gradient-to-br ${step.color} group-hover:scale-110 transition-transform`}>
                      <StepIcon className="w-5 h-5" />
                    </div>
                  </div>

                  {/* Title & Badge */}
                  <h3 className="text-base font-bold text-white mb-1 group-hover:text-indigo-300 transition-colors">
                    {step.title}
                  </h3>

                  <div className="mb-3">
                    <span className="inline-block bg-slate-900/90 text-slate-300 text-[11px] font-medium px-2.5 py-1 rounded-lg border border-slate-700/60 truncate max-w-full">
                      {step.badge}
                    </span>
                  </div>

                  <p className="text-slate-400 text-xs leading-relaxed mb-4">
                    {step.desc}
                  </p>
                </div>

                {/* Metric & Navigation Button */}
                <div className="pt-3 border-t border-slate-700/50 mt-2">
                  <div className="text-[11px] font-semibold text-slate-300 mb-2 truncate">
                    📊 {step.metric}
                  </div>

                  <button className={`w-full py-2 px-3 rounded-xl font-bold text-xs flex items-center justify-center gap-1.5 transition-all ${
                    isActive 
                      ? 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/30' 
                      : 'bg-slate-700/60 group-hover:bg-indigo-600 text-slate-200 group-hover:text-white'
                  }`}>
                    <span>{step.btnText}</span>
                    <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                  </button>
                </div>

              </div>

            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ConnectedStudentPipeline;
