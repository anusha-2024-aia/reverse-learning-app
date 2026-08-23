import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, CheckCircle2, ArrowRight, Upload } from 'lucide-react';

const ResumeIntelligenceCard = ({ resumeSummary }) => {
    const navigate = useNavigate();

    const hasResume = resumeSummary?.has_resume;
    const fileName = resumeSummary?.file_name;
    const projectsCount = resumeSummary?.projects_count || 0;
    const questionsCount = resumeSummary?.questions_count || 0;
    const lastInterviewScore = resumeSummary?.last_interview_score;
    const recommendedPrep = resumeSummary?.recommended_prep;

    return (
        <div className="bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl relative overflow-hidden flex flex-col justify-between mb-8">
            <div>
                {/* Header */}
                <div className="flex items-center justify-between gap-4 mb-4">
                    <div className="flex items-center gap-2.5 text-white font-bold text-lg">
                        <div className="p-2 bg-indigo-600/20 text-indigo-400 rounded-xl border border-indigo-500/30">
                            <FileText className="w-5 h-5" />
                        </div>
                        <span>Resume Intelligence</span>
                    </div>

                    <span className={`text-xs font-black uppercase px-2.5 py-1 rounded-full border ${
                        hasResume 
                            ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
                            : 'bg-amber-500/20 text-amber-300 border-amber-500/30'
                    }`}>
                        {hasResume ? '✓ Resume analyzed' : 'No Resume Uploaded'}
                    </span>
                </div>

                {hasResume ? (
                    <div className="space-y-3 mb-4">
                        <div className="bg-slate-900/90 p-3 rounded-xl border border-slate-800 flex items-center justify-between text-xs">
                            <span className="text-slate-400 font-medium truncate max-w-[200px]">{fileName}</span>
                            <span className="font-bold text-emerald-400 flex items-center gap-1">
                                <CheckCircle2 className="w-3.5 h-3.5" /> Active Profile
                            </span>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs text-center">
                            <div className="bg-slate-900/60 p-2.5 rounded-xl border border-slate-800">
                                <span className="block text-[10px] text-slate-500 font-bold uppercase">Projects</span>
                                <span className="text-lg font-black text-white">{projectsCount}</span>
                            </div>
                            <div className="bg-slate-900/60 p-2.5 rounded-xl border border-slate-800">
                                <span className="block text-[10px] text-slate-500 font-bold uppercase">Personalized Questions</span>
                                <span className="text-lg font-black text-indigo-400">{questionsCount}</span>
                            </div>
                            <div className="bg-slate-900/60 p-2.5 rounded-xl border border-slate-800">
                                <span className="block text-[10px] text-slate-500 font-bold uppercase">Last Interview</span>
                                <span className="text-lg font-black text-emerald-400">
                                    {lastInterviewScore !== null && lastInterviewScore !== undefined ? `${lastInterviewScore}%` : 'N/A'}
                                </span>
                            </div>
                            <div className="bg-slate-900/60 p-2.5 rounded-xl border border-slate-800 flex flex-col justify-center">
                                <span className="block text-[10px] text-slate-500 font-bold uppercase">Recommended Prep</span>
                                <span className="text-xs font-bold text-amber-300 truncate">
                                    {recommendedPrep || 'Database Design'}
                                </span>
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="p-4 bg-slate-900/60 rounded-xl border border-slate-800 text-xs text-slate-400 mb-4 space-y-1">
                        <p className="text-slate-200 font-semibold">Upload your resume to generate personalized interview questions.</p>
                        <p className="text-slate-400">Supported formats: PDF, DOCX</p>
                    </div>
                )}
            </div>

            <button
                onClick={() => navigate('/resume')}
                className="w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl text-xs flex items-center justify-center gap-2 transition-all shadow-lg shadow-indigo-600/30"
            >
                <span>{hasResume ? 'View Personalized Questions' : 'Upload Resume'}</span>
                <ArrowRight className="w-4 h-4" />
            </button>
        </div>
    );
};

export default ResumeIntelligenceCard;
