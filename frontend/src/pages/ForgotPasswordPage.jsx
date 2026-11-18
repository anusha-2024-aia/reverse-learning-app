import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { KeyRound, Mail, ShieldCheck, ArrowRight, ArrowLeft, CheckCircle2, AlertCircle, Sparkles, Lock } from 'lucide-react';
import api from '../api/axios';

const ForgotPasswordPage = () => {
    const navigate = useNavigate();
    const [email, setEmail] = useState('maya.lin@berkeley.edu');
    const [token, setToken] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');

    const [step1Loading, setStep1Loading] = useState(false);
    const [step1Message, setStep1Message] = useState(null);
    const [step2Loading, setStep2Loading] = useState(false);
    const [step2Message, setStep2Message] = useState(null);
    const [error, setError] = useState(null);

    const handleSendToken = async (e) => {
        e.preventDefault();
        setError(null);
        setStep1Message(null);
        setStep1Loading(true);

        try {
            const res = await api.post('/auth/forgot-password', { email: email.trim() });
            setStep1Message(res.data?.message || "Verification code dispatched.");
            if (res.data?.dev_token) {
                setToken(res.data.dev_token);
            }
        } catch (err) {
            setError(err.response?.data?.detail || "Could not dispatch recovery token.");
        } finally {
            setStep1Loading(false);
        }
    };

    const handleResetPassword = async (e) => {
        e.preventDefault();
        setError(null);
        setStep2Message(null);

        if (!token.trim()) {
            setError("Please enter the 6-digit verification token.");
            return;
        }

        if (newPassword.length < 6) {
            setError("Password must be at least 6 characters.");
            return;
        }

        if (newPassword !== confirmPassword) {
            setError("Passwords do not match.");
            return;
        }

        setStep2Loading(true);

        try {
            const res = await api.post('/auth/reset-password', {
                email: email.trim(),
                token: token.trim(),
                new_password: newPassword
            });
            setStep2Message(res.data?.message || "Password updated successfully. Redirecting to login...");
            setTimeout(() => {
                navigate('/login');
            }, 1800);
        } catch (err) {
            setError(err.response?.data?.detail || "Invalid or expired token.");
        } finally {
            setStep2Loading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#080C14] text-slate-100 flex flex-col justify-center items-center p-4 md:p-8 selection:bg-cyan-500/30 selection:text-cyan-200">
            {/* Header */}
            <div className="w-full max-w-4xl space-y-2 text-center mb-8">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-950/60 border border-cyan-800 text-[10px] font-black uppercase tracking-wider text-cyan-400">
                    <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span>
                    SECURITY & RECOVERY TELEMETRY
                </div>
                <h1 className="text-2xl md:text-3xl font-black text-white tracking-tight">
                    Academic Access Recovery
                </h1>
                <p className="text-xs text-slate-400 max-w-md mx-auto">
                    Multi-factor credential recovery for accredited university accounts and diagnostic profiles.
                </p>
            </div>

            {error && (
                <div className="w-full max-w-4xl mb-6 p-4 rounded-2xl bg-rose-950/40 border border-rose-500/40 text-rose-300 text-xs flex items-center gap-2.5">
                    <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
                    <span>{error}</span>
                </div>
            )}

            {/* Split Recovery Cards matching Stitch Screenshot 8 */}
            <div className="w-full max-w-4xl grid grid-cols-1 md:grid-cols-2 gap-6">

                {/* Step 1: Request Token Card */}
                <div className="bg-[#0B0F19] border border-slate-800/80 rounded-3xl p-6 md:p-8 space-y-5 shadow-2xl flex flex-col justify-between">
                    <div className="space-y-4">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
                                <Mail className="w-5 h-5" />
                            </div>
                            <div>
                                <h3 className="text-sm font-black text-white uppercase tracking-wider">Reset Your Security Credentials</h3>
                                <p className="text-[11px] text-slate-400">Step 1 • Identity Verification</p>
                            </div>
                        </div>

                        <p className="text-xs text-slate-300 leading-relaxed">
                            Enter your registered university email. We will generate a cryptographic verification token for your session.
                        </p>

                        <form onSubmit={handleSendToken} className="space-y-4">
                            <div>
                                <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1" htmlFor="recovery-email">
                                    University Email (.edu)
                                </label>
                                <input
                                    id="recovery-email"
                                    type="email"
                                    required
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="maya.lin@berkeley.edu"
                                    className="w-full bg-[#080C14] border border-slate-700/80 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-cyan-500 font-medium"
                                />
                            </div>

                            {step1Message && (
                                <div className="p-3 bg-cyan-950/40 border border-cyan-500/40 rounded-xl text-cyan-300 text-xs flex items-start gap-2">
                                    <Sparkles className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                                    <div>
                                        <div className="font-bold">{step1Message}</div>
                                        <div className="text-[10px] text-slate-400 mt-0.5">Check your inbox or review local console output for the 6-digit code.</div>
                                    </div>
                                </div>
                            )}

                            <button
                                type="submit"
                                disabled={step1Loading}
                                className="w-full py-3 px-4 rounded-xl bg-[#080C14] hover:bg-slate-800 border border-cyan-500/40 text-cyan-300 font-bold text-xs flex items-center justify-center gap-2 transition-all disabled:opacity-50"
                            >
                                <span>{step1Loading ? 'Dispatching Token...' : 'Send Secure Verification Link'}</span>
                                <ArrowRight className="w-3.5 h-3.5" />
                            </button>
                        </form>
                    </div>

                    <div className="pt-4 border-t border-slate-800/80 text-[11px] text-slate-500 flex items-center gap-1.5">
                        <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                        <span>256-bit token entropy • 15 min TTL expiry</span>
                    </div>
                </div>

                {/* Step 2: Instant Token & Password Reset Card */}
                <div className="bg-[#0B0F19] border border-slate-800/80 rounded-3xl p-6 md:p-8 space-y-5 shadow-2xl flex flex-col justify-between">
                    <div className="space-y-4">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400">
                                <KeyRound className="w-5 h-5" />
                            </div>
                            <div>
                                <h3 className="text-sm font-black text-white uppercase tracking-wider">Instant Token & Credentials</h3>
                                <p className="text-[11px] text-slate-400">Step 2 • Update Password</p>
                            </div>
                        </div>

                        <form onSubmit={handleResetPassword} className="space-y-3.5">
                            <div>
                                <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1" htmlFor="verification-token">
                                    6-digit Verification Token
                                </label>
                                <input
                                    id="verification-token"
                                    type="text"
                                    maxLength={6}
                                    required
                                    value={token}
                                    onChange={(e) => setToken(e.target.value)}
                                    placeholder="849201"
                                    className="w-full bg-[#080C14] border border-slate-700/80 rounded-xl px-4 py-2.5 text-sm text-cyan-400 font-mono tracking-widest text-center focus:outline-none focus:border-cyan-500 font-bold"
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1" htmlFor="new-password">
                                    New Access Password
                                </label>
                                <input
                                    id="new-password"
                                    type="password"
                                    required
                                    value={newPassword}
                                    onChange={(e) => setNewPassword(e.target.value)}
                                    placeholder="••••••••••••"
                                    className="w-full bg-[#080C14] border border-slate-700/80 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-cyan-500 font-medium"
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1" htmlFor="confirm-new-password">
                                    Confirm New Password
                                </label>
                                <input
                                    id="confirm-new-password"
                                    type="password"
                                    required
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    placeholder="••••••••••••"
                                    className="w-full bg-[#080C14] border border-slate-700/80 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-cyan-500 font-medium"
                                />
                            </div>

                            {step2Message && (
                                <div className="p-3 bg-emerald-950/40 border border-emerald-500/40 rounded-xl text-emerald-300 text-xs flex items-center gap-2">
                                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                                    <span>{step2Message}</span>
                                </div>
                            )}

                            <button
                                type="submit"
                                disabled={step2Loading}
                                className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-cyan-500 via-indigo-600 to-purple-600 hover:opacity-95 text-white font-black text-xs shadow-lg shadow-cyan-500/20 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
                            >
                                <span>{step2Loading ? 'Updating...' : 'Update Credentials & Return to Login'}</span>
                                <ArrowRight className="w-3.5 h-3.5" />
                            </button>
                        </form>
                    </div>

                    <div className="pt-4 border-t border-slate-800/80 text-center">
                        <Link to="/login" className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white font-semibold transition-colors">
                            <ArrowLeft className="w-3.5 h-3.5" />
                            <span>Back to Student Login</span>
                        </Link>
                    </div>
                </div>

            </div>
        </div>
    );
};

export default ForgotPasswordPage;
