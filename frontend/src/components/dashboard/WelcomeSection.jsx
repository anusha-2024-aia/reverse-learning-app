import React from 'react';
import { Flame } from 'lucide-react';

const WelcomeSection = ({ user, streak, insight }) => {
    const currentStreak = streak?.current_streak ?? user?.streak ?? 0;

    return (
        <div className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
                <div className="flex items-center gap-3">
                    <h1 className="text-3xl md:text-4xl font-black text-white">
                        Good morning, {user?.name || 'Student'} 👋
                    </h1>
                    {currentStreak > 0 && (
                        <span className="bg-gradient-to-r from-orange-500/20 to-amber-500/20 border border-orange-500/40 text-orange-300 px-3 py-1 rounded-full text-xs font-black flex items-center gap-1.5 shadow-md">
                            <Flame className="w-4 h-4 text-orange-400 fill-current animate-pulse" />
                            {currentStreak} Day Streak
                        </span>
                    )}
                </div>
                <p className="text-slate-400 text-base md:text-lg mt-1">
                    {insight || "Ready to improve your learning today?"}
                </p>
            </div>
        </div>
    );
};

export default WelcomeSection;
