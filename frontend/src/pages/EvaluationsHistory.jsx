import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Target, Award, Calendar, ChevronRight, BarChart2, Loader2, RefreshCw } from 'lucide-react';
import TopicTimeline from '../components/evaluations/TopicTimeline';

const EvaluationsHistory = () => {
  const [evaluations, setEvaluations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTopicId, setSelectedTopicId] = useState(null);
  const [selectedTopicData, setSelectedTopicData] = useState(null);
  const [loadingTimeline, setLoadingTimeline] = useState(false);

  const fetchEvaluations = async () => {
    setLoading(true);
    try {
      const res = await api.get('/evaluations/mine');
      setEvaluations(res.data || []);
    } catch (err) {
      console.error("Failed to load evaluation history", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvaluations();
  }, []);

  const handleSelectTopic = async (topicId) => {
    setSelectedTopicId(topicId);
    setLoadingTimeline(true);
    try {
      const res = await api.get(`/evaluations/topic/${topicId}`);
      setSelectedTopicData(res.data);
    } catch (err) {
      console.error("Failed to load topic timeline", err);
    } finally {
      setLoadingTimeline(false);
    }
  };

  // Group evaluations by topic
  const topicMap = {};
  evaluations.forEach(e => {
    if (!topicMap[e.topic_id]) {
      topicMap[e.topic_id] = {
        topic_id: e.topic_id,
        topic_name: e.topic_name,
        curriculum_name: e.curriculum_name,
        attempts: 0,
        best_score: 0,
        latest_score: e.overall_score || e.ai_score || 0,
        last_date: e.created_at
      };
    }
    const t = topicMap[e.topic_id];
    t.attempts += 1;
    const score = e.overall_score || e.ai_score || 0;
    if (score > t.best_score) t.best_score = score;
  });

  const topicList = Object.values(topicMap);

  return (
    <div className="p-8 max-w-7xl mx-auto w-full pb-20">
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
        <div>
          <h1 className="text-4xl font-black text-white flex items-center gap-3">
            <Award className="text-indigo-400 w-10 h-10" />
            Evaluation History
          </h1>
          <p className="text-slate-400 mt-2 text-lg">
            Review your multi-dimensional attempt trajectories and longitudinal performance improvements.
          </p>
        </div>
        <button
          onClick={fetchEvaluations}
          className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 text-sm font-medium transition-colors"
        >
          <RefreshCw className="w-4 h-4" /> Refresh
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <Loader2 className="w-10 h-10 text-indigo-400 animate-spin" />
        </div>
      ) : topicList.length === 0 ? (
        <div className="bg-slate-800 rounded-2xl p-12 border border-slate-700 text-center space-y-4">
          <BarChart2 className="w-16 h-16 text-slate-600 mx-auto" />
          <h3 className="text-xl font-bold text-slate-200">No evaluations yet!</h3>
          <p className="text-slate-400 max-w-md mx-auto">
            Complete your first explanation evaluation in the Study Room to start tracking multi-dimensional score trends.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Topics Table / List */}
          <div className="lg:col-span-1 space-y-3">
            <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">Evaluated Topics</h3>
            {topicList.map((item) => {
              const isSelected = selectedTopicId === item.topic_id;
              return (
                <div
                  key={item.topic_id}
                  onClick={() => handleSelectTopic(item.topic_id)}
                  className={`bg-slate-800 rounded-xl p-4 border transition-all cursor-pointer hover:border-indigo-500/80 ${
                    isSelected ? 'border-indigo-500 ring-2 ring-indigo-500/20 bg-slate-800/90' : 'border-slate-700'
                  }`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h4 className="font-bold text-slate-100">{item.topic_name}</h4>
                      <span className="text-xs text-slate-400">{item.curriculum_name}</span>
                    </div>
                    <ChevronRight className={`w-5 h-5 transition-transform ${isSelected ? 'text-indigo-400 translate-x-1' : 'text-slate-500'}`} />
                  </div>

                  <div className="flex items-center gap-4 text-xs text-slate-300 mt-3 pt-3 border-t border-slate-700/50">
                    <div>
                      <span className="text-slate-500">Latest:</span> <span className="font-bold text-indigo-400">{item.latest_score}%</span>
                    </div>
                    <div>
                      <span className="text-slate-500">Best:</span> <span className="font-bold text-emerald-400">{item.best_score}%</span>
                    </div>
                    <div>
                      <span className="text-slate-500">Attempts:</span> <span className="font-bold">{item.attempts}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Timeline Detail View */}
          <div className="lg:col-span-2">
            {loadingTimeline ? (
              <div className="bg-slate-800 rounded-2xl p-12 border border-slate-700 flex justify-center items-center min-h-[400px]">
                <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
              </div>
            ) : selectedTopicData ? (
              <TopicTimeline topicData={selectedTopicData} />
            ) : (
              <div className="bg-slate-800/40 rounded-2xl p-12 border border-slate-700/60 border-dashed text-center flex flex-col items-center justify-center min-h-[400px] text-slate-400 space-y-2">
                <Target className="w-12 h-12 opacity-30 text-indigo-400" />
                <h4 className="font-bold text-slate-300">Select a Topic</h4>
                <p className="text-xs text-slate-400 max-w-xs">
                  Click any topic on the left to inspect its multi-dimensional score trajectory and attempt timeline.
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default EvaluationsHistory;
