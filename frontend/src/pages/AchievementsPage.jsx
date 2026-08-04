import React, { useState, useEffect } from 'react';
import { Star, Flame, Rocket, Award, ShieldCheck, Moon, Sun, Crown, CheckCircle, Zap, Map as MapIcon, Book, Target, PenTool } from 'lucide-react';

const ICONS = {
    'star': Star,
    'flame': Flame,
    'rocket': Rocket,
    'award': Award,
    'shield-check': ShieldCheck,
    'moon': Moon,
    'sun': Sun,
    'crown': Crown,
    'check-circle': CheckCircle,
    'zap': Zap,
    'map': MapIcon,
    'book': Book,
    'target': Target,
    'pen-tool': PenTool
};

const AchievementsPage = () => {
    const [data, setData] = useState({ total_points: 0, achievements: [] });
    const [streakData, setStreakData] = useState({ current_streak: 0, longest_streak: 0 });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        Promise.all([
            fetch('http://localhost:8000/api/achievements/mine').then(res => res.json()),
            fetch('http://localhost:8000/api/achievements/streak').then(res => res.json())
        ])
        .then(([achievementsRes, streakRes]) => {
            setData(achievementsRes);
            setStreakData(streakRes);
            setLoading(false);
        })
        .catch(err => {
            console.error("Failed to load achievements", err);
            setLoading(false);
        });
    }, []);

    if (loading) {
        return <div className="p-8 text-center text-slate-400 mt-20">Loading achievements...</div>;
    }

    return (
        <div className="p-8 max-w-7xl mx-auto w-full pb-20">
            <h1 className="text-4xl font-black mb-2 flex items-center gap-3">
                <Award className="w-8 h-8 text-yellow-400" />
                Your Achievements
            </h1>
            <p className="text-slate-400 mb-10 text-lg">Unlock badges and earn points as you master new skills.</p>

            <div className="grid md:grid-cols-2 gap-6 mb-12">
                <div className="bg-gradient-to-br from-slate-800 to-slate-900 p-8 rounded-2xl border border-slate-700 shadow-xl flex items-center justify-between">
                    <div>
                        <h3 className="text-slate-400 font-bold uppercase tracking-wider text-sm mb-1">Total Points</h3>
                        <div className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-amber-600">
                            {data.total_points}
                        </div>
                    </div>
                    <Star className="w-16 h-16 text-yellow-500/20" />
                </div>
                
                <div className="bg-gradient-to-br from-slate-800 to-slate-900 p-8 rounded-2xl border border-slate-700 shadow-xl flex items-center justify-between">
                    <div>
                        <h3 className="text-slate-400 font-bold uppercase tracking-wider text-sm mb-1">Current Streak</h3>
                        <div className="text-5xl font-black text-white flex items-end gap-3">
                            {streakData.current_streak} <span className="text-lg text-slate-500 mb-1">days</span>
                        </div>
                        <p className="text-sm text-slate-500 mt-2 font-medium">Personal Best: {streakData.longest_streak} days</p>
                    </div>
                    <Flame className="w-16 h-16 text-orange-500/20" />
                </div>
            </div>

            <div className="mb-6 flex justify-between items-end">
                <h2 className="text-2xl font-bold text-white">Badges</h2>
                <span className="text-slate-400 text-sm">
                    {data.achievements.filter(a => a.unlocked).length} / {data.achievements.length} Unlocked
                </span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                {data.achievements.map(ach => {
                    const Icon = ICONS[ach.icon_name] || Star;
                    const isUnlocked = ach.unlocked;

                    return (
                        <div 
                            key={ach.id} 
                            className={`relative p-6 rounded-2xl border transition-all duration-300 flex flex-col items-center text-center group ${
                                isUnlocked 
                                    ? 'bg-slate-800 border-indigo-500/30 hover:border-indigo-400 shadow-lg hover:-translate-y-1 cursor-pointer' 
                                    : 'bg-slate-900/50 border-slate-800 opacity-60 grayscale'
                            }`}
                        >
                            <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-4 ${
                                isUnlocked ? 'bg-gradient-to-br from-indigo-500/20 to-blue-500/20' : 'bg-slate-800'
                            }`}>
                                <Icon className={`w-8 h-8 ${isUnlocked ? 'text-indigo-400' : 'text-slate-600'}`} />
                            </div>
                            <h3 className={`font-bold mb-1 ${isUnlocked ? 'text-white' : 'text-slate-500'}`}>
                                {ach.name}
                            </h3>
                            <p className="text-xs text-slate-500 line-clamp-2">
                                {ach.description}
                            </p>
                            
                            {isUnlocked && (
                                <div className="mt-4 pt-4 border-t border-slate-700/50 w-full flex justify-between items-center text-xs">
                                    <span className="text-yellow-500 font-bold">+{ach.points} pts</span>
                                    <span className="text-slate-500">{new Date(ach.unlocked_at).toLocaleDateString()}</span>
                                </div>
                            )}
                            
                            {!isUnlocked && (
                                <div className="mt-4 pt-4 border-t border-slate-800 w-full text-xs font-bold text-slate-600">
                                    {ach.points} pts to unlock
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default AchievementsPage;
