import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import StudyRoom from './pages/StudyRoom'
import Dashboard from './pages/Dashboard'
import SyllabusTracker from './pages/SyllabusTracker'
import StudyHistory from './pages/StudyHistory'
import AchievementsPage from './pages/AchievementsPage'
import AchievementNotification from './components/AchievementNotification'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import StitchLayout from './components/layout/StitchLayout'
import LoginPage from './pages/LoginPage'
import SignupPage from './pages/SignupPage'
import MockInterview from './pages/MockInterview'
import KnowledgeGaps from './pages/KnowledgeGaps'
import LearningPath from './pages/LearningPath'
import EvaluationsHistory from './pages/EvaluationsHistory'
import SmartRevision from './pages/SmartRevision'
import ResumeIntelligence from './pages/ResumeIntelligence'
import CommunicationCoach from './pages/CommunicationCoach'
import AnalyticsPage from './pages/AnalyticsPage'
import VirtualStudyRoom from './pages/VirtualStudyRoom'
import ProfileSettings from './pages/ProfileSettings'
import ForgotPasswordPage from './pages/ForgotPasswordPage'

// Consistent wrapper for all authenticated screens guaranteeing persistent sidebar & topbar
const AuthenticatedRoute = ({ children }) => (
  <ProtectedRoute>
    <StitchLayout>
      {children}
    </StitchLayout>
  </ProtectedRoute>
)

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-[#080C14] text-slate-100 flex flex-col font-sans relative selection:bg-cyan-500/30 selection:text-cyan-200">
          <AchievementNotification />
          <main className="flex-1 flex flex-col relative overflow-x-hidden">
            <Routes>
              {/* Public Unauthenticated Routes */}
              <Route path="/login" element={<LoginPage />} />
              <Route path="/signup" element={<SignupPage />} />
              <Route path="/forgot-password" element={<ForgotPasswordPage />} />

              {/* Core Authenticated Routes with Persistent Navigation */}
              <Route path="/" element={<AuthenticatedRoute><Dashboard /></AuthenticatedRoute>} />
              <Route path="/knowledge-gaps" element={<AuthenticatedRoute><KnowledgeGaps /></AuthenticatedRoute>} />
              <Route path="/study" element={<AuthenticatedRoute><StudyRoom /></AuthenticatedRoute>} />
              <Route path="/revision" element={<AuthenticatedRoute><SmartRevision /></AuthenticatedRoute>} />

              <Route path="/resume" element={<AuthenticatedRoute><ResumeIntelligence /></AuthenticatedRoute>} />
              <Route path="/resume-intelligence" element={<AuthenticatedRoute><ResumeIntelligence /></AuthenticatedRoute>} />
              <Route path="/interview" element={<AuthenticatedRoute><MockInterview /></AuthenticatedRoute>} />
              <Route path="/mock-interview" element={<AuthenticatedRoute><MockInterview /></AuthenticatedRoute>} />
              <Route path="/study-room" element={<AuthenticatedRoute><VirtualStudyRoom /></AuthenticatedRoute>} />
              <Route path="/analytics" element={<AuthenticatedRoute><AnalyticsPage /></AuthenticatedRoute>} />
              <Route path="/insights" element={<AuthenticatedRoute><AnalyticsPage /></AuthenticatedRoute>} />

              <Route path="/profile" element={<AuthenticatedRoute><ProfileSettings /></AuthenticatedRoute>} />
              <Route path="/settings" element={<AuthenticatedRoute><ProfileSettings /></AuthenticatedRoute>} />

              {/* Extended Learning & History Routes */}
              <Route path="/achievements" element={<AuthenticatedRoute><AchievementsPage /></AuthenticatedRoute>} />
              <Route path="/history" element={<AuthenticatedRoute><StudyHistory /></AuthenticatedRoute>} />
              <Route path="/syllabi" element={<AuthenticatedRoute><SyllabusTracker /></AuthenticatedRoute>} />
              <Route path="/learning-path" element={<AuthenticatedRoute><LearningPath /></AuthenticatedRoute>} />
              <Route path="/learning-roadmap" element={<AuthenticatedRoute><LearningPath /></AuthenticatedRoute>} />
              <Route path="/communication-coach" element={<AuthenticatedRoute><CommunicationCoach /></AuthenticatedRoute>} />
              <Route path="/evaluations" element={<AuthenticatedRoute><EvaluationsHistory /></AuthenticatedRoute>} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
