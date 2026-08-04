import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

const StatsCard = ({ title, value, subtitle, trend }) => {
    return (
        <div className="bg-slate-800 p-6 rounded-2xl border border-slate-700 flex flex-col justify-between h-full shadow-lg">
            <div>
                <h3 className="text-slate-400 font-medium mb-1 text-sm uppercase tracking-wider">{title}</h3>
                <div className="flex items-end gap-3 mb-2">
                    <span className="text-4xl font-black text-white leading-none">{value}</span>
                    {trend && (
                        <div className={`flex items-center text-sm font-bold pb-1 ${
                            trend === 'improving' ? 'text-green-400' :
                            trend === 'declining' ? 'text-red-400' :
                            'text-slate-400'
                        }`}>
                            {trend === 'improving' && <TrendingUp className="w-4 h-4 mr-1" />}
                            {trend === 'declining' && <TrendingDown className="w-4 h-4 mr-1" />}
                            {trend === 'stable' && <Minus className="w-4 h-4 mr-1" />}
                            {trend === 'improving' ? 'Up' : trend === 'declining' ? 'Down' : 'Stable'}
                        </div>
                    )}
                </div>
            </div>
            {subtitle && <p className="text-slate-500 text-sm">{subtitle}</p>}
        </div>
    );
};

export default StatsCard;
