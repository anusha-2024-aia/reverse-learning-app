import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, BookOpen, BrainCircuit, Zap, AlertCircle, ArrowUpRight, Flame, Award, Star, Mic, Target, ListTodo, Activity, TrendingUp } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import api from '../api/axios';

const Dashboard = () => {
    const [curricula, setCurricula] = useState([]);
    const [summary, setSummary] = useState(null);
    const [weakTopics, setWeakTopics] = useState([]);
    const [strongTopics, setStrongTopics] = useState([]);
    const [scoreTrend, setScoreTrend] = useState([]);
    const [aiInsight, setAiInsight] = useState("");
    const [recentInterview, setRecentInterview] = useState(null);
    const [roadmap, setRoadmap] = useState(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        Promise.allSettled([
            api.get('/curricula'),
            api.get('/insights/summary'),
            api.get('/insights/weak-topics'),
            api.get('/interview/history'),
            api.get('/roadmap/mine'),
            api.get('/insights/strong-topics'),
            api.get('/insights/score-trend'),
            api.get('/insights/ai-insight')
        ])
        .then(([curriculaRes, summaryRes, weakTopicsRes, interviewRes, roadmapRes, strongTopicsRes, trendRes, insightRes]) => {
            if (curriculaRes.status === 'fulfilled') setCurricula(curriculaRes.value.data.curricula || []);
            if (summaryRes.status === 'fulfilled') setSummary(summaryRes.value.data);
            if (weakTopicsRes.status === 'fulfilled') setWeakTopics(weakTopicsRes.value.data.weak_topics || []);
            if (interviewRes.status === 'fulfilled' && interviewRes.value.data.length > 0) {
                setRecentInterview(interviewRes.value.data[0]);
            }
            if (roadmapRes.status === 'fulfilled' && roadmapRes.value.data.roadmap_id) {
                setRoadmap(roadmapRes.value.data);
            }
            if (strongTopicsRes.status === 'fulfilled') setStrongTopics(strongTopicsRes.value.data.strong_topics || []);
            if (trendRes.status === 'fulfilled') {
                const rawTrend = trendRes.value.data.trend || [];
                const formattedTrend = rawTrend.map(t => ({ date: t.date, score: Math.round(t.avg_score) }));
                setScoreTrend(formattedTrend);
            }
            if (insightRes.status === 'fulfilled') setAiInsight(insightRes.value.data.insight || "");
            
            setLoading(false);
        })
        .catch(err => {
            console.error(err);
            setLoading(false);
        });
    }, []);

    const calculateRoadmapProgress = () => {
        if (!roadmap || !roadmap.items || roadmap.items.length === 0) return 0;
        const completed = roadmap.items.filter(i => i.status === 'completed').length;
        return Math.round((completed / roadmap.items.length) * 100);
    };

    return (
        <div className="p-8 max-w-7xl mx-auto w-full pb-20">
            <h1 className="text-4xl font-bold mb-8">Your Dashboard</h1>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
                <div className="col-span-full md:col-span-2 bg-gradient-to-br from-indigo-900 to-slate-800 p-8 rounded-2xl border border-indigo-500/30 shadow-xl">
                    <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                        <BrainCircuit className="text-indigo-400" />
                        YOUR NEXT STEP
                    </h2>
                    {weakTopics && weakTopics.length > 0 ? (
                        <p className="text-slate-200 mb-6 max-w-lg text-lg">
                            Practice <strong>{weakTopics[0].topic_name}</strong> — your recent score is {weakTopics[0].average_score}%.
                        </p>
                    ) : (
                        <p className="text-slate-300 mb-6 max-w-lg">
                            Jump back into your last active curriculum or start a new one to continue mastering your skills through reverse learning.
                        </p>
                    )}
                    <button 
                        onClick={() => {
                            if (weakTopics && weakTopics.length > 0) {
                                navigate('/study', { state: { topicId: weakTopics[0].topic_id } });
                            } else {
                                navigate('/syllabi');
                            }
                        }}
                        className="bg-indigo-500 hover:bg-indigo-400 text-white px-6 py-3 rounded-lg font-medium flex items-center gap-2 transition-colors shadow-lg hover:shadow-indigo-500/25"
                    >
                        {weakTopics && weakTopics.length > 0 ? 'Study Weak Topic' : 'View My Syllabi'} <ArrowRight className="w-4 h-4" />
                    </button>
                </div>
                
                {loading ? (
                    <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700 animate-pulse h-48 flex items-center justify-center">
                        <span className="text-slate-500">Loading stats...</span>
                    </div>
                ) : (
                    <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700 flex flex-col justify-center items-center text-center shadow-lg">
                        <h3 className="text-lg font-semibold text-slate-400 mb-2 uppercase tracking-wider text-sm">Learning Streak</h3>
                        <div className="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-red-400 flex items-center gap-2">
                            <Flame className="w-12 h-12 text-orange-500" />
                            {summary?.current_streak || 0}
                        </div>
                        <p className="text-slate-400 mt-2">Days</p>
                    </div>
                )}
            </div>

            {/* Comprehensive Stats Section */}
            {!loading && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
                    {/* Achievements */}
                    <div className="bg-slate-800/80 p-6 rounded-xl border border-slate-700 flex flex-col cursor-pointer hover:bg-slate-800 transition-colors" onClick={() => navigate('/achievements')}>
                        <div className="flex items-center gap-3 mb-4">
                            <div className="bg-yellow-500/20 p-2 rounded-lg">
                                <Award className="w-6 h-6 text-yellow-400" />
                            </div>
                            <h3 className="font-bold text-slate-200">ACHIEVEMENTS</h3>
                        </div>
                        <div className="flex-1 flex flex-col justify-end">
                            <div className="text-2xl font-bold text-white mb-1">Check unlocks</div>
                            <div className="text-sm text-slate-400">View your trophy case</div>
                        </div>
                    </div>

                    {/* Roadmap Progress */}
                    <div className="bg-slate-800/80 p-6 rounded-xl border border-slate-700 flex flex-col cursor-pointer hover:bg-slate-800 transition-colors" onClick={() => navigate('/syllabi')}>
                        <div className="flex items-center gap-3 mb-4">
                            <div className="bg-indigo-500/20 p-2 rounded-lg">
                                <Target className="w-6 h-6 text-indigo-400" />
                            </div>
                            <h3 className="font-bold text-slate-200">ROADMAP</h3>
                        </div>
                        <div className="flex-1 flex flex-col justify-end">
                            <div className="text-3xl font-bold text-white mb-1">{calculateRoadmapProgress()}%</div>
                            <div className="text-sm text-slate-400">Complete</div>
                        </div>
                    </div>

                    {/* Interview Readiness */}
                    <div className="bg-slate-800/80 p-6 rounded-xl border border-slate-700 flex flex-col cursor-pointer hover:bg-slate-800 transition-colors" onClick={() => navigate('/interview')}>
                        <div className="flex items-center gap-3 mb-4">
                            <div className="bg-green-500/20 p-2 rounded-lg">
                                <Activity className="w-6 h-6 text-green-400" />
                            </div>
                            <h3 className="font-bold text-slate-200">INTERVIEW READINESS</h3>
                        </div>
                        <div className="flex-1 flex flex-col justify-end">
                            <div className="text-3xl font-bold text-white mb-1">
                                {recentInterview ? `${recentInterview.overall_score}%` : 'N/A'}
                            </div>
                            <div className="text-sm text-slate-400">Based on recent mocks</div>
                        </div>
                    </div>

                    {/* Voice Communication */}
                    <div className="bg-slate-800/80 p-6 rounded-xl border border-slate-700 flex flex-col cursor-pointer hover:bg-slate-800 transition-colors" onClick={() => navigate('/interview')}>
                        <div className="flex items-center gap-3 mb-4">
                            <div className="bg-purple-500/20 p-2 rounded-lg">
                                <Mic className="w-6 h-6 text-purple-400" />
                            </div>
                            <h3 className="font-bold text-slate-200">VOICE COMMUNICATION</h3>
                        </div>
                        <div className="flex-1 flex flex-col justify-end">
                            <div className="text-3xl font-bold text-white mb-1">
                                {recentInterview ? `${recentInterview.communication_score}%` : 'N/A'}
                            </div>
                            <div className="text-sm text-slate-400">Average clarity score</div>
                        </div>
                    </div>
                </div>
            )}

            {/* AI Learning Insight & Progress Over Time */}
            {!loading && (
                <div className="grid lg:grid-cols-3 gap-8 mb-12">
                    {/* AI Insight Text Block */}
                    <div className="lg:col-span-1 bg-gradient-to-br from-purple-900/40 to-slate-800 p-6 rounded-xl border border-purple-500/30 flex flex-col justify-center">
                        <div className="flex items-center gap-3 mb-4">
                            <Star className="w-6 h-6 text-purple-400" />
                            <h3 className="font-bold text-slate-200">AI LEARNING INSIGHT</h3>
                        </div>
                        <p className="text-slate-300 text-lg leading-relaxed">
                            {aiInsight || "Complete more evaluations to receive personalized AI learning insights."}
                        </p>
                    </div>

                    {/* Progress Over Time Chart */}
                    <div className="lg:col-span-2 bg-slate-800/80 p-6 rounded-xl border border-slate-700">
                        <h3 className="text-xl font-bold flex items-center gap-2 mb-6">
                            <TrendingUp className="w-5 h-5 text-green-400" />
                            PROGRESS OVER TIME
                        </h3>
                        <div className="h-64 w-full">
                            {scoreTrend && scoreTrend.length > 0 ? (
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={scoreTrend}>
                                        <XAxis dataKey="date" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                                        <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} domain={[0, 100]} />
                                        <Tooltip 
                                            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#f8fafc' }}
                                        />
                                        <Line type="monotone" dataKey="score" stroke="#4ade80" strokeWidth={3} dot={{ fill: '#4ade80', strokeWidth: 2 }} activeDot={{ r: 8 }} />
                                    </LineChart>
                                </ResponsiveContainer>
                            ) : (
                                <div className="h-full w-full flex items-center justify-center">
                                    <span className="text-slate-500">Not enough data to map progress yet.</span>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* Split View for Recent Mocks, Weak Topics, and Strong Topics */}
            {!loading && (
                <div className="grid lg:grid-cols-3 gap-8 mb-12">
                    {/* Weak Topics */}
                    <div className="bg-slate-800/80 p-6 rounded-xl border border-slate-700">
                        <div className="flex items-center justify-between mb-6">
                            <h3 className="text-xl font-bold flex items-center gap-2">
                                <AlertCircle className="w-5 h-5 text-red-400" />
                                WEAK TOPICS
                            </h3>
                            <button onClick={() => navigate('/insights')} className="text-sm text-indigo-400 hover:text-indigo-300">View All</button>
                        </div>
                        {weakTopics && weakTopics.length > 0 ? (
                            <div className="space-y-3">
                                {weakTopics.slice(0, 3).map((topic, i) => (
                                    <div 
                                        key={i} 
                                        onClick={() => navigate('/study', { state: { topicId: topic.topic_id } })}
                                        className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg cursor-pointer hover:bg-slate-900 transition-colors border border-transparent hover:border-slate-700"
                                    >
                                        <span className="font-medium text-slate-200">{topic.topic_name}</span>
                                        <span className="text-red-400 font-bold flex items-center gap-2">
                                            {topic.average_score}% <ArrowRight className="w-4 h-4 opacity-50" />
                                        </span>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-slate-400">No weak topics identified yet. Keep practicing!</p>
                        )}
                    </div>

                    {/* Recent Mock Interview */}
                    <div className="bg-slate-800/80 p-6 rounded-xl border border-slate-700">
                        <div className="flex items-center justify-between mb-6">
                            <h3 className="text-xl font-bold flex items-center gap-2">
                                <ListTodo className="w-5 h-5 text-blue-400" />
                                RECENT MOCK INTERVIEW
                            </h3>
                            <button onClick={() => navigate('/interview')} className="text-sm text-indigo-400 hover:text-indigo-300">New Mock</button>
                        </div>
                        {recentInterview ? (
                            <div className="space-y-4">
                                <div className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg">
                                    <span className="text-slate-300">Technical</span>
                                    <span className="font-bold text-white">{recentInterview.technical_score}%</span>
                                </div>
                                <div className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg">
                                    <span className="text-slate-300">Communication</span>
                                    <span className="font-bold text-white">{recentInterview.communication_score}%</span>
                                </div>
                                <div className="flex items-center justify-between p-3 bg-slate-900/50 border border-indigo-500/30 rounded-lg shadow-inner">
                                    <span className="text-indigo-300 font-bold">Overall Score</span>
                                    <span className="font-bold text-indigo-400 text-lg">{recentInterview.overall_score}%</span>
                                </div>
                            </div>
                        ) : (
                            <p className="text-slate-400">No recent mock interviews found. Start one to see your readiness!</p>
                        )}
                    </div>

                    {/* Strongest Topics */}
                    <div className="bg-slate-800/80 p-6 rounded-xl border border-slate-700">
                        <div className="flex items-center justify-between mb-6">
                            <h3 className="text-xl font-bold flex items-center gap-2">
                                <Star className="w-5 h-5 text-yellow-400" />
                                STRONGEST TOPICS
                            </h3>
                        </div>
                        {strongTopics && strongTopics.length > 0 ? (
                            <div className="space-y-3">
                                {strongTopics.slice(0, 3).map((topic, i) => (
                                    <div 
                                        key={i} 
                                        className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg border border-transparent"
                                    >
                                        <span className="font-medium text-slate-200">{topic.topic_name}</span>
                                        <span className="text-green-400 font-bold flex items-center gap-2">
                                            {topic.average_score}%
                                        </span>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-slate-400">No strong topics identified yet. Keep going!</p>
                        )}
                    </div>
                </div>
            )}

            {/* Available Curricula */}
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
