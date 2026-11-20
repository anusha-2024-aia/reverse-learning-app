import React, { useState, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Sparkles, CheckCircle2, ShieldCheck, ArrowRight,
  GraduationCap, Lock, Mail, User, School, BookOpen,
  Eye, EyeOff, AlertCircle
} from 'lucide-react';
import { AuthContext } from '../context/AuthContext';

const SignupPage = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [university, setUniversity] = useState('');
  const [focusTrack, setFocusTrack] = useState('Distributed Systems & Cloud Infrastructure');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [agreeTerms, setAgreeTerms] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { signup, demoLogin } = useContext(AuthContext);

  const handleInputChange = (setter) => (e) => {
    setter(e.target.value);
    if (error) setError(null);
    if (success) setSuccess(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    const trimmedName = name.trim();
    const trimmedEmail = email.trim();

    if (!trimmedName) {
      setError("Full Legal Name is required.");
      return;
    }

    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailRegex.test(trimmedEmail)) {
      setError("Please enter a valid email address (e.g. name@example.com).");
      return;
    }

    if (!password) {
      setError("Password is required.");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Password confirmation does not match.");
      return;
    }

    if (!agreeTerms) {
      setError("You must accept the academic honesty terms.");
      return;
    }

    setIsLoading(true);

    const result = await signup(trimmedName, trimmedEmail, password, confirmPassword, university.trim(), focusTrack);
    if (result.success) {
      setSuccess("Account created successfully! Redirecting to Sign In...");
      setTimeout(() => {
        navigate('/login', {
          state: {
            registeredEmail: trimmedEmail,
            message: "Account created successfully! Please sign in with your credentials."
          }
        });
      }, 900);
    } else {
      setError(result.error || "An error occurred during signup.");
    }

    setIsLoading(false);
  };

  const handleDemoSignIn = async () => {
    setError(null);
    if (demoLogin) {
      const res = await demoLogin();
      if (res.success) {
        navigate('/');
      } else {
        setError(res.error || 'Demo login failed');
      }
    }
  };

  const hasMinLength = password.length >= 8;
  const hasUppercase = /[A-Z]/.test(password);
  const hasSpecial = /[0-9!@#$%^&*]/.test(password);

  const isDuplicateEmailError = error && (
    error.toLowerCase().includes('already registered') ||
    error.toLowerCase().includes('already exists')
  );

  return (
    <div className="min-h-screen bg-[#080C14] text-slate-100 flex items-center justify-center p-4 md:p-8 selection:bg-cyan-500/30 selection:text-cyan-200">
      <div className="w-full max-w-6xl grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">

        {/* LEFT COLUMN: Platform Value & Testimonials (Cols 6) */}
        <div className="lg:col-span-6 space-y-8 p-4">
          <div className="space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-950/60 border border-cyan-800 text-[10px] font-black uppercase tracking-wider text-cyan-400">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span>
              REVERSE LEARNING STUDIO • FALL 2025
            </div>

            <h1 className="text-3xl md:text-5xl font-black text-white tracking-tight leading-tight">
              Join 14,000+ Students Reverse-Engineering Complex CS Concepts.
            </h1>

            <p className="text-sm text-slate-400 leading-relaxed max-w-xl">
              Shift away from rote drills. Master distributed algorithms, kernel foundations, target engineering track benchmarks, and reverse-engineer with rigorous feedback.
            </p>
          </div>

          {/* Platform Metric Pills */}
          <div className="grid grid-cols-3 gap-3">
            <div className="p-3.5 rounded-2xl bg-[#0B0F19] border border-slate-800">
              <div className="text-lg md:xl font-black text-white font-mono">14.3k</div>
              <div className="text-[10px] text-slate-400 font-semibold uppercase mt-0.5">Active Learners</div>
            </div>
            <div className="p-3.5 rounded-2xl bg-[#0B0F19] border border-slate-800">
              <div className="text-lg md:xl font-black text-cyan-400 font-mono">92.4k</div>
              <div className="text-[10px] text-slate-400 font-semibold uppercase mt-0.5">Concept Maps</div>
            </div>
            <div className="p-3.5 rounded-2xl bg-[#0B0F19] border border-slate-800">
              <div className="text-lg md:xl font-black text-purple-400 font-mono">3.8x</div>
              <div className="text-[10px] text-slate-400 font-semibold uppercase mt-0.5">Retention Lift</div>
            </div>
          </div>

          {/* Feature List */}
          <div className="space-y-3.5 text-xs text-slate-300">
            <div className="flex items-start gap-3">
              <div className="w-5 h-5 rounded-lg bg-cyan-500/10 flex items-center justify-center text-cyan-400 shrink-0 mt-0.5">
                <ShieldCheck className="w-3.5 h-3.5" />
              </div>
              <div>
                <span className="font-bold text-white">Automated Root-Cause Misconception Isolation:</span> Pinpoints granular knowledge deficits down to algorithmic invariants before midterms.
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="w-5 h-5 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-400 shrink-0 mt-0.5">
                <CheckCircle2 className="w-3.5 h-3.5" />
              </div>
              <div>
                <span className="font-bold text-white">Real-Time Voice AI Mock Interviews:</span> Practice technical system design rounds against rigorous Staff Engineer rubrics.
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="w-5 h-5 rounded-lg bg-purple-500/10 flex items-center justify-center text-purple-400 shrink-0 mt-0.5">
                <GraduationCap className="w-3.5 h-3.5" />
              </div>
              <div>
                <span className="font-bold text-white">Institutional Syllabus Sync:</span> Synchronizes directly with course calendars, exam dates, and live problem sets.
              </div>
            </div>
          </div>

          {/* Testimonial Quote */}
          <div className="p-4 rounded-2xl bg-[#0B0F19]/80 border border-slate-800/80 space-y-2">
            <p className="text-xs text-slate-300 italic leading-relaxed">
              &quot;Reverse Studio diagnosed my metric breakdown in distributed systems with LSM-Trees. Simulated my L5 interview seamlessly.&quot;
            </p>
            <div className="flex items-center gap-2.5 pt-1">
              <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-cyan-400 to-indigo-500 flex items-center justify-center text-xs font-black text-slate-950">
                ML
              </div>
              <div>
                <div className="text-xs font-bold text-white">Maya Lin</div>
                <div className="text-[10px] text-cyan-400">UC Berkeley CS &apos;26 • Systems Infrastructure Track</div>
              </div>
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: Create Student Account Form (Cols 6) */}
        <div className="lg:col-span-6 bg-[#0B0F19] border border-slate-800/80 rounded-3xl p-6 md:p-8 shadow-2xl space-y-5">
          <div>
            <h2 className="text-xl md:text-2xl font-black text-white tracking-tight">Create Your Student Account</h2>
            <p className="text-xs text-slate-400 mt-1">
              Enter your academic credentials to begin your personalized reverse syllabus.
            </p>
          </div>

          {/* 1-Click Fast Pass Demo Banner */}
          <button
            type="button"
            onClick={handleDemoSignIn}
            className="w-full p-3 rounded-2xl bg-gradient-to-r from-cyan-950/60 to-purple-950/60 border border-cyan-500/30 hover:border-cyan-400/60 text-left flex items-center justify-between group transition-all"
          >
            <div className="flex items-center gap-2.5">
              <Sparkles className="w-4 h-4 text-cyan-400" />
              <div className="text-xs font-black text-cyan-300">
                1-Click Demo Pass (Sign In as Maya Lin)
              </div>
            </div>
            <span className="text-xs font-bold text-cyan-400 group-hover:translate-x-1 transition-transform">→</span>
          </button>

          {/* Success Banner */}
          {success && (
            <div className="p-3.5 bg-emerald-950/60 border border-emerald-500/50 rounded-xl text-emerald-300 text-xs flex items-center gap-2.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>{success}</span>
            </div>
          )}

          {/* Error Banner with Smart Duplicate Email Action Link */}
          {error && (
            <div className="p-3.5 bg-rose-950/50 border border-rose-500/50 rounded-xl text-rose-300 text-xs flex items-start gap-2.5">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
              <div className="flex-1">
                {isDuplicateEmailError ? (
                  <span>
                    This email is already registered. Please{' '}
                    <Link to="/login" className="text-cyan-300 hover:text-cyan-200 font-bold underline">
                      Sign In
                    </Link>{' '}
                    or use another email.
                  </span>
                ) : (
                  <span>{error}</span>
                )}
              </div>
            </div>
          )}

          <form noValidate onSubmit={handleSubmit} className="space-y-3.5">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1" htmlFor="name">
                Full Legal Name
              </label>
              <div className="relative">
                <input
                  id="name"
                  type="text"
                  required
                  placeholder="Your Full Name"
                  className="w-full bg-[#080C14] border border-slate-700/80 rounded-xl px-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-medium"
                  value={name}
                  onChange={handleInputChange(setName)}
                  disabled={isLoading}
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1" htmlFor="email">
                Email Address
              </label>
              <div className="relative">
                <input
                  id="email"
                  type="email"
                  required
                  placeholder="you@example.com"
                  className="w-full bg-[#080C14] border border-slate-700/80 rounded-xl px-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-medium"
                  value={email}
                  onChange={handleInputChange(setEmail)}
                  disabled={isLoading}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1" htmlFor="university">
                  University / Institution
                </label>
                <input
                  id="university"
                  type="text"
                  placeholder="e.g. UC Berkeley, Stanford"
                  value={university}
                  onChange={handleInputChange(setUniversity)}
                  className="w-full bg-[#080C14] border border-slate-700/80 rounded-xl px-3 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-medium"
                  disabled={isLoading}
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1" htmlFor="focusTrack">
                  Primary Focus Track
                </label>
                <select
                  id="focusTrack"
                  value={focusTrack}
                  onChange={handleInputChange(setFocusTrack)}
                  className="w-full bg-[#080C14] border border-slate-700/80 rounded-xl px-3 py-2.5 text-xs text-white focus:outline-none focus:border-cyan-500 font-medium"
                  disabled={isLoading}
                >
                  <option value="Distributed Systems & Cloud Infrastructure">Distributed Systems & Cloud</option>
                  <option value="AI Systems & Machine Learning Infrastructure">AI Systems & Infrastructure</option>
                  <option value="Full Stack & Core Software Engineering">Full Stack SWE</option>
                  <option value="Operating Systems & Embedded Kernels">Operating Systems & Kernels</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1" htmlFor="password">
                  Access Password
                </label>
                <div className="relative">
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    required
                    placeholder="••••••••••••"
                    className="w-full bg-[#080C14] border border-slate-700/80 rounded-xl pl-4 pr-10 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-medium"
                    value={password}
                    onChange={handleInputChange(setPassword)}
                    disabled={isLoading}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200"
                    aria-label="Toggle access visibility"
                  >
                    {showPassword ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1" htmlFor="confirmPassword">
                  Confirm Password
                </label>
                <div className="relative">
                  <input
                    id="confirmPassword"
                    type={showConfirmPassword ? 'text' : 'password'}
                    required
                    placeholder="••••••••••••"
                    className="w-full bg-[#080C14] border border-slate-700/80 rounded-xl pl-4 pr-10 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-medium"
                    value={confirmPassword}
                    onChange={handleInputChange(setConfirmPassword)}
                    disabled={isLoading}
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200"
                    aria-label="Toggle confirm visibility"
                  >
                    {showConfirmPassword ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>
            </div>

            {/* Password strength checklist */}
            <div className="flex items-center gap-4 text-[10px] text-slate-400 pt-1">
              <span className={`flex items-center gap-1 ${hasMinLength ? 'text-emerald-400' : 'text-slate-500'}`}>
                {hasMinLength ? '✓' : '•'} 8+ chars
              </span>
              <span className={`flex items-center gap-1 ${hasUppercase ? 'text-emerald-400' : 'text-slate-500'}`}>
                {hasUppercase ? '✓' : '•'} 1 uppercase
              </span>
              <span className={`flex items-center gap-1 ${hasSpecial ? 'text-emerald-400' : 'text-slate-500'}`}>
                {hasSpecial ? '✓' : '•'} 1 number/symbol
              </span>
            </div>

            {/* Terms checkbox */}
            <div className="pt-2">
              <label className="flex items-start gap-2.5 cursor-pointer text-xs text-slate-400 leading-snug">
                <input
                  type="checkbox"
                  checked={agreeTerms}
                  onChange={(e) => { setAgreeTerms(e.target.checked); if (error) setError(null); }}
                  className="mt-0.5 rounded bg-[#080C14] border-slate-700 text-cyan-500 focus:ring-0"
                  disabled={isLoading}
                />
                <span>
                  I accept the <span className="text-cyan-400 font-medium">Academic Honesty Policy</span> and consent to personalized algorithmic diagnostic telemetry.
                </span>
              </label>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-gradient-to-r from-cyan-500 via-indigo-600 to-purple-600 hover:opacity-95 text-white font-black py-3 px-4 rounded-xl shadow-lg shadow-cyan-500/20 transition-all text-xs flex items-center justify-center gap-2 disabled:opacity-50"
            >
              <span>{isLoading ? 'Creating Account...' : 'Create Student Account'}</span>
              {!isLoading && <ArrowRight className="w-3.5 h-3.5" />}
            </button>
          </form>

          <p className="text-center text-slate-400 text-xs pt-1">
            Already registered?{' '}
            <Link to="/login" className="text-cyan-400 hover:text-cyan-300 font-bold ml-1">
              Sign In →
            </Link>
          </p>
        </div>

      </div>
    </div>
  );
};

export default SignupPage;
