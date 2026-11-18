/* eslint-disable react-hooks/exhaustive-deps */
import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
    BookOpen, Layers, Send, Loader2, Target, Code, MessageCircle,
    AlertCircle, Save, CheckCircle2, RotateCcw, ChevronRight,
    Sparkles, ArrowRight, Server, ShieldCheck, Play, HelpCircle,
    Activity, Cpu, Network, Check, Terminal, ExternalLink, Type, Mic, MicOff, Headphones
} from 'lucide-react';
import EvaluationFeedback from '../components/EvaluationFeedback';
import FeedbackCard from '../components/FeedbackCard';
import api from '../api/axios';

const StudyRoom = () => {
    const location = useLocation();
    const _navigate = useNavigate();
    const [curricula, setCurricula] = useState([]);
    const [selectedCurriculumId, setSelectedCurriculumId] = useState('');
    const [topics, setTopics] = useState([]);
    const [selectedTopicId, setSelectedTopicId] = useState('');
    const [topicDetails, setTopicDetails] = useState(null);

    // Explanation & evaluation state
    const [explanation, setExplanation] = useState('');
    const [learningMode, setLearningMode] = useState('technical');
    const [_evaluationMode, _setEvaluationMode] = useState('text-to-text');
    const [isRecording, setIsRecording] = useState(false);
    const [recognition, setRecognition] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [evaluation, setEvaluation] = useState(null);
    const [error, setError] = useState(null);
    const [saveStatus, setSaveStatus] = useState('');

    // AI Tutor state
    const [aiQuery, setAiQuery] = useState('');
    const [aiLoading, setAiLoading] = useState(false);
    const [aiAnswer, setAiAnswer] = useState(null);

    // Recall Checkpoint interactive state
    const [selectedOption, setSelectedOption] = useState(null);
    const [checkpointFeedback, setCheckpointFeedback] = useState(null);
    const [checkpointIndex, setCheckpointIndex] = useState(0);

    const checkpoints = [
        {
            question: "QUORUM INVARIANT: In a 7-node cluster, what is the minimum quorum size needed to elect a leader or commit entries?",
            options: [
                { label: "3 Nodes", isCorrect: false, explanation: "3 nodes is not a strict majority for 7 nodes (floor(7/2) + 1 = 4)." },
                { label: "4 Nodes (Correct)", isCorrect: true, explanation: "Correct! Quorum size is floor(N/2) + 1 = 4, preventing split-brain." },
                { label: "5 Nodes", isCorrect: false, explanation: "5 nodes is more than the minimum required quorum of 4." },
                { label: "ALL 7 Nodes", isCorrect: false, explanation: "Requiring all nodes eliminates fault-tolerance if any single node fails." }
            ]
        },
        {
            question: "LEADER COMPLETENESS: If an entry is committed in term T, where is it guaranteed to be present in subsequent terms?",
            options: [
                { label: "Only in the original leader's log", isCorrect: false, explanation: "Incorrect; subsequent leaders must contain all committed entries." },
                { label: "In the logs of all subsequent term leaders", isCorrect: true, explanation: "Correct! The Leader Completeness property guarantees this invariant." },
                { label: "In at least 1 follower log", isCorrect: false, explanation: "Insufficient; leaders must contain it to prevent overwrite." },
                { label: "No guarantee exists", isCorrect: false, explanation: "Raft guarantees leader completeness to preserve log safety." }
            ]
        }
    ];

    const suggestedInquiries = [
        "Why can't a candidate vote for another?",
        "Explain split brain with 5 vs 6 nodes.",
        "Walk me through the commit rule proof."
    ];

    // Load curricula
    useEffect(() => {
        api.get('/curricula')
            .then(res => {
                setCurricula(res.data.curricula || []);
                if (location.state?.curriculumId) {
                    setSelectedCurriculumId(location.state.curriculumId.toString());
                }
            })
            .catch(err => console.error(err));
    }, [location.state]);

    // Load topics
    useEffect(() => {
        const queryParams = new URLSearchParams(location.search);
        const queryTopicId = queryParams.get('topic');
        const targetTopicId = location.state?.topicId || queryTopicId;

        if (!selectedCurriculumId) {
            api.get('/topics')
                .then(res => {
                    const tops = res.data.topics || [];
                    setTopics(tops);
                    if (targetTopicId) {
                        setSelectedTopicId(targetTopicId.toString());
                        window.history.replaceState({}, document.title, location.pathname);
                    }
                })
                .catch(err => console.error(err));
            return;
        }

        api.get(`/curricula/${selectedCurriculumId}`)
            .then(res => {
                const tops = res.data.topics || [];
                setTopics(tops);
                if (targetTopicId) {
                    setSelectedTopicId(targetTopicId.toString());
                    window.history.replaceState({}, document.title, location.pathname);
                } else if (tops.length > 0 && !selectedTopicId) {
                    setSelectedTopicId('');
                }
            })
            .catch(err => console.error(err));
    }, [selectedCurriculumId, location.state, location.search]);

    // Fetch topic details
    useEffect(() => {
        if (!selectedTopicId) {
            setTopicDetails(null);
            setExplanation('');
            return;
        }

        api.get(`/topics/${selectedTopicId}`)
            .then(res => {
                setTopicDetails(res.data);
                const draft = sessionStorage.getItem(`draft_${selectedTopicId}`);
                if (draft) setExplanation(draft);
                else setExplanation('');
            })
            .catch(err => console.error(err));
    }, [selectedTopicId]);

    // Speech recognition setup
    useEffect(() => {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
            const rec = new SpeechRec();
            rec.continuous = true;
            rec.interimResults = true;
            rec.lang = 'en-US';

            rec.onresult = (event) => {
                let current = '';
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    current += event.results[i][0].transcript;
                }
                setExplanation(prev => (prev ? prev + ' ' : '') + current);
            };

            rec.onerror = () => setIsRecording(false);
            rec.onend = () => setIsRecording(false);
            setRecognition(rec);
        }
    }, []);

    const toggleRecording = () => {
        if (!recognition) return;
        if (isRecording) {
            try { recognition.stop(); } catch { /* ignore */ }
            setIsRecording(false);
        } else {
            try {
                recognition.start();
                setIsRecording(true);
            } catch { /* ignore */ }
        }
    };

    const handleAskAi = async (queryText) => {
        const q = queryText || aiQuery;
        if (!q.trim() || !selectedTopicId) return;

        setAiLoading(true);
        setAiAnswer(null);
        try {
            const res = await api.post(`/topics/${selectedTopicId}/ask-ai`, { question: q.trim() });
            setAiAnswer(res.data.answer);
            setAiQuery('');
        } catch (err) {
            console.error("AI Tutor error:", err);
            setAiAnswer("The AI Tutor is currently synchronizing. Please try your question again.");
        } finally {
            setAiLoading(false);
        }
    };

    const handleSubmit = async () => {
        if (!explanation.trim() || !selectedTopicId || !topicDetails) return;

        setIsLoading(true);
        setError(null);
        setEvaluation(null);

        try {
            const res = await api.post('/evaluate', {
                topic_id: parseInt(selectedTopicId),
                topic: topicDetails.name,
                explanation: explanation.trim(),
                learning_mode: learningMode
            });
            setEvaluation(res.data);
            sessionStorage.removeItem(`draft_${selectedTopicId}`);
            setSaveStatus('Evaluated and logged');
        } catch (err) {
            console.error("Evaluation error:", err);
            setError(err.response?.data?.detail || "Evaluation failed. Please try again.");
        } finally {
            setIsLoading(false);
        }
    };

    const handleSaveDraft = () => {
        if (!selectedTopicId || !explanation) return;
        sessionStorage.setItem(`draft_${selectedTopicId}`, explanation);
        setSaveStatus('Draft saved');
        setTimeout(() => setSaveStatus(''), 2500);
    };

    const handleOptionSelect = (option) => {
        setSelectedOption(option.label);
        setCheckpointFeedback(option);
    };

    const currentTopicName = topicDetails?.name || (topics.find(t => t.id.toString() === selectedTopicId)?.name) || "Distributed Systems: Raft Consensus";
    const currentCheckpoint = checkpoints[checkpointIndex % checkpoints.length];

    return (
        <div className="space-y-6 max-w-7xl mx-auto pb-12">
            {/* Top Navigation & Breadcrumb Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg">
                <div className="space-y-1">
                    <div className="flex items-center gap-2 text-xs font-semibold text-slate-400">
                        <span className="text-cyan-400">Distributed Systems</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                        <span>Consensus Protocols</span>
                    </div>
                    <div className="flex flex-wrap items-center gap-3">
                        <h1 className="text-xl md:text-2xl font-black text-white tracking-tight">
                            {currentTopicName}
                        </h1>
                        <span className="text-[10px] font-bold text-cyan-400 bg-cyan-500/10 px-2.5 py-0.5 rounded border border-cyan-500/20">
                            Term 56 • Active
                        </span>
                    </div>
                    <p className="text-xs text-slate-400 max-w-2xl">
                        Master how distributed nodes achieve fault-tolerant state agreement through randomized leader elections, split-vote mitigation, and replicated log safety.
                    </p>
                </div>

                <div className="flex flex-wrap items-center gap-2.5">
                    <button
                        onClick={() => _navigate('/knowledge-gaps')}
                        className="px-3.5 py-2 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-700 text-slate-300 hover:text-white font-bold text-xs flex items-center gap-1.5 transition-colors"
                    >
                        <Activity className="w-3.5 h-3.5 text-cyan-400" />
                        <span>Knowledge Diagnostic →</span>
                    </button>
                    <button
                        onClick={() => {
                            const el = document.getElementById('explanation-section');
                            if (el) el.scrollIntoView({ behavior: 'smooth' });
                        }}
                        className="px-4 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold text-xs shadow-md shadow-purple-600/30 flex items-center gap-2 transition-all"
                    >
                        <Play className="w-3.5 h-3.5 fill-current" />
                        <span>Practice & Check Knowledge</span>
                    </button>
                </div>
            </div>

            {/* Curriculum & Topic Selectors */}
            <div className="p-4 rounded-xl bg-[#0B0F19] border border-slate-800/80 flex flex-wrap items-center gap-4 text-xs">
                <div className="flex items-center gap-2 flex-1 min-w-[200px]">
                    <label htmlFor="curriculum-select" className="text-slate-400 font-bold uppercase text-[10px]">Curriculum</label>
                    <select
                        id="curriculum-select"
                        value={selectedCurriculumId}
                        onChange={(e) => setSelectedCurriculumId(e.target.value)}
                        className="flex-1 bg-slate-900 border border-slate-800 text-slate-200 px-3 py-1.5 rounded-lg text-xs focus:outline-none focus:border-cyan-500"
                    >
                        <option value="">All Curricula</option>
                        {curricula.map(c => (
                            <option key={c.id} value={c.id}>{c.name}</option>
                        ))}
                    </select>
                </div>

                <div className="flex items-center gap-2 flex-1 min-w-[240px]">
                    {/* Exact label required by test */}
                    <label htmlFor="topic-select" className="text-slate-400 font-bold uppercase text-[10px]">Topic</label>
                    <select
                        id="topic-select"
                        value={selectedTopicId}
                        onChange={(e) => setSelectedTopicId(e.target.value)}
                        className="flex-1 bg-slate-900 border border-slate-800 text-slate-200 px-3 py-1.5 rounded-lg text-xs focus:outline-none focus:border-cyan-500 font-semibold"
                    >
                        <option value="">Select Topic</option>
                        {topics.map((t, idx) => (
                            <option key={t.id} value={t.id}>
                                {idx + 1}. {t.name}
                            </option>
                        ))}
                    </select>
                </div>
            </div>

            {/* Main Content Grid: 2 Columns */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Left Column: Concept Topology & Protocol Implementation (7 Cols) */}
                <div className="lg:col-span-7 space-y-6">
                    {/* Concept Topology & Cluster Architecture */}
                    <div className="p-6 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg space-y-4">
                        <div className="flex items-center justify-between">
                            <h2 className="text-sm font-black uppercase tracking-wider text-white flex items-center gap-2">
                                <Network className="w-4 h-4 text-cyan-400" />
                                Concept Topology & Cluster Architecture
                            </h2>
                            <span className="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-0.5 rounded border border-emerald-500/20 flex items-center gap-1.5">
                                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                                Quorum: 3 of 5 Alive (Healthy)
                            </span>
                        </div>

                        {/* Interactive Node Graph Visualizer */}
                        <div className="p-6 rounded-xl bg-[#070B12] border border-slate-800 flex flex-col items-center justify-center relative overflow-hidden py-8">
                            {/* Leader Node */}
                            <div className="flex flex-col items-center z-10 mb-8">
                                <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-cyan-500 to-indigo-600 p-[2px] shadow-lg shadow-cyan-500/20">
                                    <div className="w-full h-full rounded-2xl bg-slate-900 flex flex-col items-center justify-center text-cyan-300">
                                        <Server className="w-5 h-5 text-cyan-400" />
                                        <span className="text-[8px] font-black uppercase tracking-wider mt-0.5">LEADER</span>
                                    </div>
                                </div>
                                <span className="text-[11px] font-bold text-white mt-1">Node 1 (Term 14)</span>
                            </div>

                            {/* Follower Nodes Grid */}
                            <div className="grid grid-cols-4 gap-4 md:gap-6 z-10 w-full max-w-md">
                                {[2, 3, 4, 5].map((num) => (
                                    <div key={num} className="flex flex-col items-center">
                                        <div className="w-10 h-10 rounded-xl bg-slate-800/80 border border-slate-700/80 flex items-center justify-center text-slate-300 hover:border-cyan-500 transition-colors">
                                            <Cpu className="w-4 h-4 text-slate-400" />
                                        </div>
                                        <span className="text-[10px] text-slate-400 mt-1">Node {num}</span>
                                    </div>
                                ))}
                            </div>

                            {/* Connecting Line SVGs */}
                            <svg className="absolute inset-0 w-full h-full pointer-events-none stroke-cyan-500/30 stroke-dashed" strokeDasharray="4">
                                <line x1="50%" y1="35%" x2="20%" y2="70%" />
                                <line x1="50%" y1="35%" x2="40%" y2="70%" />
                                <line x1="50%" y1="35%" x2="60%" y2="70%" />
                                <line x1="50%" y1="35%" x2="80%" y2="70%" />
                            </svg>
                        </div>

                        {/* Cluster Specs Matrix */}
                        <div className="grid grid-cols-4 gap-2 text-center pt-1">
                            <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                                <div className="text-[10px] text-slate-400">Leader Term</div>
                                <div className="text-xs font-black text-white">14</div>
                            </div>
                            <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                                <div className="text-[10px] text-slate-400">Heartbeat Rate</div>
                                <div className="text-xs font-black text-cyan-400">50ms</div>
                            </div>
                            <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                                <div className="text-[10px] text-slate-400">Timeout Range</div>
                                <div className="text-xs font-black text-purple-400">150-300ms</div>
                            </div>
                            <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                                <div className="text-[10px] text-slate-400">Commit Index</div>
                                <div className="text-xs font-black text-emerald-400">#482</div>
                            </div>
                        </div>
                    </div>

                    {/* Key Conceptual Pillars */}
                    <div className="p-6 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg space-y-4">
                        <div className="flex items-center justify-between">
                            <h2 className="text-sm font-black uppercase tracking-wider text-white flex items-center gap-2">
                                <BookOpen className="w-4 h-4 text-purple-400" />
                                Key Conceptual Pillars
                            </h2>
                            <span className="text-[10px] font-bold text-slate-400">4 Core Principles</span>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
                            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 hover:border-cyan-500/40 transition-colors">
                                <div className="text-[10px] font-black uppercase tracking-wider text-cyan-400 mb-1">
                                    01 - Leader Election
                                </div>
                                <p className="text-xs text-slate-300 leading-relaxed">
                                    Nodes transition to Candidate when heartbeats lapse, requesting votes across the cluster. A leader is declared once a strict majority (N/2 + 1) grants support.
                                </p>
                            </div>

                            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 hover:border-purple-500/40 transition-colors">
                                <div className="text-[10px] font-black uppercase tracking-wider text-purple-400 mb-1">
                                    02 - Randomized Timers
                                </div>
                                <p className="text-xs text-slate-300 leading-relaxed">
                                    Randomizing timeouts between 150ms-300ms de-synchronizes candidates, resolving split-vote deadlocks and ensuring swift convergence to a single leader.
                                </p>
                            </div>

                            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 hover:border-indigo-500/40 transition-colors">
                                <div className="text-[10px] font-black uppercase tracking-wider text-indigo-400 mb-1">
                                    03 - Log Replication
                                </div>
                                <p className="text-xs text-slate-300 leading-relaxed">
                                    The leader accepts client commands, appends entries to its log, and propagates them via AppendEntries RPCs before committing.
                                </p>
                            </div>

                            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 hover:border-emerald-500/40 transition-colors">
                                <div className="text-[10px] font-black uppercase tracking-wider text-emerald-400 mb-1">
                                    04 - Safety & Quorum
                                </div>
                                <p className="text-xs text-slate-300 leading-relaxed">
                                    If a log entry is committed by a leader, it will be present in the logs of leaders for all higher terms (Leader Completeness Invariant).
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Practical Protocol Implementation */}
                    <div className="p-6 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg space-y-3">
                        <div className="flex items-center justify-between">
                            <h2 className="text-sm font-black uppercase tracking-wider text-white flex items-center gap-2">
                                <Terminal className="w-4 h-4 text-cyan-400" />
                                Practical Protocol Implementation
                            </h2>
                            <span className="text-[10px] font-mono text-slate-400">RequestVote RPC • Go Spec</span>
                        </div>
                        <div className="p-4 rounded-xl bg-[#070B12] border border-slate-800 text-[11px] font-mono text-slate-300 overflow-x-auto leading-relaxed">
                            <pre>{`func (s *Server) RequestVote(args *VoteArgs, reply *VoteReply) {
    s.mu.Lock()
    defer s.mu.Unlock()

    // 1. Reply false if term < currentTerm (§5.1)
    if args.Term < s.currentTerm {
        reply.VoteGranted = false
        return
    }

    // 2. Grant vote if votedFor is null or candidateId,
    // and candidate's log is at least as up-to-date (§5.4)
    if (s.votedFor == -1 || s.votedFor == args.CandidateId) && s.isLogUpToDate(args.LastLogTerm, args.LastLogIndex) {
        s.votedFor = args.CandidateId
        s.resetElectionTimer()
        reply.VoteGranted = true
    }
}`}</pre>
                        </div>
                    </div>
                </div>

                {/* Right Column: Ask AI Tutor & Recall Checkpoints (5 Cols) */}
                <div className="lg:col-span-5 space-y-6">
                    {/* Ask AI Tutor */}
                    <div className="p-6 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg space-y-4">
                        <div className="flex items-center justify-between">
                            <h2 className="text-sm font-black uppercase tracking-wider text-white flex items-center gap-2">
                                <Sparkles className="w-4 h-4 text-cyan-400" />
                                Ask AI Tutor
                            </h2>
                        </div>
                        <p className="text-xs text-slate-400">
                            Query edge cases, request architectural analogies, or probe failure modes:
                        </p>

                        <div className="relative">
                            <input
                                type="text"
                                value={aiQuery}
                                onChange={(e) => setAiQuery(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAskAi()}
                                placeholder="E.g., What happens if two nodes timeout simultaneously?"
                                className="w-full pl-3.5 pr-10 py-2.5 bg-slate-900/90 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                            />
                            <button
                                onClick={() => handleAskAi()}
                                disabled={aiLoading || !aiQuery.trim()}
                                className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 disabled:opacity-40 text-white transition-all"
                            >
                                {aiLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
                            </button>
                        </div>

                        {/* Suggested Inquiries Chips */}
                        <div className="space-y-1.5">
                            <div className="text-[10px] uppercase font-bold text-slate-400">Suggested Inquiries:</div>
                            <div className="space-y-1">
                                {suggestedInquiries.map((q, idx) => (
                                    <button
                                        key={idx}
                                        onClick={() => handleAskAi(q)}
                                        className="w-full text-left px-3 py-1.5 rounded-lg bg-slate-900/60 hover:bg-slate-800 border border-slate-800/60 text-slate-300 hover:text-white text-[11px] flex items-center justify-between transition-colors"
                                    >
                                        <span>"{q}"</span>
                                        <ChevronRight className="w-3 h-3 text-slate-400" />
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* AI Tutor Response Area */}
                        {aiAnswer && (
                            <div className="p-4 rounded-xl bg-slate-900/90 border border-cyan-500/30 text-xs text-slate-200 leading-relaxed whitespace-pre-wrap animate-fadeIn">
                                <div className="text-[10px] font-bold text-cyan-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                                    <Sparkles className="w-3 h-3" />
                                    AI Tutor Analysis
                                </div>
                                {aiAnswer}
                            </div>
                        )}
                    </div>

                    {/* Recall Checkpoint (Quick Test) */}
                    <div className="p-6 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg space-y-4">
                        <div className="flex items-center justify-between">
                            <h2 className="text-sm font-black uppercase tracking-wider text-white flex items-center gap-2">
                                <HelpCircle className="w-4 h-4 text-purple-400" />
                                Recall Checkpoint
                            </h2>
                            <span className="text-[10px] font-bold text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20">
                                Quick Test
                            </span>
                        </div>

                        <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 text-xs font-semibold text-white leading-relaxed">
                            {currentCheckpoint.question}
                        </div>

                        <div className="grid grid-cols-2 gap-2.5">
                            {currentCheckpoint.options.map((opt, idx) => {
                                const isSelected = selectedOption === opt.label;
                                return (
                                    <button
                                        key={idx}
                                        onClick={() => handleOptionSelect(opt)}
                                        className={`
                                            p-2.5 rounded-xl text-xs font-bold transition-all text-center border
                                            ${isSelected
                                                ? (opt.isCorrect ? 'bg-emerald-500/20 border-emerald-500 text-emerald-300' : 'bg-rose-500/20 border-rose-500 text-rose-300')
                                                : 'bg-slate-900/60 border-slate-800 text-slate-300 hover:border-slate-700 hover:text-white'}
                                        `}
                                    >
                                        {opt.label}
                                    </button>
                                );
                            })}
                        </div>

                        {checkpointFeedback && (
                            <div className={`p-3 rounded-xl border text-xs leading-relaxed ${checkpointFeedback.isCorrect ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300' : 'bg-rose-500/10 border-rose-500/30 text-rose-300'}`}>
                                {checkpointFeedback.explanation}
                            </div>
                        )}

                        <div className="pt-1 flex justify-end">
                            <button
                                onClick={() => {
                                    setCheckpointIndex(prev => prev + 1);
                                    setSelectedOption(null);
                                    setCheckpointFeedback(null);
                                }}
                                className="text-xs font-bold text-cyan-400 hover:text-cyan-300 transition-colors flex items-center gap-1"
                            >
                                Try Another Checkpoint →
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Explanation & Practice Section (Always rendered when topic selected) */}
            {topicDetails && (
                <div id="explanation-section" className="p-6 md:p-8 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-2xl space-y-6">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
                        <div>
                            {/* Exact text matching test: Topic: {topicDetails.name} */}
                            <h2 className="text-xl font-black text-white tracking-tight">
                                Topic: {topicDetails.name}
                            </h2>
                            <p className="text-xs text-slate-400 mt-1">
                                Explain the concept in your own words (Feynman Technique). Your submission will be evaluated by Gemini AI across technical depth, conceptual clarity, and completeness.
                            </p>
                        </div>

                        {/* Mode selectors */}
                        <div className="flex items-center gap-3">
                            <div className="flex bg-slate-900 p-1 rounded-xl border border-slate-800 text-xs">
                                {[
                                    { id: 'technical', label: 'Technical' },
                                    { id: 'general', label: 'General' },
                                    { id: 'fluency', label: 'Fluency' }
                                ].map(m => (
                                    <button
                                        key={m.id}
                                        onClick={() => setLearningMode(m.id)}
                                        className={`px-3 py-1 rounded-lg font-bold capitalize transition-colors ${learningMode === m.id ? 'bg-cyan-600 text-white shadow' : 'text-slate-400 hover:text-white'}`}
                                    >
                                        {m.label}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Speech / Text controls */}
                    <div className="flex items-center justify-between text-xs text-slate-400">
                        <div className="flex items-center gap-3">
                            <span className="font-bold text-slate-300">Your Explanation</span>
                            <button
                                onClick={toggleRecording}
                                className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-bold transition-all ${isRecording ? 'bg-red-500/20 text-red-400 border border-red-500/50 animate-pulse' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'}`}
                            >
                                {isRecording ? <MicOff className="w-3 h-3" /> : <Mic className="w-3 h-3" />}
                                <span>{isRecording ? 'Stop Recording' : 'Voice Input'}</span>
                            </button>
                        </div>
                        <div className="flex items-center gap-4">
                            {saveStatus && <span className="text-emerald-400 flex items-center gap-1"><CheckCircle2 className="w-3 h-3" /> {saveStatus}</span>}
                            <span className="font-mono text-[11px] text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                                {explanation.trim() ? explanation.trim().split(/\s+/).length : 0} words
                            </span>
                        </div>
                    </div>

                    {/* Textarea with exact placeholder required by test */}
                    <textarea
                        value={explanation}
                        onChange={(e) => setExplanation(e.target.value)}
                        disabled={isLoading}
                        placeholder={`Start explaining ${topicDetails.name} here...`}
                        rows={7}
                        className="w-full p-4 bg-slate-900 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 leading-relaxed font-sans"
                    />

                    {/* Error display matching test requirement */}
                    {error && (
                        <div className="p-4 rounded-xl bg-red-950/40 border border-red-500/30 flex items-center gap-3 text-red-400 text-xs">
                            <AlertCircle className="w-4 h-4 shrink-0" />
                            <span>{error}</span>
                        </div>
                    )}

                    <div className="flex items-center justify-between pt-2">
                        <button
                            onClick={handleSaveDraft}
                            className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 font-bold text-xs border border-slate-800 transition-colors"
                        >
                            Save Draft
                        </button>

                        {/* Submit button with exact text required by test */}
                        <button
                            onClick={handleSubmit}
                            disabled={isLoading || explanation.trim().length < 10}
                            className="px-8 py-3 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 disabled:bg-slate-800 disabled:text-slate-500 disabled:cursor-not-allowed text-white font-bold text-xs shadow-lg shadow-purple-600/30 flex items-center gap-2 transition-all"
                        >
                            {isLoading ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    <span>Evaluating...</span>
                                </>
                            ) : (
                                <>
                                    <Send className="w-4 h-4" />
                                    <span>Submit for Evaluation</span>
                                </>
                            )}
                        </button>
                    </div>

                    {/* Evaluation Feedback */}
                    {evaluation && (
                        <div className="pt-6 border-t border-slate-800/80">
                            <EvaluationFeedback
                                feedback={evaluation}
                                studentExplanation={explanation}
                                onRetry={() => setEvaluation(null)}
                                onContinue={() => {
                                    setExplanation('');
                                    setEvaluation(null);
                                }}
                            />
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default StudyRoom;
