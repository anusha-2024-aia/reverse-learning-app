import React, { useState } from 'react';
import { BookOpen, Send, Loader2, BrainCircuit, Layers, Target, Code, MessageCircle, Sparkles, Trophy, ArrowRight, Map as MapIcon, RotateCcw } from 'lucide-react';
import { evaluateExplanationStream } from '../services/api';
import FeedbackCard from '../components/FeedbackCard';
import SyllabusTracker from '../components/SyllabusTracker';

const StudyRoom = () => {
    const [currentStep, setCurrentStep] = useState(1);
    const [topic, setTopic] = useState('Core Foundations');
    const [explanation, setExplanation] = useState('');
    const [learningMode, setLearningMode] = useState('technical');
    const [isLoading, setIsLoading] = useState(false);
    const [evaluation, setEvaluation] = useState(null);
    const [thinkingText, setThinkingText] = useState('');
    const [error, setError] = useState(null);

    const modes = [
        { id: 'general', label: 'General Knowledge', icon: Target, description: 'Core concepts & analogies' },
        { id: 'technical', label: 'Technical & DSA', icon: Code, description: 'Complexity & logic' },
        { id: 'fluency', label: 'English Fluency', icon: MessageCircle, description: 'Tone & vocabulary' }
    ];

    const handleSubmit = async (e) => {
        if (e) e.preventDefault();
        if (!topic || !explanation) return;

        setIsLoading(true);
        setError(null);
        setEvaluation(null);
        setThinkingText('');
        setCurrentStep(4); // Move to results step

        try {
            const rawOutput = await evaluateExplanationStream(topic, explanation, learningMode, (fullText) => {
                if (fullText.includes('<thinking>')) {
                    const startTag = '<thinking>';
                    const endTag = '</thinking>';
                    const startIndex = fullText.indexOf(startTag) + startTag.length;
                    const endIndex = fullText.indexOf(endTag);

                    let thinking;
                    if (endIndex !== -1) {
                        thinking = fullText.substring(startIndex, endIndex).trim();
                    } else {
                        thinking = fullText.substring(startIndex).trim();
                    }
                    setThinkingText(thinking);
                }
            });

            if (rawOutput.includes('<json>')) {
                const jsonStr = rawOutput.split('<json>')[1].split('</json>')[0].trim();
                try {
                    const result = JSON.parse(jsonStr);
                    setEvaluation(result);
                } catch (_err) {
                    console.error("JSON parse error:", _err);
                    setError('Failed to parse the evaluation data. Please try again.');
                }
            } else {
                const firstBrace = rawOutput.indexOf('{');
                const lastBrace = rawOutput.lastIndexOf('}');
                if (firstBrace !== -1 && lastBrace !== -1 && lastBrace > firstBrace) {
                    try {
                        const jsonStr = rawOutput.substring(firstBrace, lastBrace + 1);
                        setEvaluation(JSON.parse(jsonStr));
                    } catch (_e) {
                        setError('Failed to extract valid feedback from the AI.');
                    }
                } else {
                    setError('The AI did not return a valid evaluation format.');
                }
            }
        } catch (err) {
            setError('Failed to get evaluation. Please ensure the backend is running.');
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    const handleTopicSelect = (selectedTopicName) => {
        setTopic(selectedTopicName);
        setCurrentStep(3);
    };

    const handleRetry = () => {
        setEvaluation(null);
        setThinkingText('');
        setCurrentStep(3);
    };

    const handleClaimMastery = () => {
        setCurrentStep(5);
    };

    const handleReturnToMap = () => {
        setEvaluation(null);
        setExplanation('');
        setCurrentStep(2);
    };

    // --- Screen Components ---

    const ScreenWrapper = ({ children, title, subtitle }) => (
        <div className="max-w-5xl mx-auto bg-white text-slate-900 rounded-3xl shadow-2xl p-8 md:p-12 animate-in fade-in slide-in-from-bottom-8 duration-700 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-50 rounded-full -mr-32 -mt-32 blur-3xl opacity-50"></div>
            {title && (
                <div className="text-center mb-10 relative z-10">
                    <h1 className="text-4xl font-black text-slate-900 mb-2 tracking-tighter uppercase">
                        {title}
                    </h1>
                    {subtitle && <p className="text-slate-500 font-medium">{subtitle}</p>}
                </div>
            )}
            <div className="relative z-10">
                {children}
            </div>
        </div>
    );

    return (
        <div className="min-h-screen bg-slate-900 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-indigo-900 via-slate-900 to-black p-6 md:p-12 font-sans overflow-x-hidden relative">
            {/* Global Decorative Elements */}
            <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-indigo-600/10 rounded-full blur-[120px] pointer-events-none"></div>
            <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-blue-600/5 rounded-full blur-[120px] pointer-events-none"></div>

            {/* Step 1: Welcome Screen (Floating Hero) */}
            {currentStep === 1 && (
                <div className="min-h-[80vh] flex items-center justify-center animate-in fade-in zoom-in duration-1000 text-white">
                    <div className="max-w-2xl w-full text-center relative z-10">
                        <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-full text-indigo-400 text-xs font-black uppercase tracking-[0.2em] mb-8 shadow-2xl backdrop-blur-md">
                            <Sparkles className="w-4 h-4" />
                            AI Learning Co-Pilot
                        </div>

                        <h1 className="text-5xl md:text-7xl font-extrabold text-white mb-6 tracking-tight leading-none">
                            Welcome back, <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-blue-400">Engineer.</span>
                        </h1>

                        <div className="mb-12">
                            <p className="text-xl text-slate-400 italic font-medium leading-relaxed max-w-lg mx-auto">
                                "If you can't explain it simply, you don't understand it well enough."
                            </p>
                            <p className="text-sm font-black text-indigo-500 uppercase mt-4 tracking-widest">— Albert Einstein</p>
                        </div>

                        <button
                            onClick={() => setCurrentStep(2)}
                            className="group relative px-10 py-5 bg-indigo-500 hover:bg-indigo-400 text-white rounded-full font-bold text-lg transition-all duration-300 shadow-[0_0_20px_rgba(99,102,241,0.4)] hover:scale-105 active:scale-95 overflow-hidden"
                        >
                            <span className="relative z-10 flex items-center gap-3">
                                Start Your Journey
                                <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
                            </span>
                        </button>

                        <div className="mt-20 flex justify-center gap-12 opacity-30 grayscale">
                            <div className="text-white text-xs font-black uppercase tracking-widest">Active Recall</div>
                            <div className="text-white text-xs font-black uppercase tracking-widest">Feynman Technique</div>
                            <div className="text-white text-xs font-black uppercase tracking-widest">Metacognition</div>
                        </div>
                    </div>
                </div>
            )}

            {/* Step 2: Skill Islands (Light Card) */}
            {currentStep === 2 && (
                <ScreenWrapper title="Choose Your Target" subtitle="Select a node from your isometric syllabus roadmap to begin.">
                    <SyllabusTracker currentTopic={topic} onSelectTopic={handleTopicSelect} />
                </ScreenWrapper>
            )}

            {/* Step 3: Input Room (Light Card) */}
            {currentStep === 3 && (
                <ScreenWrapper title="Input Room" subtitle={`Currently exploring: ${topic}`}>
                    <form onSubmit={handleSubmit} className="space-y-8">
                        {/* Learning Mode Selector */}
                        <div className="space-y-4">
                            <div className="flex items-center gap-2 mb-2">
                                <Layers className="w-4 h-4 text-indigo-500" />
                                <label className="text-xs font-black text-slate-400 uppercase tracking-widest">
                                    Learning Context
                                </label>
                            </div>
                            <div className="flex flex-wrap gap-3">
                                {modes.map((mode) => (
                                    <button
                                        key={mode.id}
                                        type="button"
                                        onClick={() => setLearningMode(mode.id)}
                                        className={`flex flex-col items-center p-4 transition-all duration-300 text-left group flex-1 min-w-[140px]
                                            ${learningMode === mode.id
                                                ? 'bg-indigo-600 text-white shadow-md rounded-lg scale-[1.02]'
                                                : 'bg-slate-50 text-slate-600 border border-slate-200 hover:bg-slate-100 rounded-lg'}`}
                                    >
                                        <mode.icon className={`w-5 h-5 mb-2 transition-colors ${learningMode === mode.id ? 'text-white' : 'text-indigo-400 group-hover:text-indigo-600'}`} />
                                        <span className="text-xs font-black uppercase tracking-tight mb-1">{mode.label}</span>
                                        <span className={`text-[10px] text-center leading-tight transition-colors ${learningMode === mode.id ? 'text-indigo-100' : 'text-slate-400'}`}>
                                            {mode.description}
                                        </span>
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div className="grid grid-cols-1 gap-8">
                            <div>
                                <label htmlFor="topic" className="block text-xs font-black text-slate-400 uppercase tracking-widest mb-3">
                                    Target Concept
                                </label>
                                <input
                                    id="topic"
                                    type="text"
                                    value={topic}
                                    readOnly
                                    className="w-full px-6 py-4 rounded-2xl bg-slate-50 border border-slate-200 text-slate-500 font-bold shadow-inner cursor-not-allowed"
                                />
                            </div>

                            <div>
                                <label htmlFor="explanation" className="block text-xs font-black text-slate-400 uppercase tracking-widest mb-3">
                                    Your Explanation
                                </label>
                                <textarea
                                    id="explanation"
                                    rows={8}
                                    value={explanation}
                                    onChange={(e) => setExplanation(e.target.value)}
                                    placeholder="Explain the concept as if you were teaching it to a curious student..."
                                    className="w-full px-6 py-4 rounded-2xl bg-slate-50 border border-slate-200 focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 focus:bg-white transition-all text-slate-900 font-medium placeholder:text-slate-300 shadow-inner leading-relaxed"
                                    required
                                />
                            </div>
                        </div>

                        <div className="flex gap-4">
                            <button
                                type="button"
                                onClick={() => setCurrentStep(2)}
                                className="px-8 py-4 bg-slate-100 text-slate-600 font-black rounded-2xl hover:bg-slate-200 transition-all flex items-center gap-2"
                            >
                                <MapIcon className="w-5 h-5" />
                                BACK TO MAP
                            </button>
                            <button
                                type="submit"
                                disabled={isLoading || !topic || !explanation}
                                className="flex-1 flex items-center justify-center gap-3 bg-indigo-600 hover:bg-indigo-700 text-white font-black py-4 px-8 rounded-2xl transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-xl shadow-indigo-900/10 active:scale-[0.98]"
                            >
                                <Send className="w-5 h-5" />
                                ANALYZE EXPLANATION
                            </button>
                        </div>
                    </form>
                </ScreenWrapper>
            )}

            {/* Step 4: Evaluation Results (Light Card) */}
            {currentStep === 4 && (
                <ScreenWrapper title="Evaluation" subtitle={`Reviewing your understanding of ${topic}`}>
                    {thinkingText && !evaluation && (
                        <div className="mb-10 animate-in fade-in slide-in-from-bottom-8 duration-700">
                            <div className="bg-slate-50 border border-slate-200 rounded-3xl p-8 relative overflow-hidden">
                                <div className="absolute top-0 left-0 w-1 h-full bg-indigo-500"></div>
                                <div className="flex items-center gap-3 mb-6">
                                    <div className="p-2 bg-indigo-100 text-indigo-600 rounded-xl">
                                        <BrainCircuit className="w-6 h-6 animate-pulse" />
                                    </div>
                                    <div>
                                        <h2 className="text-sm font-black text-slate-800 uppercase tracking-widest">AI Cognition Phase</h2>
                                        <p className="text-[10px] font-bold text-slate-400 uppercase tracking-tight">Processing pedagogical nuances</p>
                                    </div>
                                </div>
                                <div className="text-slate-600 italic font-medium leading-relaxed whitespace-pre-wrap pl-4 border-l-2 border-slate-100">
                                    {thinkingText}
                                    {isLoading && <span className="inline-block w-2 h-4 ml-1 bg-indigo-500 animate-pulse" />}
                                </div>
                            </div>
                        </div>
                    )}

                    {error && (
                        <div className="mb-6 p-6 bg-rose-50 text-rose-700 rounded-2xl border border-rose-100 flex flex-col items-center gap-4 font-bold text-center">
                            <div className="w-3 h-3 rounded-full bg-rose-500 animate-pulse"></div>
                            <p>{error}</p>
                            <button
                                onClick={() => setCurrentStep(3)}
                                className="text-xs uppercase tracking-widest bg-rose-600 text-white px-4 py-2 rounded-lg hover:bg-rose-700 transition-colors"
                            >
                                Return to Input
                            </button>
                        </div>
                    )}

                    <FeedbackCard
                        evaluation={evaluation}
                        isLoading={isLoading}
                        onRetry={handleRetry}
                        onClaimMastery={handleClaimMastery}
                    />
                </ScreenWrapper>
            )}

            {/* Step 5: Mastery Screen (Floating Hero) */}
            {currentStep === 5 && (
                <div className="min-h-[80vh] flex flex-col items-center justify-center animate-in zoom-in slide-in-from-bottom-20 duration-1000 text-white text-center">
                    <div className="mb-8 inline-block p-6 bg-white/10 backdrop-blur-md rounded-full shadow-[0_20px_50px_rgba(255,255,255,0.1)] border-4 border-white/20">
                        <Trophy className="w-16 h-16 text-emerald-400 drop-shadow-lg" />
                    </div>

                    <h1 className="text-5xl md:text-7xl font-black text-white mb-6 tracking-tighter leading-none uppercase drop-shadow-2xl">
                        Outstanding!
                    </h1>

                    <p className="text-2xl md:text-3xl text-emerald-400 drop-shadow-md font-extrabold mb-8 decoration-white/20 underline decoration-4 underline-offset-[12px]">
                        You have mastered {topic}.
                    </p>

                    <div className="bg-white/5 backdrop-blur-lg p-10 rounded-3xl border border-white/10 mb-12 shadow-2xl max-w-2xl">
                        <p className="text-lg text-slate-300 font-medium leading-relaxed">
                            You proved your technical depth and communication skills.
                            The next phase, <span className="font-black text-white uppercase tracking-tight">System Architecture & Cloud Deployment</span>, is now <span className="text-yellow-400 font-black italic">UNLOCKED</span>.
                        </p>
                    </div>

                    <button
                        onClick={handleReturnToMap}
                        className="group px-12 py-5 bg-white text-slate-900 rounded-full font-black text-xl transition-all duration-300 shadow-[0_20px_50px_rgba(0,0,0,0.3)] hover:scale-105 flex items-center gap-3 mx-auto active:scale-95"
                    >
                        Return to Map
                        <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
                    </button>
                </div>
            )}
        </div>
    );
};

export default StudyRoom;
