import React, { useState, useEffect } from 'react';
import api from '../services/api';
import WelcomeSection from '../components/dashboard/WelcomeSection';
import OverallScoreCard from '../components/dashboard/OverallScoreCard';
import PerformanceCards from '../components/dashboard/PerformanceCards';
import AIInsightCard from '../components/dashboard/AIInsightCard';
import RecommendedActionCard from '../components/dashboard/RecommendedActionCard';
import TopicPerformance from '../components/dashboard/TopicPerformance';
import ProgressChart from '../components/dashboard/ProgressChart';
import RecentActivity from '../components/dashboard/RecentActivity';
import QuickActions from '../components/dashboard/QuickActions';
import CurrentFocusCard from '../components/adaptive/CurrentFocusCard';
import SmartRevisionCard from '../components/dashboard/SmartRevisionCard';
import ResumeIntelligenceCard from '../components/dashboard/ResumeIntelligenceCard';
import { Loader2 } from 'lucide-react';



const Dashboard = () => {
    const [data, setData] = useState(null);
    const [adaptiveRec, setAdaptiveRec] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const loadDashboard = async () => {
        try {
            setLoading(true);
            const res = await api.get('/dashboard-data');
            setData(res.data);
            
            try {
                const recRes = await api.get('/adaptive-learning/recommendation');
                setAdaptiveRec(recRes.data);
            } catch (recErr) {
                console.error("Adaptive rec error:", recErr);
            }
            
            setLoading(false);
        } catch (err) {
            console.error("Dashboard error:", err);
            setError(true);
            setLoading(false);
        }
    };

    useEffect(() => {
        loadDashboard();
    }, []);

    if (loading) {
        return (
            <div className="flex-1 overflow-y-auto bg-slate-900 text-slate-200 p-8 flex items-center justify-center">
                <div className="flex flex-col items-center gap-4">
                    <Loader2 className="w-12 h-12 text-indigo-500 animate-spin" />
                    <p className="text-slate-400 font-medium animate-pulse">Loading your learning intelligence...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex-1 overflow-y-auto bg-slate-900 text-slate-200 p-8 flex flex-col items-center justify-center">
                <p className="text-xl text-red-400 mb-4">Unable to load your learning data.</p>
                <p className="text-slate-400 mb-6">Please try again.</p>
                <button 
                    onClick={() => {
                        setLoading(true);
                        setError(null);
                        loadDashboard();
                    }}
                    className="bg-indigo-600 hover:bg-indigo-500 px-6 py-2 rounded-lg text-white font-medium transition-colors"
                >
                    Retry
                </button>
            </div>
        );
    }

    if (!data) return null;

    // Empty State Check
    if (data.summary.overallScore === 0 && data.recentActivity.length === 0) {
        return (
            <div className="flex-1 overflow-y-auto bg-slate-900 text-slate-200 p-8 lg:p-12">
                <div className="max-w-4xl mx-auto text-center py-20">
                    <h1 className="text-4xl font-bold text-white mb-6">Welcome to Reverse Learning 👋</h1>
                    <p className="text-xl text-slate-300 mb-8 max-w-2xl mx-auto">
                        Your learning intelligence dashboard will appear after your first evaluation.
                        Start by explaining a concept or taking a mock interview.
                    </p>
                    <div className="flex justify-center gap-4">
                        <button 
                            onClick={() => window.location.href = '/syllabi'}
                            className="bg-indigo-600 hover:bg-indigo-500 px-8 py-4 rounded-xl text-white font-bold transition-colors shadow-lg"
                        >
                            Start First Evaluation
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="flex-1 overflow-y-auto bg-slate-900 text-slate-200 p-8 lg:p-12 relative">
            <div className="max-w-7xl mx-auto relative z-10">
                
                <WelcomeSection user={data.user} streak={data.summary} insight={data.aiInsight?.text} />


                {/* PHASE 5: DYNAMIC ROADMAP SUMMARY BANNER */}
                {data.roadmapSummary && (
                  <div className="bg-gradient-to-r from-slate-900 via-indigo-950/70 to-slate-900 border border-slate-800 rounded-2xl p-6 mb-8 shadow-xl relative overflow-hidden">
                    <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="bg-indigo-600 text-white text-[10px] font-black uppercase tracking-wider px-2.5 py-0.5 rounded-full">
                            🎯 {data.roadmapSummary.target_role}
                          </span>
                          <span className="text-xs text-slate-400">Roadmap Progress</span>
                        </div>
                        <h3 className="text-xl font-black text-white">
                          Personalized Career Roadmap ({data.roadmapSummary.progress}%)
                        </h3>
                        {data.roadmapSummary.latest_change && data.roadmapSummary.latest_change.reason && (
                          <p className="text-xs text-indigo-300 font-medium flex items-center gap-1.5 pt-0.5">
                            <span>🔄 Latest Update:</span> {data.roadmapSummary.latest_change.reason}
                          </p>
                        )}
                      </div>

                      <button
                        onClick={() => window.location.href = '/learning-path'}
                        className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-bold text-xs transition-colors shadow-lg shadow-indigo-600/30 flex items-center gap-2 flex-shrink-0"
                      >
                        <span>View Full Roadmap</span> →
                      </button>
                    </div>
                  </div>
                )}
                
                {/* PHASE 6: SMART REVISION WIDGET */}
                {data.revisionSummary && (
                    <SmartRevisionCard revisionSummary={data.revisionSummary} />
                )}

                {/* PHASE 8: RESUME INTELLIGENCE WIDGET */}
                <ResumeIntelligenceCard resumeSummary={data.resumeSummary} />

                <div className="mb-8">
                    <CurrentFocusCard recommendation={adaptiveRec} />
                </div>


                
                <OverallScoreCard score={data.summary?.overallScore} />
                
                <PerformanceCards summary={data.summary} />
                
                <div className="grid lg:grid-cols-3 gap-6 mb-8">
                    <div className="lg:col-span-2">
                        <AIInsightCard insight={data.aiInsight} />
                    </div>
                    <div className="lg:col-span-1">
                        <RecommendedActionCard action={data.recommendedAction} />
                    </div>
                </div>
                
                <TopicPerformance strongest={data.strongestTopics} weakest={data.weakestTopics} />
                
                <div className="grid lg:grid-cols-3 gap-6 mb-8">
                    <div className="lg:col-span-2">
                        <ProgressChart progress={data.progress} />
                    </div>
                    <div className="lg:col-span-1">
                        <RecentActivity activity={data.recentActivity} />
                    </div>
                </div>

                
                <QuickActions />

            </div>
        </div>
    );
};

export default Dashboard;
