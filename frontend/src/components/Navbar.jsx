import React from 'react';
import { NavLink } from 'react-router-dom';
import { BookOpen, Home, Layers, History, BarChart2, Award, Mic, LogOut, Map, RotateCcw, FileText, MessageSquare } from 'lucide-react';
import { AuthContext } from '../context/AuthContext';

const Navbar = () => {
    const { isLoggedIn, logout } = React.useContext(AuthContext);
    
    if (!isLoggedIn) return null;

    return (
        <header className="sticky top-0 z-50 bg-slate-900/80 backdrop-blur-md border-b border-white/10 p-4">
            <div className="max-w-7xl mx-auto flex items-center justify-between">
                <div className="flex items-center gap-2 text-indigo-400 font-bold text-xl tracking-tight">
                    <BookOpen className="w-6 h-6" />
                    Reverse Learning
                </div>
                <nav className="flex items-center gap-6">
                    <NavLink to="/" className={({ isActive }) => `flex items-center gap-2 text-sm font-medium transition-colors ${isActive ? 'text-indigo-400' : 'text-slate-400 hover:text-slate-200'}`}>
                        <Home className="w-4 h-4" /> Dashboard
                    </NavLink>
                    <NavLink to="/resume" className={({ isActive }) => `flex items-center gap-2 text-sm font-medium transition-colors ${isActive ? 'text-indigo-400' : 'text-slate-400 hover:text-slate-200'}`}>
                        <FileText className="w-4 h-4" /> Resume
                    </NavLink>
                    <NavLink to="/revision" className={({ isActive }) => `flex items-center gap-2 text-sm font-medium transition-colors ${isActive ? 'text-indigo-400' : 'text-slate-400 hover:text-slate-200'}`}>
                        <RotateCcw className="w-4 h-4" /> Revision
                    </NavLink>

                    <NavLink to="/learning-roadmap" className={({ isActive }) => `flex items-center gap-2 text-sm font-medium transition-colors ${isActive ? 'text-indigo-400' : 'text-slate-400 hover:text-slate-200'}`}>
                        <Map className="w-4 h-4" /> Roadmap
                    </NavLink>

                    <NavLink to="/study" className={({ isActive }) => `flex items-center gap-2 text-sm font-medium transition-colors ${isActive ? 'text-indigo-400' : 'text-slate-400 hover:text-slate-200'}`}>
                        <Layers className="w-4 h-4" /> Study Room
                    </NavLink>
                    <NavLink to="/interview" className={({ isActive }) => `flex items-center gap-2 text-sm font-medium transition-colors ${isActive ? 'text-indigo-400' : 'text-slate-400 hover:text-slate-200'}`}>
                        <Mic className="w-4 h-4" /> Interview
                    </NavLink>
                    <NavLink to="/communication-coach" className={({ isActive }) => `flex items-center gap-2 text-sm font-medium transition-colors ${isActive ? 'text-indigo-400' : 'text-slate-400 hover:text-slate-200'}`}>
                        <MessageSquare className="w-4 h-4" /> Coach
                    </NavLink>
                    <NavLink to="/syllabi" className={({ isActive }) => `flex items-center gap-2 text-sm font-medium transition-colors ${isActive ? 'text-indigo-400' : 'text-slate-400 hover:text-slate-200'}`}>
                        <BookOpen className="w-4 h-4" /> Syllabi
                    </NavLink>
                    <NavLink to="/insights" className={({ isActive }) => `flex items-center gap-2 text-sm font-medium transition-colors ${isActive ? 'text-indigo-400' : 'text-slate-400 hover:text-slate-200'}`}>
                        <BarChart2 className="w-4 h-4" /> Insights
                    </NavLink>
                    <NavLink to="/achievements" className={({ isActive }) => `flex items-center gap-2 text-sm font-medium transition-colors ${isActive ? 'text-indigo-400' : 'text-slate-400 hover:text-slate-200'}`}>
                        <Award className="w-4 h-4" /> Achievements
                    </NavLink>
                    <NavLink to="/history" className={({ isActive }) => `flex items-center gap-2 text-sm font-medium transition-colors ${isActive ? 'text-indigo-400' : 'text-slate-400 hover:text-slate-200'}`}>
                        <History className="w-4 h-4" /> History
                    </NavLink>
                    <NavLink to="/evaluations" className={({ isActive }) => `flex items-center gap-2 text-sm font-medium transition-colors ${isActive ? 'text-indigo-400' : 'text-slate-400 hover:text-slate-200'}`}>
                        <Award className="w-4 h-4" /> Evaluations
                    </NavLink>
                    <button 
                        onClick={logout}
                        className="ml-4 flex items-center gap-2 text-sm font-medium text-red-400 hover:text-red-300 transition-colors"
                    >
                        <LogOut className="w-4 h-4" /> Logout
                    </button>
                </nav>
            </div>
        </header>
    );
};

export default Navbar;
