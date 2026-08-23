import React from 'react';
import { TrendingUp } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const ProgressChart = ({ progress }) => {
    return (
        <div className="bg-slate-800/80 p-6 rounded-2xl border border-slate-700 h-full flex flex-col">
            <h3 className="text-xl font-bold flex items-center gap-2 mb-6">
                <TrendingUp className="w-5 h-5 text-green-400" />
                📈 Learning Progress
            </h3>
            <div className="flex-1 w-full min-h-[250px]">
                {progress && progress.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={progress}>
                            <XAxis dataKey="date" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                            <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} domain={[0, 100]} />
                            <Tooltip 
                                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#f8fafc' }}
                            />
                            <Line type="monotone" dataKey="average_score" stroke="#4ade80" strokeWidth={3} dot={{ fill: '#4ade80', strokeWidth: 2 }} activeDot={{ r: 8 }} />
                        </LineChart>
                    </ResponsiveContainer>
                ) : (
                    <div className="h-full w-full flex items-center justify-center border-2 border-dashed border-slate-700 rounded-xl">
                        <span className="text-slate-500">Complete more evaluations to see your progress trend.</span>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ProgressChart;
