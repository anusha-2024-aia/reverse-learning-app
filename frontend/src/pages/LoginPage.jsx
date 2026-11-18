import React, { useState, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Sparkles, GraduationCap, Lock, Mail, ArrowRight, ShieldCheck, CheckCircle2 } from 'lucide-react';
import { AuthContext } from '../context/AuthContext';

const LoginPage = () => {
  const [usernameOrEmail, setUsernameOrEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(true);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isDemoLoading, setIsDemoLoading] = useState(false);
  const navigate = useNavigate();
  const { login, demoLogin } = useContext(AuthContext);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    const result = await login(usernameOrEmail, password);
    if (result.success) {
      navigate('/');
    } else {
      setError(result.error);
    }

    setIsLoading(false);
  };

  const handleDemoSignIn = async () => {
    setError(null);
    setIsDemoLoading(true);
    if (demoLogin) {
      const result = await demoLogin();
      if (result.success) {
        navigate('/');
      } else {
        setError(result.error || 'Demo login failed');
      }
    } else {
      // Fallback
      const result = await login('maya.lin@berkeley.edu', 'DemoStudent2025!');
      if (result.success) {
        navigate('/');
      } else {
        setError(result.error);
      }
    }
    setIsDemoLoading(false);
  };

  return (
    <div className="min-h-screen bg-[#080C14] text-slate-100 flex flex-col justify-center items-center p-4 selection:bg-cyan-500/30 selection:text-cyan-200">
      {/* Background glow ambient effects */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[500px] h-[350px] bg-gradient-to-tr from-cyan-500/10 via-indigo-500/10 to-purple-500/10 rounded-full blur-3xl pointer-events-none"></div>

      <div className="w-full max-w-md bg-[#0B0F19] rounded-3xl p-8 shadow-2xl border border-slate-800/80 relative z-10 space-y-6">
        {/* Header Icon & Title */}
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-cyan-500 to-purple-600 flex items-center justify-center mx-auto shadow-lg shadow-cyan-500/20">
            <GraduationCap className="w-6 h-6 text-white" />
          </div>
          <h2 className="text-2xl font-black text-white tracking-tight">Welcome Back</h2>
          <p className="text-xs text-slate-400 font-medium">
            Continuous Learning Studio & Cognitive Diagnostics
          </p>
        </div>

        {/* Demo Student Fast Pass Pill */}
        <button
          type="button"
          onClick={handleDemoSignIn}
          disabled={isDemoLoading}
          className="w-full p-3 rounded-2xl bg-gradient-to-r from-cyan-950/60 to-indigo-950/60 border border-cyan-500/30 hover:border-cyan-400/60 text-left flex items-center justify-between group transition-all"
        >
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-xl bg-cyan-500/20 flex items-center justify-center text-cyan-400">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <div className="text-xs font-black text-cyan-300">
                {isDemoLoading ? 'Signing in as Maya Lin...' : '1-Click Demo Account (Maya Lin)'}
              </div>
              <div className="text-[10px] text-slate-400">UC Berkeley CS • 84% Mastery • Fully Seeded</div>
            </div>
          </div>
          <span className="text-xs font-bold text-cyan-400 group-hover:translate-x-1 transition-transform">→</span>
        </button>

        {error && (
          <div className="p-3 bg-rose-950/50 border border-rose-500/50 rounded-xl text-rose-300 text-xs">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5" htmlFor="username">
              Username or Email
            </label>
            <div className="relative">
              <input
                id="username"
                type="text"
                required
                className="w-full bg-[#080C14] border border-slate-700/80 rounded-xl px-4 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-medium"
                placeholder="Institutional email or username"
                value={usernameOrEmail}
                onChange={(e) => setUsernameOrEmail(e.target.value)}
              />
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-400" htmlFor="password">
                Password
              </label>
              <Link to="/forgot-password" className="text-[11px] font-semibold text-cyan-400 hover:text-cyan-300 transition-colors">
                Forgot Password?
              </Link>
            </div>
            <div className="relative">
              <input
                id="password"
                type="password"
                required
                className="w-full bg-[#080C14] border border-slate-700/80 rounded-xl px-4 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-medium"
                placeholder="••••••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <div className="flex items-center">
            <label className="flex items-center gap-2 cursor-pointer text-xs text-slate-400">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="rounded bg-[#080C14] border-slate-700 text-cyan-500 focus:ring-0"
              />
              <span>Remember me for 30 days</span>
            </label>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-black py-3 px-4 rounded-xl shadow-lg shadow-cyan-500/20 transition-all text-xs flex items-center justify-center gap-2 disabled:opacity-50"
          >
            <span>{isLoading ? 'Logging in...' : 'Log In'}</span>
            {!isLoading && <ArrowRight className="w-3.5 h-3.5" />}
          </button>
        </form>

        <div className="relative text-center my-4">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-slate-800"></div>
          </div>
          <span className="relative bg-[#0B0F19] px-3 text-[10px] font-bold uppercase tracking-wider text-slate-500">
            OR AUTHENTICATE WITH INSTITUTIONAL SSO
          </span>
        </div>

        <div className="space-y-2">
          <button
            type="button"
            onClick={handleDemoSignIn}
            className="w-full py-2.5 px-4 rounded-xl bg-[#080C14] hover:bg-slate-800 border border-slate-700 text-xs font-semibold text-slate-300 flex items-center justify-center gap-2 transition-colors"
          >
            <span>Continue with Google Workspace (Berkeley SSO)</span>
          </button>
          <button
            type="button"
            onClick={handleDemoSignIn}
            className="w-full py-2.5 px-4 rounded-xl bg-[#080C14] hover:bg-slate-800 border border-slate-700 text-xs font-semibold text-slate-300 flex items-center justify-center gap-2 transition-colors"
          >
            <span>Continue with GitHub Education</span>
          </button>
        </div>

        <p className="text-center text-slate-400 text-xs pt-2">
          Don't have an account?{' '}
          <Link to="/signup" className="text-cyan-400 hover:text-cyan-300 font-bold ml-1">
            Create Student Account →
          </Link>
        </p>
      </div>
    </div>
  );
};

export default LoginPage;
