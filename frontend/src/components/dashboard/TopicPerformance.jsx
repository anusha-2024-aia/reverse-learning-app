import React from 'react';
import { ArrowRight, Star, AlertCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const TopicBar = ({ topic, score, isStrong, onClick }) => {
    return (
        <div 
            onClick={onClick}
            className="flex flex-col p-3 bg-slate-900/50 rounded-lg cursor-pointer hover:bg-slate-900 transition-colors border border-transparent hover:border-slate-700"
        >
            <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-slate-200">{topic}</span>
                <span className={`font-bold flex items-center gap-2 ${isStrong ? 'text-green-400' : 'text-red-400'}`}>
                    {score}% <ArrowRight className="w-4 h-4 opacity-50" />
                </span>
            </div>
            
            <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                <div 
                    className={`h-full rounded-full ${isStrong ? 'bg-green-500' : 'bg-red-500'}`} 
                    style={{ width: `${score}%` }}
                ></div>
            </div>
        </div>
    );
};

const TopicPerformance = ({ strongest, weakest }) => {
    const navigate = useNavigate();

    return (
        <div className="grid lg:grid-cols-2 gap-8 mb-8">
            <div className="bg-slate-800/80 p-6 rounded-2xl border border-slate-700">
                <div className="flex items-center justify-between mb-6">
                    <h3 className="text-xl font-bold flex items-center gap-2">
                        <Star className="w-5 h-5 text-yellow-400" />
                        💪 Your Strongest Topics
                    </h3>
                </div>
                {strongest && strongest.length > 0 ? (
                    <div className="space-y-3">
                        {strongest.slice(0, 3).map((topic, i) => (
                            <TopicBar 
                                key={i} 
                                topic={topic.topic_name} 
                                score={topic.avg_score || topic.score} 
                                isStrong={true}
                                onClick={() => navigate('/study', { state: { topicId: topic.topic_id } })}
                            />
                        ))}
                    </div>
                ) : (
                    <p className="text-slate-400">Complete more evaluations to discover your strengths.</p>
                )}
            </div>

            <div className="bg-slate-800/80 p-6 rounded-2xl border border-slate-700">
                <div className="flex items-center justify-between mb-6">
                    <h3 className="text-xl font-bold flex items-center gap-2">
                        <AlertCircle className="w-5 h-5 text-red-400" />
                        ⚠️ Topics That Need Attention
                    </h3>
                    <button onClick={() => navigate('/knowledge-gaps')} className="text-sm text-indigo-400 hover:text-indigo-300">View All</button>
                </div>
                {weakest && weakest.length > 0 ? (
                    <div className="space-y-3">
                        {weakest.slice(0, 3).map((topic, i) => (
                            <TopicBar 
                                key={i} 
                                topic={topic.topic_name} 
                                score={topic.avg_score || topic.score} 
                                isStrong={false}
                                onClick={() => navigate('/study', { state: { topicId: topic.topic_id } })}
                            />
                        ))}
                    </div>
                ) : (
                    <p className="text-slate-400">No weak topics identified yet. Keep practicing!</p>
                )}
            </div>
        </div>
    );
};

export default TopicPerformance;
