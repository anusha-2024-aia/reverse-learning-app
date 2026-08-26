import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    BarChart2, TrendingUp, Award, CheckCircle2, AlertTriangle,
    Calendar, Sparkles, ArrowRight, Clock, Target, Mic, MessageSquare,
    Layers, Activity, RotateCcw, BookOpen, ChevronRight, Loader2, Play
} from 'lucide-react';
import api from '../api/axios';

const AnalyticsPage = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [range, setRange] = useState('30d');
    const [analytics, setAnalytics] = useState(null);

    const fetchAnalytics = async (selectedRange) => {
        setLoading(true);
        try {
            const res = await api.get(`/analytics?range=${selectedRange}`);
            setAnalytics(res.data);
        } catch (err) {
            console.error("Failed to fetch analytics:", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAnalytics(range);
    }, [range]);

    const handleRangeChange = (newRange) => {
        setRange(newRange);
    };

    if (loading && !analytics) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh]">
                <Loader2 className="w-10 h-10 text-indigo-500 animate-spin mb-4" />
                <p className="text-slate-400 font-medium text-lg">Gathering your learning analytics...</p>
            </div>
        );
    }

    const {
        summary = {},
        scoreTrend = [],
        topicMastery = [],
        strongestTopics = [],
        weakestTopics = [],
        learningActivity = [],
        weeklySummary = {},
        goalProgress = {},
        communicationAnalytics = {},
        interviewPerformance = {},
        revisionStats = {},
        knowledgeGapStats = {},
        aiInsight = {},
        recommendedNextAction = null,
        has_enough_data = false
    } = analytics || {};

    const ranges = [
        { label: '7D', value: '7d' },
        { label: '30D', value: '30d' },
        { label: '3M', value: '90d' },
        { label: '6M', value: '6m' },
        { label: 'All', value: 'all' }
    ];

    return (
        <div className="p-6 md:p-10 max-w-7xl mx-auto w-full pb-24 text-slate-100">
            {/* Header & Subtitle */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-10">
                <div>
                    <h1 className="text-3xl md:text-4xl font-black flex items-center gap-3 text-white tracking-tight">
                        <div className="p-2.5 bg-indigo-600/20 border border-indigo-500/30 rounded-xl text-indigo-400">
                            <BarChart2 className="w-8 h-8" />
                        </div>
                        Learning Analytics
                    </h1>
                    <p className="text-slate-400 mt-2 text-base md:text-lg">
                        Understand your progress, identify your weaknesses, and track your journey toward your career goal.
                    </p>
                </div>

                {/* Date Range Selector Filter */}
                <div className="flex items-center bg-slate-800/90 border border-slate-700 p-1.5 rounded-xl self-start md:self-auto shadow-inner">
                    {ranges.map((r) => (
                        <button
                            key={r.value}
                            onClick={() => handleRangeChange(r.value)}
                            className={`px-3.5 py-1.5 rounded-lg text-sm font-semibold transition-all ${
                                range === r.value
                                    ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50'
                            }`}
                        >
                            {r.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* EMPTY STATE - Brand New User */}
            {!has_enough_data && (
                <div className="bg-gradient-to-br from-slate-800/90 to-indigo-950/40 border border-indigo-500/20 rounded-3xl p-8 md:p-12 text-center mb-10 shadow-2xl backdrop-blur-xl">
                    <div className="w-20 h-20 bg-indigo-600/20 border border-indigo-500/30 rounded-full flex items-center justify-center mx-auto mb-6 text-indigo-400">
                        <Sparkles className="w-10 h-10" />
                    </div>
                    <h2 className="text-2xl md:text-3xl font-bold text-white mb-3">Start Building Your Analytics</h2>
                    <p className="text-slate-400 max-w-xl mx-auto mb-8 text-base md:text-lg">
                        You haven't completed enough learning activities yet. Complete your first concept evaluation, study room session, or mock interview to start seeing your performance insights!
                    </p>
                    <button
                        onClick={() => navigate('/study')}
                        className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold px-8 py-4 rounded-xl shadow-lg shadow-indigo-600/30 transition-all hover:scale-105"
                    >
                        <Play className="w-5 h-5 fill-current" />
                        Start Learning Now
                    </button>
                </div>
            )}

            {/* ROW 1: Summary Cards */}
            <div className="grid grid-cols-2 lg:grid-cols-5 gap-4 md:gap-6 mb-8">
                <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-5 shadow-lg backdrop-blur-md">
                    <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Overall Score</span>
                    <div className="text-3xl md:text-4xl font-black text-white mt-2 flex items-baseline gap-1">
                        {summary.overallScore || 0}<span className="text-indigo-400 text-xl">%</span>
                    </div>
                    <div className="mt-3 flex items-center gap-1 text-xs text-indigo-400 font-medium">
                        <TrendingUp className="w-3.5 h-3.5" /> Calculated dynamically
                    </div>
                </div>

                <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-5 shadow-lg backdrop-blur-md">
                    <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Technical Mastery</span>
                    <div className="text-3xl md:text-4xl font-black text-emerald-400 mt-2 flex items-baseline gap-1">
                        {summary.technicalMastery || 0}<span className="text-emerald-500 text-xl">%</span>
                    </div>
                    <div className="mt-3 text-xs text-slate-400">Evaluation & test performance</div>
                </div>

                <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-5 shadow-lg backdrop-blur-md">
                    <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Communication</span>
                    <div className="text-3xl md:text-4xl font-black text-cyan-400 mt-2 flex items-baseline gap-1">
                        {summary.communicationScore || 0}<span className="text-cyan-500 text-xl">%</span>
                    </div>
                    <div className="mt-3 text-xs text-slate-400">Clarity, pace & structure</div>
                </div>

                <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-5 shadow-lg backdrop-blur-md">
                    <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Interview Readiness</span>
                    <div className="text-3xl md:text-4xl font-black text-purple-400 mt-2 flex items-baseline gap-1">
                        {summary.interviewReadiness || 0}<span className="text-purple-500 text-xl">%</span>
                    </div>
                    <div className="mt-3 text-xs text-slate-400">Mock interview score</div>
                </div>

                <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-5 shadow-lg backdrop-blur-md col-span-2 lg:col-span-1">
                    <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Learning Streak</span>
                    <div className="text-3xl md:text-4xl font-black text-amber-400 mt-2 flex items-baseline gap-1">
                        {summary.learningStreak || 0}<span className="text-amber-500 text-xl"> Days</span>
                    </div>
                    <div className="mt-3 text-xs text-amber-400 font-medium">Consecutive activity</div>
                </div>
            </div>

            {/* ROW 2: Overall Score Trend Line Chart */}
            <div className="bg-slate-800/90 border border-slate-700/90 rounded-2xl p-6 md:p-8 mb-8 shadow-xl">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h2 className="text-xl font-bold text-white flex items-center gap-2">
                            <TrendingUp className="w-5 h-5 text-indigo-400" />
                            Score Trend
                        </h2>
                        <p className="text-slate-400 text-sm mt-1">Historical score progression over time across evaluations and interviews</p>
                    </div>
                </div>

                {scoreTrend && scoreTrend.length > 1 ? (
                    <div className="relative h-64 w-full flex items-end gap-2 md:gap-4 pt-8 pb-4 px-2 border-b border-slate-700/60">
                        {scoreTrend.map((item, idx) => {
                            const val = item.overall || 0;
                            const heightPct = Math.max(10, Math.min(100, val));
                            return (
                                <div key={idx} className="flex-1 flex flex-col items-center group relative h-full justify-end">
                                    {/* Tooltip */}
                                    <div className="absolute -top-12 opacity-0 group-hover:opacity-100 transition-all duration-200 bg-slate-900 border border-slate-700 text-xs text-slate-200 py-1.5 px-3 rounded-lg shadow-xl pointer-events-none whitespace-nowrap z-20">
                                        <div className="font-bold text-indigo-400">{item.date}</div>
                                        <div>Overall: {val}% | Tech: {item.technical}%</div>
                                    </div>
                                    <div className="text-xs font-bold text-indigo-300 mb-2 opacity-80 group-hover:opacity-100">
                                        {val}%
                                    </div>
                                    <div
                                        style={{ height: `${heightPct}%` }}
                                        className="w-full bg-gradient-to-t from-indigo-600/40 via-indigo-500 to-indigo-400 rounded-t-lg transition-all duration-300 group-hover:brightness-125 group-hover:shadow-lg group-hover:shadow-indigo-500/20"
                                    />
                                    <span className="text-[11px] text-slate-400 mt-2 font-medium truncate max-w-full">
                                        {item.date}
                                    </span>
                                </div>
                            );
                        })}
                    </div>
                ) : (
                    <div className="py-12 text-center text-slate-400 border border-dashed border-slate-700/60 rounded-xl">
                        <Activity className="w-8 h-8 text-slate-500 mx-auto mb-2" />
                        <p className="font-medium text-slate-300">Complete more evaluations to see your progress trend.</p>
                        <p className="text-xs text-slate-500 mt-1">Requires at least 2 learning evaluations or interviews.</p>
                    </div>
                )}
            </div>

            {/* ROW 3: Topic Mastery & Learning Activity */}
            <div className="grid lg:grid-cols-2 gap-8 mb-8">
                {/* Topic Mastery Horizontal Bars */}
                <div className="bg-slate-800/90 border border-slate-700/90 rounded-2xl p-6 md:p-8 shadow-xl">
                    <h2 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
                        <Layers className="w-5 h-5 text-emerald-400" />
                        Topic Mastery
                    </h2>
                    <p className="text-slate-400 text-sm mb-6">Calculated from AI evaluations & knowledge gap performance</p>

                    {topicMastery && topicMastery.length > 0 ? (
                        <div className="space-y-4">
                            {topicMastery.map((topic, idx) => (
                                <div key={idx} className="bg-slate-900/60 border border-slate-700/50 rounded-xl p-3.5">
                                    <div className="flex justify-between items-center mb-1.5 text-sm">
                                        <span className="font-bold text-white">{topic.topic_name}</span>
                                        <div className="flex items-center gap-2">
                                            <span className={`text-xs px-2 py-0.5 rounded font-semibold ${
                                                topic.mastery_score >= 80 ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' :
                                                topic.mastery_score >= 65 ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30' :
                                                'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                                            }`}>
                                                {topic.status}
                                            </span>
                                            <span className="font-black text-emerald-400">{topic.mastery_score}%</span>
                                        </div>
                                    </div>
                                    <div className="w-full bg-slate-800 rounded-full h-2.5 overflow-hidden">
                                        <div
                                            className={`h-full rounded-full transition-all duration-500 ${
                                                topic.mastery_score >= 80 ? 'bg-emerald-500' :
                                                topic.mastery_score >= 65 ? 'bg-indigo-500' : 'bg-amber-500'
                                            }`}
                                            style={{ width: `${Math.min(100, topic.mastery_score)}%` }}
                                        />
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="py-8 text-center text-slate-400 italic">No topic mastery data logged yet.</div>
                    )}
                </div>

                {/* Learning Activity Chart */}
                <div className="bg-slate-800/90 border border-slate-700/90 rounded-2xl p-6 md:p-8 shadow-xl flex flex-col justify-between">
                    <div>
                        <h2 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
                            <Activity className="w-5 h-5 text-cyan-400" />
                            Learning Activity
                        </h2>
                        <p className="text-slate-400 text-sm mb-6">Daily activities including explanations, revisions, and practice sessions</p>

                        <div className="grid grid-cols-7 gap-2 items-end h-40 pt-4 pb-2">
                            {learningActivity.slice(-7).map((act, idx) => (
                                <div key={idx} className="flex flex-col items-center h-full justify-end group">
                                    <div className="text-xs font-bold text-cyan-300 mb-1 group-hover:scale-110 transition-transform">
                                        {act.count}
                                    </div>
                                    <div
                                        style={{ height: `${Math.max(12, Math.min(100, act.count * 20))}%` }}
                                        className="w-full bg-gradient-to-t from-cyan-600 to-cyan-400 rounded-t-md transition-all group-hover:brightness-125"
                                    />
                                    <span className="text-xs text-slate-400 mt-2 font-medium">{act.day_name}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="mt-6 pt-4 border-t border-slate-700/70 grid grid-cols-3 gap-3 text-center">
                        <div className="bg-slate-900/50 p-2.5 rounded-xl border border-slate-700/40">
                            <div className="text-slate-400 text-xs">Evaluations</div>
                            <div className="text-lg font-bold text-white mt-0.5">{weeklySummary.evaluations || 0}</div>
                        </div>
                        <div className="bg-slate-900/50 p-2.5 rounded-xl border border-slate-700/40">
                            <div className="text-slate-400 text-xs">Interviews</div>
                            <div className="text-lg font-bold text-white mt-0.5">{weeklySummary.interviews || 0}</div>
                        </div>
                        <div className="bg-slate-900/50 p-2.5 rounded-xl border border-slate-700/40">
                            <div className="text-slate-400 text-xs">Revisions</div>
                            <div className="text-lg font-bold text-white mt-0.5">{weeklySummary.revisions || 0}</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* ROW 4: Goal Progress (Dynamic Learning Roadmap) */}
            <div className="bg-gradient-to-r from-slate-800/90 via-slate-800 to-indigo-950/40 border border-indigo-500/30 rounded-2xl p-6 md:p-8 mb-8 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div className="flex-1">
                    <div className="flex items-center gap-2 text-indigo-400 font-semibold text-sm mb-1 uppercase tracking-wider">
                        <Target className="w-4 h-4" /> Career Goal
                    </div>
                    <h2 className="text-2xl font-black text-white">{goalProgress.target_role || "Full Stack Developer"}</h2>

                    <div className="mt-4 max-w-xl">
                        <div className="flex justify-between items-center text-sm font-bold mb-1.5">
                            <span className="text-slate-300">Roadmap Progress</span>
                            <span className="text-indigo-400">{goalProgress.progress || 0}%</span>
                        </div>
                        <div className="w-full bg-slate-900 rounded-full h-3.5 border border-slate-700 p-0.5 overflow-hidden">
                            <div
                                className="bg-gradient-to-r from-indigo-500 to-cyan-400 h-full rounded-full transition-all duration-500"
                                style={{ width: `${Math.min(100, goalProgress.progress || 0)}%` }}
                            />
                        </div>
                    </div>
                </div>

                <div className="flex flex-col sm:flex-row gap-3">
                    <button
                        onClick={() => navigate('/learning-roadmap')}
                        className="inline-flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold px-6 py-3.5 rounded-xl shadow-lg shadow-indigo-600/30 transition-all hover:scale-105"
                    >
                        <BookOpen className="w-5 h-5" />
                        View Roadmap
                    </button>
                </div>
            </div>

            {/* ROW 5 & ROW 6: Communication & Interview Analytics */}
            <div className="grid lg:grid-cols-2 gap-8 mb-8">
                {/* Communication Progress */}
                <div className="bg-slate-800/90 border border-slate-700/90 rounded-2xl p-6 md:p-8 shadow-xl">
                    <div className="flex justify-between items-start mb-6">
                        <div>
                            <h2 className="text-xl font-bold text-white flex items-center gap-2">
                                <MessageSquare className="w-5 h-5 text-cyan-400" />
                                Communication Progress
                            </h2>
                            <p className="text-slate-400 text-sm mt-1">Clarity, grammar & vocabulary metrics from voice sessions</p>
                        </div>
                        {communicationAnalytics.improvement > 0 && (
                            <span className="bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 px-3 py-1 rounded-full text-xs font-bold">
                                +{communicationAnalytics.improvement} pts
                            </span>
                        )}
                    </div>

                    <div className="grid grid-cols-3 gap-4 mb-6 text-center">
                        <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-700/50">
                            <div className="text-xs text-slate-400">Clarity</div>
                            <div className="text-lg font-bold text-cyan-300 mt-1">
                                {communicationAnalytics.metrics?.clarity?.latest || 0}%
                            </div>
                        </div>
                        <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-700/50">
                            <div className="text-xs text-slate-400">Grammar</div>
                            <div className="text-lg font-bold text-cyan-300 mt-1">
                                {communicationAnalytics.metrics?.grammar?.latest || 0}%
                            </div>
                        </div>
                        <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-700/50">
                            <div className="text-xs text-slate-400">Vocabulary</div>
                            <div className="text-lg font-bold text-cyan-300 mt-1">
                                {communicationAnalytics.metrics?.vocabulary?.latest || 0}%
                            </div>
                        </div>
                    </div>
                </div>

                {/* Interview Performance */}
                <div className="bg-slate-800/90 border border-slate-700/90 rounded-2xl p-6 md:p-8 shadow-xl">
                    <h2 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
                        <Mic className="w-5 h-5 text-purple-400" />
                        Interview Performance
                    </h2>
                    <p className="text-slate-400 text-sm mb-6">AI Adaptive Mock Interview metrics & difficulty progression</p>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6 text-center">
                        <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-700/50">
                            <div className="text-xs text-slate-400">Completed</div>
                            <div className="text-xl font-bold text-white mt-1">{interviewPerformance.completed || 0}</div>
                        </div>
                        <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-700/50">
                            <div className="text-xs text-slate-400">Avg Score</div>
                            <div className="text-xl font-bold text-purple-400 mt-1">{interviewPerformance.average_score || 0}%</div>
                        </div>
                        <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-700/50">
                            <div className="text-xs text-slate-400">Best Score</div>
                            <div className="text-xl font-bold text-emerald-400 mt-1">{interviewPerformance.best_score || 0}%</div>
                        </div>
                        <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-700/50">
                            <div className="text-xs text-slate-400">Technical</div>
                            <div className="text-xl font-bold text-indigo-400 mt-1">{interviewPerformance.technical_avg || 0}%</div>
                        </div>
                    </div>

                    {/* Difficulty Progression */}
                    {interviewPerformance.difficulty_progression && interviewPerformance.difficulty_progression.length > 0 && (
                        <div className="bg-slate-900/40 p-3.5 rounded-xl border border-slate-700/50 text-xs">
                            <span className="font-semibold text-slate-300">Adaptive Difficulty Level: </span>
                            <span className="text-purple-300 font-bold ml-1">
                                {interviewPerformance.difficulty_progression[0]?.transition || "MEDIUM"}
                            </span>
                        </div>
                    )}
                </div>
            </div>

            {/* ROW 7: Knowledge Gaps & Revision Analytics */}
            <div className="grid lg:grid-cols-2 gap-8 mb-8">
                <div className="bg-slate-800/90 border border-slate-700/90 rounded-2xl p-6 md:p-8 shadow-xl">
                    <h2 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
                        <AlertTriangle className="w-5 h-5 text-amber-400" />
                        Knowledge Gap Resolution
                    </h2>
                    <p className="text-slate-400 text-sm mb-4">Resolution rate of identified conceptual weaknesses</p>

                    <div className="flex items-center justify-between text-sm font-bold mb-2">
                        <span className="text-slate-300">Gap Resolution Rate</span>
                        <span className="text-amber-400">{knowledgeGapStats.resolution_rate || 0}%</span>
                    </div>
                    <div className="w-full bg-slate-900 rounded-full h-3 border border-slate-700 overflow-hidden mb-6">
                        <div
                            className="bg-amber-500 h-full rounded-full transition-all duration-500"
                            style={{ width: `${Math.min(100, knowledgeGapStats.resolution_rate || 0)}%` }}
                        />
                    </div>

                    <div className="grid grid-cols-3 gap-3 text-center">
                        <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-700/40">
                            <div className="text-xs text-slate-400">Open Gaps</div>
                            <div className="text-lg font-bold text-amber-400 mt-0.5">{knowledgeGapStats.open_gaps || 0}</div>
                        </div>
                        <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-700/40">
                            <div className="text-xs text-slate-400">Improving</div>
                            <div className="text-lg font-bold text-indigo-400 mt-0.5">{knowledgeGapStats.improving_gaps || 0}</div>
                        </div>
                        <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-700/40">
                            <div className="text-xs text-slate-400">Resolved</div>
                            <div className="text-lg font-bold text-emerald-400 mt-0.5">{knowledgeGapStats.resolved_gaps || 0}</div>
                        </div>
                    </div>
                </div>

                <div className="bg-slate-800/90 border border-slate-700/90 rounded-2xl p-6 md:p-8 shadow-xl">
                    <h2 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
                        <RotateCcw className="w-5 h-5 text-indigo-400" />
                        Smart Revision Activity
                    </h2>
                    <p className="text-slate-400 text-sm mb-6">Spaced-repetition revision metrics & retention rate</p>

                    <div className="grid grid-cols-4 gap-3 text-center">
                        <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-700/50">
                            <div className="text-xs text-slate-400">Due Today</div>
                            <div className="text-xl font-bold text-amber-400 mt-1">{revisionStats.due_today || 0}</div>
                        </div>
                        <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-700/50">
                            <div className="text-xs text-slate-400">Completed</div>
                            <div className="text-xl font-bold text-emerald-400 mt-1">{revisionStats.completed || 0}</div>
                        </div>
                        <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-700/50">
                            <div className="text-xs text-slate-400">Overdue</div>
                            <div className="text-xl font-bold text-rose-400 mt-1">{revisionStats.overdue || 0}</div>
                        </div>
                        <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-700/50">
                            <div className="text-xs text-slate-400">Success</div>
                            <div className="text-xl font-bold text-indigo-400 mt-1">{revisionStats.success_rate || 0}%</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* ROW 8: Strongest & Weakest Topics */}
            <div className="grid md:grid-cols-2 gap-8 mb-8">
                {/* Strongest Topics */}
                <div className="bg-slate-800/90 border border-slate-700/90 rounded-2xl p-6 md:p-8 shadow-xl">
                    <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                        <Award className="w-5 h-5 text-amber-400" />
                        Strongest Topics
                    </h2>
                    {strongestTopics && strongestTopics.length > 0 ? (
                        <div className="space-y-3">
                            {strongestTopics.map((topic, idx) => (
                                <div key={idx} className="flex items-center justify-between bg-slate-900/60 border border-slate-700/50 p-4 rounded-xl">
                                    <div className="flex items-center gap-3">
                                        <span className="text-xl">{idx === 0 ? '🥇' : idx === 1 ? '🥈' : '🥉'}</span>
                                        <span className="font-bold text-white">{topic.topic_name}</span>
                                    </div>
                                    <span className="font-black text-emerald-400 text-lg">{topic.mastery_score}%</span>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="text-slate-400 text-sm italic">Complete evaluations to discover your top strengths.</p>
                    )}
                </div>

                {/* Weakest Topics */}
                <div className="bg-slate-800/90 border border-slate-700/90 rounded-2xl p-6 md:p-8 shadow-xl">
                    <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                        <AlertTriangle className="w-5 h-5 text-rose-400" />
                        Weakest Topics
                    </h2>
                    {weakestTopics && weakestTopics.length > 0 ? (
                        <div className="space-y-3">
                            {weakestTopics.map((topic, idx) => (
                                <div key={idx} className="flex items-center justify-between bg-slate-900/60 border border-slate-700/50 p-4 rounded-xl">
                                    <div className="flex items-center gap-3">
                                        <AlertTriangle className="w-4 h-4 text-rose-400" />
                                        <span className="font-bold text-white">{topic.topic_name}</span>
                                    </div>
                                    <div className="flex items-center gap-3">
                                        <span className="font-black text-rose-400 text-lg">{topic.mastery_score}%</span>
                                        <button
                                            onClick={() => navigate('/study', { state: { topicId: topic.topic_id } })}
                                            className="text-xs bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/40 text-rose-300 font-semibold px-3 py-1.5 rounded-lg transition-colors"
                                        >
                                            Practice
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="text-slate-400 text-sm italic">No conceptual weaknesses detected yet!</p>
                    )}
                </div>
            </div>

            {/* ROW 9: AI Learning Insight */}
            <div className="bg-gradient-to-r from-indigo-900/60 via-slate-800 to-indigo-950/60 border border-indigo-500/40 rounded-2xl p-6 md:p-8 mb-8 shadow-xl">
                <div className="flex items-center gap-3 mb-3">
                    <div className="p-2 bg-indigo-500/20 border border-indigo-500/40 rounded-lg text-indigo-300">
                        <Sparkles className="w-5 h-5" />
                    </div>
                    <h2 className="text-xl font-bold text-white">AI Learning Insight</h2>
                </div>
                <p className="text-slate-200 text-base leading-relaxed pl-1">
                    {aiInsight.text || "Your learning metrics are updating based on your evaluations and study room activity."}
                </p>
            </div>

            {/* ROW 10: Recommended Next Action */}
            {recommendedNextAction && (
                <div className="bg-slate-800/90 border border-emerald-500/40 rounded-2xl p-6 md:p-8 shadow-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
                    <div className="flex-1">
                        <div className="flex items-center gap-2 text-emerald-400 font-semibold text-xs mb-1 uppercase tracking-wider">
                            <CheckCircle2 className="w-4 h-4" /> Recommended Next Action
                        </div>
                        <h3 className="text-2xl font-black text-white">{recommendedNextAction.topic_name || "Binary Search"}</h3>
                        <p className="text-slate-300 text-sm mt-2">
                            {recommendedNextAction.recommendation_text || recommendedNextAction.reason || "Review boundary conditions and solve practice problems before moving forward."}
                        </p>
                    </div>

                    <button
                        onClick={() => navigate('/study', { state: { topicId: recommendedNextAction.topic_id } })}
                        className="inline-flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold px-7 py-3.5 rounded-xl shadow-lg shadow-emerald-600/30 transition-all hover:scale-105"
                    >
                        <Play className="w-4 h-4 fill-current" />
                        Start Practice
                    </button>
                </div>
            )}
        </div>
    );
};

export default AnalyticsPage;
