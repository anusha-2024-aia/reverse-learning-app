import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { LineChart, BarChart2, Loader2, BookOpen } from 'lucide-react';
import StatsCard from '../components/StatsCard';
import ProgressChart from '../components/ProgressChart';
import TopicList from '../components/TopicList';
import CurriculumProgressBar from '../components/CurriculumProgressBar';
import api from '../api/axios';

const InsightsDashboard = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState({
        summary: null,
        scoreTrend: null,
        weakTopics: null,
        mostImproved: null,
        mostAttempted: null,
        grammarTrend: null,
        curriculumStats: null
    });

    useEffect(() => {
        const fetchInsights = async () => {
            try {
                const [
                    summaryRes, scoreTrendRes, weakTopicsRes, 
                    mostImprovedRes, mostAttemptedRes, grammarTrendRes, curriculumStatsRes
                ] = await Promise.all([
                    api.get('/insights/summary'),
                    api.get('/insights/score-trend?days=14'),
                    api.get('/insights/weak-topics'),
                    api.get('/insights/most-improved'),
                    api.get('/insights/most-attempted'),
                    api.get('/insights/grammar-trend?days=14'),
                    api.get('/insights/curriculum-stats')
                ]);

                setData({
                    summary: summaryRes.data,
                    scoreTrend: scoreTrendRes.data,
                    weakTopics: weakTopicsRes.data,
                    mostImproved: mostImprovedRes.data,
                    mostAttempted: mostAttemptedRes.data,
                    grammarTrend: grammarTrendRes.data,
                    curriculumStats: curriculumStatsRes.data
                });
            } catch (error) {
                console.error("Failed to fetch insights:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchInsights();
    }, []);

    const handleStudyTopic = (topicId) => {
        navigate('/study', { state: { topicId } });
    };

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh]">
                <Loader2 className="w-10 h-10 text-indigo-500 animate-spin mb-4" />
                <p className="text-slate-400 font-medium">Crunching your learning data...</p>
            </div>
        );
    }

    const { summary, scoreTrend, weakTopics, mostImproved, mostAttempted, grammarTrend, curriculumStats } = data;

    return (
        <div className="p-8 max-w-7xl mx-auto w-full pb-20">
            <h1 className="text-4xl font-black mb-2 flex items-center gap-3">
                <BarChart2 className="w-8 h-8 text-indigo-400" />
                Learning Analytics
            </h1>
            <p className="text-slate-400 mb-10 text-lg">Track your progress and identify areas for improvement.</p>

            {/* Stats Row */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-10">
                <StatsCard 
                    title="Total Evaluations" 
                    value={summary?.total_evaluations || 0} 
                    subtitle={`${summary?.days_active || 0} days active`} 
                />
                <StatsCard 
                    title="Average Score" 
                    value={summary?.average_score || 0} 
                    subtitle="Out of 10" 
                    trend={scoreTrend?.overall_trend} 
                />
                <StatsCard 
                    title="Current Streak" 
                    value={`${summary?.current_streak || 0}d`} 
                    subtitle="Consecutive days" 
                />
                <StatsCard 
                    title="Best Score" 
                    value={summary?.best_score || 0} 
                    subtitle="Highest achieved" 
                />
            </div>

            {/* Charts Row */}
            <div className="grid lg:grid-cols-2 gap-6 mb-10">
                <ProgressChart 
                    data={scoreTrend?.trend || []} 
                    title="Score Trend (Last 14 Days)" 
                    dataKey="average_score" 
                    yAxisLabel="Avg Score" 
                    color="#6366f1"
                />
                <ProgressChart 
                    data={grammarTrend?.grammar_score_over_time || []} 
                    title={`Grammar Improvement (${grammarTrend?.current_error_free_percentage || 0}% Error-Free)`}
                    dataKey="error_free_percentage" 
                    yAxisLabel="% Error-Free" 
                    isArea={true}
                    color="#10b981"
                />
            </div>

            {/* Lists Row */}
            <div className="grid lg:grid-cols-3 gap-6 mb-10">
                <div className="h-[400px]">
                    <TopicList 
                        type="weak" 
                        topics={weakTopics?.weak_topics || []} 
                        onSelectTopic={handleStudyTopic} 
                    />
                </div>
                <div className="h-[400px]">
                    <TopicList 
                        type="improved" 
                        topics={mostImproved?.improved_topics || []} 
                    />
                </div>
                <div className="h-[400px]">
                    <TopicList 
                        type="attempted" 
                        topics={mostAttempted?.most_attempted || []} 
                    />
                </div>
            </div>

            {/* Curriculum Progress */}
            <div className="bg-slate-800 rounded-2xl border border-slate-700 shadow-lg p-6 lg:p-8">
                <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                    <BookOpen className="w-6 h-6 text-indigo-400" />
                    Per-Curriculum Progress
                </h3>
                
                {curriculumStats?.curriculums && curriculumStats.curriculums.length > 0 ? (
                    <div className="grid md:grid-cols-2 gap-x-12 gap-y-8">
                        {curriculumStats.curriculums.map(curr => (
                            <CurriculumProgressBar key={curr.curriculum_id} curr={curr} />
                        ))}
                    </div>
                ) : (
                    <p className="text-slate-500 italic text-center py-8">No curriculum progress data available yet.</p>
                )}
            </div>
        </div>
    );
};

export default InsightsDashboard;
