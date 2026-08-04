import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';

const ProgressChart = ({ data, title, dataKey, yAxisLabel, isArea = false, color = "#6366f1" }) => {
    return (
        <div className="bg-slate-800 p-6 rounded-2xl border border-slate-700 shadow-lg w-full h-80 flex flex-col">
            <h3 className="text-lg font-bold text-slate-200 mb-6">{title}</h3>
            <div className="flex-1 w-full h-full min-h-0">
                <ResponsiveContainer width="100%" height="100%">
                    {isArea ? (
                        <AreaChart data={data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                            <defs>
                                <linearGradient id={`color${dataKey}`} x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor={color} stopOpacity={0.8}/>
                                    <stop offset="95%" stopColor={color} stopOpacity={0}/>
                                </linearGradient>
                            </defs>
                            <XAxis dataKey="date" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                            <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} domain={['auto', 'auto']} />
                            <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                            <Tooltip 
                                contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f8fafc' }}
                                itemStyle={{ color: color }}
                                cursor={{ stroke: '#475569', strokeWidth: 1, strokeDasharray: '5 5' }}
                            />
                            <Area type="monotone" dataKey={dataKey} name={yAxisLabel} stroke={color} strokeWidth={3} fillOpacity={1} fill={`url(#color${dataKey})`} />
                        </AreaChart>
                    ) : (
                        <LineChart data={data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                            <XAxis dataKey="date" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                            <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} domain={['auto', 'auto']} />
                            <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                            <Tooltip 
                                contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f8fafc' }}
                                itemStyle={{ color: color }}
                                cursor={{ stroke: '#475569', strokeWidth: 1, strokeDasharray: '5 5' }}
                            />
                            <Line type="monotone" dataKey={dataKey} name={yAxisLabel} stroke={color} strokeWidth={3} dot={{ fill: color, strokeWidth: 2, r: 4 }} activeDot={{ r: 6 }} />
                        </LineChart>
                    )}
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default ProgressChart;
