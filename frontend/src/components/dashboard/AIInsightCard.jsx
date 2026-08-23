import React from 'react';
import { Sparkles } from 'lucide-react';

const AIInsightCard = ({ insight }) => {
    return (
        <div className="bg-gradient-to-br from-purple-900/40 to-slate-800 p-6 rounded-2xl border border-purple-500/30 flex flex-col justify-center h-full">
            <div className="flex items-center gap-3 mb-4">
                <Sparkles className="w-6 h-6 text-purple-400" />
                <h3 className="font-bold text-slate-200 uppercase tracking-wider text-sm">✨ AI Learning Insight</h3>
            </div>
            {insight && insight.text ? (
                <p className="text-slate-300 text-lg leading-relaxed font-medium">
                    {insight.text}
                </p>
            ) : (
                <p className="text-slate-500 italic">
                    AI insight is temporarily unavailable.
                </p>
            )}
        </div>
    );
};

export default AIInsightCard;
