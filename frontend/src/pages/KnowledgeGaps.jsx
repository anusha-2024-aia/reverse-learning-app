import React, { useState, useEffect } from 'react';
import { ShieldAlert, TrendingUp, TrendingDown, Target, BookOpen, AlertTriangle, CheckCircle, BrainCircuit } from 'lucide-react';
import api from '../api/axios';
import { useNavigate } from 'react-router-dom';

const KnowledgeGaps = () => {
    const [gaps, setGaps] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('ALL');
    const navigate = useNavigate();

    useEffect(() => {
        api.get('/knowledge-gaps')
            .then(res => {
                setGaps(res.data.gaps || []);
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setLoading(false);
            });
    }, []);

    const filteredGaps = gaps.filter(gap => {
        if (filter === 'ALL') return true;
        return gap.severity === filter;
    });

    const getSeverityBadge = (severity) => {
        switch (severity) {
            case 'CRITICAL': return <span className="bg-red-500/20 text-red-400 px-3 py-1 rounded-full text-xs font-black tracking-wider flex items-center gap-1"><AlertTriangle className="w-3 h-3"/> CRITICAL</span>;
            case 'HIGH': return <span className="bg-orange-500/20 text-orange-400 px-3 py-1 rounded-full text-xs font-black tracking-wider flex items-center gap-1"><AlertTriangle className="w-3 h-3"/> HIGH</span>;
            case 'MEDIUM': return <span className="bg-yellow-500/20 text-yellow-400 px-3 py-1 rounded-full text-xs font-black tracking-wider flex items-center gap-1"><Target className="w-3 h-3"/> MEDIUM</span>;
            case 'LOW': return <span className="bg-blue-500/20 text-blue-400 px-3 py-1 rounded-full text-xs font-black tracking-wider flex items-center gap-1"><BookOpen className="w-3 h-3"/> LOW</span>;
            case 'RESOLVED': return <span className="bg-green-500/20 text-green-400 px-3 py-1 rounded-full text-xs font-black tracking-wider flex items-center gap-1"><CheckCircle className="w-3 h-3"/> RESOLVED</span>;
            default: return null;
        }
    };

    const getTrendIcon = (trend) => {
        if (trend === 'IMPROVING') return <span className="text-green-400 flex items-center gap-1"><TrendingUp className="w-4 h-4"/> Improving</span>;
        if (trend === 'DECLINING') return <span className="text-red-400 flex items-center gap-1"><TrendingDown className="w-4 h-4"/> Declining</span>;
        return <span className="text-slate-400 flex items-center gap-1">Stable</span>;
    };

    return (
        <div className="p-8 max-w-7xl mx-auto w-full pb-20">
            <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
                <div>
                    <h1 className="text-4xl font-bold flex items-center gap-3">
                        <BrainCircuit className="text-indigo-400 w-10 h-10" />
                        Knowledge Gaps
                    </h1>
                    <p className="text-slate-400 mt-2 text-lg">AI-powered engine detecting your learning blind spots based on historical performance.</p>
                </div>
            </div>

            {/* Filters */}
            <div className="flex flex-wrap gap-2 mb-8">
                {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'RESOLVED'].map(f => (
                    <button 
                        key={f}
                        onClick={() => setFilter(f)}
                        className={`px-4 py-2 rounded-full text-sm font-bold tracking-wider transition-colors border ${
                            filter === f 
                                ? 'bg-indigo-600 border-indigo-500 text-white' 
                                : 'bg-slate-800/50 border-slate-700 text-slate-400 hover:bg-slate-700'
                        }`}
                    >
                        {f}
                    </button>
                ))}
            </div>

            {loading ? (
                <div className="flex justify-center p-12"><div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div></div>
            ) : filteredGaps.length > 0 ? (
                <div className="grid lg:grid-cols-2 gap-6">
                    {filteredGaps.map(gap => (
                        <div key={gap.topic_id} className="bg-slate-800/80 p-6 rounded-xl border border-slate-700 hover:border-indigo-500/30 transition-all flex flex-col h-full">
                            <div className="flex justify-between items-start mb-4">
                                <div>
                                    <h3 className="text-2xl font-bold text-white mb-2">{gap.topic_name}</h3>
                                    <div className="flex items-center gap-4">
                                        {getSeverityBadge(gap.severity)}
                                        {getTrendIcon(gap.trend)}
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className="text-3xl font-black text-indigo-400">{gap.mastery_score}%</div>
                                    <div className="text-xs font-bold tracking-wider text-slate-500 uppercase">Mastery</div>
                                </div>
                            </div>

                            <div className="grid grid-cols-3 gap-4 mb-6 bg-slate-900/50 p-4 rounded-lg">
                                <div>
                                    <div className="text-lg font-bold text-slate-200">{gap.recent_score}%</div>
                                    <div className="text-xs text-slate-400">Latest</div>
                                </div>
                                <div>
                                    <div className="text-lg font-bold text-slate-200">{gap.average_score}%</div>
                                    <div className="text-xs text-slate-400">Average</div>
                                </div>
                                <div>
                                    <div className="text-lg font-bold text-slate-200">{gap.attempts}</div>
                                    <div className="text-xs text-slate-400">Attempts</div>
                                </div>
                            </div>

                            <div className="flex-1 bg-indigo-900/20 border border-indigo-500/20 p-4 rounded-lg mb-6">
                                <h4 className="text-xs font-black text-indigo-300 uppercase tracking-wider mb-2">AI Recommendation</h4>
                                <p className="text-slate-300 text-sm leading-relaxed">{gap.recommendation}</p>
                            </div>

                            <button 
                                onClick={() => navigate('/study', { state: { topicId: gap.topic_id } })}
                                className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-3 rounded-lg transition-colors flex items-center justify-center gap-2"
                            >
                                <Target className="w-4 h-4" /> Resolve Gap
                            </button>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="text-center p-12 bg-slate-800/50 rounded-xl border border-slate-700">
                    <ShieldAlert className="w-16 h-16 text-slate-600 mx-auto mb-4" />
                    <h2 className="text-2xl font-bold text-white mb-2">No gaps found</h2>
                    <p className="text-slate-400 max-w-md mx-auto">
                        {filter === 'ALL' 
                            ? "You don't have enough evaluation data yet. Complete some mock interviews to start mapping your knowledge gaps!"
                            : `You don't currently have any topics flagged with a severity of ${filter}.`}
                    </p>
                    {filter !== 'ALL' && (
                        <button onClick={() => setFilter('ALL')} className="mt-6 text-indigo-400 hover:text-indigo-300 font-bold">
                            View all topics
                        </button>
                    )}
                </div>
            )}
        </div>
    );
};

export default KnowledgeGaps;
