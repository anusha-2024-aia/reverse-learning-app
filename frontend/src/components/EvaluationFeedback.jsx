import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  CheckCircle2, AlertTriangle, BookOpen, Target, MessageCircle, 
  Code, ChevronDown, ChevronRight, FileText, TrendingUp, TrendingDown, 
  Sparkles, Award, Zap, Brain
} from 'lucide-react';

const dimensionMeta = [
  { key: 'technicalAccuracy', label: 'Technical Accuracy', weight: '20%' },
  { key: 'conceptUnderstanding', label: 'Concept Understanding', weight: '20%' },
  { key: 'completeness', label: 'Completeness', weight: '10%' },
  { key: 'examples', label: 'Examples', weight: '10%' },
  { key: 'relevance', label: 'Relevance', weight: '10%' },
  { key: 'communication', label: 'Communication', weight: '10%' },
  { key: 'grammar', label: 'Grammar', weight: '10%' },
  { key: 'vocabulary', label: 'Vocabulary', weight: '10%' }
];

const CollapsibleSection = ({ title, icon: Icon, colorClass, children, defaultOpen = false }) => {
    const [isOpen, setIsOpen] = useState(defaultOpen);

    return (
        <div className={`mb-4 bg-slate-900/50 rounded-xl overflow-hidden border border-slate-700/50 border-l-4 ${colorClass}`}>
            <button 
                onClick={() => setIsOpen(!isOpen)}
                className="w-full px-5 py-4 flex items-center justify-between hover:bg-slate-800/50 transition-colors focus:outline-none"
            >
                <div className="flex items-center gap-3">
                    <Icon className={`w-5 h-5 ${colorClass.replace('border-l-', 'text-')}`} />
                    <h3 className="font-bold text-slate-200 tracking-wide">{title}</h3>
                </div>
                {isOpen ? <ChevronDown className="w-5 h-5 text-slate-400" /> : <ChevronRight className="w-5 h-5 text-slate-400" />}
            </button>
            
            <div className={`transition-all duration-300 ease-in-out ${isOpen ? 'max-h-[2000px] opacity-100' : 'max-h-0 opacity-0 overflow-hidden'}`}>
                <div className="px-5 pb-5 pt-2 text-slate-300 border-t border-slate-800">
                    {children}
                </div>
            </div>
        </div>
    );
};

