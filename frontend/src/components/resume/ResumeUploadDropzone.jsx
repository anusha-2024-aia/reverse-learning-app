import React, { useState } from 'react';
import { Upload, FileText, CheckCircle2, AlertCircle, Loader2, RefreshCw } from 'lucide-react';
import api from '../../api/axios';

const ResumeUploadDropzone = ({ onUploadSuccess, isReplacement = false, activeFileName: _ACTIVE_FILE_NAME = null }) => {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [stage, setStage] = useState('');
    const [error, setError] = useState(null);

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (!selectedFile) return;

        setError(null);
        const ext = selectedFile.name.split('.').pop().toLowerCase();
        if (ext !== 'pdf' && ext !== 'docx') {
            setError('Please upload a PDF or DOCX resume.');
            return;
        }

        if (selectedFile.size > 10 * 1024 * 1024) {
            setError('File size exceeds the 10 MB limit.');
            return;
        }

        setFile(selectedFile);
    };

    const handleUpload = async () => {
        if (!file) return;

        setLoading(true);
        setError(null);
        setStage('Uploading Resume...');

        const formData = new FormData();
        formData.append('file', file);

        try {
            setTimeout(() => setStage('Extracting Resume Text...'), 800);
            setTimeout(() => setStage('Identifying Skills...'), 1600);
            setTimeout(() => setStage('Identifying Projects...'), 2400);
            setTimeout(() => setStage('Analyzing Resume with AI...'), 3200);
            setTimeout(() => setStage('Generating Personalized Questions...'), 4200);

            const endpoint = '/resume/upload';
            const res = await api.post(endpoint, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            setStage('Complete ✓');
            setTimeout(() => {
                setLoading(false);
                if (onUploadSuccess) onUploadSuccess(res.data);
            }, 600);

        } catch (err) {
            console.error("Resume upload error:", err);
            setError(err.response?.data?.detail || 'Unable to analyze your resume right now. Please try again.');
            setLoading(false);
            setStage('');
        }
    };

    return (
        <div className="bg-slate-800/80 border border-slate-700/80 rounded-3xl p-8 shadow-2xl relative overflow-hidden text-center max-w-2xl mx-auto space-y-6">
            <div className="w-16 h-16 bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 rounded-2xl flex items-center justify-center mx-auto shadow-lg">
                <FileText className="w-8 h-8" />
            </div>

            <div>
                <h2 className="text-2xl font-black text-white">
                    {isReplacement ? 'Replace Resume' : 'Resume Intelligence'}
                </h2>
                <p className="text-sm text-slate-400 mt-1 max-w-md mx-auto">
                    Upload your resume and let AI generate interview questions based on your actual skills, projects, and experience.
                </p>
            </div>

            {/* Dropzone Container */}
            <div className="border-2 border-dashed border-slate-700 hover:border-indigo-500/60 transition-all rounded-2xl p-8 bg-slate-900/50 cursor-pointer relative">
                <input 
                    type="file" 
                    accept=".pdf,.docx" 
                    onChange={handleFileChange}
                    disabled={loading}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
                />
                
                {file ? (
                    <div className="flex items-center justify-center gap-3 text-emerald-400 font-bold text-base">
                        <CheckCircle2 className="w-6 h-6" />
                        <span>{file.name} (Ready to analyze)</span>
                    </div>
                ) : (
                    <div className="space-y-2">
                        <Upload className="w-8 h-8 text-slate-400 mx-auto" />
                        <span className="text-sm font-bold text-slate-200 block">
                            Click or drag resume file here
                        </span>
                        <span className="text-xs text-slate-500 block font-medium">
                            Supported formats: PDF, DOCX (Max 10 MB)
                        </span>
                    </div>
                )}
            </div>

            {/* Stage Indicator */}
            {loading && (
                <div className="p-4 bg-indigo-950/40 border border-indigo-500/30 rounded-2xl space-y-2 animate-pulse">
                    <div className="flex items-center justify-center gap-2 text-indigo-300 font-bold text-xs uppercase tracking-wider">
                        <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
                        <span>{stage}</span>
                    </div>
                </div>
            )}

            {/* Error Message */}
            {error && (
                <div className="p-4 bg-rose-950/40 border border-rose-500/40 rounded-2xl text-xs text-rose-300 flex items-center justify-center gap-2 font-medium">
                    <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
                    <span>{error}</span>
                </div>
            )}

            {/* Submit Button */}
            {file && !loading && (
                <button
                    onClick={handleUpload}
                    className="w-full py-4 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-2xl shadow-lg shadow-indigo-600/30 transition-all text-sm flex items-center justify-center gap-2"
                >
                    <RefreshCw className="w-4 h-4" />
                    <span>{isReplacement ? 'Re-analyze & Replace Resume' : 'Analyze Resume'}</span>
                </button>
            )}
        </div>
    );
};

export default ResumeUploadDropzone;
