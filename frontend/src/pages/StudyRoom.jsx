import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { BookOpen, Layers, Send, Loader2, Target, Code, MessageCircle, AlertCircle, Save, CheckCircle2, RotateCcw, ChevronRight } from 'lucide-react';
import FeedbackCard from '../components/FeedbackCard';

const StudyRoom = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const [curricula, setCurricula] = useState([]);
    const [selectedCurriculumId, setSelectedCurriculumId] = useState('');
    const [topics, setTopics] = useState([]);
    const [selectedTopicId, setSelectedTopicId] = useState('');
    const [topicDetails, setTopicDetails] = useState(null);
    
    const [explanation, setExplanation] = useState('');
    const [learningMode, setLearningMode] = useState('technical');
    const [isLoading, setIsLoading] = useState(false);
    const [evaluation, setEvaluation] = useState(null);
    const [error, setError] = useState(null);
    const [saveStatus, setSaveStatus] = useState('');

    const modes = [
        { id: 'general', label: 'General Knowledge', icon: Target, description: 'Core concepts & analogies' },
        { id: 'technical', label: 'Technical & DSA', icon: Code, description: 'Complexity & logic' },
        { id: 'fluency', label: 'English Fluency', icon: MessageCircle, description: 'Tone & vocabulary' }
    ];

    // Load curricula
    useEffect(() => {
        fetch('http://localhost:8000/api/curricula')
            .then(res => res.json())
            .then(data => {
                setCurricula(data.curricula || []);
                // If coming from SyllabusTracker with pre-selected
                if (location.state?.curriculumId) {
                    setSelectedCurriculumId(location.state.curriculumId.toString());
                }
            })
            .catch(err => console.error(err));
    }, [location.state]);

    // Load topics when curriculum changes
    useEffect(() => {
        if (!selectedCurriculumId) {
            setTopics([]);
            return;
        }
        fetch(`http://localhost:8000/api/curricula/${selectedCurriculumId}`)
            .then(res => res.json())
            .then(data => {
                setTopics(data.topics || []);
                // Auto-select topic if passed via location state
                if (location.state?.topicId) {
                    setSelectedTopicId(location.state.topicId.toString());
                    // clear state so it doesn't get stuck if user changes curriculum
                    window.history.replaceState({}, document.title)
                } else if (data.topics && data.topics.length > 0) {
                    setSelectedTopicId('');
                }
            })
            .catch(err => console.error(err));
    }, [selectedCurriculumId, location.state]);

    // Fetch topic details and load draft
    useEffect(() => {
        if (!selectedTopicId) {
            setTopicDetails(null);
            setExplanation('');
            return;
        }
        
        fetch(`http://localhost:8000/api/topics/${selectedTopicId}`)
            .then(res => res.json())
            .then(data => {
                setTopicDetails(data);
                // Load draft
                const draft = sessionStorage.getItem(`draft_${selectedTopicId}`);
                if (draft) {
                    setExplanation(draft);
                } else {
                    setExplanation('');
                }
            })
            .catch(err => console.error(err));
    }, [selectedTopicId]);

    // Auto-save draft
    useEffect(() => {
        if (!selectedTopicId) return;
        
        const saveDraft = () => {
            if (explanation.trim().length > 0) {
                sessionStorage.setItem(`draft_${selectedTopicId}`, explanation);
                setSaveStatus('Draft saved');
                setTimeout(() => setSaveStatus(''), 2000);
            }
        };

        const interval = setInterval(saveDraft, 10000);
        return () => clearInterval(interval);
    }, [explanation, selectedTopicId]);

    const handleSubmit = async () => {
        if (!selectedTopicId || !explanation.trim()) return;

        setIsLoading(true);
        setError(null);
        setEvaluation(null);

        try {
            const res = await fetch('http://localhost:8000/api/evaluate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    topic_id: parseInt(selectedTopicId),
                    topic: topicDetails.name,
                    explanation,
                    learning_mode: learningMode
                })
            });
            
            if (!res.ok) throw new Error('Evaluation failed');
            const data = await res.json();
            setEvaluation(data);
            // Clear draft on successful submit
            sessionStorage.removeItem(`draft_${selectedTopicId}`);
        } catch (err) {
            console.error(err);
            setError('Failed to get evaluation. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleNextTopic = () => {
        setEvaluation(null);
        setExplanation('');
        
        const currentIndex = topics.findIndex(t => t.id.toString() === selectedTopicId);
        if (currentIndex !== -1 && currentIndex < topics.length - 1) {
            setSelectedTopicId(topics[currentIndex + 1].id.toString());
        }
    };

    const wordCount = explanation.trim() ? explanation.trim().split(/\s+/).length : 0;

    return (
        <div className="p-8 max-w-5xl mx-auto w-full pb-20">
            <h1 className="text-4xl font-black mb-8 flex items-center gap-3">
                <BookOpen className="w-8 h-8 text-indigo-400" />
                Reverse Learning Studio
            </h1>

            {/* Selectors */}
            <div className="bg-slate-800 p-6 rounded-2xl border border-slate-700 shadow-lg mb-8 flex flex-col md:flex-row gap-4">
                <div className="flex-1">
                    <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Curriculum</label>
                    <select 
                        value={selectedCurriculumId}
                        onChange={(e) => {
                            setSelectedCurriculumId(e.target.value);
                            setEvaluation(null);
                        }}
                        className="w-full bg-slate-900 border border-slate-700 rounded-lg py-3 px-4 text-white focus:outline-none focus:border-indigo-500 transition-colors"
                    >
                        <option value="">-- Select Curriculum --</option>
                        {curricula.map(c => (
                            <option key={c.id} value={c.id}>{c.name}</option>
                        ))}
                    </select>
                </div>
                
                <div className="flex-1">
                    <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Topic</label>
                    <select 
                        value={selectedTopicId}
                        onChange={(e) => {
                            setSelectedTopicId(e.target.value);
                            setEvaluation(null);
                        }}
                        disabled={!selectedCurriculumId || topics.length === 0}
                        className="w-full bg-slate-900 border border-slate-700 rounded-lg py-3 px-4 text-white focus:outline-none focus:border-indigo-500 transition-colors disabled:opacity-50"
                    >
                        <option value="">-- Select Topic --</option>
                        {topics.map((t, idx) => (
                            <option key={t.id} value={t.id}>{idx + 1}. {t.name}</option>
                        ))}
                    </select>
                </div>
            </div>

            {topicDetails && !evaluation && (
                <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    <div className="bg-indigo-900/30 border border-indigo-500/30 rounded-xl p-6">
                        <h2 className="text-2xl font-bold text-white mb-2">Topic: {topicDetails.name}</h2>
                        <p className="text-indigo-200">{topicDetails.description}</p>
                        <div className="mt-4 pt-4 border-t border-indigo-500/20 text-sm font-medium text-indigo-300">
                            Task: Explain how {topicDetails.name} works to test your understanding.
                        </div>
                    </div>

                    <div className="bg-slate-800 rounded-2xl border border-slate-700 shadow-lg overflow-hidden">
                        <div className="p-4 bg-slate-800/80 border-b border-slate-700 flex justify-between items-center">
                            <span className="font-semibold text-slate-300">Your Explanation</span>
                            <div className="flex items-center gap-4">
                                {saveStatus && <span className="text-xs text-green-400 flex items-center gap-1"><CheckCircle2 className="w-3 h-3"/> {saveStatus}</span>}
                                <span className="text-xs text-slate-500 font-mono bg-slate-900 px-2 py-1 rounded">{wordCount} words</span>
                            </div>
                        </div>
                        <textarea
                            value={explanation}
                            onChange={(e) => setExplanation(e.target.value)}
                            placeholder={`Start explaining ${topicDetails.name} here...`}
                            className="w-full h-64 bg-slate-900 text-slate-100 p-6 focus:outline-none resize-none leading-relaxed"
                        ></textarea>
                        
                        <div className="p-6 bg-slate-800/80 border-t border-slate-700">
                            <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
                                <Layers className="w-4 h-4 inline-block mr-1 text-indigo-400" /> Learning Mode
                            </label>
                            <div className="flex flex-wrap gap-3 mb-6">
                                {modes.map((mode) => (
                                    <button
                                        key={mode.id}
                                        onClick={() => setLearningMode(mode.id)}
                                        className={`flex flex-col items-start p-4 transition-all duration-300 text-left flex-1 min-w-[140px] border rounded-xl
                                            ${learningMode === mode.id
                                                ? 'bg-indigo-600 border-indigo-500 text-white shadow-md'
                                                : 'bg-slate-900 text-slate-400 border-slate-700 hover:border-slate-600'}`}
                                    >
                                        <div className="flex items-center gap-2 mb-1">
                                            <mode.icon className={`w-4 h-4 ${learningMode === mode.id ? 'text-white' : 'text-indigo-400'}`} />
                                            <span className="text-sm font-bold">{mode.label}</span>
                                        </div>
                                        <span className={`text-xs ${learningMode === mode.id ? 'text-indigo-200' : 'text-slate-500'}`}>
                                            {mode.description}
                                        </span>
                                    </button>
                                ))}
                            </div>

                            {error && (
                                <div className="mb-6 p-4 bg-red-900/30 border border-red-500/30 rounded-lg flex items-center gap-2 text-red-400">
                                    <AlertCircle className="w-5 h-5" /> {error}
                                </div>
                            )}

                            <div className="flex gap-4">
                                <button
                                    onClick={handleSubmit}
                                    disabled={isLoading || explanation.trim().length < 10}
                                    className="flex-1 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-700 disabled:text-slate-500 text-white py-4 rounded-xl font-bold flex items-center justify-center gap-2 transition-colors shadow-lg hover:shadow-indigo-500/25"
                                >
                                    {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                                    {isLoading ? 'Evaluating...' : 'Submit for Evaluation'}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {evaluation && (
                <div className="space-y-6 animate-in slide-in-from-bottom-8 duration-700">
                    <div className="bg-slate-800 rounded-3xl border border-slate-700 shadow-2xl overflow-hidden p-8">
                        <div className="flex justify-between items-start mb-8">
                            <h2 className="text-3xl font-black text-white">AI Feedback</h2>
                            
                            <div className="flex items-center justify-center w-24 h-24 rounded-full border-4 shadow-lg shrink-0" 
                                style={{
                                    borderColor: evaluation.score >= 8 ? '#10b981' : evaluation.score >= 5 ? '#f59e0b' : '#ef4444',
                                    background: 'rgba(15, 23, 42, 0.5)'
                                }}>
                                <div className="text-center">
                                    <span className="text-3xl font-black text-white">{evaluation.score}</span>
                                    <span className="text-sm text-slate-400 block -mt-1">/ 10</span>
                                </div>
                            </div>
                        </div>
                        
                        {evaluation.summary && (
                            <div className="mb-8">
                                <h3 className="text-lg font-bold text-slate-300 mb-2 border-b border-slate-700 pb-2">Summary</h3>
                                <p className="text-slate-300 leading-relaxed text-lg">{evaluation.summary}</p>
                            </div>
                        )}
                        
                        <div className="grid md:grid-cols-2 gap-6 mb-8">
                            {evaluation.grammar_issues && evaluation.grammar_issues.length > 0 && (
                                <div className="bg-slate-900 rounded-xl p-6 border border-slate-700">
                                    <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4">Grammar & Clarity</h3>
                                    <ul className="space-y-3">
                                        {evaluation.grammar_issues.map((issue, i) => (
                                            <li key={i} className="flex gap-2 text-sm">
                                                <span className="text-red-400 shrink-0 mt-0.5">•</span>
                                                <span className="text-slate-300">{issue}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {evaluation.vocabulary_suggestions && evaluation.vocabulary_suggestions.length > 0 && (
                                <div className="bg-slate-900 rounded-xl p-6 border border-slate-700">
                                    <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4">Vocabulary Suggestions</h3>
                                    <div className="flex flex-wrap gap-2">
                                        {evaluation.vocabulary_suggestions.map((word, i) => (
                                            <span key={i} className="bg-indigo-900/50 text-indigo-300 border border-indigo-500/30 px-3 py-1.5 rounded-full text-sm font-medium">
                                                {word}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                        
                        {evaluation.advanced_version && (
                            <div className="mb-8 bg-slate-900/50 rounded-xl p-6 border border-slate-700 border-l-4 border-l-indigo-500">
                                <h3 className="text-sm font-bold text-indigo-400 uppercase tracking-wider mb-4">Advanced Explanation Version</h3>
                                <p className="text-slate-300 leading-relaxed italic">"{evaluation.advanced_version}"</p>
                            </div>
                        )}
                        
                        {evaluation.follow_up_question && (
                            <div className="mb-8 bg-blue-900/20 rounded-xl p-6 border border-blue-500/30">
                                <h3 className="text-sm font-bold text-blue-400 uppercase tracking-wider mb-2 flex items-center gap-2">
                                    <MessageCircle className="w-4 h-4" /> Challenge Question
                                </h3>
                                <p className="text-slate-200 text-lg font-medium">{evaluation.follow_up_question}</p>
                            </div>
                        )}
                        
                        <div className="flex flex-col sm:flex-row gap-4 mt-8 pt-8 border-t border-slate-700">
                            <button 
                                onClick={() => setEvaluation(null)}
                                className="px-6 py-3 bg-slate-800 hover:bg-slate-700 text-white rounded-xl font-medium transition-colors flex items-center justify-center gap-2"
                            >
                                <RotateCcw className="w-5 h-5" /> Retry This Topic
                            </button>
                            
                            <button 
                                onClick={handleNextTopic}
                                className="flex-1 px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-medium transition-colors flex items-center justify-center gap-2 shadow-lg"
                            >
                                Next Topic <ChevronRight className="w-5 h-5" />
                            </button>
                        </div>
                        
                        <div className="mt-6 text-center text-sm text-green-400 flex items-center justify-center gap-2">
                            <CheckCircle2 className="w-4 h-4" /> Evaluation successfully saved to your Study History
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default StudyRoom;
