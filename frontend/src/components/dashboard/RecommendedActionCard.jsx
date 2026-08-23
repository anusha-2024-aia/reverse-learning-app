import React from 'react';
import { Target, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const RecommendedActionCard = ({ action }) => {
    const navigate = useNavigate();

    return (
        <div className="bg-slate-800/80 p-8 rounded-2xl border border-indigo-500/50 shadow-lg flex flex-col justify-between h-full">
            <div>
                <h3 className="text-xl font-bold flex items-center gap-2 mb-6">
                    <Target className="w-6 h-6 text-indigo-400" />
                    🎯 Recommended Next Action
                </h3>
                
                {action && action.has_gap ? (
                    <div className="space-y-4 mb-8">
                        <h4 className="text-2xl font-bold text-white">{action.topic}</h4>
                        <div>
                            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1 block">Why?</span>
                            <p className="text-slate-300">{action.reason}</p>
                        </div>
                        <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700">
                            <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider mb-2 block">Recommended Plan</span>
                            <p className="text-slate-200">{action.recommendation}</p>
                        </div>
                    </div>
                ) : action && action.topic_name ? (
                    <div className="space-y-4 mb-8">
                        <h4 className="text-2xl font-bold text-white">Review {action.topic_name}</h4>
                        <div>
                            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1 block">Why?</span>
                            <p className="text-slate-300">Your mastery score is at {action.mastery_score}%.</p>
                        </div>
                        <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700">
                            <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider mb-2 block">Recommended Plan</span>
                            <p className="text-slate-200">{action.recommendation}</p>
                        </div>
                    </div>
                ) : (
                    <div className="mb-8">
                        <p className="text-slate-400 text-lg">No critical actions pending. Continue your normal learning path or explore a new curriculum.</p>
                    </div>
                )}
            </div>

            <button 
                onClick={() => {
                    if (action && (action.topic_id || action.topic_name)) {
                        navigate('/study', { state: { topicId: action.topic_id } });
                    } else {
                        navigate('/syllabi');
                    }
                }}
                className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-4 rounded-xl transition-colors flex items-center justify-center gap-2 shadow-lg shadow-indigo-500/20"
            >
                Start Practice <ArrowRight className="w-5 h-5" />
            </button>
        </div>
    );
};

export default RecommendedActionCard;
