import React from 'react';
import { BookOpen, Target, BrainCircuit, Activity } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const QuickActionBtn = ({ icon: Icon, label, onClick }) => (
    <button 
        onClick={onClick}
        className="flex items-center gap-3 p-4 bg-slate-800/80 hover:bg-slate-700/80 rounded-xl border border-slate-700 hover:border-indigo-500/50 transition-all shadow-md group w-full text-left"
    >
        <div className="p-2 bg-indigo-500/10 text-indigo-400 rounded-lg group-hover:bg-indigo-500 group-hover:text-white transition-colors">
            <Icon className="w-5 h-5" />
        </div>
        <span className="font-medium text-slate-200 group-hover:text-white transition-colors">{label}</span>
    </button>
);

const QuickActions = () => {
    const navigate = useNavigate();

    return (
        <div className="mb-8">
            <h3 className="text-xl font-bold mb-4 text-slate-200">Quick Actions</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <QuickActionBtn icon={BookOpen} label="Explain a Concept" onClick={() => navigate('/syllabi')} />
                <QuickActionBtn icon={Target} label="Practice Weak Topic" onClick={() => navigate('/knowledge-gaps')} />
                <QuickActionBtn icon={BrainCircuit} label="Start Mock Interview" onClick={() => navigate('/interviews')} />
                <QuickActionBtn icon={Activity} label="View Analytics" onClick={() => navigate('/insights')} />
            </div>
        </div>
    );
};

export default QuickActions;
