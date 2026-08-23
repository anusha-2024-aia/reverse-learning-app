import React, { useState } from 'react';
import { Target, Clock, Sparkles, CheckCircle2, ArrowRight, ArrowLeft, Brain, Code, Rocket } from 'lucide-react';

const OnboardingModal = ({ isOpen, onClose, onComplete }) => {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);

  // Form State
  const [careerGoal, setCareerGoal] = useState("Get placed as a software developer in a top company.");
  const [targetRole, setTargetRole] = useState("Full Stack Developer");
  const [customRole, setCustomRole] = useState("");
  const [currentSkills, setCurrentSkills] = useState(["HTML", "CSS", "JavaScript"]);
  const [customSkillInput, setCustomSkillInput] = useState("");
  const [experienceLevel, setExperienceLevel] = useState("BEGINNER");
  const [hoursPerDay, setHoursPerDay] = useState(2.0);
  const [daysPerWeek, setDaysPerWeek] = useState(6);
  const [preferredAreas, setPreferredAreas] = useState(["Web Development", "Backend Development", "Databases"]);

  if (!isOpen) return null;

  const popularRoles = [
    "Full Stack Developer",
    "Frontend Developer",
    "Backend Developer",
    "Data Scientist",
    "AI/ML Engineer",
    "Software Developer",
    "Cloud/DevOps Engineer",
    "Data Analyst"
  ];

  const skillOptions = [
    "HTML", "CSS", "JavaScript", "React", "Python", "Java", "SQL",
    "Node.js", "C++", "Data Structures", "Git", "TypeScript"
  ];

  const preferenceOptions = [
    "Web Development",
    "Backend Development",
    "Databases & SQL",
    "AI & Machine Learning",
    "System Design",
    "Cloud & DevOps",
    "Data Structures & Algorithms",
    "Interview Prep & Soft Skills"
  ];

  const handleAddSkill = (skill) => {
    if (!currentSkills.includes(skill)) {
      setCurrentSkills([...currentSkills, skill]);
    } else {
      setCurrentSkills(currentSkills.filter(s => s !== skill));
    }
  };

  const handleAddCustomSkill = (e) => {
    e.preventDefault();
    if (customSkillInput.trim() && !currentSkills.includes(customSkillInput.trim())) {
      setCurrentSkills([...currentSkills, customSkillInput.trim()]);
      setCustomSkillInput("");
    }
  };

  const handleTogglePref = (pref) => {
    if (preferredAreas.includes(pref)) {
      setPreferredAreas(preferredAreas.filter(p => p !== pref));
    } else {
      setPreferredAreas([...preferredAreas, pref]);
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    const finalRole = customRole.trim() || targetRole;
    const payload = {
      target_role: finalRole,
      current_skills: currentSkills,
      experience_level: experienceLevel,
      career_goal: careerGoal,
      hours_per_day: hoursPerDay,
      days_per_week: daysPerWeek,
      preferred_areas: preferredAreas
    };
    
    await onComplete(payload);
    setLoading(false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md overflow-y-auto">
      <div className="bg-slate-900 border border-slate-700/80 rounded-2xl w-full max-w-2xl overflow-hidden shadow-2xl transition-all my-8">
        
        {/* Top Progress Header */}
        <div className="bg-slate-800/60 border-b border-slate-700/50 p-6 flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2 text-indigo-400 font-bold text-sm">
              <Sparkles className="w-4 h-4" /> PHASE 5 ONBOARDING
            </div>
            <h2 className="text-xl font-bold text-white mt-1">Personalized AI Roadmap Setup</h2>
          </div>
          <div className="text-right">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Step {step} of 7</span>
            <div className="w-32 bg-slate-700 h-2 rounded-full mt-2 overflow-hidden">
              <div 
                className="bg-gradient-to-r from-indigo-500 to-emerald-400 h-full transition-all duration-300"
                style={{ width: `${(step / 7) * 100}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Content Body */}
        <div className="p-6 md:p-8 space-y-6">

          {/* STEP 1: CAREER GOAL */}
          {step === 1 && (
            <div className="space-y-4 animate-in fade-in duration-200">
              <div className="flex items-center gap-3 text-indigo-400">
                <Target className="w-8 h-8" />
                <div>
                  <h3 className="text-lg font-bold text-white">What is your primary career goal?</h3>
                  <p className="text-sm text-slate-400">Describe what success looks like for you right now.</p>
                </div>
              </div>

              <textarea
                value={careerGoal}
                onChange={(e) => setCareerGoal(e.target.value)}
                rows={4}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl p-4 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
                placeholder="e.g. I want to become a Full Stack Engineer and get hired at a high-growth tech company."
              />

              <div className="space-y-2">
                <p className="text-xs text-slate-400 font-medium uppercase tracking-wider">Suggestions:</p>
                <div className="flex flex-wrap gap-2">
                  {[
                    "Get placed as a Full Stack Developer",
                    "Transition into AI / Data Science",
                    "Master Backend Engineering & System Design",
                    "Prepare for upcoming campus placements"
                  ].map((sug, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => setCareerGoal(sug)}
                      className="text-xs bg-slate-800/80 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-lg border border-slate-700 transition-colors"
                    >
                      {sug}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* STEP 2: TARGET ROLE */}
          {step === 2 && (
            <div className="space-y-4 animate-in fade-in duration-200">
              <div className="flex items-center gap-3 text-indigo-400">
                <Rocket className="w-8 h-8" />
                <div>
                  <h3 className="text-lg font-bold text-white">Select Your Target Role</h3>
                  <p className="text-sm text-slate-400">Your roadmap will be specifically designed for this position.</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                {popularRoles.map((role) => (
                  <button
                    key={role}
                    type="button"
                    onClick={() => { setTargetRole(role); setCustomRole(""); }}
                    className={`p-3 rounded-xl border text-left font-medium text-sm transition-all flex items-center justify-between ${
                      targetRole === role && !customRole
                        ? 'bg-indigo-600/20 border-indigo-500 text-white shadow-lg'
                        : 'bg-slate-800/50 border-slate-700/60 text-slate-300 hover:bg-slate-800'
                    }`}
                  >
                    <span>{role}</span>
                    {targetRole === role && !customRole && <CheckCircle2 className="w-4 h-4 text-indigo-400" />}
                  </button>
                ))}
              </div>

              <div className="pt-2">
                <label className="text-xs text-slate-400 font-medium block mb-1">Or enter a custom role:</label>
                <input
                  type="text"
                  value={customRole}
                  onChange={(e) => setCustomRole(e.target.value)}
                  placeholder="e.g. Quantitative Developer, iOS Architect..."
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl p-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>
          )}

          {/* STEP 3: CURRENT SKILLS */}
          {step === 3 && (
            <div className="space-y-4 animate-in fade-in duration-200">
              <div className="flex items-center gap-3 text-indigo-400">
                <Code className="w-8 h-8" />
                <div>
                  <h3 className="text-lg font-bold text-white">What are your existing skills?</h3>
                  <p className="text-sm text-slate-400">Select topics you already have some familiarity with.</p>
                </div>
              </div>

              <div className="flex flex-wrap gap-2">
                {skillOptions.map((sk) => {
                  const selected = currentSkills.includes(sk);
                  return (
                    <button
                      key={sk}
                      type="button"
                      onClick={() => handleAddSkill(sk)}
                      className={`px-3 py-1.5 rounded-lg text-sm font-medium border transition-colors ${
                        selected
                          ? 'bg-indigo-600 text-white border-indigo-500'
                          : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-750'
                      }`}
                    >
                      {selected ? `✓ ${sk}` : `+ ${sk}`}
                    </button>
                  );
                })}
              </div>

              <form onSubmit={handleAddCustomSkill} className="flex gap-2 pt-2">
                <input
                  type="text"
                  value={customSkillInput}
                  onChange={(e) => setCustomSkillInput(e.target.value)}
                  placeholder="Add another skill..."
                  className="flex-1 bg-slate-800 border border-slate-700 rounded-xl p-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
                <button type="submit" className="bg-slate-700 hover:bg-slate-600 text-white px-4 rounded-xl text-sm font-medium transition-colors">
                  Add
                </button>
              </form>

              {currentSkills.length > 0 && (
                <div className="pt-2">
                  <span className="text-xs text-slate-400 font-medium">Selected ({currentSkills.length}):</span>
                  <div className="flex flex-wrap gap-1.5 mt-1">
                    {currentSkills.map(s => (
                      <span key={s} className="bg-indigo-900/40 text-indigo-300 border border-indigo-700/50 text-xs px-2.5 py-1 rounded-md">
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* STEP 4: EXPERIENCE LEVEL */}
          {step === 4 && (
            <div className="space-y-4 animate-in fade-in duration-200">
              <div className="flex items-center gap-3 text-indigo-400">
                <Brain className="w-8 h-8" />
                <div>
                  <h3 className="text-lg font-bold text-white">What is your current experience level?</h3>
                  <p className="text-sm text-slate-400">This configures the starting depth of your learning roadmap.</p>
                </div>
              </div>

              <div className="space-y-3">
                {[
                  { id: "BEGINNER", title: "Beginner", desc: "Starting from fundamentals. Need clear step-by-step guidance." },
                  { id: "INTERMEDIATE", title: "Intermediate", desc: "Built small projects. Ready for framework concepts & system fundamentals." },
                  { id: "ADVANCED", title: "Advanced", desc: "Experienced developer. Focus on architecture, scalability & optimization." }
                ].map((lvl) => (
                  <button
                    key={lvl.id}
                    type="button"
                    onClick={() => setExperienceLevel(lvl.id)}
                    className={`w-full p-4 rounded-xl border text-left transition-all flex items-start gap-4 ${
                      experienceLevel === lvl.id
                        ? 'bg-indigo-600/20 border-indigo-500 shadow-lg'
                        : 'bg-slate-800/50 border-slate-700/60 hover:bg-slate-800'
                    }`}
                  >
                    <div className={`p-2 rounded-lg ${experienceLevel === lvl.id ? 'bg-indigo-600 text-white' : 'bg-slate-700 text-slate-400'}`}>
                      <Brain className="w-5 h-5" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-white">{lvl.title}</span>
                        {experienceLevel === lvl.id && <CheckCircle2 className="w-5 h-5 text-indigo-400" />}
                      </div>
                      <p className="text-xs text-slate-400 mt-1">{lvl.desc}</p>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* STEP 5: AVAILABLE TIME */}
          {step === 5 && (
            <div className="space-y-6 animate-in fade-in duration-200">
              <div className="flex items-center gap-3 text-indigo-400">
                <Clock className="w-8 h-8" />
                <div>
                  <h3 className="text-lg font-bold text-white">Available Study Time</h3>
                  <p className="text-sm text-slate-400">Your roadmap pace & daily schedule will strictly respect your schedule.</p>
                </div>
              </div>

              <div className="bg-slate-800/60 border border-slate-700/60 p-5 rounded-xl space-y-4">
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium text-slate-200">Hours per day</span>
                    <span className="text-base font-bold text-indigo-400">{hoursPerDay} hours/day</span>
                  </div>
                  <input
                    type="range"
                    min="0.5"
                    max="8"
                    step="0.5"
                    value={hoursPerDay}
                    onChange={(e) => setHoursPerDay(parseFloat(e.target.value))}
                    className="w-full accent-indigo-500 h-2 bg-slate-700 rounded-lg cursor-pointer"
                  />
                  <div className="flex justify-between text-xs text-slate-500 mt-1">
                    <span>30 mins</span>
                    <span>2 hrs</span>
                    <span>4 hrs</span>
                    <span>8 hrs</span>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium text-slate-200">Days per week</span>
                    <span className="text-base font-bold text-emerald-400">{daysPerWeek} days/week</span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="7"
                    step="1"
                    value={daysPerWeek}
                    onChange={(e) => setDaysPerWeek(parseInt(e.target.value))}
                    className="w-full accent-emerald-500 h-2 bg-slate-700 rounded-lg cursor-pointer"
                  />
                  <div className="flex justify-between text-xs text-slate-500 mt-1">
                    <span>1 day</span>
                    <span>3 days</span>
                    <span>5 days</span>
                    <span>7 days</span>
                  </div>
                </div>

                <div className="bg-indigo-950/40 border border-indigo-800/40 p-3 rounded-lg text-xs text-indigo-300 flex items-center gap-2">
                  <Clock className="w-4 h-4 flex-shrink-0" />
                  <span>Total weekly commitment: <strong>{hoursPerDay * daysPerWeek} hours/week</strong></span>
                </div>
              </div>
            </div>
          )}

          {/* STEP 6: PREFERRED LEARNING AREAS */}
          {step === 6 && (
            <div className="space-y-4 animate-in fade-in duration-200">
              <div className="flex items-center gap-3 text-indigo-400">
                <Sparkles className="w-8 h-8" />
                <div>
                  <h3 className="text-lg font-bold text-white">Preferred Learning Areas</h3>
                  <p className="text-sm text-slate-400">Choose domains you want prioritized in your custom curriculum.</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2.5">
                {preferenceOptions.map((pref) => {
                  const selected = preferredAreas.includes(pref);
                  return (
                    <button
                      key={pref}
                      type="button"
                      onClick={() => handleTogglePref(pref)}
                      className={`p-3 rounded-xl border text-left text-xs font-semibold transition-all flex items-center justify-between ${
                        selected
                          ? 'bg-indigo-600/20 border-indigo-500 text-white'
                          : 'bg-slate-800/40 border-slate-700/60 text-slate-400 hover:bg-slate-800'
                      }`}
                    >
                      <span>{pref}</span>
                      {selected && <CheckCircle2 className="w-4 h-4 text-indigo-400 flex-shrink-0" />}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* STEP 7: SUMMARY & GENERATE */}
          {step === 7 && (
            <div className="space-y-6 animate-in fade-in duration-200">
              <div className="text-center space-y-2">
                <div className="w-12 h-12 bg-indigo-600/20 text-indigo-400 border border-indigo-500/40 rounded-full flex items-center justify-center mx-auto">
                  <Rocket className="w-6 h-6 animate-bounce" />
                </div>
                <h3 className="text-2xl font-black text-white">Ready to Generate Your Roadmap!</h3>
                <p className="text-sm text-slate-400 max-w-md mx-auto">
                  Our AI will synthesize your goal, skills, time, and preferences into a dynamic career learning pathway.
                </p>
              </div>

              <div className="bg-slate-800/80 border border-slate-700 p-5 rounded-xl space-y-3 text-sm">
                <div className="flex justify-between border-b border-slate-700/60 pb-2">
                  <span className="text-slate-400">Target Role:</span>
                  <span className="font-bold text-white">{customRole.trim() || targetRole}</span>
                </div>
                <div className="flex justify-between border-b border-slate-700/60 pb-2">
                  <span className="text-slate-400">Experience Level:</span>
                  <span className="font-semibold text-indigo-300">{experienceLevel}</span>
                </div>
                <div className="flex justify-between border-b border-slate-700/60 pb-2">
                  <span className="text-slate-400">Available Pace:</span>
                  <span className="font-semibold text-emerald-400">{hoursPerDay} hrs/day ({daysPerWeek} days/wk)</span>
                </div>
                <div className="flex justify-between border-b border-slate-700/60 pb-2">
                  <span className="text-slate-400">Current Skills:</span>
                  <span className="text-slate-300 truncate max-w-xs">{currentSkills.join(", ") || "None specified"}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Preferred Focus:</span>
                  <span className="text-slate-300 truncate max-w-xs">{preferredAreas.join(", ") || "All Areas"}</span>
                </div>
              </div>
            </div>
          )}

        </div>

        {/* Bottom Action Footer */}
        <div className="bg-slate-800/80 border-t border-slate-700/50 p-6 flex justify-between items-center">
          {step > 1 ? (
            <button
              type="button"
              disabled={loading}
              onClick={() => setStep(step - 1)}
              className="flex items-center gap-2 px-4 py-2.5 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-xl font-medium text-sm transition-colors"
            >
              <ArrowLeft className="w-4 h-4" /> Back
            </button>
          ) : (
            <div></div>
          )}

          {step < 7 ? (
            <button
              type="button"
              onClick={() => setStep(step + 1)}
              className="flex items-center gap-2 px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-bold text-sm transition-colors shadow-lg shadow-indigo-600/30"
            >
              Next Step <ArrowRight className="w-4 h-4" />
            </button>
          ) : (
            <button
              type="button"
              disabled={loading}
              onClick={handleSubmit}
              className="flex items-center gap-2 px-8 py-3 bg-gradient-to-r from-indigo-600 to-emerald-500 hover:from-indigo-500 hover:to-emerald-400 text-white rounded-xl font-black text-sm transition-all shadow-xl shadow-indigo-500/25"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Generating AI Roadmap...
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5" /> Generate My Roadmap
                </>
              )}
            </button>
          )}
        </div>

      </div>
    </div>
  );
};

export default OnboardingModal;
