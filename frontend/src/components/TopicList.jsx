import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, ArrowUpRight, AlertCircle, Target, Zap } from 'lucide-react';

const TopicList = ({ topics, type, onSelectTopic }) => {
    // type can be 'weak', 'improved', 'attempted'
    
    if (!topics || topics.length === 0) {
        return (
            <div className="bg-slate-800 p-6 rounded-2xl border border-slate-700 shadow-lg h-full flex flex-col items-center justify-center text-slate-500 min-h-[300px]">
                <Target className="w-12 h-12 mb-4 opacity-50" />
                <p>Not enough data to show insights yet.</p>
                <p className="text-sm mt-2">Complete more evaluations!</p>
            </div>
        );
    }

    const getTitle = () => {
        if (type === 'weak') return "Weak Topics — Time to Focus";
        if (type === 'improved') return "Most Improved Topics";
        return "Most Attempted Topics";
    };
    
    const getIcon = () => {
        if (type === 'weak') return <AlertCircle className="w-5 h-5 text-red-400" />;
        if (type === 'improved') return <ArrowUpRight className="w-5 h-5 text-green-400" />;
        return <Zap className="w-5 h-5 text-yellow-400" />;
    };

    return (
        <div className="bg-slate-800 rounded-2xl border border-slate-700 shadow-lg h-full overflow-hidden flex flex-col">
            <div className="p-6 border-b border-slate-700 flex items-center gap-3">
                {getIcon()}
                <h3 className="text-lg font-bold text-white">{getTitle()}</h3>
            </div>
            <div className="flex-1 overflow-y-auto">
                <ul className="divide-y divide-slate-700/50">
                    {topics.map((t, i) => (
                        <li key={t.topic_id} className="p-4 hover:bg-slate-700/30 transition-colors">
                            <div className="flex justify-between items-start mb-2">
                                <span className="font-semibold text-slate-200">
                                    <span className="text-slate-500 font-mono mr-2">{i + 1}.</span> 
                                    {t.topic_name}
                                </span>
                                {type === 'weak' && (
                                    <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                                        t.avg_score < 5 ? 'bg-red-500/20 text-red-400' :
                                        t.avg_score < 7 ? 'bg-yellow-500/20 text-yellow-400' :
                                        'bg-green-500/20 text-green-400'
                                    }`}>
                                        {t.avg_score}/10
                                    </span>
                                )}
                                {type === 'improved' && (
                                    <span className="px-2 py-0.5 rounded text-xs font-bold bg-green-500/20 text-green-400">
                                        +{t.improvement} pts
                                    </span>
                                )}
                                {type === 'attempted' && (
                                    <span className="px-2 py-0.5 rounded text-xs font-bold bg-indigo-500/20 text-indigo-400">
                                        {t.attempts} attempts
                                    </span>
                                )}
                            </div>
                            
                            {type === 'weak' && (
                                <div className="flex justify-between items-center mt-3">
                                    <span className="text-xs text-slate-400">Best: {t.best_score}/10 ({t.attempts} attempts)</span>
                                    <button 
                                        onClick={() => onSelectTopic(t.topic_id)}
                                        className="text-indigo-400 hover:text-indigo-300 text-xs font-medium flex items-center gap-1 group bg-indigo-500/10 px-3 py-1.5 rounded-full transition-colors"
                                    >
                                        Study This <ArrowRight className="w-3 h-3 group-hover:translate-x-1 transition-transform" />
                                    </button>
                                </div>
                            )}
                            
                            {type === 'improved' && (
                                <div className="mt-2 text-xs text-slate-400 flex items-center gap-2">
                                    <div className="flex-1 bg-slate-900 h-2 rounded-full overflow-hidden flex">
                                        <div className="bg-slate-600 h-full" style={{ width: `${(t.first_score/10)*100}%` }}></div>
                                        <div className="bg-green-500 h-full" style={{ width: `${(t.improvement/10)*100}%` }}></div>
                                    </div>
                                    <span className="w-20 text-right">{t.first_score} → {t.latest_score}</span>
                                </div>
                            )}
                            
                            {type === 'attempted' && (
                                <div className="mt-2 text-xs text-slate-400">
                                    Avg score: <span className="font-medium text-slate-300">{t.average_score}/10</span>
                                </div>
                            )}
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
};

export default TopicList;
