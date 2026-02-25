import React from 'react';
import { Lock, CheckCircle, Target, ArrowRight } from 'lucide-react';

const SyllabusTracker = ({ currentTopic, onSelectTopic }) => {
    // Mock syllabus data - Reset to starting state
    const topics = [
        { id: 1, name: 'Core Foundations', status: 'active' },
        { id: 2, name: 'Data Structures', status: 'pending' },
        { id: 3, name: 'Algorithms & Logic', status: 'pending' },
        { id: 4, name: 'System Architecture', status: 'locked' },
        { id: 5, name: 'Cloud Deployment', status: 'locked' },
    ];

    return (
        <div className="w-full relative overflow-hidden bg-slate-50/50 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] rounded-3xl p-8 border border-slate-200/60 shadow-inner mb-12 group transition-all duration-700">
            {/* Custom Animation Style */}
            <style dangerouslySetInnerHTML={{
                __html: `
                @keyframes pulse-slow {
                    0%, 100% { transform: scale(1.1); filter: brightness(1); }
                    50% { transform: scale(1.15); filter: brightness(1.2); }
                }
                .animate-pulse-slow {
                    animation: pulse-slow 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
                }
                @keyframes shimmer {
                    0% { transform: translateX(-100%); }
                    100% { transform: translateX(100%); }
                }
            ` }} />

            <div className="flex items-center justify-between mb-10 relative z-10">
                <div className="flex items-center gap-4">
                    <div className="p-3 bg-white rounded-2xl border border-slate-200 shadow-sm text-blue-600 transition-transform group-hover:rotate-12 duration-500">
                        <Target className="w-6 h-6" />
                    </div>
                    <div>
                        <h3 className="text-base font-black text-slate-900 uppercase tracking-widest leading-none mb-1">Skill Islands</h3>
                        <p className="text-[10px] font-black text-slate-400 uppercase tracking-tighter">Your Isometric Learning Journey</p>
                    </div>
                </div>
                <div className="px-4 py-1.5 bg-blue-600/5 border border-blue-200 rounded-full flex items-center gap-2">
                    <div className="w-1.5 h-1.5 bg-blue-600 rounded-full animate-pulse"></div>
                    <span className="text-[10px] font-black text-blue-700 uppercase tracking-widest">Phase 2 Explorations</span>
                </div>
            </div>

            <div className="relative flex items-center justify-between gap-4 overflow-x-auto pb-6 pt-4 no-scrollbar">
                {topics.map((topic, index) => (
                    <React.Fragment key={topic.id}>
                        {/* Skill Island Node */}
                        <div className="flex flex-col items-center gap-5 min-w-[140px] relative">
                            <button
                                onClick={() => topic.status !== 'locked' && onSelectTopic(topic.name)}
                                disabled={topic.status === 'locked'}
                                className={`group relative w-20 h-20 rounded-2xl flex items-center justify-center transition-all duration-500
                                    ${topic.status === 'active'
                                        ? 'bg-blue-600 text-white border-4 border-blue-200/50 shadow-[0_15px_30px_-5px_rgba(37,99,235,0.5)] scale-110 animate-pulse-slow z-20'
                                        : topic.status === 'completed'
                                            ? 'bg-emerald-50 border-2 border-emerald-400 text-emerald-700 shadow-[0_10px_20px_-5px_rgba(16,185,129,0.3)] transform hover:-translate-y-2'
                                            : topic.status === 'pending'
                                                ? 'bg-white text-slate-700 border-2 border-slate-200 hover:border-blue-400 transition-all shadow-sm hover:-translate-y-1'
                                                : 'bg-slate-100 border-2 border-slate-200 text-slate-400 shadow-inner opacity-60 grayscale cursor-not-allowed'}`}
                            >
                                {/* Platform 3D Effect for non-active */}
                                {topic.status !== 'active' && (
                                    <div className={`absolute -bottom-1 left-1.5 right-1.5 h-full rounded-2xl -z-10 transition-colors
                                        ${topic.status === 'completed' ? 'bg-emerald-200' : 'bg-slate-200'}`}></div>
                                )}

                                {topic.status === 'active' ? (
                                    <div className="flex flex-col items-center">
                                        <div className="font-black text-2xl leading-none italic">0{topic.id}</div>
                                        <div className="text-[8px] font-black uppercase mt-1 tracking-widest opacity-80">Active</div>
                                    </div>
                                ) : topic.status === 'completed' ? (
                                    <CheckCircle className="w-8 h-8 drop-shadow-sm" />
                                ) : topic.status === 'pending' ? (
                                    <div className="font-black text-xl text-slate-400 group-hover:text-blue-500 transition-colors">0{topic.id}</div>
                                ) : (
                                    <Lock className="w-6 h-6 opacity-40" />
                                )}

                                {topic.status === 'active' && (
                                    <div className="absolute -top-2 -right-2 flex">
                                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                                        <div className="relative w-4 h-4 bg-blue-500 rounded-full border-2 border-white"></div>
                                    </div>
                                )}
                            </button>

                            <div className="text-center px-2">
                                <span className={`text-[11px] font-black uppercase tracking-tighter leading-tight block mb-0.5
                                    ${topic.status === 'active' ? 'text-blue-600' :
                                        topic.status === 'completed' ? 'text-emerald-700' :
                                            topic.status === 'pending' ? 'text-slate-600 group-hover:text-blue-500' : 'text-slate-400'}`}
                                >
                                    {topic.name}
                                </span>
                                <span className={`text-[8px] font-black uppercase tracking-widest
                                    ${topic.status === 'active' ? 'text-blue-500' :
                                        topic.status === 'completed' ? 'text-emerald-500' :
                                            topic.status === 'pending' ? 'text-slate-400' : 'text-slate-300'}`}
                                >
                                    {topic.status === 'active' ? 'Active' :
                                        topic.status === 'completed' ? 'Mastered' :
                                            topic.status === 'pending' ? 'Pending' : 'Locked'}
                                </span>
                            </div>
                        </div>

                        {/* Energy Beam Connector */}
                        {index < topics.length - 1 && (
                            <div className="flex-1 min-w-[40px] h-1.5 relative -mt-10">
                                <div className={`absolute inset-0 rounded-full h-full w-full transition-all duration-1000
                                    ${topic.status === 'completed' || (topic.status === 'active' && topics[index + 1].status === 'pending')
                                        ? 'bg-gradient-to-r from-blue-400 to-slate-200'
                                        : 'bg-slate-200 opacity-30 shadow-inner'}`}
                                ></div>
                            </div>
                        )}
                    </React.Fragment>
                ))}
            </div>
        </div>
    );
};

export default SyllabusTracker;
