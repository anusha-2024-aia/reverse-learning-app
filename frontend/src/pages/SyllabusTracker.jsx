import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle2, Circle, ArrowRight, PlayCircle, Loader2, ChevronDown, ChevronUp } from 'lucide-react';
import api from '../api/axios';

const SyllabusTracker = () => {
    const [curricula, setCurricula] = useState([]);
    const [expandedCurricula, setExpandedCurricula] = useState({});
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchProgress = async () => {
            try {
                // Fetch all curricula
                const res = await api.get('/curricula');
                const data = res.data;
                
                // Fetch progress for each
                const progressPromises = data.curricula.map(async (c) => {
                    const progRes = await api.get(`/curricula/${c.id}/progress`);
                    const progData = progRes.data;
                    
                    const completedTopics = progData.topics.filter(t => t.best_score !== null).length;
                    const totalTopics = progData.topics.length;
                    const progressPercent = totalTopics > 0 ? Math.round((completedTopics / totalTopics) * 100) : 0;
                    
                    return {
                        ...c,
                        progressPercent,
                        completedTopics,
                        totalTopics,
                        topics: progData.topics
                    };
                });
                
                const curriculaWithProgress = await Promise.all(progressPromises);
                setCurricula(curriculaWithProgress);
            } catch (err) {
                console.error("Failed to fetch progress", err);
            } finally {
                setLoading(false);
            }
        };
        
        fetchProgress();
    }, []);

    const startStudying = (curriculumId, topicId = null) => {
        navigate('/study', { state: { curriculumId, topicId } });
    };

    const toggleExpand = (curriculumId) => {
        setExpandedCurricula(prev => ({
            ...prev,
            [curriculumId]: !prev[curriculumId]
        }));
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[50vh]">
                <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
            </div>
        );
    }

    return (
        <div className="p-8 max-w-5xl mx-auto w-full">
            <h1 className="text-4xl font-bold mb-8">Your Syllabi & Progress</h1>
            
            <div className="space-y-8">
                {curricula.map(c => (
                    <div key={c.id} className="bg-slate-800 rounded-2xl border border-slate-700 overflow-hidden shadow-lg">
                        <div 
                            className="p-6 border-b border-slate-700 bg-slate-800/80 cursor-pointer hover:bg-slate-700/50 transition-colors"
                            onClick={() => toggleExpand(c.id)}
                        >
                            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
                                <div className="flex items-center gap-3">
                                    {expandedCurricula[c.id] ? (
                                        <ChevronUp className="w-6 h-6 text-slate-400" />
                                    ) : (
                                        <ChevronDown className="w-6 h-6 text-slate-400" />
                                    )}
                                    <div>
                                        <h2 className="text-2xl font-bold text-white mb-1">{c.name}</h2>
                                        <p className="text-sm text-slate-400">{c.description}</p>
                                    </div>
                                </div>
                                <button 
                                    onClick={(e) => {
                                        e.stopPropagation(); // Prevent accordion from toggling when clicking start
                                        startStudying(c.id);
                                    }}
                                    className="bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-2 rounded-lg font-medium flex items-center justify-center gap-2 transition-colors whitespace-nowrap"
                                >
                                    <PlayCircle className="w-5 h-5" /> Start Studying
                                </button>
                            </div>
                            
                            {/* Progress Bar */}
                            <div className="space-y-2">
                                <div className="flex justify-between text-sm font-medium">
                                    <span className="text-slate-300">Overall Progress</span>
                                    <span className="text-indigo-400">{c.progressPercent}% ({c.completedTopics}/{c.totalTopics})</span>
                                </div>
                                <div className="w-full bg-slate-700 rounded-full h-2.5 overflow-hidden">
                                    <div 
                                        className="bg-gradient-to-r from-indigo-500 to-blue-400 h-2.5 rounded-full transition-all duration-1000 ease-out" 
                                        style={{ width: `${c.progressPercent}%` }}
                                    ></div>
                                </div>
                            </div>
                        </div>
                        
                        {expandedCurricula[c.id] && (
                            <div className="p-0 animate-in slide-in-from-top-2 duration-200">
                                <table className="w-full text-left text-sm">
                                    <tbody>
                                        {c.topics.map((t, idx) => (
                                            <tr key={t.id} className="border-b border-slate-700/50 hover:bg-slate-700/30 transition-colors">
                                                <td className="py-4 px-6 w-12 text-center text-slate-500 font-mono">{idx + 1}</td>
                                                <td className="py-4 px-4 font-medium text-slate-200">
                                                    <div className="flex items-center gap-3">
                                                        {t.best_score !== null ? (
                                                            <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0" />
                                                        ) : (
                                                            <Circle className="w-5 h-5 text-slate-600 flex-shrink-0" />
                                                        )}
                                                        {t.name}
                                                    </div>
                                                </td>
                                                <td className="py-4 px-4 text-right">
                                                    {t.best_score !== null ? (
                                                        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-900 border border-slate-700">
                                                            <span className="text-xs font-bold text-slate-400 uppercase">Score:</span>
                                                            <span className={`font-black ${t.best_score >= 8 ? 'text-green-400' : t.best_score >= 5 ? 'text-yellow-400' : 'text-red-400'}`}>
                                                                {t.best_score}/10
                                                            </span>
                                                        </span>
                                                    ) : (
                                                        <span className="text-slate-500 text-sm italic">Not attempted</span>
                                                    )}
                                                </td>
                                                <td className="py-4 px-6 text-right w-32">
                                                    <button 
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            startStudying(c.id, t.id);
                                                        }}
                                                        className="text-indigo-400 hover:text-indigo-300 font-medium text-sm flex items-center gap-1 justify-end w-full group"
                                                    >
                                                        Study <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default SyllabusTracker;
