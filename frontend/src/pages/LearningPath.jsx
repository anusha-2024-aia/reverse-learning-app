import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import api from '../services/api';
import RoadmapTimeline from '../components/roadmap/RoadmapTimeline';
import RoadmapHistory from '../components/roadmap/RoadmapHistory';
import DailyPlanCard from '../components/roadmap/DailyPlanCard';
import OnboardingModal from '../components/roadmap/OnboardingModal';
import PreferencesModal from '../components/roadmap/PreferencesModal';
import { 
  Sparkles, Target, Clock, RefreshCw, Sliders, ArrowRight, 
  AlertTriangle, CheckCircle2, Award, Brain, Rocket, Loader2 
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const LearningPath = () => {
  const { token } = useContext(AuthContext);
  const navigate = useNavigate();

  const [roadmapData, setRoadmapData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [recalculating, setRecalculating] = useState(false);
  const [error, setError] = useState(null);

  const [showOnboarding, setShowOnboarding] = useState(false);
  const [showPreferences, setShowPreferences] = useState(false);

  const fetchRoadmap = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.get('/roadmap/mine');
      setRoadmapData(res.data);

      if (!res.data || !res.data.roadmap_id || !res.data.onboarding_completed) {
        setShowOnboarding(true);
      }
    } catch (err) {
      console.error("Failed to fetch roadmap:", err);
      setError("Unable to load your dynamic roadmap. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      fetchRoadmap();
    }
  }, [token]);

  const handleRecalculate = async () => {
    try {
      setRecalculating(true);
      const res = await api.post('/roadmap/recalculate');
      setRoadmapData(res.data);
    } catch (err) {
      console.error("Failed to recalculate roadmap:", err);
    } finally {
      setRecalculating(false);
    }
  };

  const handleOnboardingComplete = async (payload) => {
    try {
      setLoading(true);
      const res = await api.post('/roadmap/onboarding', payload);
      setRoadmapData(res.data);
      setShowOnboarding(false);
    } catch (err) {
      console.error("Onboarding error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdatePreferences = async (payload) => {
    try {
      setLoading(true);
      const res = await api.patch('/roadmap/preferences', payload);
      setRoadmapData(res.data);
      setShowPreferences(false);
    } catch (err) {
      console.error("Failed to update preferences:", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !roadmapData) {
    return (
      <div className="flex-1 overflow-y-auto bg-slate-900 p-8 flex flex-col items-center justify-center">
        <Loader2 className="w-10 h-10 text-indigo-400 animate-spin mb-4" />
        <p className="text-slate-400 text-sm font-medium animate-pulse">Building your dynamic career roadmap...</p>
      </div>
    );
  }

  const currentFocus = roadmapData?.current_focus;
  const items = roadmapData?.items || [];
  const progress = roadmapData?.progress || 0.0;
  const targetRole = roadmapData?.target_role || "Full Stack Developer";
  const estimatedHours = roadmapData?.estimated_hours || 0;
  const estimatedDays = roadmapData?.estimated_days || 0;

  return (
    <div className="flex-1 overflow-y-auto bg-slate-900 text-slate-100 p-4 md:p-8 lg:p-12 relative">
      <div className="max-w-7xl mx-auto space-y-8">

        {/* TOP HEADER & ROADMAP OVERVIEW BANNER */}
        <div className="bg-gradient-to-r from-slate-900 via-indigo-950/60 to-slate-900 border border-slate-800 rounded-3xl p-6 md:p-8 shadow-2xl relative overflow-hidden">
          
          <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl -z-0"></div>

          <div className="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
            <div className="space-y-2">
              <div className="flex flex-wrap items-center gap-2">
                <span className="bg-indigo-600 text-white text-xs font-black uppercase tracking-wider px-3 py-1 rounded-lg shadow-md flex items-center gap-1.5">
                  <Target className="w-3.5 h-3.5" /> {targetRole}
                </span>
                <span className="bg-slate-800 text-slate-300 text-xs font-semibold px-3 py-1 rounded-lg border border-slate-700">
                  Pace: {roadmapData?.hours_per_day || 2} hrs/day
                </span>
                {roadmapData?.experience_level && (
                  <span className="bg-slate-800 text-indigo-300 text-xs font-semibold px-3 py-1 rounded-lg border border-slate-700">
                    {roadmapData.experience_level}
                  </span>
                )}
              </div>

              <h1 className="text-3xl md:text-4xl font-black text-white tracking-tight">
                Dynamic Career Roadmap
              </h1>
              <p className="text-slate-400 text-sm max-w-2xl">
                Continuously recalculated based on your actual demonstrated evaluation performance, knowledge gaps, and career goals.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-3 w-full md:w-auto justify-start md:justify-end">
              <button
                onClick={() => setShowPreferences(true)}
                className="px-4 py-2.5 bg-slate-800/80 hover:bg-slate-750 text-slate-200 border border-slate-700 rounded-xl text-xs font-bold transition-all flex items-center gap-2"
              >
                <Sliders className="w-4 h-4 text-indigo-400" /> Edit Goal / Pace
              </button>

              <button
                onClick={handleRecalculate}
                disabled={recalculating}
                className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition-all shadow-lg shadow-indigo-600/30 flex items-center gap-2"
              >
                <RefreshCw className={`w-4 h-4 ${recalculating ? 'animate-spin' : ''}`} />
                {recalculating ? 'Recalculating...' : 'Recalculate Now'}
              </button>
            </div>
          </div>

          {/* ROADMAP PROGRESS METRICS */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8 pt-6 border-t border-slate-800/80">
            
            <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-2xl flex items-center gap-4">
              <div className="p-3 bg-indigo-600/20 text-indigo-400 rounded-xl border border-indigo-500/30">
                <Award className="w-6 h-6" />
              </div>
              <div>
                <span className="text-xs text-slate-400 font-medium">Overall Mastery Progress</span>
                <div className="flex items-center gap-2 mt-0.5">
                  <span className="text-2xl font-black text-white">{progress}%</span>
                  <div className="w-24 bg-slate-800 h-2 rounded-full overflow-hidden">
                    <div className="bg-gradient-to-r from-indigo-500 to-emerald-400 h-full" style={{ width: `${progress}%` }}></div>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-2xl flex items-center gap-4">
              <div className="p-3 bg-emerald-600/20 text-emerald-400 rounded-xl border border-emerald-500/30">
                <Clock className="w-6 h-6" />
              </div>
              <div>
                <span className="text-xs text-slate-400 font-medium">Remaining Study Time</span>
                <p className="text-2xl font-black text-white">{estimatedHours} <span className="text-xs text-slate-400 font-normal">hours</span></p>
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-2xl flex items-center gap-4">
              <div className="p-3 bg-purple-600/20 text-purple-400 rounded-xl border border-purple-500/30">
                <Rocket className="w-6 h-6" />
              </div>
              <div>
                <span className="text-xs text-slate-400 font-medium">Estimated Job Readiness</span>
                <p className="text-2xl font-black text-white">{estimatedDays} <span className="text-xs text-slate-400 font-normal">learning days</span></p>
              </div>
            </div>

          </div>

        </div>

        {/* ERROR STATE BANNER */}
        {error && (
          <div className="bg-rose-950/40 border border-rose-800 p-4 rounded-2xl text-rose-200 flex justify-between items-center text-sm">
            <span>{error}</span>
            <button onClick={fetchRoadmap} className="px-3 py-1 bg-rose-800 hover:bg-rose-700 text-white text-xs rounded-lg font-bold">
              Try Again
            </button>
          </div>
        )}

        {/* CURRENT FOCUS ALERT SECTION */}
        {currentFocus && (
          <div className={`p-6 rounded-3xl border shadow-xl transition-all ${
            currentFocus.status === 'WEAK' 
              ? 'bg-gradient-to-r from-rose-950/60 via-slate-900 to-slate-900 border-rose-500/80 shadow-rose-950/20 ring-1 ring-rose-500/30'
              : 'bg-gradient-to-r from-indigo-950/50 via-slate-900 to-slate-900 border-indigo-500/50'
          }`}>
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <div className="space-y-1.5 flex-1">
                <div className="flex items-center gap-2">
                  <span className={`text-xs font-black uppercase tracking-wider px-3 py-1 rounded-full ${
                    currentFocus.status === 'WEAK' ? 'bg-rose-600 text-white' : 'bg-indigo-600 text-white'
                  }`}>
                    🎯 CURRENT FOCUS TOPIC
                  </span>
                  <span className="text-xs text-slate-400">Mastery: <strong>{Math.round(currentFocus.mastery_score)}%</strong></span>
                </div>

                <h2 className="text-2xl font-black text-white">{currentFocus.topic_name}</h2>
                <p className="text-sm text-slate-300 font-medium">
                  {currentFocus.reason || `Based on your recent performance, mastering ${currentFocus.topic_name} is your top priority.`}
                </p>
              </div>

              <button
                onClick={() => navigate(`/study?topic=${encodeURIComponent(currentFocus.topic_name)}`)}
                className={`px-6 py-3.5 rounded-2xl font-black text-sm text-white flex items-center gap-2 shadow-lg transition-all flex-shrink-0 ${
                  currentFocus.status === 'WEAK'
                    ? 'bg-rose-600 hover:bg-rose-500 shadow-rose-600/30'
                    : 'bg-indigo-600 hover:bg-indigo-500 shadow-indigo-600/30'
                }`}
              >
                <span>Continue Learning</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* MAIN TWO-COLUMN DASHBOARD LAYOUT */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">

          {/* LEFT COLUMN: DAILY PLAN & TIMELINE (2 cols) */}
          <div className="lg:col-span-2 space-y-8">

            {/* Daily Learning Plan */}
            <DailyPlanCard dailyPlan={roadmapData?.daily_plan} />

            {/* Complete Roadmap Timeline */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-black text-white flex items-center gap-2">
                  <span>🗺️</span> Full Learning Pathway ({items.length} topics)
                </h2>
                <span className="text-xs text-slate-500 font-semibold uppercase">Sequential Priority Queue</span>
              </div>

              <RoadmapTimeline items={items} />
            </div>

          </div>

          {/* RIGHT COLUMN: CHANGE HISTORY FEED (1 col) */}
          <div className="lg:col-span-1 space-y-6 sticky top-24">
            <RoadmapHistory history={roadmapData?.history || []} />

            {/* Re-generate Roadmap Banner */}
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-3 text-xs text-slate-400">
              <div className="font-bold text-slate-200 text-sm flex items-center gap-2">
                <Brain className="w-4 h-4 text-indigo-400" /> Career Goal Changed?
              </div>
              <p>
                You can re-generate your complete roadmap at any time by updating your target role or experience preferences.
              </p>
              <button
                onClick={() => setShowOnboarding(true)}
                className="w-full py-2.5 bg-slate-800 hover:bg-slate-750 text-indigo-300 font-bold rounded-xl border border-slate-700 transition-colors"
              >
                Re-Run Onboarding Wizard
              </button>
            </div>
          </div>

        </div>

      </div>

      {/* MODALS */}
      <OnboardingModal
        isOpen={showOnboarding}
        onClose={() => setShowOnboarding(false)}
        onComplete={handleOnboardingComplete}
      />

      <PreferencesModal
        isOpen={showPreferences}
        onClose={() => setShowPreferences(false)}
        currentPreferences={{
          target_role: targetRole,
          hours_per_day: roadmapData?.hours_per_day || 2.0,
          days_per_week: roadmapData?.days_per_week || 6,
          experience_level: roadmapData?.experience_level || "BEGINNER",
          career_goal: roadmapData?.career_goal || ""
        }}
        onSave={handleUpdatePreferences}
      />

    </div>
  );
};

export default LearningPath;
