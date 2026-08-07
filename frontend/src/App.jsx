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
              <Route path="/study" element={<ProtectedRoute><StudyRoom /></ProtectedRoute>} />
              <Route path="/interview" element={<ProtectedRoute><MockInterview /></ProtectedRoute>} />
              <Route path="/syllabi" element={<ProtectedRoute><SyllabusTracker /></ProtectedRoute>} />
              <Route path="/history" element={<ProtectedRoute><StudyHistory /></ProtectedRoute>} />
              <Route path="/insights" element={<ProtectedRoute><InsightsDashboard /></ProtectedRoute>} />
              <Route path="/achievements" element={<ProtectedRoute><AchievementsPage /></ProtectedRoute>} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
