import React, { useState, useEffect } from 'react';
import { Star, Flame, Rocket, Award, ShieldCheck, Moon, Sun, Crown, CheckCircle, Zap, Map as MapIcon, Book, Target, PenTool, Lock } from 'lucide-react';
import api from '../api/axios';

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
    const [data, setData] = useState({ total_points: 0, achievements: [], streak: { current_streak: 0, longest_streak: 0 } });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.get('/achievements/mine')
            .then(res => {
                setData(res.data);
                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to load achievements", err);
                setLoading(false);
            });
    }, []);

    if (loading) {
        return (
            <div className="p-8 text-center text-slate-400 mt-20 flex flex-col items-center gap-3">
                <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                <p>Loading your learning achievements...</p>
            </div>
        );
    }

    const currentStreak = data.streak?.current_streak || 0;
    const longestStreak = data.streak?.longest_streak || 0;
    const unlockedCount = data.unlocked_count || data.achievements.filter(a => a.unlocked).length;
    const totalCount = data.total_count || data.achievements.length;

    return (
        <div className="p-6 md:p-12 max-w-7xl mx-auto w-full pb-20 space-y-8">
            <div>
                <h1 className="text-3xl md:text-4xl font-black text-white tracking-tight flex items-center gap-3 mb-2">
                    <Award className="w-9 h-9 text-amber-400" />
                    Learning Gamification & Badges
                </h1>
                <p className="text-slate-400 text-sm md:text-base">
                    Track your genuine activity, maintain your study streak, and earn verified achievement badges.
                </p>
            </div>

            {/* Top Cards: Total Points & Streak */}
            <div className="grid md:grid-cols-2 gap-6">
                
                {/* Streak Card */}
                <div className="bg-gradient-to-br from-slate-900 via-orange-950/30 to-slate-900 p-8 rounded-3xl border border-orange-500/30 shadow-2xl flex items-center justify-between relative overflow-hidden">
                    <div className="space-y-2 relative z-10">
                        <span className="text-orange-400 font-bold uppercase tracking-wider text-xs block">
                            Daily Streak
                        </span>
                        <div className="text-5xl md:text-6xl font-black text-white flex items-center gap-3">
                            <span>🔥 {currentStreak}</span>
                            <span className="text-lg text-slate-400 font-semibold uppercase tracking-wider">Day Streak</span>
                        </div>
                        <p className="text-xs text-orange-300 font-medium pt-1">
                            Longest: <strong>{longestStreak} Days</strong>
                        </p>
                    </div>
                    <Flame className="w-24 h-24 text-orange-500/20 absolute -right-2 -bottom-2 pointer-events-none" />
                </div>

                {/* Total Points Card */}
                <div className="bg-gradient-to-br from-slate-900 via-indigo-950/30 to-slate-900 p-8 rounded-3xl border border-indigo-500/30 shadow-2xl flex items-center justify-between relative overflow-hidden">
                    <div className="space-y-2 relative z-10">
                        <span className="text-indigo-400 font-bold uppercase tracking-wider text-xs block">
                            Total Points
                        </span>
                        <div className="text-5xl md:text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-amber-300 via-yellow-400 to-amber-500">
                            {data.total_points} <span className="text-lg text-slate-400 font-normal">pts</span>
                        </div>
                        <p className="text-xs text-indigo-300 font-medium pt-1">
                            Badges Unlocked: <strong>{unlockedCount} / {totalCount}</strong>
                        </p>
                    </div>
                    <Star className="w-24 h-24 text-amber-500/15 absolute -right-2 -bottom-2 pointer-events-none" />
                </div>

            </div>

            {/* Badges Section Header */}
            <div className="flex justify-between items-end border-b border-slate-800 pb-4">
                <div>
                    <h2 className="text-2xl font-black text-white">Achievement Badges</h2>
                    <p className="text-xs text-slate-400 mt-1">Unlocked based on real backend activity checks</p>
                </div>
                <span className="text-xs font-bold bg-slate-800 text-indigo-300 px-3 py-1.5 rounded-full border border-slate-700">
                    {unlockedCount} / {totalCount} Unlocked
                </span>
            </div>

            {/* Badges Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                {data.achievements.map(ach => {
                    const Icon = ICONS[ach.icon_name] || Star;
                    const isUnlocked = ach.unlocked;

                    return (
                        <div 
                            key={ach.id} 
                            className={`relative p-6 rounded-3xl border transition-all duration-300 flex flex-col justify-between text-center group ${
                                isUnlocked 
                                    ? 'bg-slate-800/90 border-indigo-500/40 hover:border-indigo-400 shadow-xl hover:-translate-y-1' 
                                    : 'bg-slate-900/60 border-slate-800/80 opacity-70'
                            }`}
                        >
                            {/* Icon & Details */}
                            <div>
                                <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4 relative ${
                                    isUnlocked 
                                        ? 'bg-gradient-to-br from-indigo-500/20 to-blue-500/20 text-indigo-400 border border-indigo-500/30 shadow-md' 
                                        : 'bg-slate-800/80 text-slate-600 border border-slate-700/60'
                                }`}>
                                    <Icon className="w-8 h-8" />
                                    {!isUnlocked && (
                                        <Lock className="w-4 h-4 text-slate-500 absolute top-1 right-1" />
                                    )}
                                </div>

                                <h3 className={`font-bold text-base mb-1 ${isUnlocked ? 'text-white' : 'text-slate-400'}`}>
                                    {ach.name}
                                </h3>

                                <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed mb-3">
                                    {ach.description}
                                </p>
                            </div>

                            {/* Unlocked / Progress Footer */}
                            <div className="mt-4 pt-3 border-t border-slate-800/80">
                                {isUnlocked ? (
                                    <div className="flex justify-between items-center text-xs">
                                        <span className="text-amber-400 font-black">+{ach.points} pts</span>
                                        <span className="text-emerald-400 font-semibold text-[11px] flex items-center gap-1">
                                            Unlocked {ach.unlocked_at ? new Date(ach.unlocked_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) : ''}
                                        </span>
                                    </div>
                                ) : (
                                    <div className="space-y-1.5">
                                        <div className="flex justify-between text-[11px] font-semibold text-slate-400">
                                            <span>Progress</span>
                                            <span className="font-mono">{ach.current_value} / {ach.target_value}</span>
                                        </div>
                                        <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden border border-slate-800 p-0.5">
                                            <div 
                                                className="bg-indigo-500 h-full rounded-full transition-all duration-300"
                                                style={{ width: `${Math.max(5, ach.progress_percentage || 0)}%` }}
                                            ></div>
                                        </div>
                                        <span className="text-[10px] text-slate-500 font-bold block pt-0.5">+{ach.points} pts to unlock</span>
                                    </div>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default AchievementsPage;
