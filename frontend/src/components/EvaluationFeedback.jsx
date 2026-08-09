import React, { useState } from 'react';
import { CheckCircle2, AlertTriangle, BookOpen, Target, MessageCircle, Code, ChevronDown, ChevronRight, FileText } from 'lucide-react';

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
    const [showFullExplanation, setShowFullExplanation] = useState(false);
    
    // Parse if it's a string, else use as object
    const data = typeof feedback === 'string' ? JSON.parse(feedback) : feedback;
    
    // Helper to extract nested json if needed (depending on how backend sends it)
    const parsedData = data.ai_feedback_json 
        ? (typeof data.ai_feedback_json === 'string' ? JSON.parse(data.ai_feedback_json) : data.ai_feedback_json) 
        : data;

    const score = data.score ?? parsedData.score ?? 0;
    const summary = data.summary ?? parsedData.summary ?? "";
    const strengths = data.strengths ?? parsedData.strengths ?? [];
    const weaknesses = data.weaknesses ?? parsedData.weaknesses ?? [];
    const correctVersion = data.correct_version ?? parsedData.correct_version ?? "";
    const followUp = data.follow_up_question ?? parsedData.follow_up_question ?? "";
    const learningSuggestions = data.learning_suggestions ?? parsedData.learning_suggestions ?? [];
    const feedbackSections = data.feedback_sections ?? parsedData.feedback_sections ?? [];

    const getScoreColor = (s) => {
        if (s >= 8) return { border: '#10b981', text: 'text-emerald-400', glow: 'shadow-emerald-500/20' };
        if (s >= 5) return { border: '#f59e0b', text: 'text-amber-400', glow: 'shadow-amber-500/20' };
        return { border: '#ef4444', text: 'text-red-400', glow: 'shadow-red-500/20' };
    };

    const scoreStyle = getScoreColor(score);

    return (
        <div className="bg-slate-800 rounded-3xl border border-slate-700 shadow-2xl overflow-hidden animate-in slide-in-from-bottom-8 duration-700 w-full mb-8">
            {/* Header / Top Section */}
            <div className="p-8 pb-6 bg-slate-800/80 border-b border-slate-700">
                <div className="flex flex-col md:flex-row gap-8 items-start justify-between">
                    <div className="flex-1">
                        <h2 className="text-3xl font-black text-white mb-6 flex items-center gap-3">
                            <Target className="w-8 h-8 text-indigo-400" />
                            Evaluation Results
                        </h2>
                        {summary && (
                            <div className="bg-slate-900/40 rounded-2xl p-6 border border-slate-700/50">
                                <h3 className="text-lg font-bold text-slate-300 mb-3 border-b border-slate-700 pb-2">Smart Summary</h3>
                                <p className="text-slate-300 leading-relaxed text-lg">{summary}</p>
                            </div>
                        )}
                    </div>
                    
                    <div className={`flex flex-col items-center justify-center w-32 h-32 rounded-full border-4 shadow-xl shrink-0 bg-slate-900/50 ${scoreStyle.glow}`}
                         style={{ borderColor: scoreStyle.border }}>
                        <span className={`text-5xl font-black ${scoreStyle.text}`}>{score}</span>
                        <span className="text-sm text-slate-400 font-bold uppercase tracking-widest block -mt-1">/ 10</span>
                    </div>
                </div>
            </div>

            {/* Collapsible Sections */}
            <div className="p-8 bg-slate-800/50">
                
                {strengths && strengths.length > 0 && (
                    <CollapsibleSection title="Strengths" icon={CheckCircle2} colorClass="border-l-emerald-500" defaultOpen={true}>
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

                {weaknesses && weaknesses.length > 0 && (
                    <CollapsibleSection title="Areas to Improve" icon={AlertTriangle} colorClass="border-l-red-500" defaultOpen={true}>
                        <ul className="space-y-3">
                            {weaknesses.map((weak, idx) => (
                                <li key={idx} className="flex gap-3">
                                    <AlertTriangle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
                                    <span className="text-slate-200 leading-relaxed">{weak}</span>
                                </li>
                            ))}
                        </ul>
                    </CollapsibleSection>
                )}

                {correctVersion && (
                    <CollapsibleSection title="Ideal Answer" icon={BookOpen} colorClass="border-l-indigo-500">
                        <div className="bg-indigo-900/20 rounded-xl p-5 border border-indigo-500/20 italic text-lg leading-relaxed text-slate-200">
                            "{correctVersion}"
                        </div>
                    </CollapsibleSection>
                )}

                {feedbackSections && feedbackSections.length > 0 && (
                    <CollapsibleSection title="Detailed Feedback" icon={Code} colorClass="border-l-cyan-500">
                        <div className="grid md:grid-cols-2 gap-4">
                            {feedbackSections.map((section, idx) => (
                                <div key={idx} className="bg-slate-900/50 rounded-xl p-5 border border-slate-700/50">
                                    <h4 className="text-cyan-400 font-bold text-sm uppercase tracking-wider mb-2">{section.title}</h4>
                                    <p className="text-slate-300 leading-relaxed">{section.content}</p>
                                </div>
                            ))}
                        </div>
                    </CollapsibleSection>
                )}

                {learningSuggestions && learningSuggestions.length > 0 && (
                    <CollapsibleSection title="Recommended Learning Path" icon={Target} colorClass="border-l-fuchsia-500">
                        <ul className="space-y-2">
                            {learningSuggestions.map((sugg, idx) => (
                                <li key={idx} className="flex items-center gap-3 p-3 bg-slate-900/40 rounded-lg border border-slate-700/30">
                                    <div className="w-2 h-2 rounded-full bg-fuchsia-500"></div>
                                    <span className="text-slate-200">{sugg}</span>
                                </li>
                            ))}
                        </ul>
                    </CollapsibleSection>
                )}

                {followUp && (
                    <CollapsibleSection title="Follow-up Question" icon={MessageCircle} colorClass="border-l-amber-500" defaultOpen={true}>
                        <div className="bg-amber-900/10 rounded-xl p-5 border border-amber-500/20 text-slate-200 text-lg leading-relaxed">
                            {followUp}
                        </div>
                    </CollapsibleSection>
                )}

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
