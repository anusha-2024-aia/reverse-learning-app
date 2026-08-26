import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
    Mic, TrendingUp, Sparkles, AlertCircle, CheckCircle2, 
    MessageSquare, Volume2, Flame, Award, ArrowRight, Zap, RefreshCw, BarChart2
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import api from '../api/axios';

const CommunicationCoach = () => {
    const navigate = useNavigate();

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [progressData, setProgressData] = useState(null);
    const [summaryData, setSummaryData] = useState(null);
    const [_history, setHistory] = useState([]);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            setError(null);
            try {
                const [progRes, sumRes, histRes] = await Promise.all([
                    api.get('/communication/progress'),
                    api.get('/communication/summary'),
                    api.get('/communication/history')
                ]);

                setProgressData(progRes.data);
                setSummaryData(sumRes.data);
                setHistory(histRes.data || []);
            } catch (err) {
                console.error("Error fetching communication data:", err);
                setError("Unable to load communication coaching metrics.");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    if (loading) {
        return (
            <div className="flex-1 flex items-center justify-center bg-slate-900 text-slate-100 p-12">
                <div className="text-center space-y-4">
                    <RefreshCw className="w-8 h-8 animate-spin text-indigo-400 mx-auto" />
                    <p className="text-sm font-medium text-slate-400">Loading AI Communication Coach...</p>
                </div>
            </div>
        );
    }

    const hasData = progressData && progressData.has_data;
    const beforeVsNow = progressData?.before_vs_latest;

    return (
        <div className="flex-1 overflow-y-auto bg-slate-900 text-slate-100 p-6 md:p-12 relative">
            <div className="max-w-6xl mx-auto space-y-8">

                {/* Header Banner */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
                    <div className="flex items-center gap-4">
                        <div className="p-3.5 bg-indigo-600/20 text-indigo-400 rounded-2xl border border-indigo-500/30 shadow-lg">
                            <Mic className="w-8 h-8" />
                        </div>
                        <div>
                            <h1 className="text-3xl md:text-4xl font-black text-white tracking-tight">
                                AI Communication Coach
                            </h1>
                            <p className="text-slate-400 text-sm md:text-base mt-1 font-medium">
                                Analyze speaking pace, clarity, grammar, and filler words to communicate your technical knowledge effectively.
                            </p>
                        </div>
                    </div>

                    <button
                        onClick={() => navigate('/mock-interview')}
                        className="px-5 py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-2xl text-xs flex items-center gap-2 shadow-xl shadow-indigo-600/25 transition-all self-start md:self-auto"
                    >
                        <span>Start Adaptive Interview</span>
                        <ArrowRight className="w-4 h-4" />
                    </button>
                </div>

                {error && (
                    <div className="p-4 bg-rose-950/40 border border-rose-500/40 rounded-2xl text-xs text-rose-300 flex items-center gap-2">
                        <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
                        <span>{error}</span>
                    </div>
                )}

                {!hasData ? (
                    /* Empty State */
                    <div className="bg-slate-800/80 border border-slate-700/80 rounded-3xl p-12 text-center max-w-2xl mx-auto space-y-6 shadow-2xl">
                        <div className="w-16 h-16 bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 rounded-2xl flex items-center justify-center mx-auto">
                            <Volume2 className="w-8 h-8" />
                        </div>
                        <div className="space-y-2">
                            <h2 className="text-2xl font-bold text-white">No Voice Interviews Analyzed Yet</h2>
                            <p className="text-sm text-slate-400 max-w-md mx-auto leading-relaxed">
                                Complete your first AI Adaptive Mock Interview using voice input to unlock speaking pace tracking, filler word detection, grammar analysis, and improvement trends over time!
                            </p>
                        </div>
                        <button
                            onClick={() => navigate('/mock-interview')}
                            className="px-6 py-3.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-2xl text-xs inline-flex items-center gap-2 shadow-xl"
                        >
                            <span>Start First Voice Interview</span>
                            <ArrowRight className="w-4 h-4" />
                        </button>
                    </div>
                ) : (
                    /* Main Dashboard View */
                    <div className="space-y-8">

                        {/* Top Hero Cards: Overall Score & Delta */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

                            {/* Overall Score */}
                            <div className="bg-gradient-to-br from-slate-900 via-indigo-950/60 to-slate-900 border border-slate-800 p-6 rounded-3xl shadow-xl flex items-center justify-between">
                                <div className="space-y-1">
                                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">Overall Communication</span>
                                    <div className="text-4xl font-black text-indigo-400 font-mono">
                                        {summaryData?.communication_score || beforeVsNow?.latest_interview?.overall || 70}%
                                    </div>
                                    <span className="text-[11px] text-slate-400 block">Target Goal: {summaryData?.target_goal || 85}%</span>
                                </div>
                                <div className="w-14 h-14 bg-indigo-600/20 border border-indigo-500/30 rounded-2xl flex items-center justify-center text-indigo-400">
                                    <Award className="w-7 h-7" />
                                </div>
                            </div>

                            {/* Improvement Delta */}
                            <div className="bg-slate-800/80 border border-slate-700/80 p-6 rounded-3xl shadow-xl flex items-center justify-between">
                                <div className="space-y-1">
                                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">Overall Improvement</span>
                                    <div className={`text-3xl font-black font-mono ${
                                        (progressData?.overall_improvement_delta || 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'
                                    }`}>
                                        {(progressData?.overall_improvement_delta || 0) >= 0 ? '+' : ''}
                                        {progressData?.overall_improvement_delta || 0} pts
                                    </div>
                                    <span className="text-[11px] text-slate-400 block">Across {progressData?.total_interviews_analyzed} interview evaluations</span>
                                </div>
                                <div className="w-14 h-14 bg-emerald-500/20 border border-emerald-500/30 rounded-2xl flex items-center justify-center text-emerald-400">
                                    <TrendingUp className="w-7 h-7" />
                                </div>
                            </div>

                            {/* Filler Reduction */}
                            <div className="bg-slate-800/80 border border-slate-700/80 p-6 rounded-3xl shadow-xl flex items-center justify-between">
                                <div className="space-y-1">
                                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">Filler Word Reduction</span>
                                    <div className="text-3xl font-black text-amber-400 font-mono">
                                        -{progressData?.filler_percentage_reduction || 0}%
                                    </div>
                                    <span className="text-[11px] text-slate-400 block">
                                        {beforeVsNow?.first_interview?.filler_words || 0} fillers → {beforeVsNow?.latest_interview?.filler_words || 0} fillers
                                    </span>
                                </div>
                                <div className="w-14 h-14 bg-amber-500/20 border border-amber-500/30 rounded-2xl flex items-center justify-center text-amber-400">
                                    <MessageSquare className="w-7 h-7" />
                                </div>
                            </div>

                        </div>

                        {/* Sub-Metrics Progress Bars */}
                        <div className="bg-slate-800/90 border border-slate-700 p-8 rounded-3xl space-y-6 shadow-xl">
                            <h2 className="text-lg font-bold text-white flex items-center gap-2">
                                <BarChart2 className="w-5 h-5 text-indigo-400" />
                                Core Communication Breakdown
                            </h2>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                
                                {/* Clarity */}
                                <div className="space-y-2">
                                    <div className="flex justify-between items-center text-xs font-bold">
                                        <span className="text-slate-300 uppercase tracking-wider">Clarity</span>
                                        <span className="text-indigo-400 font-mono text-sm">{beforeVsNow?.latest_interview?.clarity || 80}%</span>
                                    </div>
                                    <div className="w-full h-3 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
                                        <div 
                                            className="h-full bg-indigo-500 rounded-full transition-all duration-500"
                                            style={{ width: `${beforeVsNow?.latest_interview?.clarity || 80}%` }}
                                        />
                                    </div>
                                </div>

                                {/* Grammar */}
                                <div className="space-y-2">
                                    <div className="flex justify-between items-center text-xs font-bold">
                                        <span className="text-slate-300 uppercase tracking-wider">Grammar</span>
                                        <span className="text-emerald-400 font-mono text-sm">{beforeVsNow?.latest_interview?.grammar || 75}%</span>
                                    </div>
                                    <div className="w-full h-3 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
                                        <div 
                                            className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                                            style={{ width: `${beforeVsNow?.latest_interview?.grammar || 75}%` }}
                                        />
                                    </div>
                                </div>

                                {/* Vocabulary */}
                                <div className="space-y-2">
                                    <div className="flex justify-between items-center text-xs font-bold">
                                        <span className="text-slate-300 uppercase tracking-wider">Vocabulary</span>
                                        <span className="text-amber-400 font-mono text-sm">{beforeVsNow?.latest_interview?.vocabulary || 78}%</span>
                                    </div>
                                    <div className="w-full h-3 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
                                        <div 
                                            className="h-full bg-amber-500 rounded-full transition-all duration-500"
                                            style={{ width: `${beforeVsNow?.latest_interview?.vocabulary || 78}%` }}
                                        />
                                    </div>
                                </div>

                                {/* Answer Structure */}
                                <div className="space-y-2">
                                    <div className="flex justify-between items-center text-xs font-bold">
                                        <span className="text-slate-300 uppercase tracking-wider">Answer Structure</span>
                                        <span className="text-rose-400 font-mono text-sm">{beforeVsNow?.latest_interview?.structure || 76}%</span>
                                    </div>
                                    <div className="w-full h-3 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
                                        <div 
                                            className="h-full bg-rose-500 rounded-full transition-all duration-500"
                                            style={{ width: `${beforeVsNow?.latest_interview?.structure || 76}%` }}
                                        />
                                    </div>
                                </div>

                                {/* Speaking Pace */}
                                <div className="p-4 bg-slate-950 rounded-2xl border border-slate-800 flex items-center justify-between">
                                    <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">Speaking Pace</span>
                                    <span className="text-xs font-black bg-indigo-950 text-indigo-300 border border-indigo-800 px-3 py-1 rounded-full">
                                        {beforeVsNow?.latest_interview?.pace || "Good"}
                                    </span>
                                </div>

                                {/* Filler Words */}
                                <div className="p-4 bg-slate-950 rounded-2xl border border-slate-800 flex items-center justify-between">
                                    <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">Filler Words Detected</span>
                                    <span className="text-xs font-black font-mono text-amber-400 bg-amber-950 border border-amber-800 px-3 py-1 rounded-full">
                                        {beforeVsNow?.latest_interview?.filler_words || 0}
                                    </span>
                                </div>

                            </div>
                        </div>

                        {/* COMMUNICATION PROGRESS TREND GRAPH */}
                        <div className="bg-slate-800/90 border border-slate-700 p-8 rounded-3xl space-y-6 shadow-xl">
                            <div className="flex items-center justify-between">
                                <div>
                                    <h2 className="text-lg font-bold text-white">Communication Score Progress</h2>
                                    <p className="text-xs text-slate-400 mt-0.5">Tracking score evolution across interviews</p>
                                </div>
                                <span className="text-xs font-bold text-emerald-400 font-mono bg-emerald-950 border border-emerald-800 px-3 py-1 rounded-full">
                                    +{(progressData?.overall_improvement_delta || 0)} Points Delta
                                </span>
                            </div>

                            <div className="h-64 w-full pt-4">
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={progressData.history_trend || []}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
                                        <XAxis dataKey="interview" stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                                        <YAxis domain={[0, 100]} stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                                        <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', fontSize: '12px' }} />
                                        <Line type="monotone" dataKey="score" stroke="#6366f1" strokeWidth={4} dot={{ fill: '#818cf8', r: 6 }} activeDot={{ r: 8 }} />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        {/* BEFORE VS LATEST COMPARISON TABLE */}
                        {beforeVsNow && (
                            <div className="bg-slate-800/90 border border-slate-700 p-8 rounded-3xl space-y-6 shadow-xl">
                                <h2 className="text-lg font-bold text-white">Before vs. Latest Interview Comparison</h2>

                                <div className="overflow-x-auto">
                                    <table className="w-full text-left text-xs text-slate-300">
                                        <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider font-bold border-b border-slate-800">
                                            <tr>
                                                <th className="p-4">Metric</th>
                                                <th className="p-4">First Interview</th>
                                                <th className="p-4">Latest Interview</th>
                                                <th className="p-4">Change</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-slate-800 font-medium">
                                            <tr>
                                                <td className="p-4 font-bold text-white">Overall Communication</td>
                                                <td className="p-4 font-mono">{beforeVsNow.first_interview.overall}%</td>
                                                <td className="p-4 font-mono text-indigo-400 font-bold">{beforeVsNow.latest_interview.overall}%</td>
                                                <td className="p-4 font-mono font-bold text-emerald-400">
                                                    +{beforeVsNow.latest_interview.overall - beforeVsNow.first_interview.overall} pts
                                                </td>
                                            </tr>
                                            <tr>
                                                <td className="p-4">Clarity</td>
                                                <td className="p-4 font-mono">{beforeVsNow.first_interview.clarity}</td>
                                                <td className="p-4 font-mono text-white font-bold">{beforeVsNow.latest_interview.clarity}</td>
                                                <td className="p-4 font-mono text-emerald-400">
                                                    {beforeVsNow.latest_interview.clarity - beforeVsNow.first_interview.clarity >= 0 ? '+' : ''}
                                                    {beforeVsNow.latest_interview.clarity - beforeVsNow.first_interview.clarity}
                                                </td>
                                            </tr>
                                            <tr>
                                                <td className="p-4">Grammar</td>
                                                <td className="p-4 font-mono">{beforeVsNow.first_interview.grammar}</td>
                                                <td className="p-4 font-mono text-white font-bold">{beforeVsNow.latest_interview.grammar}</td>
                                                <td className="p-4 font-mono text-emerald-400">
                                                    {beforeVsNow.latest_interview.grammar - beforeVsNow.first_interview.grammar >= 0 ? '+' : ''}
                                                    {beforeVsNow.latest_interview.grammar - beforeVsNow.first_interview.grammar}
                                                </td>
                                            </tr>
                                            <tr>
                                                <td className="p-4">Vocabulary</td>
                                                <td className="p-4 font-mono">{beforeVsNow.first_interview.vocabulary}</td>
                                                <td className="p-4 font-mono text-white font-bold">{beforeVsNow.latest_interview.vocabulary}</td>
                                                <td className="p-4 font-mono text-emerald-400">
                                                    {beforeVsNow.latest_interview.vocabulary - beforeVsNow.first_interview.vocabulary >= 0 ? '+' : ''}
                                                    {beforeVsNow.latest_interview.vocabulary - beforeVsNow.first_interview.vocabulary}
                                                </td>
                                            </tr>
                                            <tr>
                                                <td className="p-4">Answer Structure</td>
                                                <td className="p-4 font-mono">{beforeVsNow.first_interview.structure}</td>
                                                <td className="p-4 font-mono text-white font-bold">{beforeVsNow.latest_interview.structure}</td>
                                                <td className="p-4 font-mono text-emerald-400">
                                                    {beforeVsNow.latest_interview.structure - beforeVsNow.first_interview.structure >= 0 ? '+' : ''}
                                                    {beforeVsNow.latest_interview.structure - beforeVsNow.first_interview.structure}
                                                </td>
                                            </tr>
                                            <tr>
                                                <td className="p-4">Filler Words</td>
                                                <td className="p-4 font-mono">{beforeVsNow.first_interview.filler_words}</td>
                                                <td className="p-4 font-mono text-white font-bold">{beforeVsNow.latest_interview.filler_words}</td>
                                                <td className="p-4 font-mono text-emerald-400">
                                                    {beforeVsNow.latest_interview.filler_words - beforeVsNow.first_interview.filler_words} fillers
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        )}

                        {/* Top Filler Words Breakdown */}
                        {progressData.top_filler_words && progressData.top_filler_words.length > 0 && (
                            <div className="bg-slate-800/90 border border-slate-700 p-8 rounded-3xl space-y-4 shadow-xl">
                                <h2 className="text-lg font-bold text-white">Detected Filler Words Frequency</h2>
                                <div className="flex flex-wrap gap-3">
                                    {progressData.top_filler_words.map((item, idx) => (
                                        <div key={idx} className="bg-slate-950 border border-slate-800 px-4 py-2.5 rounded-2xl flex items-center gap-2">
                                            <span className="text-xs font-bold text-slate-300">"{item.filler}"</span>
                                            <span className="text-xs font-black font-mono bg-indigo-950 text-indigo-300 border border-indigo-800 px-2 py-0.5 rounded-full">
                                                {item.count}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Personalized AI Coach Summary */}
                        {summaryData && (
                            <div className="bg-gradient-to-r from-indigo-950/60 via-slate-900 to-indigo-950/60 border border-indigo-500/30 p-8 rounded-3xl space-y-6 shadow-2xl">
                                <div className="flex items-center gap-2 text-indigo-400 font-bold uppercase tracking-wider text-xs">
                                    <Sparkles className="w-4 h-4" /> AI Communication Coach Summary
                                </div>

                                <div className="grid md:grid-cols-3 gap-4">
                                    <div className="bg-slate-950/80 p-4 rounded-2xl border border-slate-800">
                                        <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400 block">✓ Strongest Area</span>
                                        <span className="text-sm font-bold text-white mt-1 block">{summaryData.strongest_area}</span>
                                    </div>
                                    <div className="bg-slate-950/80 p-4 rounded-2xl border border-slate-800">
                                        <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-400 block">⚡ Improving</span>
                                        <span className="text-sm font-bold text-white mt-1 block">{summaryData.improving_area}</span>
                                    </div>
                                    <div className="bg-slate-950/80 p-4 rounded-2xl border border-slate-800">
                                        <span className="text-[10px] font-bold uppercase tracking-wider text-amber-400 block">⚠ Needs Focus</span>
                                        <span className="text-sm font-bold text-white mt-1 block">{summaryData.needs_focus}</span>
                                    </div>
                                </div>

                                <div className="bg-slate-950/90 p-6 rounded-2xl border border-slate-800 space-y-2">
                                    <span className="text-xs font-bold text-indigo-300 uppercase tracking-wider block">AI Coach Recommendation</span>
                                    <p className="text-xs md:text-sm text-slate-200 leading-relaxed font-medium">
                                        "{summaryData.recommendation}"
                                    </p>
                                </div>
                            </div>
                        )}

                    </div>
                )}

            </div>
        </div>
    );
};

export default CommunicationCoach;
