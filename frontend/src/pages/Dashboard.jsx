import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, BookOpen, BrainCircuit, Zap, AlertCircle, ArrowUpRight, Flame, Award, Star } from 'lucide-react';

const Dashboard = () => {
    const [curricula, setCurricula] = useState([]);
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        Promise.all([
            fetch('http://localhost:8000/api/curricula').then(res => res.json()),
            fetch('http://localhost:8000/api/insights/summary').then(res => res.json())
        ])
        .then(([curriculaData, summaryData]) => {
            setCurricula(curriculaData.curricula || []);
            setSummary(summaryData);
            setLoading(false);
        })
        .catch(err => {
            console.error(err);
            setLoading(false);
        });
    }, []);

    return (
        <div className="p-8 max-w-7xl mx-auto w-full pb-20">
            <h1 className="text-4xl font-bold mb-8">Your Dashboard</h1>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="col-span-full md:col-span-2 bg-gradient-to-br from-indigo-900 to-slate-800 p-8 rounded-2xl border border-indigo-500/30 shadow-xl">
                    <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                        <BrainCircuit className="text-indigo-400" />
                        Continue Learning
                    </h2>
                    <p className="text-slate-300 mb-6 max-w-lg">
                        Jump back into your last active curriculum or start a new one to continue mastering your skills through reverse learning.
                    </p>
                    <button 
                        onClick={() => navigate('/syllabi')}
                        className="bg-indigo-500 hover:bg-indigo-400 text-white px-6 py-3 rounded-lg font-medium flex items-center gap-2 transition-colors shadow-lg hover:shadow-indigo-500/25"
                    >
                        View My Syllabi <ArrowRight className="w-4 h-4" />
                    </button>
                </div>
                
                {loading ? (
                    <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700 animate-pulse h-48 flex items-center justify-center">
                        <span className="text-slate-500">Loading stats...</span>
                    </div>
                ) : (
                    <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700 flex flex-col justify-center items-center text-center shadow-lg">
                        <h3 className="text-lg font-semibold text-slate-400 mb-2 uppercase tracking-wider text-sm">Curricula Available</h3>
                        <div className="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-blue-400">
                            {curricula.length}
                        </div>
                    </div>
                )}
            </div>

            {/* Highlights Section */}
            {!loading && summary && (
                <div className="mt-12 mb-6">
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-2xl font-bold flex items-center gap-2">
                            <Zap className="w-6 h-6 text-yellow-400" />
                            Activity & Achievements
                        </h2>
                        <button 
                            onClick={() => navigate('/achievements')}
                            className="text-indigo-400 hover:text-indigo-300 text-sm font-medium flex items-center gap-1 transition-colors group"
                        >
                            View All Achievements <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                        </button>
                    </div>
                    
                    <div className="grid md:grid-cols-3 gap-6">
                        <div className="bg-slate-800/80 p-6 rounded-xl border border-slate-700 flex items-start gap-4">
                            <div className="bg-orange-500/20 p-3 rounded-full">
                                <Flame className="w-6 h-6 text-orange-400" />
                            </div>
                            <div>
                                <h4 className="text-slate-400 text-sm font-bold uppercase tracking-wider mb-1">Current Streak</h4>
                                <p className="text-white font-medium text-lg">{summary.current_streak} Days</p>
                                <p className="text-xs text-slate-500 mt-1">Keep the momentum going!</p>
                            </div>
                        </div>
                        
                        <div className="bg-slate-800/80 p-6 rounded-xl border border-slate-700 flex items-start gap-4">
                            <div className="bg-indigo-500/20 p-3 rounded-full">
                                <Award className="w-6 h-6 text-indigo-400" />
                            </div>
                            <div>
                                <h4 className="text-slate-400 text-sm font-bold uppercase tracking-wider mb-1">Evaluations</h4>
                                <p className="text-white font-medium text-lg">{summary.total_evaluations} Completed</p>
                                <p className="text-xs text-slate-500 mt-1">Practice makes perfect</p>
                            </div>
                        </div>
                        
                        <div className="bg-slate-800/80 p-6 rounded-xl border border-slate-700 flex items-start gap-4 cursor-pointer hover:bg-slate-800 transition-colors" onClick={() => navigate('/achievements')}>
                            <div className="bg-yellow-500/20 p-3 rounded-full">
                                <Star className="w-6 h-6 text-yellow-400" />
                            </div>
                            <div>
                                <h4 className="text-slate-400 text-sm font-bold uppercase tracking-wider mb-1">Badges</h4>
                                <p className="text-white font-medium text-lg">Check unlocks</p>
                                <p className="text-xs text-slate-500 mt-1">View your trophy case</p>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            <h2 className="text-2xl font-bold mt-12 mb-6 flex items-center gap-2">
                <BookOpen className="w-6 h-6 text-indigo-400" />
                Available Curricula
            </h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {curricula.map(c => (
                    <div key={c.id} className="bg-slate-800/80 backdrop-blur p-6 rounded-xl border border-slate-700 hover:border-indigo-500/50 transition-all hover:-translate-y-1 hover:shadow-xl cursor-pointer flex flex-col" onClick={() => navigate('/syllabi')}>
                        <h3 className="text-xl font-bold mb-2 text-white">{c.name}</h3>
                        <p className="text-sm text-slate-400 mb-6 flex-1">{c.description}</p>
                        <div className="flex items-center justify-between pt-4 border-t border-slate-700/50">
                            <span className={`px-2 py-1 rounded text-xs font-black uppercase tracking-wider
                                ${c.difficulty === 'beginner' ? 'bg-green-500/20 text-green-400' : 
                                  c.difficulty === 'intermediate' ? 'bg-yellow-500/20 text-yellow-400' : 
                                  'bg-red-500/20 text-red-400'}`}>
                                {c.difficulty}
                            </span>
                            <span className="text-sm text-indigo-400 font-medium flex items-center gap-1 bg-indigo-500/10 px-2 py-1 rounded">
                                <BookOpen className="w-3 h-3" /> {c.topic_count} Topics
                            </span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Dashboard;
