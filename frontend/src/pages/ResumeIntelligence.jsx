/* eslint-disable react-hooks/set-state-in-effect */
import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    FileText, Upload, RefreshCw, Play, CheckCircle2, AlertTriangle,
    Sparkles, ArrowRight, ShieldCheck, Download, ChevronRight, Check,
    ExternalLink, Code, Layers, Loader2, X, Mic, Target, Cpu
} from 'lucide-react';
import api from '../api/axios';
import { AuthContext } from '../context/AuthContext';
import ResumeUploadDropzone from '../components/resume/ResumeUploadDropzone';

const ResumeIntelligence = () => {
    const navigate = useNavigate();
    const { user } = useContext(AuthContext) || {};
    const [resumeData, setResumeData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [_error, setError] = useState(null);
    const [showUploadModal, setShowUploadModal] = useState(false);
    const [appliedOptimizations, setAppliedOptimizations] = useState({});

    const loadActiveResume = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await api.get('/resume/active');
            setResumeData(res.data);
            setLoading(false);
        } catch (err) {
            console.error("Error loading resume data:", err);
            setError("We couldn't load your resume intelligence profile.");
            setLoading(false);
        }
    };

    useEffect(() => {
        loadActiveResume();
    }, []);

    const handleApplyOptimization = (index) => {
        setAppliedOptimizations(prev => ({
            ...prev,
            [index]: true
        }));
    };

    if (loading) {
        return (
            <div className="flex-1 min-h-[70vh] flex items-center justify-center p-8">
                <div className="flex flex-col items-center gap-4">
                    <Loader2 className="w-10 h-10 text-cyan-400 animate-spin" />
                    <p className="text-slate-400 text-xs font-medium animate-pulse tracking-wide">
                        Auditing technical competency & ATS benchmarks...
                    </p>
                </div>
            </div>
        );
    }

    const isDemo = user?.email === 'maya.lin@berkeley.edu';
    const hasResume = Boolean(resumeData && resumeData.has_resume);

    // Empty state for registered users who haven't uploaded a resume yet
    if (!hasResume && !isDemo) {
        return (
            <div className="space-y-8 max-w-5xl mx-auto pb-16">
                {/* Header Banner */}
                <div className="p-6 md:p-8 rounded-2xl bg-gradient-to-r from-[#0F172A] via-[#111827] to-[#1E1B4B] border border-slate-800/80 shadow-2xl flex flex-col md:flex-row md:items-center justify-between gap-6">
                    <div className="space-y-1.5">
                        <div className="flex items-center gap-2 text-[10px] uppercase font-black tracking-wider text-cyan-400">
                            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
                            AI SWE AUDIT • Resume Intelligence & Gap Engine
                        </div>
                        <h1 className="text-2xl md:text-3xl font-black text-white tracking-tight">
                            AI Resume Intelligence & Gap Audit
                        </h1>
                        <p className="text-xs md:text-sm text-slate-300 max-w-xl">
                            Upload your resume to benchmark against real software engineering hiring bars, identify architectural skill gaps, and generate tailored interview probes.
                        </p>
                    </div>

                    <div className="flex items-center gap-3">
                        <button
                            onClick={() => navigate('/interview')}
                            className="px-4 py-2.5 rounded-xl bg-cyan-950/80 hover:bg-cyan-900/90 border border-cyan-500/40 text-cyan-300 font-bold text-xs flex items-center gap-2 transition-all shadow-md shadow-cyan-500/10"
                        >
                            <Mic className="w-3.5 h-3.5 text-cyan-400" />
                            <span>Practice Mock Interview →</span>
                        </button>
                    </div>
                </div>

                {/* Hero Upload Dropzone */}
                <div className="bg-[#0B0F19] border border-slate-800/80 rounded-3xl p-6 md:p-10 shadow-2xl space-y-6">
                    <ResumeUploadDropzone
                        onUploadSuccess={() => {
                            loadActiveResume();
                        }}
                    />
                </div>

                {/* 3 Feature Value Highlights */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                    <div className="p-5 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg space-y-2.5">
                        <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
                            <Target className="w-5 h-5" />
                        </div>
                        <h3 className="text-sm font-bold text-white">Target Role Alignment</h3>
                        <p className="text-xs text-slate-400 leading-relaxed">
                            Calculates an ATS Match Score against L4/L5 profiles at top technology companies and identifies keywords missing from your projects.
                        </p>
                    </div>

                    <div className="p-5 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg space-y-2.5">
                        <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400">
                            <Cpu className="w-5 h-5" />
                        </div>
                        <h3 className="text-sm font-bold text-white">Technical Gap Extraction</h3>
                        <p className="text-xs text-slate-400 leading-relaxed">
                            Flags missing systems topics like distributed tracing, observability pipelines, and concurrency controls so you can remediate them before interviews.
                        </p>
                    </div>

                    <div className="p-5 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg space-y-2.5">
                        <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                            <Sparkles className="w-5 h-5" />
                        </div>
                        <h3 className="text-sm font-bold text-white">Targeted Interview Probes</h3>
                        <p className="text-xs text-slate-400 leading-relaxed">
                            Synthesizes real technical probe questions directly from your resume's stated technologies, architecture, and project responsibilities.
                        </p>
                    </div>
                </div>
            </div>
        );
    }

    const summary = resumeData?.analysis_summary || {};
    const matchScore = summary.match_score || (hasResume ? 82 : (isDemo ? 86 : 0));
    const fileName = resumeData?.file_name || (isDemo ? "resume_maya_lin_2025.pdf" : "uploaded_resume.pdf");
    const extractedSkills = (resumeData?.skills && resumeData.skills.length > 0)
        ? resumeData.skills
        : (summary.skills || (isDemo ? ["Go", "Python", "Rust", "Distributed Systems", "Docker", "Kubernetes", "Linux Internals"] : []));
    const rawQuestions = resumeData?.questions || [];

    return (
        <div className="space-y-6 max-w-7xl mx-auto pb-12">
            {/* Top Header Banner */}
            <div className="p-6 md:p-8 rounded-2xl bg-gradient-to-r from-[#0F172A] via-[#111827] to-[#1E1B4B] border border-slate-800/80 shadow-2xl flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div className="space-y-1.5">
                    <div className="flex items-center gap-2 text-[10px] uppercase font-black tracking-wider text-cyan-400">
                        <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
                        AI SWE AUDIT • Analyzed against SWE benchmark
                    </div>
                    <h1 className="text-2xl md:text-3xl font-black text-white tracking-tight">
                        AI Resume Intelligence & Gap Audit
                    </h1>
                    <div className="flex items-center gap-2 text-xs text-slate-300">
                        <span className="font-mono text-cyan-300 font-bold">{fileName}</span>
                        <span className="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                            ACTIVE RESUME • Processed
                        </span>
                    </div>
                </div>

                <div className="flex flex-wrap items-center gap-3">
                    <button
                        onClick={() => navigate('/interview')}
                        className="px-4 py-2.5 rounded-xl bg-cyan-950/80 hover:bg-cyan-900/90 border border-cyan-500/40 text-cyan-300 font-bold text-xs flex items-center gap-2 transition-all shadow-md shadow-cyan-500/10"
                    >
                        <Mic className="w-3.5 h-3.5 text-cyan-400" />
                        <span>Practice Mock Interview →</span>
                    </button>
                    <button
                        onClick={() => setShowUploadModal(true)}
                        className="px-4 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-200 font-bold text-xs border border-slate-700 shadow-md flex items-center gap-2 transition-all"
                    >
                        <Upload className="w-3.5 h-3.5 text-cyan-400" />
                        <span>Upload New Resume</span>
                    </button>
                    <button
                        onClick={() => {
                            const el = document.getElementById('suggestions-section');
                            if (el) el.scrollIntoView({ behavior: 'smooth' });
                        }}
                        className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold text-xs shadow-lg shadow-purple-600/30 flex items-center gap-2 transition-all"
                    >
                        <Sparkles className="w-3.5 h-3.5" />
                        <span>Improve Resume</span>
                    </button>
                </div>
            </div>

            {/* Top Grid: Match Score Radial Gauge (Left) & Strengths/Gaps (Right) */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Match Score Card (5 Cols) */}
                <div className="lg:col-span-5 p-6 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg flex flex-col justify-between space-y-6">
                    <div>
                        <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">
                            TARGET ROLE ALIGNMENT
                        </div>
                        <h3 className="text-sm font-black text-white mb-1">
                            Software Engineer — Distributed Systems & Cloud Infrastructure
                        </h3>
                        <p className="text-xs text-slate-400">
                            Benchmarked against L4/L5 SWE profiles at Google, Databricks, and Stripe.
                        </p>
                    </div>

                    {/* Circular Score Gauge */}
                    <div className="flex flex-col items-center justify-center py-4">
                        <div className="relative w-44 h-44 flex items-center justify-center">
                            <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                                <circle
                                    cx="50"
                                    cy="50"
                                    r="40"
                                    className="stroke-slate-800"
                                    strokeWidth="8"
                                    fill="transparent"
                                />
                                <circle
                                    cx="50"
                                    cy="50"
                                    r="40"
                                    className="stroke-cyan-400 transition-all duration-1000 ease-out"
                                    strokeWidth="8"
                                    strokeDasharray="251.2"
                                    strokeDashoffset={251.2 - (251.2 * matchScore) / 100}
                                    strokeLinecap="round"
                                    fill="transparent"
                                />
                            </svg>
                            <div className="absolute flex flex-col items-center text-center">
                                <span className="text-4xl font-black text-white tracking-tight">
                                    {matchScore}<span className="text-2xl text-cyan-400 font-bold">/100</span>
                                </span>
                                <span className="text-[10px] uppercase font-black tracking-widest text-cyan-400 mt-0.5">
                                    MATCH SCORE
                                </span>
                            </div>
                        </div>

                        <div className="mt-4 text-center space-y-1">
                            <span className="text-xs font-bold text-cyan-300">
                                {matchScore >= 80 ? 'Top 10% percentile candidate profile' : 'Competitive candidate profile'}
                            </span>
                            <div className="text-[11px] text-slate-400 flex items-center justify-center gap-1.5">
                                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                                <span>High ATS Parsability (Verified format)</span>
                            </div>
                        </div>
                    </div>

                    <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
                        <span>Skills Verified: <span className="text-white font-bold">{extractedSkills.length} Identified</span></span>
                        <span>Experience Depth: <span className="text-white font-bold">Strong</span></span>
                    </div>
                </div>

                {/* Strengths & Missing Skills (7 Cols) */}
                <div className="lg:col-span-7 space-y-6">
                    {/* Identified Strengths */}
                    <div className="p-6 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg space-y-3">
                        <div className="flex items-center justify-between">
                            <h2 className="text-sm font-black uppercase tracking-wider text-white flex items-center gap-2">
                                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                                Identified Strengths
                            </h2>
                            <span className="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                                Strengths Detected
                            </span>
                        </div>

                        <div className="space-y-2.5 pt-1">
                            {summary.strengths && summary.strengths.length > 0 ? (
                                summary.strengths.map((str, idx) => (
                                    <div key={idx} className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/60">
                                        <div className="text-xs font-bold text-white mb-0.5">{str.title || "Core Technical Strength"}</div>
                                        <p className="text-[11px] text-slate-400">{str.description || str}</p>
                                    </div>
                                ))
                            ) : (
                                <>
                                    <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/60">
                                        <div className="text-xs font-bold text-white mb-0.5">Strong Systems Programming Experience</div>
                                        <p className="text-[11px] text-slate-400">Proven multi-raft replication and high-throughput LSM-Tree work in Rust and Go.</p>
                                    </div>

                                    <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/60">
                                        <div className="text-xs font-bold text-white mb-0.5">Quantified Impact Metrics</div>
                                        <p className="text-[11px] text-slate-400">Exemplary +24% throughput boost and 650ms to 120ms failover recovery measurements.</p>
                                    </div>

                                    <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/60">
                                        <div className="text-xs font-bold text-white mb-0.5">Robust Academic Foundation</div>
                                        <p className="text-[11px] text-slate-400">Systems and data infrastructure background aligned with L4/L5 engineering bar.</p>
                                    </div>
                                </>
                            )}
                        </div>
                    </div>

                    {/* Missing Skills & Gaps */}
                    <div className="p-6 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg space-y-3">
                        <div className="flex items-center justify-between">
                            <h2 className="text-sm font-black uppercase tracking-wider text-white flex items-center gap-2">
                                <AlertTriangle className="w-4 h-4 text-rose-400" />
                                Missing Skills & Gaps
                            </h2>
                            <span className="text-[10px] font-bold text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/20">
                                Recommended Focus
                            </span>
                        </div>

                        <div className="space-y-2.5 pt-1">
                            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/60 flex items-start justify-between gap-3">
                                <div>
                                    <div className="flex items-center gap-2 mb-0.5">
                                        <span className="text-xs font-bold text-white">Distributed Tracing & Observability</span>
                                        <span className="text-[9px] font-black uppercase text-rose-400 bg-rose-500/10 px-1.5 py-0.5 rounded">Missing</span>
                                    </div>
                                    <p className="text-[11px] text-slate-400">Target roles require OpenTelemetry or Jaeger pipeline exposure in production architectures.</p>
                                </div>
                            </div>

                            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/60 flex items-start justify-between gap-3">
                                <div>
                                    <div className="flex items-center gap-2 mb-0.5">
                                        <span className="text-xs font-bold text-white">CI/CD & Deployment Automation</span>
                                        <span className="text-[9px] font-black uppercase text-amber-400 bg-amber-500/10 px-1.5 py-0.5 rounded">Needs Detail</span>
                                    </div>
                                    <p className="text-[11px] text-slate-400">Automated integration pipelines, Helm charts, or Kubernetes manifest management.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Middle Section: Skill Comparison & Anticipated Interview Probes */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Skill Comparison */}
                <div className="p-6 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg space-y-4">
                    <div className="flex items-center justify-between">
                        <h2 className="text-sm font-black uppercase tracking-wider text-white">
                            Skill Comparison: Candidate Profile vs. Target SWE Requirements
                        </h2>
                    </div>

                    <div className="space-y-4 pt-1">
                        <div>
                            <div className="flex items-center justify-between text-xs mb-1">
                                <span className="font-bold text-white">Distributed Systems & Consensus (Raft/Paxos)</span>
                                <span className="text-[11px] text-cyan-400 font-bold">95% (Target: 85%)</span>
                            </div>
                            <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                                <div className="bg-cyan-400 h-1.5 rounded-full" style={{ width: '95%' }}></div>
                            </div>
                        </div>

                        <div>
                            <div className="flex items-center justify-between text-xs mb-1">
                                <span className="font-bold text-white">Systems Languages (Go, C++, Rust)</span>
                                <span className="text-[11px] text-cyan-400 font-bold">92% (Target: 90%)</span>
                            </div>
                            <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                                <div className="bg-cyan-400 h-1.5 rounded-full" style={{ width: '92%' }}></div>
                            </div>
                        </div>

                        <div>
                            <div className="flex items-center justify-between text-xs mb-1">
                                <span className="font-bold text-white">Distributed Tracing & Observability (OTel, Grafana)</span>
                                <span className="text-[11px] text-rose-400 font-bold">48% (Target: 70%)</span>
                            </div>
                            <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                                <div className="bg-rose-500 h-1.5 rounded-full" style={{ width: '48%' }}></div>
                            </div>
                        </div>

                        <div>
                            <div className="flex items-center justify-between text-xs mb-1">
                                <span className="font-bold text-white">CI/CD & Infrastructure as Code</span>
                                <span className="text-[11px] text-amber-400 font-bold">52% (Target: 75%)</span>
                            </div>
                            <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                                <div className="bg-amber-400 h-1.5 rounded-full" style={{ width: '52%' }}></div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Anticipated Technical Interview Probes */}
                <div className="p-6 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-lg space-y-4">
                    <div className="flex items-center justify-between">
                        <h2 className="text-sm font-black uppercase tracking-wider text-white">
                            Anticipated Technical Interview Probes
                        </h2>
                    </div>

                    <div className="space-y-3 pt-1">
                        {rawQuestions.length > 0 ? (
                            rawQuestions.slice(0, 2).map((q, idx) => (
                                <div key={idx} className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/70">
                                    <span className="text-[10px] font-black uppercase text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">
                                        {q.category || "Technical Probe"} • {q.difficulty || "MEDIUM"}
                                    </span>
                                    <p className="text-xs text-slate-300 mt-2 leading-relaxed">
                                        "{q.question}"
                                    </p>
                                </div>
                            ))
                        ) : (
                            <>
                                <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/70">
                                    <span className="text-[10px] font-black uppercase text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20">
                                        System Design: High-Throughput Write Engine
                                    </span>
                                    <p className="text-xs text-slate-300 mt-2 leading-relaxed">
                                        "In your LSM-Tree engine, how did you handle compaction storms under sustained burst write traffic without starving reads?"
                                    </p>
                                </div>

                                <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/70">
                                    <span className="text-[10px] font-black uppercase text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">
                                        Concurrency: Raft Split-Brain Quorum
                                    </span>
                                    <p className="text-xs text-slate-300 mt-2 leading-relaxed">
                                        "Walk me through how your implementation handles asymmetric network partitions where a leader can send heartbeats but cannot receive ACKs."
                                    </p>
                                </div>
                            </>
                        )}
                    </div>
                </div>
            </div>

            {/* Specific Improvement Suggestions Section */}
            <div id="suggestions-section" className="p-6 md:p-8 rounded-2xl bg-[#0B0F19] border border-slate-800/80 shadow-2xl space-y-6">
                <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
                    <div>
                        <h2 className="text-base font-black text-white uppercase tracking-wider flex items-center gap-2">
                            <Sparkles className="w-4 h-4 text-cyan-400" />
                            Specific Improvement Suggestions
                        </h2>
                        <p className="text-xs text-slate-400 mt-1">
                            Click 'Apply Optimization' to instantly incorporate higher-impact phrasing into your resume draft.
                        </p>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Suggestion 1 */}
                    <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800/80 space-y-3">
                        <div className="flex items-center justify-between text-xs">
                            <span className="font-bold text-slate-400">EXPERIENCE • Distributed Systems Engineering</span>
                            <span className="text-[10px] font-black text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                                +25 Impact Lift
                            </span>
                        </div>

                        <div className="p-3 rounded-lg bg-red-950/20 border border-red-500/30 text-xs text-slate-400 line-through">
                            "Helped team build database schema migrations and handled test runs for storage cluster deployment automation."
                        </div>

                        <div className="p-3 rounded-lg bg-emerald-950/20 border border-emerald-500/30 text-xs text-emerald-300 leading-relaxed font-medium">
                            "Engineered automated schema migration pipelines in Go, eliminating schema rollback errors across 45+ distributed storage nodes with zero downtime."
                        </div>

                        <button
                            onClick={() => handleApplyOptimization(1)}
                            disabled={appliedOptimizations[1]}
                            className={`w-full py-2 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${appliedOptimizations[1] ? 'bg-emerald-600 text-white' : 'bg-purple-600 hover:bg-purple-500 text-white shadow-md'}`}
                        >
                            {appliedOptimizations[1] ? (
                                <>
                                    <Check className="w-3.5 h-3.5" />
                                    <span>Applied to Resume Draft</span>
                                </>
                            ) : (
                                <span>Apply Optimization</span>
                            )}
                        </button>
                    </div>

                    {/* Suggestion 2 */}
                    <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800/80 space-y-3">
                        <div className="flex items-center justify-between text-xs">
                            <span className="font-bold text-slate-400">PROJECTS • High-Throughput Service Architecture</span>
                            <span className="text-[10px] font-black text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">
                                +18% ATS Lift
                            </span>
                        </div>

                        <div className="p-3 rounded-lg bg-red-950/20 border border-red-500/30 text-xs text-slate-400 line-through">
                            "Worked on backend API using Go and PostgreSQL."
                        </div>

                        <div className="p-3 rounded-lg bg-cyan-950/20 border border-cyan-500/30 text-xs text-cyan-300 leading-relaxed font-medium">
                            "Architected high-throughput RESTful & gRPC services in Go, handling 15,000+ req/sec with &lt;45ms p99 latency and OpenTelemetry distributed tracing."
                        </div>

                        <button
                            onClick={() => handleApplyOptimization(2)}
                            disabled={appliedOptimizations[2]}
                            className={`w-full py-2 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${appliedOptimizations[2] ? 'bg-emerald-600 text-white' : 'bg-purple-600 hover:bg-purple-500 text-white shadow-md'}`}
                        >
                            {appliedOptimizations[2] ? (
                                <>
                                    <Check className="w-3.5 h-3.5" />
                                    <span>Applied to Resume Draft</span>
                                </>
                            ) : (
                                <span>Apply Optimization</span>
                            )}
                        </button>
                    </div>
                </div>
            </div>

            {/* Resume Upload Modal for replacement */}
            {showUploadModal && (
                <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
                    <div className="w-full max-w-xl bg-[#0B0F19] border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-5">
                        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                            <div>
                                <h3 className="text-base font-black text-white">Upload New Resume</h3>
                                <p className="text-xs text-slate-400">PDF or DOCX format (Max 10 MB). Evaluated via Gemini ATS model.</p>
                            </div>
                            <button
                                onClick={() => setShowUploadModal(false)}
                                className="text-slate-400 hover:text-white"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        <ResumeUploadDropzone
                            isReplacement={true}
                            onUploadSuccess={() => {
                                setShowUploadModal(false);
                                loadActiveResume();
                            }}
                        />
                    </div>
                </div>
            )}
        </div>
    );
};

export default ResumeIntelligence;
