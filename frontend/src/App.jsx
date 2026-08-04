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

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col font-sans relative">
        <Navbar />
        <AchievementNotification />
        <main className="flex-1 flex flex-col relative overflow-x-hidden">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/study" element={<StudyRoom />} />
            <Route path="/syllabi" element={<SyllabusTracker />} />
            <Route path="/history" element={<StudyHistory />} />
            <Route path="/insights" element={<InsightsDashboard />} />
            <Route path="/achievements" element={<AchievementsPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
