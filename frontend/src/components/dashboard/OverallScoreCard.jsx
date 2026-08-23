import React from 'react';
import { TrendingUp } from 'lucide-react';

const OverallScoreCard = ({ score }) => {
    return (
        <div className="bg-gradient-to-br from-indigo-900 to-slate-800 p-8 rounded-2xl border border-indigo-500/30 shadow-xl mb-8 flex flex-col justify-center items-center text-center">
            <h2 className="text-xl font-bold text-slate-300 mb-6 uppercase tracking-wider">Overall Learning Score</h2>
            
            {score > 0 ? (
                <>
                    <div className="text-7xl font-black text-white mb-4 drop-shadow-lg">
                        {score}<span className="text-4xl text-indigo-400">%</span>
                    </div>
                    <div className="flex items-center gap-2 text-green-400 bg-green-500/10 px-4 py-2 rounded-full font-bold mb-4">
                        <TrendingUp className="w-5 h-5" /> Based on your latest evaluations
                    </div>
                    <p className="text-slate-300">Keep practicing to boost your overall intelligence score.</p>
                </>
            ) : (
                <div className="py-8">
                    <p className="text-slate-400 text-lg mb-2">Not enough data yet</p>
                    <p className="text-slate-500">Complete your first evaluation to generate your learning score.</p>
                </div>
            )}
        </div>
    );
};

export default OverallScoreCard;
