import React from 'react';

const CurriculumProgressBar = ({ curr }) => {
    const progressPercent = curr.total_topics > 0 ? Math.round((curr.completed_topics / curr.total_topics) * 100) : 0;
    
    return (
        <div className="mb-6 last:mb-0">
            <div className="flex justify-between items-end mb-2">
                <div>
                    <h4 className="font-bold text-slate-200">{curr.curriculum_name}</h4>
                    <span className="text-xs text-slate-400">{curr.completed_topics}/{curr.total_topics} topics completed (Avg: {curr.average_score})</span>
                </div>
                <span className="text-indigo-400 font-bold text-sm">{progressPercent}%</span>
            </div>
            <div className="w-full bg-slate-900 rounded-full h-2.5 overflow-hidden">
                <div 
                    className="bg-gradient-to-r from-indigo-500 to-blue-400 h-2.5 rounded-full transition-all duration-1000 ease-out" 
                    style={{ width: `${progressPercent}%` }}
                ></div>
            </div>
        </div>
    );
};

export default CurriculumProgressBar;