const EvaluationFeedback = ({ feedback, studentExplanation, onContinue, onRetry }) => {
    const navigate = useNavigate();
    const [selectedDimension, setSelectedDimension] = useState(null);
    const [showFullExplanation, setShowFullExplanation] = useState(false);
    
    // Parse if it's a string, else use as object
    const data = typeof feedback === 'string' ? JSON.parse(feedback) : feedback;
    
    const parsedData = data.ai_feedback_json 
        ? (typeof data.ai_feedback_json === 'string' ? JSON.parse(data.ai_feedback_json) : data.ai_feedback_json) 
        : data;

    const overallScore = data.overall_score ?? data.score ?? parsedData.score ?? 0;
    const attemptNumber = data.attempt_number ?? 1;
    const improvementPoints = data.improvement_points;
    const aiInsight = data.ai_insight ?? parsedData.overallInsight;
    const dimensions = data.dimensions || {};

    const summary = data.summary ?? parsedData.summary ?? "";
    const strengths = data.strengths ?? parsedData.strengths ?? [];
    const weaknesses = data.weaknesses ?? parsedData.weaknesses ?? [];
    const knowledgeGaps = data.knowledge_gaps ?? parsedData.knowledgeGaps ?? [];
    const correctVersion = data.correct_version ?? parsedData.correct_version ?? "";
    const followUp = data.follow_up_question ?? parsedData.follow_up_question ?? "";
    const nextRecommendation = data.next_recommendation;

    const getScoreColor = (s) => {
        if (s >= 80) return { bg: 'bg-emerald-500', text: 'text-emerald-400', border: 'border-emerald-500/50', glow: 'shadow-emerald-500/20' };
        if (s >= 60) return { bg: 'bg-indigo-500', text: 'text-indigo-400', border: 'border-indigo-500/50', glow: 'shadow-indigo-500/20' };
        if (s >= 40) return { bg: 'bg-amber-500', text: 'text-amber-400', border: 'border-amber-500/50', glow: 'shadow-amber-500/20' };
        return { bg: 'bg-red-500', text: 'text-red-400', border: 'border-red-500/50', glow: 'shadow-red-500/20' };
    };

    const overallStyle = getScoreColor(overallScore);

    return (
        <div className="bg-slate-800 rounded-3xl border border-slate-700 shadow-2xl overflow-hidden animate-in slide-in-from-bottom-8 duration-700 w-full mb-8">
            {/* Header / Overall Score */}
            <div className="p-8 pb-6 bg-gradient-to-br from-slate-900 via-slate-800 to-indigo-950/40 border-b border-slate-700">
                <div className="flex flex-col md:flex-row gap-8 items-center justify-between">
                    <div className="flex-1 text-center md:text-left">
                        <div className="flex items-center justify-center md:justify-start gap-2 text-indigo-400 font-bold text-xs uppercase tracking-widest mb-2">
                            <Sparkles className="w-4 h-4" /> Multi-Dimensional AI Evaluation 2.0
                        </div>
                        <h2 className="text-3xl font-black text-white mb-2">Evaluation Results</h2>
                        <div className="flex items-center justify-center md:justify-start gap-3">
                            <span className="text-xs px-2.5 py-1 rounded-full bg-slate-700 text-slate-300 font-semibold border border-slate-600">
                                Attempt #{attemptNumber}
                            </span>
                            {improvementPoints !== null && improvementPoints !== undefined && (
                                <span className={`text-xs px-2.5 py-1 rounded-full font-bold flex items-center gap-1 border ${
                                    improvementPoints >= 0 
                                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' 
                                        : 'bg-red-500/10 text-red-400 border-red-500/30'
                                }`}>
                                    {improvementPoints >= 0 ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
                                    {improvementPoints >= 0 ? `+${improvementPoints}` : improvementPoints} pts vs last attempt
                                </span>
                            )}
                            {attemptNumber === 1 && (
                                <span className="text-xs px-2.5 py-1 rounded-full bg-indigo-500/10 text-indigo-300 font-medium border border-indigo-500/30">
                                    First Attempt
                                </span>
                            )}
                        </div>
                    </div>
                    
                    {/* Prominent Score Card */}
                    <div className={`flex flex-col items-center justify-center w-36 h-36 rounded-3xl border-4 bg-slate-900/80 shadow-2xl shrink-0 ${overallStyle.border} ${overallStyle.glow}`}>
                        <span className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Overall</span>
                        <span className={`text-5xl font-black ${overallStyle.text}`}>{overallScore}%</span>
                    </div>
                </div>

                {/* AI Summary */}
                {summary && (
                    <div className="mt-6 bg-slate-900/60 rounded-2xl p-5 border border-slate-700/60">
                        <p className="text-slate-200 leading-relaxed text-base">{summary}</p>
                    </div>
                )}

                {/* Longitudinal AI Insight Banner */}
                {aiInsight && (
                    <div className="mt-4 bg-gradient-to-r from-indigo-900/40 via-purple-900/30 to-slate-900 p-4 rounded-xl border border-indigo-500/30 flex items-start gap-3">
                        <Brain className="w-6 h-6 text-indigo-400 shrink-0 mt-0.5" />
                        <div>
                            <div className="text-xs font-bold text-indigo-300 uppercase tracking-wider mb-0.5">📈 AI Longitudinal Progress Insight</div>
                            <p className="text-sm text-slate-200 leading-relaxed">{aiInsight}</p>
                        </div>
                    </div>
                )}
            </div>

            {/* 8 Dimension Breakdown */}
            <div className="p-8 border-b border-slate-700 bg-slate-800/80">
                <h3 className="text-xl font-bold text-slate-100 mb-4 flex items-center gap-2">
                    <Award className="w-5 h-5 text-indigo-400" /> Dimension Breakdown
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
                    {dimensionMeta.map((dim) => {
                        const dimObj = dimensions[dim.key] || {};
                        const dScore = dimObj.score ?? 0;
                        const dFeedback = dimObj.feedback ?? "";
                        const dStyle = getScoreColor(dScore);
                        const isSelected = selectedDimension === dim.key;

                        return (
                            <div 
                                key={dim.key} 
                                onClick={() => setSelectedDimension(isSelected ? null : dim.key)}
                                className={`bg-slate-900/60 p-4 rounded-xl border transition-all cursor-pointer hover:border-indigo-500/60 ${
                                    isSelected ? 'border-indigo-500 ring-2 ring-indigo-500/20' : 'border-slate-700/60'
                                }`}
                            >
                                <div className="flex justify-between items-center mb-1">
                                    <span className="text-xs font-bold text-slate-300">{dim.label}</span>
                                    <span className="text-xs text-slate-500">{dim.weight}</span>
                                </div>
                                <div className="flex items-baseline gap-2 mb-2">
                                    <span className={`text-2xl font-black ${dStyle.text}`}>{dScore}%</span>
                                </div>
                                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden mb-2">
                                    <div 
                                        className={`h-full rounded-full ${dStyle.bg}`} 
                                        style={{ width: `${dScore}%` }} 
                                    />
                                </div>
                                {dFeedback && (
                                    <p className="text-xs text-slate-400 line-clamp-2">{dFeedback}</p>
                                )}
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Main Details Sections */}
            <div className="p-8 bg-slate-800/40">
                {/* Strengths */}
                {strengths && strengths.length > 0 && (
                    <CollapsibleSection title="💪 What You Did Well" icon={CheckCircle2} colorClass="border-l-emerald-500" defaultOpen={true}>
                        <ul className="space-y-3">
                            {strengths.map((str, idx) => (
                                <li key={idx} className="flex gap-3">
                                    <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0 mt-0.5" />
                                    <span className="text-slate-200 leading-relaxed">{str}</span>
                                </li>
                            ))}
                        </ul>
                    </CollapsibleSection>
                )}

                {/* Knowledge Gaps */}
                {knowledgeGaps && knowledgeGaps.length > 0 && (
                    <CollapsibleSection title="🧠 Knowledge Gaps Identified" icon={AlertTriangle} colorClass="border-l-red-500" defaultOpen={true}>
                        <div className="space-y-4">
                            {knowledgeGaps.map((gap, idx) => (
                                <div key={idx} className="bg-red-950/20 rounded-xl p-4 border border-red-500/30">
                                    <div className="flex items-center justify-between mb-1">
                                        <h4 className="font-bold text-red-300 text-sm">{gap.concept}</h4>
                                        <span className="text-[10px] px-2 py-0.5 rounded uppercase font-mono font-bold bg-red-900/40 text-red-400 border border-red-500/30">
                                            {gap.severity} SEVERITY
                                        </span>
                                    </div>
                                    {gap.evidence && (
                                        <p className="text-xs text-slate-300 italic bg-slate-900/60 p-2.5 rounded border border-slate-800 font-mono mt-2">
                                            Evidence: "{gap.evidence}"
                                        </p>
                                    )}
                                </div>
                            ))}
                        </div>
                    </CollapsibleSection>
                )}

                {/* Ideal Answer */}
                {correctVersion && (
                    <CollapsibleSection title="Ideal Answer" icon={BookOpen} colorClass="border-l-indigo-500">
                        <div className="bg-indigo-900/20 rounded-xl p-5 border border-indigo-500/20 italic text-base leading-relaxed text-slate-200">
                            "{correctVersion}"
                        </div>
                    </CollapsibleSection>
                )}

                {/* Follow up Question */}
                {followUp && (
                    <CollapsibleSection title="Follow-up Question" icon={MessageCircle} colorClass="border-l-amber-500" defaultOpen={true}>
                        <div className="bg-amber-900/10 rounded-xl p-5 border border-amber-500/20 text-slate-200 text-base leading-relaxed">
                            {followUp}
                        </div>
                    </CollapsibleSection>
                )}

                {/* Original Explanation */}
                {studentExplanation && (
                    <CollapsibleSection title="Your Original Explanation" icon={FileText} colorClass="border-l-slate-500">
                        <div className="bg-slate-900/80 rounded-xl p-5 border border-slate-700 text-slate-400 font-mono text-sm leading-relaxed whitespace-pre-wrap">
                            {showFullExplanation ? studentExplanation : `${studentExplanation.substring(0, 300)}...`}
                            {studentExplanation.length > 300 && (
                                <button 
                                    onClick={() => setShowFullExplanation(!showFullExplanation)}
                                    className="block mt-4 text-indigo-400 hover:text-indigo-300 font-bold"
                                >
                                    {showFullExplanation ? "Show Less" : "Show Full Explanation"}
                                </button>
                            )}
                        </div>
                    </CollapsibleSection>
                )}
            </div>

            {/* Next Recommended Step */}
            {nextRecommendation && (
                <div className="p-6 bg-gradient-to-r from-indigo-900/60 to-slate-900 border-t border-indigo-500/30 flex flex-col md:flex-row items-center justify-between gap-4">
                    <div>
                        <div className="text-xs font-bold text-indigo-400 uppercase tracking-wider mb-1 flex items-center gap-1">
                            <Zap className="w-3.5 h-3.5" /> Adaptive Engine Recommended Next Action
                        </div>
                        <div className="text-lg font-bold text-white">
                            {nextRecommendation.action_type}: {nextRecommendation.topic_name}
                        </div>
                        <p className="text-xs text-slate-300">{nextRecommendation.reason}</p>
                    </div>
                    <button 
                        onClick={() => navigate(`/study?topic=${nextRecommendation.topic_id}&mode=${nextRecommendation.action_type.toLowerCase()}`)}
                        className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-bold transition-all shrink-0 shadow-lg shadow-indigo-600/20"
                    >
                        Start Next Action
                    </button>
                </div>
            )}

            {/* Footer Buttons */}
            <div className="p-6 bg-slate-900 border-t border-slate-700 flex flex-col sm:flex-row gap-4">
                <button 
                    onClick={onRetry}
                    className="px-6 py-4 bg-slate-800 hover:bg-slate-700 text-white rounded-xl font-medium transition-colors flex items-center justify-center"
                >
                    Retry This Topic
                </button>
                <button 
                    onClick={onContinue}
                    className="flex-1 px-6 py-4 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-bold transition-colors flex items-center justify-center gap-2 shadow-lg hover:shadow-indigo-500/25"
                >
                    Continue Next Topic
                </button>
            </div>
        </div>
    );
};

export default EvaluationFeedback;

