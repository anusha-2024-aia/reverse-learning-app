import React, { useState, useEffect } from 'react';
import { Search, Filter, BookOpen } from 'lucide-react';

const StudyHistory = () => {
    const [curricula, setCurricula] = useState([]);
    const [selectedCurriculum, setSelectedCurriculum] = useState('all');
    const [searchTopic, setSearchTopic] = useState('');
    const [history, setHistory] = useState([]); // Would be fetched from API

    useEffect(() => {
        fetch('http://localhost:8000/api/curricula')
            .then(res => res.json())
            .then(data => setCurricula(data.curricula || []))
            .catch(err => console.error(err));
        
        // Mock history data since endpoint isn't fully required by prompt for this step, but assuming it exists
        setHistory([
            { id: 1, topic_name: 'Variables & Data Types', curriculum_name: 'Python Fundamentals', score: 8, learning_mode: 'technical', date: new Date().toISOString() },
            { id: 2, topic_name: 'Lists & Tuples', curriculum_name: 'Python Fundamentals', score: 7, learning_mode: 'general', date: new Date().toISOString() }
        ]);
    }, []);

    const filteredHistory = history.filter(h => {
        if (selectedCurriculum !== 'all' && h.curriculum_name !== selectedCurriculum) return false;
        if (searchTopic && !h.topic_name.toLowerCase().includes(searchTopic.toLowerCase())) return false;
        return true;
    });

    return (
        <div className="p-8 max-w-7xl mx-auto w-full">
            <h1 className="text-4xl font-bold mb-8">Study History</h1>
            
            <div className="flex flex-col md:flex-row gap-4 mb-8">
                <div className="flex-1 relative">
                    <Search className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                    <input 
                        type="text" 
                        placeholder="Search by topic name..." 
                        value={searchTopic}
                        onChange={(e) => setSearchTopic(e.target.value)}
                        className="w-full bg-slate-800 border border-slate-700 rounded-lg py-3 pl-10 pr-4 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
                    />
                </div>
                
                <div className="w-full md:w-64 relative">
                    <Filter className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                    <select 
                        value={selectedCurriculum}
                        onChange={(e) => setSelectedCurriculum(e.target.value)}
                        className="w-full bg-slate-800 border border-slate-700 rounded-lg py-3 pl-10 pr-4 text-white focus:outline-none focus:border-indigo-500 transition-colors appearance-none"
                    >
                        <option value="all">All Curricula</option>
                        {curricula.map(c => (
                            <option key={c.id} value={c.name}>{c.name}</option>
                        ))}
                    </select>
                </div>
            </div>
            
            <div className="bg-slate-800 rounded-2xl border border-slate-700 overflow-hidden shadow-lg">
                <table className="w-full text-left">
                    <thead className="bg-slate-800/80 border-b border-slate-700">
                        <tr>
                            <th className="px-6 py-4 font-semibold text-slate-300">Topic</th>
                            <th className="px-6 py-4 font-semibold text-slate-300">Curriculum</th>
                            <th className="px-6 py-4 font-semibold text-slate-300">Mode</th>
                            <th className="px-6 py-4 font-semibold text-slate-300">Score</th>
                            <th className="px-6 py-4 font-semibold text-slate-300 text-right">Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredHistory.length > 0 ? filteredHistory.map(h => (
                            <tr key={h.id} className="border-b border-slate-700/50 hover:bg-slate-700/30 transition-colors">
                                <td className="px-6 py-4 font-medium text-white">{h.topic_name}</td>
                                <td className="px-6 py-4 text-slate-400">{h.curriculum_name}</td>
                                <td className="px-6 py-4">
                                    <span className="px-2 py-1 bg-slate-700 rounded text-xs font-medium text-slate-300 uppercase">
                                        {h.learning_mode}
                                    </span>
                                </td>
                                <td className="px-6 py-4 font-bold text-indigo-400">{h.score}/10</td>
                                <td className="px-6 py-4 text-right">
                                    <button className="text-indigo-400 hover:text-indigo-300 text-sm font-medium transition-colors">
                                        View All Feedback
                                    </button>
                                </td>
                            </tr>
                        )) : (
                            <tr>
                                <td colSpan="5" className="px-6 py-12 text-center text-slate-500">
                                    No evaluation history found.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default StudyHistory;
