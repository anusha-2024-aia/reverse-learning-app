import React from 'react';
import {
    CheckCircle,
    BrainCircuit,
    BookOpen,
    Sparkles,
    Wrench,
    Target,
    Volume2,
    Lightbulb,
    RotateCcw
} from 'lucide-react';

const CardHeader = ({ icon: IconComponent, title, iconColor = "text-gray-400" }) => (
    <div className="flex items-center gap-2 mb-4">
        <IconComponent className={`w-4 h-4 ${iconColor}`} />
        <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider">{title}</h3>
    </div>
);

const SkeletonCard = () => (
    <div className="w-full space-y-6 animate-pulse p-4">
        <div className="h-40 bg-white rounded-2xl border border-slate-200 shadow-sm w-full"></div>
        <div className="h-64 bg-white rounded-2xl border border-slate-200 shadow-sm w-full"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="h-48 bg-white rounded-2xl border border-slate-200 shadow-sm"></div>
            <div className="h-48 bg-white rounded-2xl border border-slate-200 shadow-sm"></div>
        </div>
    </div>
);

const FeedbackCard = ({ evaluation, isLoading, onRetry, onClaimMastery }) => {
    if (isLoading) return <SkeletonCard />;
    if (!evaluation) return null;

    const {
        score,
        grammatical_fixes,
        advanced_version,
        key_vocabulary,
        feedback,
        missing_concepts,
        follow_up_question
    } = evaluation;

    const playAudio = (text) => {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 0.9;
            window.speechSynthesis.speak(utterance);
        }
    };

    const getScoreStyles = (s) => {
        if (s >= 8) return { text: 'text-emerald-600', ring: 'ring-emerald-500/20', bg: 'bg-emerald-50', border: 'border-emerald-200' };
        if (s >= 5) return { text: 'text-amber-600', ring: 'ring-amber-500/20', bg: 'bg-amber-50', border: 'border-amber-200' };
        return { text: 'text-rose-600', ring: 'ring-rose-500/20', bg: 'bg-rose-50', border: 'border-rose-200' };
    };

    const styles = getScoreStyles(score);
    const cardBase = "bg-white rounded-2xl shadow-md border border-slate-200 p-8 transition-all hover:shadow-lg duration-300 relative";

    return (
        <div className="mt-12 space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-1000">

            {/* 1. Hero Summary Card */}
            <div className={cardBase}>
                <div className="flex flex-col md:flex-row items-center gap-10">
                    {/* Bolder Score Ring */}
                    <div className="relative flex-shrink-0 group">
                        <div className={`w-32 h-32 rounded-full border-[6px] ${styles.border} flex items-center justify-center ${styles.bg} shadow-lg ring-8 ${styles.ring}`}>
                            <div className="text-center">
                                <span className={`text-4xl font-black ${styles.text}`}>{score}</span>
                                <span className="block text-[10px] font-black text-slate-400 uppercase tracking-widest">/ 10</span>
                            </div>
                        </div>
                        <div className="absolute -bottom-2 -right-2 bg-white p-2 rounded-xl shadow-xl border border-slate-100 transform group-hover:rotate-12 transition-transform">
                            <Sparkles className={`w-6 h-6 ${styles.text}`} />
                        </div>
                    </div>

                    {/* Feedback Text */}
                    <div className="flex-1 text-center md:text-left">
                        <CardHeader icon={Target} title="AI EVALUATION" iconColor="text-indigo-600" />
                        <h2 className="text-xl md:text-2xl font-bold text-slate-800 leading-tight">
                            {feedback}
                        </h2>
                    </div>
                </div>
            </div>

            {/* 2. Detailed Analysis Section */}
            {missing_concepts && missing_concepts.length > 0 && (
                <div className={cardBase}>
                    <CardHeader icon={BookOpen} title="DETAILED ANALYSIS" iconColor="text-blue-600" />
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {missing_concepts.map((concept, idx) => (
                            <div key={idx} className="flex items-start gap-4 p-4 bg-slate-50 rounded-xl border border-slate-100 hover:bg-white hover:border-indigo-200 transition-all group">
                                <div className="mt-0.5 p-1.5 bg-blue-50 text-blue-600 rounded-full shadow-sm group-hover:bg-indigo-600 group-hover:text-white transition-colors">
                                    <CheckCircle className="w-4 h-4 text-inherit" />
                                </div>
                                <span className="text-sm text-slate-600 font-semibold leading-relaxed group-hover:text-slate-900">{concept}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* 3. Actionable Grid (Bento Box) */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                {/* Grammar Card */}
                {grammatical_fixes && (
                    <div className={`${cardBase} border-t-8 border-t-rose-500`}>
                        <CardHeader icon={Wrench} title="GRAMMAR & CORRECTIONS" iconColor="text-rose-500" />
                        <div className="p-5 bg-rose-50/50 rounded-xl border border-rose-100">
                            <p className="text-sm text-slate-600 leading-relaxed font-medium">
                                {grammatical_fixes}
                            </p>
                        </div>
                    </div>
                )}

                {/* Advanced Script Card with Fixed Audio Button */}
                {advanced_version && (
                    <div className={`${cardBase} border-t-8 border-t-emerald-500 group`}>
                        <CardHeader icon={BrainCircuit} title="ADVANCED PROFICIENCY SCRIPT" iconColor="text-emerald-500" />

                        {/* Audio Button - Absolutely Styled in Top Right */}
                        <button
                            onClick={() => playAudio(advanced_version)}
                            className="absolute top-6 right-6 p-3 bg-emerald-50 text-emerald-600 hover:bg-emerald-600 hover:text-white rounded-2xl border border-emerald-100 transition-all shadow-sm hover:shadow-emerald-200 hover:shadow-lg active:scale-95"
                            title="Listen to pronunciation"
                        >
                            <Volume2 className="w-5 h-5" />
                        </button>

                        <div className="mt-4 p-6 bg-slate-50/50 rounded-xl border border-slate-100 italic shadow-inner">
                            <p className="text-slate-800 font-bold leading-relaxed text-base">
                                "{advanced_version}"
                            </p>
                        </div>
                    </div>
                )}
            </div>

            {/* 4. Vocabulary Badges */}
            {key_vocabulary && key_vocabulary.length > 0 && (
                <div className={cardBase}>
                    <CardHeader icon={Sparkles} title="KEYWORD MASTERY" iconColor="text-indigo-600" />
                    <div className="flex flex-wrap gap-3 mt-2">
                        {key_vocabulary.map((word, i) => (
                            <div key={i} className="group cursor-default">
                                <span className="px-5 py-2 bg-indigo-100 text-indigo-700 font-bold text-xs rounded-full shadow-sm border border-indigo-200 flex items-center gap-2 group-hover:bg-indigo-600 group-hover:text-white transition-all uppercase tracking-wider">
                                    <div className="w-1.5 h-1.5 rounded-full bg-indigo-400 group-hover:bg-indigo-200"></div>
                                    {word}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* 5. Thinking Deeper Follow-Up Card */}
            {follow_up_question && (
                <div className={`${cardBase} bg-gradient-to-br from-purple-50/10 to-transparent border-purple-200`}>
                    <CardHeader icon={Lightbulb} title="THINKING DEEPER" iconColor="text-purple-600" />
                    <p className="text-xl text-slate-800 font-bold italic leading-relaxed pl-6 border-l-4 border-purple-400">
                        {follow_up_question}
                    </p>
                </div>
            )}

            {/* 6. Action Footer (Actionable Loop) */}
            <div className="flex flex-col sm:flex-row justify-center items-center gap-6 mt-12 pt-10 border-t border-slate-200">
                {score < 8 ? (
                    <button
                        onClick={onRetry}
                        className="w-full sm:w-auto bg-slate-900 text-white px-8 py-4 rounded-xl hover:bg-slate-800 transition-all font-bold shadow-2xl shadow-slate-900/30 flex items-center justify-center gap-3 group hover:-translate-y-1 active:translate-y-0"
                    >
                        <RotateCcw className="w-6 h-6 group-hover:rotate-180 transition-transform duration-1000" />
                        Try Again Incorporating Feedback
                    </button>
                ) : (
                    <button
                        onClick={onClaimMastery}
                        className="w-full sm:w-auto bg-emerald-600 text-white px-10 py-5 rounded-xl hover:bg-emerald-500 transition-all font-black shadow-[0_20px_40px_rgba(16,185,129,0.3)] flex items-center justify-center gap-3 group animate-bounce hover:animate-none active:scale-95"
                    >
                        <Sparkles className="w-6 h-6" />
                        CLAIM YOUR MASTERY
                    </button>
                )}
            </div>
        </div>
    );
};


export default FeedbackCard;
