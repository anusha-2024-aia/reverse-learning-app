import React, { useState, useEffect } from 'react';
import { FileText, Upload, RefreshCw, Play, CheckCircle2, AlertTriangle, Code, Layers, Sparkles, BookOpen, ChevronRight } from 'lucide-react';
import api from '../api/axios';
import ResumeUploadDropzone from '../components/resume/ResumeUploadDropzone';
import ResumeInterviewModal from '../components/resume/ResumeInterviewModal';

const ResumeIntelligence = () => {
    const [resumeData, setResumeData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showReplacementUpload, setShowReplacementUpload] = useState(false);
    const [showInterviewModal, setShowInterviewModal] = useState(false);
    const [categoryFilter, setCategoryFilter] = useState('All');
    const [difficultyFilter, setDifficultyFilter] = useState('All');

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

    const handleUploadSuccess = () => {
        setShowReplacementUpload(false);
        loadActiveResume();
    };

    const handleReanalyze = async () => {
        setLoading(true);
        try {
            await api.post('/resume/analyze');
            loadActiveResume();
        } catch (err) {
            console.error("Re-analyze error:", err);
            setError("Failed to re-analyze resume.");
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex-1 overflow-y-auto bg-slate-900 text-slate-200 p-8 flex flex-col items-center justify-center min-h-[60vh]">
                <div className="flex flex-col items-center gap-3">
                    <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                    <p className="text-slate-400 font-medium animate-pulse">Analyzing resume intelligence...</p>
                </div>
            </div>
        );
    }

    const hasResume = resumeData && resumeData.has_resume;
    const summary = resumeData?.analysis_summary || {};
    const projects = summary.projects || resumeData?.projects || [];
    const skills = summary.skills || resumeData?.skills || [];
    const questions = resumeData?.questions || [];

    const filteredQuestions = questions.filter(q => {
        const matchCat = categoryFilter === 'All' || (q.category && q.category.toUpperCase() === categoryFilter.toUpperCase());
        const matchDiff = difficultyFilter === 'All' || (q.difficulty && q.difficulty.toUpperCase() === difficultyFilter.toUpperCase());
        return matchCat && matchDiff;
    });

    return (
        <div className="flex-1 overflow-y-auto bg-slate-900 text-slate-100 p-6 md:p-12 relative">
            <div className="max-w-7xl mx-auto space-y-8">

                {/* Page Header */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-indigo-600/20 text-indigo-400 rounded-2xl border border-indigo-500/30">
                            <FileText className="w-8 h-8" />
                        </div>
                        <div>
                            <h1 className="text-3xl md:text-4xl font-black text-white tracking-tight">
                                Resume Intelligence
                            </h1>
                            <p className="text-slate-400 text-sm md:text-base mt-1 font-medium">
                                Turn your resume into a personalized interview.
                            </p>
                        </div>
                    </div>

                    {hasResume && (
                        <div className="flex items-center gap-3">
                            <button
                                onClick={handleReanalyze}
                                className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-bold transition-all border border-slate-700 flex items-center gap-2"
                            >
                                <RefreshCw className="w-4 h-4" />
                                <span>Re-analyze</span>
                            </button>
                            <button
                                onClick={() => setShowReplacementUpload(!showReplacementUpload)}
                                className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition-all flex items-center gap-2 shadow-lg shadow-indigo-600/30"
                            >
                                <Upload className="w-4 h-4" />
                                <span>Replace Resume</span>
                            </button>
                        </div>
                    )}
                </div>

                {/* REPLACEMENT UPLOAD OVERLAY */}
                {showReplacementUpload && (
                    <div className="bg-slate-800/90 p-6 rounded-3xl border border-indigo-500/40 relative animate-in fade-in duration-200">
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="text-lg font-bold text-white">Upload New Resume</h3>
                            <button onClick={() => setShowReplacementUpload(false)} className="text-slate-400 hover:text-white">
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                        <ResumeUploadDropzone onUploadSuccess={handleUploadSuccess} isReplacement={true} />
                    </div>
                )}

                {/* EMPTY STATE - NO RESUME UPLOADED */}
                {!hasResume && !showReplacementUpload && (
                    <div className="bg-slate-800/40 border border-slate-800 rounded-3xl p-12 text-center max-w-3xl mx-auto space-y-6 my-6 shadow-2xl">
                        <div className="w-20 h-20 bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 rounded-3xl flex items-center justify-center mx-auto shadow-xl">
                            <FileText className="w-10 h-10" />
                        </div>
                        <div className="space-y-2">
                            <h2 className="text-3xl font-black text-white">📄 Resume Intelligence</h2>
                            <p className="text-slate-300 text-base max-w-lg mx-auto leading-relaxed">
                                Upload your resume to generate personalized interview questions based on your actual skills, projects, and experience.
                            </p>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-lg mx-auto text-xs text-slate-300 font-semibold text-left">
                            <div className="flex items-center gap-2 bg-slate-900/60 p-3 rounded-xl border border-slate-800">
                                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                                <span>✓ Project-specific questions</span>
                            </div>
                            <div className="flex items-center gap-2 bg-slate-900/60 p-3 rounded-xl border border-slate-800">
                                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                                <span>✓ Skill-based questions</span>
                            </div>
                            <div className="flex items-center gap-2 bg-slate-900/60 p-3 rounded-xl border border-slate-800">
                                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                                <span>✓ Technical questions</span>
                            </div>
                            <div className="flex items-center gap-2 bg-slate-900/60 p-3 rounded-xl border border-slate-800">
                                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                                <span>✓ Difficulty-based questions</span>
                            </div>
                            <div className="flex items-center gap-2 bg-slate-900/60 p-3 rounded-xl border border-slate-800 md:col-span-2">
                                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                                <span>✓ Personalized interview preparation</span>
                            </div>
                        </div>

                        <ResumeUploadDropzone onUploadSuccess={handleUploadSuccess} />
                    </div>
                )}

                {/* ACTIVE RESUME DASHBOARD */}
                {hasResume && (
                    <div className="space-y-8">
                        
                        {/* Active File Bar */}
                        <div className="bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-slate-800 p-6 rounded-3xl flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xl">
                            <div className="flex items-center gap-4">
                                <div className="p-3 bg-emerald-500/20 text-emerald-400 rounded-2xl border border-emerald-500/30">
                                    <CheckCircle2 className="w-6 h-6" />
                                </div>
                                <div>
                                    <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400">
                                        ✓ Resume analyzed successfully
                                    </span>
                                    <h3 className="text-xl font-bold text-white">
                                        {resumeData.file_name}
                                    </h3>
                                </div>
                            </div>

                            <button
                                onClick={() => setShowInterviewModal(true)}
                                className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-2xl text-sm flex items-center justify-center gap-2 transition-all shadow-lg shadow-indigo-600/30"
                            >
                                <Play className="w-4 h-4 fill-current" />
                                <span>Start Personalized Interview</span>
                            </button>
                        </div>

                        {/* Metric Overview Bar */}
                        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                            <div className="bg-slate-800/80 p-5 rounded-2xl border border-slate-700/80 shadow-lg">
                                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Skills Detected</span>
                                <div className="text-3xl font-black text-white mt-1 font-mono">{skills.length}</div>
                            </div>
                            <div className="bg-slate-800/80 p-5 rounded-2xl border border-slate-700/80 shadow-lg">
                                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Projects</span>
                                <div className="text-3xl font-black text-white mt-1 font-mono">{projects.length}</div>
                            </div>
                            <div className="bg-slate-800/80 p-5 rounded-2xl border border-slate-700/80 shadow-lg">
                                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Education</span>
                                <div className="text-3xl font-black text-white mt-1 font-mono">{(summary.education || resumeData?.education || []).length}</div>
                            </div>
                            <div className="bg-slate-800/80 p-5 rounded-2xl border border-slate-700/80 shadow-lg">
                                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Experience</span>
                                <div className="text-3xl font-black text-white mt-1 font-mono">{(summary.experience || resumeData?.experience || []).length}</div>
                            </div>
                            <div className="bg-slate-800/80 p-5 rounded-2xl border border-slate-700/80 shadow-lg">
                                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Personalized Questions</span>
                                <div className="text-3xl font-black text-indigo-400 mt-1 font-mono">{questions.length}</div>
                            </div>
                        </div>

                        {/* Strongest Areas & Recommended Focus */}
                        <div className="grid md:grid-cols-2 gap-6">
                            <div className="bg-slate-800/90 border border-slate-700 p-6 rounded-3xl space-y-3">
                                <span className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
                                    <Sparkles className="w-4 h-4" /> Strongest Technical Areas
                                </span>
                                <div className="flex flex-wrap gap-2 pt-1">
                                    {(summary.strongest_areas || skills.slice(0, 4)).map((area, idx) => (
                                        <span key={idx} className="bg-emerald-950/60 text-emerald-300 border border-emerald-800 px-3 py-1.5 rounded-xl text-xs font-bold">
                                            {area}
                                        </span>
                                    ))}
                                </div>
                            </div>

                            <div className="bg-slate-800/90 border border-slate-700 p-6 rounded-3xl space-y-3">
                                <span className="text-xs font-bold uppercase tracking-wider text-indigo-400 flex items-center gap-1.5">
                                    <BookOpen className="w-4 h-4" /> Recommended Interview Focus
                                </span>
                                <div className="flex flex-wrap gap-2 pt-1">
                                    {(summary.recommended_focus || ["Project Architecture", "Database Decisions", "Scalability"]).map((focus, idx) => (
                                        <span key={idx} className="bg-indigo-950/60 text-indigo-300 border border-indigo-800 px-3 py-1.5 rounded-xl text-xs font-bold">
                                            {focus}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        </div>

                        {/* RESUME PROJECTS CARDS SECTION */}
                        <div className="space-y-4">
                            <h2 className="text-2xl font-black text-white flex items-center gap-2">
                                <Code className="w-6 h-6 text-indigo-400" />
                                Projects ({projects.length})
                            </h2>

                            {projects.length === 0 ? (
                                <div className="p-6 bg-slate-800/40 rounded-2xl text-xs text-slate-400 text-center">
                                    No distinct projects detected in resume text. General technical questions generated.
                                </div>
                            ) : (
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                    {projects.map((proj, idx) => {
                                        const projQuestionsCount = questions.filter(q => 
                                            (q.target || q.source || "").toLowerCase().includes(proj.name.toLowerCase()) ||
                                            proj.name.toLowerCase().includes((q.target || q.source || "").toLowerCase())
                                        ).length;

                                        return (
                                            <div key={idx} className="bg-slate-800/90 border border-slate-700 rounded-3xl p-6 shadow-xl flex flex-col justify-between space-y-4 hover:border-indigo-500/50 transition-all">
                                                <div>
                                                    <h3 className="text-lg font-bold text-white mb-2">{proj.name}</h3>
                                                    <p className="text-xs text-slate-400 line-clamp-3 leading-relaxed mb-4">
                                                        {proj.description || "Project extracted from resume."}
                                                    </p>
                                                    <div className="flex flex-wrap gap-1.5 mb-3">
                                                        {(proj.technologies || []).map((t, tidx) => (
                                                            <span key={tidx} className="text-[10px] font-bold bg-slate-900 text-slate-300 px-2 py-0.5 rounded border border-slate-700">
                                                                {t}
                                                            </span>
                                                        ))}
                                                    </div>
                                                    <div className="text-xs font-semibold text-slate-400 flex items-center justify-between border-t border-slate-700/60 pt-3">
                                                        <span>Interview Questions:</span>
                                                        <span className="font-bold text-indigo-400 font-mono text-sm">{projQuestionsCount > 0 ? projQuestionsCount : 'Multiple'}</span>
                                                    </div>
                                                </div>

                                                <div className="grid grid-cols-2 gap-2 pt-2">
                                                    <button
                                                        onClick={() => {
                                                            setCategoryFilter('PROJECT');
                                                            const element = document.getElementById('questions-section');
                                                            if (element) element.scrollIntoView({ behavior: 'smooth' });
                                                        }}
                                                        className="py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold rounded-xl text-xs flex items-center justify-center gap-1 transition-all border border-slate-700"
                                                    >
                                                        <span>View Questions</span>
                                                    </button>
                                                    <button
                                                        onClick={() => setShowInterviewModal(true)}
                                                        className="py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl text-xs flex items-center justify-center gap-1 transition-all shadow-md"
                                                    >
                                                        <span>Start Interview</span>
                                                    </button>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            )}
                        </div>

                        {/* SKILLS TAGS SECTION */}
                        <div className="space-y-4">
                            <h2 className="text-2xl font-black text-white flex items-center gap-2">
                                <Layers className="w-6 h-6 text-indigo-400" />
                                Skills ({skills.length})
                            </h2>
                            <div className="flex flex-wrap gap-2.5 bg-slate-800/60 p-6 rounded-3xl border border-slate-700/80">
                                {skills.map((skill, idx) => (
                                    <span key={idx} className="bg-slate-900 text-indigo-300 border border-slate-700 px-3.5 py-1.5 rounded-xl text-xs font-bold shadow">
                                        [{skill}]
                                    </span>
                                ))}
                            </div>
                        </div>

                        {/* GENERATED PERSONALIZED QUESTIONS LIST */}
                        <div id="questions-section" className="space-y-4">
                            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                                <h2 className="text-2xl font-black text-white flex items-center gap-2">
                                    <Sparkles className="w-6 h-6 text-indigo-400" />
                                    Personalized Interview Questions ({filteredQuestions.length})
                                </h2>

                                {/* Filters */}
                                <div className="flex gap-2">
                                    <select
                                        value={categoryFilter}
                                        onChange={(e) => setCategoryFilter(e.target.value)}
                                        className="bg-slate-800 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none"
                                    >
                                        <option value="All">All Categories</option>
                                        <option value="PROJECT">Project</option>
                                        <option value="TECHNICAL">Technical</option>
                                        <option value="DATABASE">Database</option>
                                        <option value="ALGORITHM">Algorithm</option>
                                        <option value="ARCHITECTURE">Architecture</option>
                                        <option value="EXPERIENCE">Experience</option>
                                        <option value="SCALABILITY">Scalability</option>
                                        <option value="BEHAVIORAL">Behavioral</option>
                                    </select>

                                    <select
                                        value={difficultyFilter}
                                        onChange={(e) => setDifficultyFilter(e.target.value)}
                                        className="bg-slate-800 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none"
                                    >
                                        <option value="All">All Difficulties</option>
                                        <option value="EASY">Easy</option>
                                        <option value="MEDIUM">Medium</option>
                                        <option value="HARD">Hard</option>
                                    </select>
                                </div>
                            </div>

                            <div className="space-y-3">
                                {filteredQuestions.map((q, idx) => (
                                    <div key={q.id || idx} className="bg-slate-800/80 border border-slate-700 p-4 rounded-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
                                        <div className="space-y-1">
                                            <div className="flex items-center gap-2">
                                                <span className="text-[10px] font-bold uppercase tracking-wider bg-indigo-950 text-indigo-300 px-2 py-0.5 rounded border border-indigo-800">
                                                    {q.category}
                                                </span>
                                                <span className="text-[10px] font-bold uppercase tracking-wider bg-slate-900 text-slate-400 px-2 py-0.5 rounded border border-slate-700">
                                                    {q.difficulty}
                                                </span>
                                                {q.target && (
                                                    <span className="text-[10px] font-semibold text-slate-400">
                                                        Target: {q.target}
                                                    </span>
                                                )}
                                            </div>
                                            <p className="text-sm font-bold text-white">
                                                {q.question}
                                            </p>
                                        </div>

                                        <button
                                            onClick={() => setShowInterviewModal(true)}
                                            className="px-4 py-2 bg-indigo-600/80 hover:bg-indigo-500 text-white font-bold rounded-xl text-xs transition-colors flex-shrink-0"
                                        >
                                            Practice
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>

                    </div>
                )}

                {/* RESUME INTERVIEW MODAL */}
                {showInterviewModal && resumeData && (
                    <ResumeInterviewModal 
                        resumeId={resumeData.resume_id}
                        initialQuestions={questions}
                        onClose={() => setShowInterviewModal(false)}
                        onComplete={loadActiveResume}
                    />
                )}

            </div>
        </div>
    );
};

export default ResumeIntelligence;
