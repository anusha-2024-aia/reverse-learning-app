import React, { useState, useEffect, useContext } from 'react';
import { Award, X } from 'lucide-react';
import api from '../api/axios';
import { AuthContext } from '../context/AuthContext';

const AchievementNotification = () => {
    const { isLoggedIn } = useContext(AuthContext);
    const [achievements, setAchievements] = useState([]);

    useEffect(() => {
        if (!isLoggedIn) return;

        const checkUnlocks = () => {
            const token = sessionStorage.getItem('token') || localStorage.getItem('token');
            if (!token) return;

            api.get('/achievements/recent-unlocks')
                .then(res => {
                    const data = res.data;
                    if (data && data.length > 0) {
                        setAchievements(prev => [...prev, ...data]);
                    }
                })
                .catch(err => {
                    if (err.response?.status !== 401) {
                        console.error("Error fetching recent achievement unlocks:", err);
                    }
                });
        };

        checkUnlocks();
        const interval = setInterval(checkUnlocks, 15000);
        return () => clearInterval(interval);
    }, [isLoggedIn]);

    const dismiss = (id) => {
        setAchievements(prev => prev.filter(a => a.id !== id));
    };

    if (!isLoggedIn || achievements.length === 0) return null;

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
