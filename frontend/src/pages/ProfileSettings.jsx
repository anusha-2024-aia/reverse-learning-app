import React, { useState, useEffect } from 'react';
import {
    User, ShieldCheck, Sparkles, Save, Download, RefreshCw,
    CheckCircle2, AlertCircle, School, BookOpen, Sliders,
    Lock, Database, GitBranch, Calendar, Loader2
} from 'lucide-react';
import api from '../api/axios';

const ProfileSettings = () => {
    const [_loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState(null);
    const [error, setError] = useState(null);

    const [profile, setProfile] = useState({
        name: 'Maya Lin',
        email: 'maya.lin@berkeley.edu',
        university: 'University of California, Berkeley',
        target_role: 'Distributed Systems & Cloud Infrastructure',
        gpa: '3.92',
        grad_year: 'Spring 2026',
        ai_strictness: 'Strict (Senior L5)',
        sync_canvas: true,
        sync_github: true,
        sync_calendar: false,
    });

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const res = await api.get('/auth/profile');
                if (res.data) {
                    setProfile(prev => ({
                        ...prev,
                        ...res.data
                    }));
                }
            } catch (_err) {
                void _err;
                // If demo or offline, keep default Maya Lin profile
            } finally {
                setLoading(false);
            }
        };
        fetchProfile();
    }, []);

    const handleSave = async (e) => {
        e.preventDefault();
        setSaving(true);
        setMessage(null);
        setError(null);
        try {
            await api.put('/auth/profile', profile);
            setMessage("Profile and calibration settings saved successfully.");
        } catch (err) {
            setError(err.response?.data?.detail || "Could not update profile.");
        } finally {
            setSaving(false);
        }
    };

    const handleExport = () => {
        const dataStr = `data:text/json;charset=utf-8,${encodeURIComponent(JSON.stringify(profile, null, 2))}`;
        const downloadAnchor = document.createElement('a');
        downloadAnchor.setAttribute('href', dataStr);
        downloadAnchor.setAttribute('download', 'maya_lin_academic_profile.json');
        document.body.appendChild(downloadAnchor);
        downloadAnchor.click();
        downloadAnchor.remove();
    };

    return (
        <div className="w-full">
            <div className="p-4 md:p-8 space-y-6 max-w-7xl mx-auto">
                {/* Header */}
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
                    <div>
                        <div className="text-[11px] font-black uppercase tracking-wider text-cyan-400 flex items-center gap-2 mb-1">
                            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
                            ACADEMIC IDENTITY & CALIBRATION
                        </div>
                        <h1 className="text-2xl md:text-3xl font-black text-white tracking-tight">
                            Student Profile & Intelligence Calibration
                        </h1>
                        <p className="text-xs text-slate-400 mt-1">
                            Manage academic identity, evaluation rigor, system integrations, and cognitive record privacy.
                        </p>
                    </div>

                    <div className="flex items-center gap-3">
                        <button
                            type="button"
                            onClick={handleExport}
                            className="px-4 py-2 rounded-xl bg-[#0B0F19] hover:bg-slate-800 border border-slate-700 text-slate-300 hover:text-white font-bold text-xs flex items-center gap-2 transition-colors"
                        >
                            <Download className="w-3.5 h-3.5 text-cyan-400" />
                            <span>Export Academic Dossier</span>
                        </button>
                        <button
                            type="button"
                            onClick={handleSave}
                            disabled={saving}
                            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-bold text-xs shadow-lg shadow-cyan-500/20 flex items-center gap-2 transition-all disabled:opacity-50"
                        >
                            <Save className="w-3.5 h-3.5" />
                            <span>{saving ? 'Saving...' : 'Save Configuration Changes'}</span>
                        </button>
                    </div>
                </div>

                {message && (
                    <div className="p-4 rounded-2xl bg-emerald-950/40 border border-emerald-500/40 text-emerald-300 text-xs flex items-center gap-2.5">
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                        <span>{message}</span>
                    </div>
                )}

                {error && (
                    <div className="p-4 rounded-2xl bg-rose-950/40 border border-rose-500/40 text-rose-300 text-xs flex items-center gap-2.5">
                        <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
                        <span>{error}</span>
                    </div>
                )}

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                    {/* Left Column: Academic Identity (Cols 8) */}
                    <div className="lg:col-span-8 space-y-6">
                        {/* Identity Card */}
                        <div className="bg-[#0B0F19] border border-slate-800/80 rounded-3xl p-6 md:p-8 space-y-6 shadow-xl">
                            <div className="flex items-center gap-4 border-b border-slate-800/80 pb-6">
                                <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-cyan-400 to-indigo-600 flex items-center justify-center text-xl font-black text-slate-950 shadow-lg shadow-cyan-500/20">
                                    ML
                                </div>
                                <div className="space-y-1">
                                    <div className="flex items-center gap-2">
                                        <h3 className="text-xl font-black text-white">{profile.name}</h3>
                                        <span className="px-2.5 py-0.5 rounded-full bg-emerald-950/80 text-emerald-400 border border-emerald-800 text-[10px] font-bold flex items-center gap-1">
                                            <ShieldCheck className="w-3 h-3" /> Verified Student
                                        </span>
                                    </div>
                                    <p className="text-xs text-slate-400">
                                        UC Berkeley Electrical Engineering & Computer Sciences • Class of 2026
                                    </p>
                                    <div className="text-[11px] text-cyan-400 font-mono font-semibold">
                                        Cumulative GPA: {profile.gpa} / 4.00 • Target: {profile.target_role}
                                    </div>
                                </div>
                            </div>

                            {/* Form fields */}
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">
                                        Full Name
                                    </label>
                                    <input
                                        type="text"
                                        value={profile.name}
                                        onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                                        className="w-full bg-[#080C14] border border-slate-700/80 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-cyan-500 font-medium"
                                    />
                                </div>

                                <div>
                                    <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">
                                        Institutional Email
                                    </label>
                                    <input
                                        type="email"
                                        value={profile.email}
                                        disabled
                                        className="w-full bg-[#080C14] border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-500 font-mono cursor-not-allowed"
                                    />
                                </div>

                                <div>
                                    <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">
                                        University / Institution
                                    </label>
                                    <input
                                        type="text"
                                        value={profile.university}
                                        onChange={(e) => setProfile({ ...profile, university: e.target.value })}
                                        className="w-full bg-[#080C14] border border-slate-700/80 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-cyan-500 font-medium"
                                    />
                                </div>

                                <div>
                                    <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">
                                        Expected Graduation
                                    </label>
                                    <input
                                        type="text"
                                        value={profile.grad_year}
                                        onChange={(e) => setProfile({ ...profile, grad_year: e.target.value })}
                                        className="w-full bg-[#080C14] border border-slate-700/80 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-cyan-500 font-medium"
                                    />
                                </div>

                                <div className="sm:col-span-2">
                                    <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">
                                        Primary Engineering Track
                                    </label>
                                    <input
                                        type="text"
                                        value={profile.target_role}
                                        onChange={(e) => setProfile({ ...profile, target_role: e.target.value })}
                                        className="w-full bg-[#080C14] border border-slate-700/80 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-cyan-500 font-medium"
                                    />
                                </div>
                            </div>
                        </div>

                        {/* Rigor & Calibration Settings */}
                        <div className="bg-[#0B0F19] border border-slate-800/80 rounded-3xl p-6 md:p-8 space-y-6 shadow-xl">
                            <div>
                                <h3 className="text-sm font-black text-white uppercase tracking-wider flex items-center gap-2">
                                    <Sliders className="w-4 h-4 text-cyan-400" />
                                    AI Evaluation Rigor & Pedagogical Calibration
                                </h3>
                                <p className="text-xs text-slate-400 mt-1">
                                    Adjust how strictly the multi-agent Socratic engine scores your system design explanations.
                                </p>
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                                {[
                                    { label: 'Lenient Tutor', desc: 'Focuses on conceptual analogies and high-level intuition.' },
                                    { label: 'Standard Academic', desc: 'Balances formal proofs with pragmatic software architecture.' },
                                    { label: 'Strict (Senior L5)', desc: 'Zero tolerance for vague invariants, splits, or hand-waving.' }
                                ].map((tier, i) => (
                                    <button
                                        key={i}
                                        type="button"
                                        onClick={() => setProfile({ ...profile, ai_strictness: tier.label })}
                                        className={`p-4 rounded-2xl text-left border transition-all ${
                                            profile.ai_strictness === tier.label
                                                ? 'bg-cyan-950/40 border-cyan-500 text-white shadow-lg shadow-cyan-500/10'
                                                : 'bg-[#080C14] border-slate-800 text-slate-400 hover:text-white'
                                        }`}
                                    >
                                        <div className="text-xs font-black text-white">{tier.label}</div>
                                        <div className="text-[11px] text-slate-400 mt-1 leading-snug">{tier.desc}</div>
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Right Column: Integrations & Privacy (Cols 4) */}
                    <div className="lg:col-span-4 space-y-6">
                        {/* Integrations Card */}
                        <div className="bg-[#0B0F19] border border-slate-800/80 rounded-3xl p-6 space-y-5 shadow-xl">
                            <h3 className="text-xs font-black text-white uppercase tracking-wider flex items-center gap-2">
                                <GitBranch className="w-4 h-4 text-purple-400" />
                                Integrations & Sync
                            </h3>

                            <div className="space-y-3">
                                <label className="flex items-center justify-between p-3 rounded-2xl bg-[#080C14] border border-slate-800 cursor-pointer">
                                    <div>
                                        <div className="text-xs font-bold text-white">Canvas LMS / bCourses</div>
                                        <div className="text-[10px] text-slate-400">Sync assignment deadlines</div>
                                    </div>
                                    <input
                                        type="checkbox"
                                        checked={profile.sync_canvas}
                                        onChange={(e) => setProfile({ ...profile, sync_canvas: e.target.checked })}
                                        className="rounded bg-slate-900 border-slate-700 text-cyan-500 focus:ring-0"
                                    />
                                </label>

                                <label className="flex items-center justify-between p-3 rounded-2xl bg-[#080C14] border border-slate-800 cursor-pointer">
                                    <div>
                                        <div className="text-xs font-bold text-white">GitHub Education</div>
                                        <div className="text-[10px] text-slate-400">Sync project repo code</div>
                                    </div>
                                    <input
                                        type="checkbox"
                                        checked={profile.sync_github}
                                        onChange={(e) => setProfile({ ...profile, sync_github: e.target.checked })}
                                        className="rounded bg-slate-900 border-slate-700 text-cyan-500 focus:ring-0"
                                    />
                                </label>

                                <label className="flex items-center justify-between p-3 rounded-2xl bg-[#080C14] border border-slate-800 cursor-pointer">
                                    <div>
                                        <div className="text-xs font-bold text-white">Google Calendar Exam Alert</div>
                                        <div className="text-[10px] text-slate-400">Notify 48h before midterm</div>
                                    </div>
                                    <input
                                        type="checkbox"
                                        checked={profile.sync_calendar}
                                        onChange={(e) => setProfile({ ...profile, sync_calendar: e.target.checked })}
                                        className="rounded bg-slate-900 border-slate-700 text-cyan-500 focus:ring-0"
                                    />
                                </label>
                            </div>
                        </div>

                        {/* Data Privacy & Erasure Card */}
                        <div className="bg-[#0B0F19] border border-slate-800/80 rounded-3xl p-6 space-y-4 shadow-xl">
                            <h3 className="text-xs font-black text-white uppercase tracking-wider flex items-center gap-2">
                                <Database className="w-4 h-4 text-emerald-400" />
                                Cognitive Record & Privacy
                            </h3>
                            <p className="text-xs text-slate-400 leading-relaxed">
                                Your concept graph contains 184 mastered invariants across Distributed Systems, Operating Systems, and Dynamic Programming.
                            </p>
                            <div className="p-3 rounded-xl bg-amber-950/20 border border-amber-500/30 text-[11px] text-amber-300">
                                Active telemetry is encrypted at rest using AES-256 with user-isolated schemas.
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ProfileSettings;
