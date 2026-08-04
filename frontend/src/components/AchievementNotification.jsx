import React, { useState, useEffect } from 'react';
import { Award, X } from 'lucide-react';

const AchievementNotification = () => {
    const [achievements, setAchievements] = useState([]);

    useEffect(() => {
        // Poll for new achievements every 10 seconds
        const interval = setInterval(() => {
            fetch('http://localhost:8000/api/achievements/recent-unlocks')
                .then(res => res.json())
                .then(data => {
                    if (data && data.length > 0) {
                        setAchievements(prev => [...prev, ...data]);
                    }
                })
                .catch(err => console.error(err));
        }, 10000);

        return () => clearInterval(interval);
    }, []);

    const dismiss = (id) => {
        setAchievements(prev => prev.filter(a => a.id !== id));
    };

    if (achievements.length === 0) return null;

    return (
        <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-3">
            {achievements.map((ach, index) => (
                <div 
                    key={`${ach.id}-${index}`} 
                    className="bg-indigo-600 text-white p-4 rounded-xl shadow-2xl flex items-center gap-4 w-80 animate-in slide-in-from-right fade-in"
                >
                    <div className="bg-white/20 p-2 rounded-full">
                        <Award className="w-6 h-6 text-yellow-300" />
                    </div>
                    <div className="flex-1">
                        <p className="text-indigo-200 text-xs font-bold uppercase tracking-wider mb-0.5">Achievement Unlocked!</p>
                        <h4 className="font-bold text-sm">{ach.name}</h4>
                        <p className="text-indigo-200 text-xs mt-1">+{ach.points} Points</p>
                    </div>
                    <button onClick={() => dismiss(ach.id)} className="text-indigo-300 hover:text-white transition-colors">
                        <X className="w-4 h-4" />
                    </button>
                </div>
            ))}
        </div>
    );
};

export default AchievementNotification;
