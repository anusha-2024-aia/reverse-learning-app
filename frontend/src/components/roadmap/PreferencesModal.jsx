import React, { useState } from 'react';
import { Sliders, AlertTriangle, Check, X } from 'lucide-react';

const PreferencesModal = ({ isOpen, onClose, currentPreferences = {}, onSave }) => {
  const [targetRole, setTargetRole] = useState(currentPreferences.target_role || "Full Stack Developer");
  const [hoursPerDay, setHoursPerDay] = useState(currentPreferences.hours_per_day || 2.0);
  const [daysPerWeek, setDaysPerWeek] = useState(currentPreferences.days_per_week || 6);
  const [experienceLevel, setExperienceLevel] = useState(currentPreferences.experience_level || "BEGINNER");
  const [careerGoal, setCareerGoal] = useState(currentPreferences.career_goal || "");
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const isRoleChanged = currentPreferences.target_role && currentPreferences.target_role.toLowerCase() !== targetRole.toLowerCase();

  const handleSave = async (e) => {
    e.preventDefault();
    setLoading(true);
    await onSave({
      target_role: targetRole,
      hours_per_day: hoursPerDay,
      days_per_week: daysPerWeek,
      experience_level: experienceLevel,
      career_goal: careerGoal
    });
    setLoading(false);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md overflow-y-auto">
      <div className="bg-slate-900 border border-slate-700/80 rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl p-6 space-y-5 my-8">
        
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-2 text-indigo-400 font-bold text-lg">
            <Sliders className="w-5 h-5" /> Edit Roadmap Preferences
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSave} className="space-y-4 text-sm">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">Target Role</label>
            <input
              type="text"
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl p-3 text-slate-100 focus:outline-none focus:border-indigo-500 font-medium"
              placeholder="e.g. Full Stack Developer, AI Engineer..."
              required
            />
          </div>

          {isRoleChanged && (
            <div className="bg-amber-950/40 border border-amber-800/50 p-3 rounded-xl text-amber-300 text-xs flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
              <span>Changing your target role will generate a new personalized roadmap for <strong>{targetRole}</strong>.</span>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">Experience Level</label>
            <select
              value={experienceLevel}
              onChange={(e) => setExperienceLevel(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl p-3 text-slate-100 focus:outline-none focus:border-indigo-500"
            >
              <option value="BEGINNER">BEGINNER (Starting from basics)</option>
              <option value="INTERMEDIATE">INTERMEDIATE (Built small apps)</option>
              <option value="ADVANCED">ADVANCED (Professional developer)</option>
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">Hours / Day</label>
              <input
                type="number"
                min="0.5"
                max="8"
                step="0.5"
                value={hoursPerDay}
                onChange={(e) => setHoursPerDay(parseFloat(e.target.value))}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl p-3 text-slate-100 focus:outline-none focus:border-indigo-500 font-medium"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">Days / Week</label>
              <input
                type="number"
                min="1"
                max="7"
                step="1"
                value={daysPerWeek}
                onChange={(e) => setDaysPerWeek(parseInt(e.target.value))}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl p-3 text-slate-100 focus:outline-none focus:border-indigo-500 font-medium"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">Career Goal</label>
            <textarea
              value={careerGoal}
              onChange={(e) => setCareerGoal(e.target.value)}
              rows={2}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl p-3 text-slate-100 focus:outline-none focus:border-indigo-500"
              placeholder="Your overarching career objective..."
            />
          </div>

          <div className="pt-3 flex justify-end gap-3 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl font-medium text-xs transition-colors"
            >
              Cancel
            </button>

            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-bold text-xs transition-colors flex items-center gap-1.5 shadow-lg shadow-indigo-600/30"
            >
              {loading ? 'Saving...' : 'Save & Recalculate'}
            </button>
          </div>
        </form>

      </div>
    </div>
  );
};

export default PreferencesModal;
