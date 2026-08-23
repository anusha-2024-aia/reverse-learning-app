import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import StudyRoom from './pages/StudyRoom'
import Dashboard from './pages/Dashboard'
import SyllabusTracker from './pages/SyllabusTracker'
import StudyHistory from './pages/StudyHistory'
import InsightsDashboard from './pages/InsightsDashboard'
import AchievementsPage from './pages/AchievementsPage'
import AchievementNotification from './components/AchievementNotification'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import LoginPage from './pages/LoginPage'
import SignupPage from './pages/SignupPage'
import MockInterview from './pages/MockInterview'
import KnowledgeGaps from './pages/KnowledgeGaps'
import LearningPath from './pages/LearningPath'
import EvaluationsHistory from './pages/EvaluationsHistory'
import SmartRevision from './pages/SmartRevision'
import ResumeIntelligence from './pages/ResumeIntelligence'
import CommunicationCoach from './pages/CommunicationCoach'

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col font-sans relative">
          <Navbar />
          <AchievementNotification />
          <main className="flex-1 flex flex-col relative overflow-x-hidden">
            <Routes>
              {/* Public Routes */}
              <Route path="/login" element={<LoginPage />} />
              <Route path="/signup" element={<SignupPage />} />
              
              {/* Protected Routes */}
              <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
              <Route path="/resume" element={<ProtectedRoute><ResumeIntelligence /></ProtectedRoute>} />
              <Route path="/resume-intelligence" element={<ProtectedRoute><ResumeIntelligence /></ProtectedRoute>} />
              <Route path="/revision" element={<ProtectedRoute><SmartRevision /></ProtectedRoute>} />

              <Route path="/study" element={<ProtectedRoute><StudyRoom /></ProtectedRoute>} />

              <Route path="/interview" element={<ProtectedRoute><MockInterview /></ProtectedRoute>} />
              <Route path="/mock-interview" element={<ProtectedRoute><MockInterview /></ProtectedRoute>} />
              <Route path="/communication-coach" element={<ProtectedRoute><CommunicationCoach /></ProtectedRoute>} />
              <Route path="/syllabi" element={<ProtectedRoute><SyllabusTracker /></ProtectedRoute>} />
              <Route path="/history" element={<ProtectedRoute><StudyHistory /></ProtectedRoute>} />
              <Route path="/insights" element={<ProtectedRoute><InsightsDashboard /></ProtectedRoute>} />
              <Route path="/achievements" element={<ProtectedRoute><AchievementsPage /></ProtectedRoute>} />
              <Route path="/knowledge-gaps" element={<ProtectedRoute><KnowledgeGaps /></ProtectedRoute>} />
              <Route path="/learning-path" element={<ProtectedRoute><LearningPath /></ProtectedRoute>} />
              <Route path="/learning-roadmap" element={<ProtectedRoute><LearningPath /></ProtectedRoute>} />
              <Route path="/evaluations" element={<ProtectedRoute><EvaluationsHistory /></ProtectedRoute>} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
