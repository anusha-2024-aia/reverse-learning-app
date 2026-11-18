import React, { useState, useEffect, useContext, useRef } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import {
    LayoutDashboard, Activity, Compass, RotateCcw,
    FileText, Mic, Video, BarChart2, Settings,
    LogOut, Search, Bell, Sparkles, ChevronRight,
    Menu, X, ChevronsLeft, ChevronsRight, ShieldCheck,
    User, Home, ArrowRight, CheckCircle2
} from 'lucide-react';
import { AuthContext } from '../../context/AuthContext';

const StitchLayout = ({ children }) => {
    const auth = useContext(AuthContext) || {};
    const user = auth.user || null;
    const logout = auth.logout || (() => {});
    const navigate = useNavigate();
    const location = useLocation();

    // Responsive and collapse state
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const [isCollapsed, setIsCollapsed] = useState(() => {
        try {
            return localStorage.getItem('reverse_studio_sidebar_collapsed') === 'true';
        } catch {
            return false;
        }
    });
    const [searchQuery, setSearchQuery] = useState('');
    const [userDropdownOpen, setUserDropdownOpen] = useState(false);
    const userMenuRef = useRef(null);
    const searchInputRef = useRef(null);

    // Keyboard shortcut (⌘K or Ctrl+K) to focus search
    useEffect(() => {
        const handleKeyDown = (e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                if (searchInputRef.current) {
                    searchInputRef.current.focus();
                }
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, []);

    // Click outside user dropdown to close it
    useEffect(() => {
        const handleClickOutside = (e) => {
            if (userMenuRef.current && !userMenuRef.current.contains(e.target)) {
                setUserDropdownOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const toggleCollapse = () => {
        const nextState = !isCollapsed;
        setIsCollapsed(nextState);
        try {
            localStorage.setItem('reverse_studio_sidebar_collapsed', String(nextState));
        } catch {
            // ignore storage errors
        }
    };

    const handleLogout = () => {
        setMobileMenuOpen(false);
        setUserDropdownOpen(false);
        logout();
        navigate('/login');
    };

    const handleSearchSubmit = (e) => {
        e.preventDefault();
        if (searchQuery.trim()) {
            navigate(`/study?search=${encodeURIComponent(searchQuery.trim())}`);
            setSearchQuery('');
        }
    };

    // Navigation sections requested in specification
    const academicHubLinks = [
        { name: 'Dashboard', path: '/', icon: LayoutDashboard },
        { name: 'Knowledge Diagnostic', path: '/knowledge-gaps', icon: Activity },
        { name: 'Topic Exploration', path: '/study', icon: Compass },
        { name: 'Smart Revision Engine', path: '/revision', icon: RotateCcw },
    ];

    const careerEngineLinks = [
        { name: 'Resume Gap Audit', path: '/resume', icon: FileText },
        { name: 'AI Mock Interview', path: '/interview', icon: Mic },
        { name: 'Virtual Study Room', path: '/study-room', icon: Video },
        { name: 'Learning Analytics', path: '/analytics', icon: BarChart2 },
    ];

    const accountLinks = [
        { name: 'Settings & Profile', path: '/profile', icon: Settings },
    ];

    // Compute dynamic breadcrumb
    const getBreadcrumb = (pathname) => {
        if (pathname === '/') return { section: 'Academic Hub', page: 'Dashboard', path: '/' };
        if (pathname.startsWith('/knowledge-gaps')) return { section: 'Academic Hub', page: 'Knowledge Diagnostic', path: '/knowledge-gaps' };
        if (pathname.startsWith('/study-room')) return { section: 'Career Engine', page: 'Virtual Study Room', path: '/study-room' };
        if (pathname.startsWith('/study')) return { section: 'Academic Hub', page: 'Topic Exploration', path: '/study' };
        if (pathname.startsWith('/revision')) return { section: 'Academic Hub', page: 'Smart Revision Engine', path: '/revision' };
        if (pathname.startsWith('/resume')) return { section: 'Career Engine', page: 'Resume Gap Audit', path: '/resume' };
        if (pathname.startsWith('/interview') || pathname.startsWith('/mock-interview')) return { section: 'Career Engine', page: 'AI Mock Interview', path: '/interview' };
        if (pathname.startsWith('/analytics') || pathname.startsWith('/insights')) return { section: 'Career Engine', page: 'Learning Analytics', path: '/analytics' };
        if (pathname.startsWith('/profile') || pathname.startsWith('/settings')) return { section: 'Account', page: 'Settings & Profile', path: '/profile' };
        if (pathname.startsWith('/achievements')) return { section: 'Academic Hub', page: 'Achievements', path: '/achievements' };
        if (pathname.startsWith('/learning-path') || pathname.startsWith('/learning-roadmap')) return { section: 'Academic Hub', page: 'Learning Roadmap', path: '/learning-path' };
        if (pathname.startsWith('/history')) return { section: 'Academic Hub', page: 'Study History', path: '/history' };
        if (pathname.startsWith('/syllabi')) return { section: 'Academic Hub', page: 'Syllabus Tracker', path: '/syllabi' };
        return { section: 'Academic Hub', page: 'Overview', path: '/' };
    };

    const breadcrumb = getBreadcrumb(location.pathname);

    const isLinkActive = (path) => {
        if (path === '/') {
            return location.pathname === '/';
        }
        return location.pathname === path || location.pathname.startsWith(path);
    };

    return (
        <div className="min-h-screen bg-[#080C14] text-slate-100 flex flex-col font-sans selection:bg-cyan-500/30 selection:text-cyan-200">
            {/* ========================================================= */}
            {/* MOBILE HEADER BAR (< lg)                                  */}
            {/* ========================================================= */}
            <div className="lg:hidden flex items-center justify-between px-4 py-3 bg-[#0B0F19] border-b border-slate-800/80 sticky top-0 z-40">
                <div className="flex items-center gap-2.5">
                    <button
                        onClick={() => setMobileMenuOpen(true)}
                        className="p-2 rounded-lg bg-slate-800/80 text-slate-300 hover:text-white transition-colors"
                        aria-label="Open navigation menu"
                    >
                        <Menu className="w-5 h-5" />
                    </button>
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-500 to-purple-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
                        <Sparkles className="w-4 h-4 text-white" />
                    </div>
                    <div>
                        <div className="text-sm font-black tracking-tight text-white flex items-center gap-1.5">
                            Reverse Studio
                        </div>
                        <div className="text-[9px] uppercase tracking-wider font-semibold text-cyan-400">
                            INTELLIGENCE PLATFORM
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    <button
                        onClick={() => navigate('/knowledge-gaps')}
                        className="px-2.5 py-1 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-[11px] font-bold shadow-md shadow-purple-600/20 transition-colors"
                    >
                        + Diagnostic
                    </button>
                    <button
                        onClick={() => setUserDropdownOpen(!userDropdownOpen)}
                        className="w-8 h-8 rounded-full bg-gradient-to-tr from-cyan-400 to-purple-600 p-[1.5px]"
                        aria-label="User profile"
                    >
                        <div className="w-full h-full rounded-full bg-slate-900 flex items-center justify-center text-xs font-bold text-cyan-300">
                            {user?.name ? user.name.charAt(0).toUpperCase() : 'M'}
                        </div>
                    </button>
                </div>
            </div>

            {/* ========================================================= */}
            {/* MOBILE DRAWER (< lg)                                      */}
            {/* ========================================================= */}
            {mobileMenuOpen && (
                <div className="lg:hidden fixed inset-0 z-50 flex">
                    {/* Backdrop */}
                    <div
                        className="fixed inset-0 bg-black/75 backdrop-blur-sm transition-opacity"
                        onClick={() => setMobileMenuOpen(false)}
                    />
                    {/* Drawer Panel */}
                    <aside className="relative w-72 max-w-[85vw] bg-[#0B0F19] border-r border-slate-800 z-50 flex flex-col h-full shadow-2xl animate-in slide-in-from-left duration-200">
                        {/* Drawer Brand Header */}
                        <div className="p-4 border-b border-slate-800/80 flex items-center justify-between">
                            <div className="flex items-center gap-2.5">
                                <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-500 to-purple-600 flex items-center justify-center shadow-lg shadow-cyan-500/25">
                                    <Sparkles className="w-4 h-4 text-white" />
                                </div>
                                <div>
                                    <div className="text-sm font-black text-white">Reverse Studio</div>
                                    <div className="text-[9px] uppercase font-bold text-cyan-400">INTELLIGENCE PLATFORM</div>
                                </div>
                            </div>
                            <button
                                onClick={() => setMobileMenuOpen(false)}
                                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
                                aria-label="Close navigation drawer"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        {/* Navigation Links inside Drawer */}
                        <div className="flex-1 overflow-y-auto px-3 py-4 space-y-5">
                            {/* Academic Hub */}
                            <div>
                                <div className="px-3 mb-2 text-[10px] font-black uppercase tracking-wider text-slate-400">
                                    ACADEMIC HUB
                                </div>
                                <nav className="space-y-1">
                                    {academicHubLinks.map((link) => {
                                        const Icon = link.icon;
                                        const active = isLinkActive(link.path);
                                        return (
                                            <NavLink
                                                key={link.path}
                                                to={link.path}
                                                onClick={() => setMobileMenuOpen(false)}
                                                className={`
                                                    flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-semibold transition-all
                                                    ${active
                                                        ? 'bg-gradient-to-r from-cyan-500/20 via-purple-500/10 to-transparent text-cyan-300 border-l-2 border-cyan-400'
                                                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'}
                                                `}
                                            >
                                                <div className="flex items-center gap-3">
                                                    <Icon className={`w-4 h-4 ${active ? 'text-cyan-400' : 'text-slate-400'}`} />
                                                    <span>{link.name}</span>
                                                </div>
                                                {active && <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>}
                                            </NavLink>
                                        );
                                    })}
                                </nav>
                            </div>

                            {/* Career Engine */}
                            <div>
                                <div className="px-3 mb-2 text-[10px] font-black uppercase tracking-wider text-slate-400">
                                    CAREER ENGINE
                                </div>
                                <nav className="space-y-1">
                                    {careerEngineLinks.map((link) => {
                                        const Icon = link.icon;
                                        const active = isLinkActive(link.path);
                                        return (
                                            <NavLink
                                                key={link.path}
                                                to={link.path}
                                                onClick={() => setMobileMenuOpen(false)}
                                                className={`
                                                    flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-semibold transition-all
                                                    ${active
                                                        ? 'bg-gradient-to-r from-cyan-500/20 via-purple-500/10 to-transparent text-cyan-300 border-l-2 border-cyan-400'
                                                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'}
                                                `}
                                            >
                                                <div className="flex items-center gap-3">
                                                    <Icon className={`w-4 h-4 ${active ? 'text-cyan-400' : 'text-slate-400'}`} />
                                                    <span>{link.name}</span>
                                                </div>
                                                {active && <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>}
                                            </NavLink>
                                        );
                                    })}
                                </nav>
                            </div>

                            {/* Account Section */}
                            <div className="pt-2 border-t border-slate-800/80">
                                <div className="px-3 mb-2 text-[10px] font-black uppercase tracking-wider text-slate-400">
                                    ACCOUNT
                                </div>
                                <nav className="space-y-1">
                                    {accountLinks.map((link) => {
                                        const Icon = link.icon;
                                        const active = isLinkActive(link.path);
                                        return (
                                            <NavLink
                                                key={link.path}
                                                to={link.path}
                                                onClick={() => setMobileMenuOpen(false)}
                                                className={`
                                                    flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-semibold transition-all
                                                    ${active
                                                        ? 'bg-gradient-to-r from-cyan-500/20 via-purple-500/10 to-transparent text-cyan-300 border-l-2 border-cyan-400'
                                                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'}
                                                `}
                                            >
                                                <div className="flex items-center gap-3">
                                                    <Icon className={`w-4 h-4 ${active ? 'text-cyan-400' : 'text-slate-400'}`} />
                                                    <span>{link.name}</span>
                                                </div>
                                                {active && <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>}
                                            </NavLink>
                                        );
                                    })}
                                    <button
                                        onClick={handleLogout}
                                        className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 transition-colors"
                                    >
                                        <LogOut className="w-4 h-4" />
                                        <span>Logout</span>
                                    </button>
                                </nav>
                            </div>
                        </div>

                        {/* Drawer Footer Status */}
                        <div className="p-3 border-t border-slate-800/80 bg-[#070B12]/80">
                            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800/60">
                                <div className="flex items-center justify-between text-xs font-semibold mb-1">
                                    <span className="text-slate-400 flex items-center gap-1.5">
                                        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                                        Syllabus Sync
                                    </span>
                                    <span className="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">
                                        Live
                                    </span>
                                </div>
                                <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden mt-1.5">
                                    <div className="bg-gradient-to-r from-cyan-500 to-purple-500 h-1.5 rounded-full" style={{ width: '84%' }}></div>
                                </div>
                            </div>
                        </div>
                    </aside>
                </div>
            )}

            {/* ========================================================= */}
            {/* MAIN DESKTOP SHELL (Sidebar + Top Bar + Body)             */}
            {/* ========================================================= */}
            <div className="flex-1 flex overflow-hidden">
                {/* Desktop Left Sidebar with Collapse/Expand */}
                <aside className={`
                    hidden lg:flex flex-col bg-[#0B0F19] border-r border-slate-800/80 transition-all duration-300 ease-in-out z-30
                    ${isCollapsed ? 'w-20' : 'w-64'}
                `}>
                    {/* Brand Header & Collapse Toggle */}
                    <div className="p-4 border-b border-slate-800/80 flex items-center justify-between">
                        {!isCollapsed ? (
                            <>
                                <div className="flex items-center gap-3 min-w-0">
                                    <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-purple-600 flex items-center justify-center shrink-0 shadow-lg shadow-cyan-500/25">
                                        <Sparkles className="w-5 h-5 text-white" />
                                    </div>
                                    <div className="min-w-0">
                                        <div className="text-sm font-black tracking-tight text-white truncate">
                                            Reverse Studio
                                        </div>
                                        <div className="text-[9px] uppercase tracking-wider font-bold text-cyan-400 truncate">
                                            INTELLIGENCE PLATFORM
                                        </div>
                                    </div>
                                </div>
                                <button
                                    onClick={toggleCollapse}
                                    title="Collapse sidebar"
                                    className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/60 transition-colors"
                                    aria-label="Collapse sidebar"
                                >
                                    <ChevronsLeft className="w-4 h-4" />
                                </button>
                            </>
                        ) : (
                            <div className="w-full flex flex-col items-center gap-3">
                                <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-purple-600 flex items-center justify-center shrink-0 shadow-lg shadow-cyan-500/25">
                                    <Sparkles className="w-5 h-5 text-white" />
                                </div>
                                <button
                                    onClick={toggleCollapse}
                                    title="Expand sidebar"
                                    className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/60 transition-colors"
                                    aria-label="Expand sidebar"
                                >
                                    <ChevronsRight className="w-4 h-4" />
                                </button>
                            </div>
                        )}
                    </div>

                    {/* Navigation Groups */}
                    <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
                        {/* Section 1: Academic Hub */}
                        <div>
                            {!isCollapsed && (
                                <div className="px-3 mb-2 text-[10px] font-black uppercase tracking-wider text-slate-400">
                                    ACADEMIC HUB
                                </div>
                            )}
                            {isCollapsed && <div className="my-2 border-t border-slate-800/60" />}
                            <nav className="space-y-1">
                                {academicHubLinks.map((link) => {
                                    const Icon = link.icon;
                                    const active = isLinkActive(link.path);
                                    return (
                                        <NavLink
                                            key={link.path}
                                            to={link.path}
                                            title={isCollapsed ? link.name : undefined}
                                            className={`
                                                flex items-center ${isCollapsed ? 'justify-center px-2' : 'justify-between px-3'} py-2.5 rounded-xl text-xs font-semibold transition-all
                                                ${active
                                                    ? 'bg-gradient-to-r from-cyan-500/15 via-purple-500/10 to-transparent text-cyan-300 border-l-2 border-cyan-400 shadow-sm shadow-cyan-500/10'
                                                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'}
                                            `}
                                        >
                                            <div className="flex items-center gap-3">
                                                <Icon className={`w-4 h-4 shrink-0 ${active ? 'text-cyan-400' : 'text-slate-400'}`} />
                                                {!isCollapsed && <span className="truncate">{link.name}</span>}
                                            </div>
                                            {!isCollapsed && active && (
                                                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 shadow-sm shadow-cyan-400"></span>
                                            )}
                                        </NavLink>
                                    );
                                })}
                            </nav>
                        </div>

                        {/* Section 2: Career Engine */}
                        <div>
                            {!isCollapsed && (
                                <div className="px-3 mb-2 text-[10px] font-black uppercase tracking-wider text-slate-400">
                                    CAREER ENGINE
                                </div>
                            )}
                            {isCollapsed && <div className="my-2 border-t border-slate-800/60" />}
                            <nav className="space-y-1">
                                {careerEngineLinks.map((link) => {
                                    const Icon = link.icon;
                                    const active = isLinkActive(link.path);
                                    return (
                                        <NavLink
                                            key={link.path}
                                            to={link.path}
                                            title={isCollapsed ? link.name : undefined}
                                            className={`
                                                flex items-center ${isCollapsed ? 'justify-center px-2' : 'justify-between px-3'} py-2.5 rounded-xl text-xs font-semibold transition-all
                                                ${active
                                                    ? 'bg-gradient-to-r from-cyan-500/15 via-purple-500/10 to-transparent text-cyan-300 border-l-2 border-cyan-400 shadow-sm shadow-cyan-500/10'
                                                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'}
                                            `}
                                        >
                                            <div className="flex items-center gap-3">
                                                <Icon className={`w-4 h-4 shrink-0 ${active ? 'text-cyan-400' : 'text-slate-400'}`} />
                                                {!isCollapsed && <span className="truncate">{link.name}</span>}
                                            </div>
                                            {!isCollapsed && active && (
                                                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 shadow-sm shadow-cyan-400"></span>
                                            )}
                                        </NavLink>
                                    );
                                })}
                            </nav>
                        </div>

                        {/* Section 3: Account */}
                        <div>
                            {!isCollapsed && (
                                <div className="px-3 mb-2 text-[10px] font-black uppercase tracking-wider text-slate-400">
                                    ACCOUNT
                                </div>
                            )}
                            {isCollapsed && <div className="my-2 border-t border-slate-800/60" />}
                            <nav className="space-y-1">
                                {accountLinks.map((link) => {
                                    const Icon = link.icon;
                                    const active = isLinkActive(link.path);
                                    return (
                                        <NavLink
                                            key={link.path}
                                            to={link.path}
                                            title={isCollapsed ? link.name : undefined}
                                            className={`
                                                flex items-center ${isCollapsed ? 'justify-center px-2' : 'justify-between px-3'} py-2.5 rounded-xl text-xs font-semibold transition-all
                                                ${active
                                                    ? 'bg-gradient-to-r from-cyan-500/15 via-purple-500/10 to-transparent text-cyan-300 border-l-2 border-cyan-400 shadow-sm shadow-cyan-500/10'
                                                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'}
                                            `}
                                        >
                                            <div className="flex items-center gap-3">
                                                <Icon className={`w-4 h-4 shrink-0 ${active ? 'text-cyan-400' : 'text-slate-400'}`} />
                                                {!isCollapsed && <span className="truncate">{link.name}</span>}
                                            </div>
                                            {!isCollapsed && active && (
                                                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 shadow-sm shadow-cyan-400"></span>
                                            )}
                                        </NavLink>
                                    );
                                })}
                                <button
                                    onClick={handleLogout}
                                    title={isCollapsed ? "Logout" : undefined}
                                    className={`
                                        w-full flex items-center ${isCollapsed ? 'justify-center px-2' : 'gap-3 px-3'} py-2.5 rounded-xl text-xs font-semibold text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 transition-colors
                                    `}
                                >
                                    <LogOut className="w-4 h-4 shrink-0" />
                                    {!isCollapsed && <span className="truncate">Logout</span>}
                                </button>
                            </nav>
                        </div>
                    </div>

                    {/* Bottom Status Card (Only shown when expanded) */}
                    {!isCollapsed && (
                        <div className="p-3 border-t border-slate-800/80 bg-[#070B12]/80 space-y-2">
                            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800/60">
                                <div className="flex items-center justify-between text-xs font-semibold mb-1">
                                    <span className="text-slate-400 flex items-center gap-1.5">
                                        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                                        Syllabus Sync
                                    </span>
                                    <span className="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">
                                        Live
                                    </span>
                                </div>
                                <div className="flex items-center justify-between text-[11px] text-slate-400 mb-1">
                                    <span>Cognitive Mastery</span>
                                    <span className="text-white font-bold">84%</span>
                                </div>
                                <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                                    <div className="bg-gradient-to-r from-cyan-500 to-purple-500 h-1.5 rounded-full" style={{ width: '84%' }}></div>
                                </div>
                            </div>
                        </div>
                    )}
                </aside>

                {/* Main Content Area */}
                <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
                    {/* ========================================================= */}
                    {/* CONSISTENT TOP NAVIGATION BAR                             */}
                    {/* ========================================================= */}
                    <header className="h-16 px-4 md:px-6 bg-[#0B0F19]/90 backdrop-blur-md border-b border-slate-800/80 flex items-center justify-between gap-4 z-20 shrink-0">
                        {/* Left: Breadcrumbs & Current Page Title */}
                        <div className="flex items-center gap-2 min-w-0">
                            <div className="flex items-center gap-1.5 text-xs">
                                <NavLink to="/" className="text-slate-400 hover:text-slate-200 transition-colors hidden sm:inline-flex items-center gap-1">
                                    <Home className="w-3.5 h-3.5" />
                                </NavLink>
                                <span className="text-slate-600 hidden sm:inline">/</span>
                                <span className="text-slate-400 font-semibold hidden md:inline truncate">{breadcrumb.section}</span>
                                <span className="text-slate-600 hidden md:inline">/</span>
                                <span className="text-white font-black truncate max-w-[200px] sm:max-w-xs">{breadcrumb.page}</span>
                            </div>
                        </div>

                        {/* Center: Search input */}
                        <form onSubmit={handleSearchSubmit} className="flex-1 max-w-md relative hidden md:block">
                            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                            <input
                                ref={searchInputRef}
                                type="text"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                placeholder="Search topics, interview simulations, flashcards..."
                                className="w-full pl-9 pr-12 py-1.5 bg-slate-900/90 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/30 transition-all font-medium"
                            />
                            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] font-mono text-slate-500 bg-slate-800/60 px-1.5 py-0.5 rounded border border-slate-700/50 pointer-events-none">
                                ⌘K
                            </div>
                        </form>

                        {/* Right: Actions, Notifications, & Profile */}
                        <div className="flex items-center gap-3 shrink-0">
                            {/* Term Badge */}
                            <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800 text-[11px] font-medium text-slate-300">
                                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
                                Fall 2025 • Week 9
                            </div>

                            {/* + Start Diagnostic CTA */}
                            <button
                                onClick={() => navigate('/knowledge-gaps')}
                                className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white text-xs font-bold shadow-md shadow-purple-600/20 transition-all"
                            >
                                <span>+ Start Diagnostic</span>
                            </button>

                            {/* Notifications */}
                            <button
                                onClick={() => navigate('/achievements')}
                                className="relative p-2 text-slate-400 hover:text-slate-200 bg-slate-900/60 border border-slate-800/80 rounded-lg transition-colors"
                                aria-label="Achievements and notifications"
                                title="Achievements & Notifications"
                            >
                                <Bell className="w-4 h-4" />
                                <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-cyan-400 ring-2 ring-[#0B0F19]"></span>
                            </button>

                            {/* User Avatar & Dropdown */}
                            <div className="relative" ref={userMenuRef}>
                                <button
                                    onClick={() => setUserDropdownOpen(!userDropdownOpen)}
                                    className="flex items-center gap-2.5 p-1 rounded-xl hover:bg-slate-800/60 transition-colors focus:outline-none"
                                    aria-label="User account menu"
                                >
                                    <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-cyan-400 to-purple-600 p-[1.5px] shadow-sm">
                                        <div className="w-full h-full rounded-full bg-slate-900 flex items-center justify-center text-xs font-bold text-cyan-300">
                                            {user?.name ? user.name.charAt(0).toUpperCase() : 'M'}
                                        </div>
                                    </div>
                                    <div className="text-left hidden xl:block">
                                        <div className="text-xs font-bold text-white leading-none">
                                            {user?.name || 'Maya Lin'}
                                        </div>
                                        <div className="text-[10px] text-cyan-400 leading-none mt-1">
                                            {user?.email || 'maya.lin@berkeley.edu'}
                                        </div>
                                    </div>
                                </button>

                                {userDropdownOpen && (
                                    <div className="absolute right-0 mt-2 w-56 bg-[#0B0F19] border border-slate-800 rounded-2xl shadow-2xl py-2 z-50 text-xs animate-in fade-in-50 zoom-in-95 duration-100">
                                        <div className="px-3.5 py-2.5 border-b border-slate-800/80">
                                            <div className="font-bold text-white flex items-center gap-1.5">
                                                <span>{user?.name || 'Maya Lin'}</span>
                                                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                                            </div>
                                            <div className="text-[10px] text-slate-400 truncate mt-0.5">
                                                {user?.email || 'maya.lin@berkeley.edu'}
                                            </div>
                                            <div className="text-[9px] text-cyan-400 font-semibold mt-1">
                                                UC Berkeley CS '26 • Honors
                                            </div>
                                        </div>

                                        <div className="py-1">
                                            <button
                                                onClick={() => { navigate('/profile'); setUserDropdownOpen(false); }}
                                                className="w-full text-left px-3.5 py-2 hover:bg-slate-800/60 text-slate-300 hover:text-white flex items-center gap-2.5 transition-colors"
                                            >
                                                <Settings className="w-3.5 h-3.5 text-cyan-400" />
                                                <span>Settings & Profile</span>
                                            </button>
                                            <button
                                                onClick={() => { navigate('/analytics'); setUserDropdownOpen(false); }}
                                                className="w-full text-left px-3.5 py-2 hover:bg-slate-800/60 text-slate-300 hover:text-white flex items-center gap-2.5 transition-colors"
                                            >
                                                <BarChart2 className="w-3.5 h-3.5 text-purple-400" />
                                                <span>Learning Analytics</span>
                                            </button>
                                            <button
                                                onClick={() => { navigate('/achievements'); setUserDropdownOpen(false); }}
                                                className="w-full text-left px-3.5 py-2 hover:bg-slate-800/60 text-slate-300 hover:text-white flex items-center gap-2.5 transition-colors"
                                            >
                                                <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                                                <span>Achievements</span>
                                            </button>
                                        </div>

                                        <div className="border-t border-slate-800/80 my-1"></div>

                                        <button
                                            onClick={handleLogout}
                                            className="w-full text-left px-3.5 py-2 hover:bg-rose-500/10 text-rose-400 flex items-center gap-2.5 transition-colors"
                                        >
                                            <LogOut className="w-3.5 h-3.5" />
                                            <span>Sign Out / Logout</span>
                                        </button>
                                    </div>
                                )}
                            </div>
                        </div>
                    </header>

                    {/* Main Content Body */}
                    <main className="flex-1 overflow-y-auto bg-[#080C14] p-4 md:p-6 lg:p-8">
                        {children}
                    </main>
                </div>
            </div>
        </div>
    );
};

export default StitchLayout;
