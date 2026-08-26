import React from 'react';
import { BrainCircuit, MessageSquare, Target, Flame } from 'lucide-react';

const PerformanceCard = ({ title, score, icon: IconComponent, description, metric, metricLabel: _METRIC_LABEL }) => (
    <div className="bg-slate-800/80 p-6 rounded-2xl border border-slate-700 hover:border-indigo-500/30 transition-all flex flex-col justify-between h-full group">
        <div>
            <div className="flex items-center gap-3 mb-4">
                <div className="p-3 bg-slate-900/80 rounded-xl text-indigo-400 group-hover:scale-110 transition-transform">
                    <IconComponent className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-bold text-slate-200">{title}</h3>
            </div>
            
            <div className="flex items-end gap-3 mb-4">
                <div className="text-4xl font-black text-white">{score > 0 ? `${score}%` : 'N/A'}</div>
                {metric && (
                    <div className="text-indigo-400 font-bold mb-1">{metric}</div>
                )}
            </div>
            
            <p className="text-sm text-slate-400">{description}</p>
        </div>
    </div>
);

const PerformanceCards = ({ summary }) => {
    if (!summary) return null;

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <PerformanceCard 
                title="Technical Mastery"
                score={summary.technicalMastery}
                icon={BrainCircuit}
                description="Your understanding of technical concepts."
            />
            <PerformanceCard 
                title="Communication"
                score={summary.communicationScore}
                icon={MessageSquare}
                description="Based on clarity, structure, and vocabulary."
            />
            <PerformanceCard 
                title="Interview Readiness"
                score={summary.interviewReadiness}
                icon={Target}
                description="Based on technical performance and practice."
            />
            <PerformanceCard 
                title="Learning Consistency"
                score={summary.learningConsistency}
                metric={`${summary.streak || 0} day streak`}
                icon={Flame}
                description="Based on your actual learning activity."
            />
        </div>
    );
};

export default PerformanceCards;
