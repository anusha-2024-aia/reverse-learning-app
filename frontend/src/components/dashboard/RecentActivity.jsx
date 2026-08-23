import React from 'react';
import { Clock, CheckCircle2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const RecentActivity = ({ activity }) => {
    const navigate = useNavigate();

    return (
        <div className="bg-slate-800/80 p-6 rounded-2xl border border-slate-700 h-full flex flex-col">
            <h3 className="text-xl font-bold flex items-center gap-2 mb-6">
                <Clock className="w-5 h-5 text-blue-400" />
                🕒 Recent Activity
            </h3>
            
            <div className="flex-1 space-y-4">
                {activity && activity.length > 0 ? (
                    activity.map((item, i) => {
                        const date = new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                        return (
                            <div 
                                key={i}
                                className="flex items-start gap-4 p-3 bg-slate-900/40 rounded-xl hover:bg-slate-900 transition-colors border border-transparent hover:border-slate-700 cursor-pointer"
                                onClick={() => navigate(item.type === 'interview' ? '/interviews' : '/insights')}
                            >
                                <div className="mt-1">
                                    <CheckCircle2 className="w-5 h-5 text-green-400" />
                                </div>
                                <div className="flex-1">
                                    <div className="flex items-center justify-between">
                                        <p className="text-xs text-slate-400 font-medium mb-1">{date}</p>
                                        <span className="text-xs font-bold bg-slate-800 px-2 py-0.5 rounded text-indigo-300">
                                            Score: {item.score}%
                                        </span>
                                    </div>
                                    <p className="text-sm font-medium text-slate-200">{item.title}</p>
                                </div>
                            </div>
                        )
                    })
                ) : (
                    <div className="h-full w-full flex items-center justify-center py-8">
                        <span className="text-slate-500">No recent activity. Start learning!</span>
                    </div>
                )}
            </div>
        </div>
    );
};

export default RecentActivity;
