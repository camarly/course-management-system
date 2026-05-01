import { Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './components/Navbar.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'
import { useAuth } from './context/AuthContext.jsx'

import LoginPage from './pages/LoginPage.jsx'
import RegisterPage from './pages/RegisterPage.jsx'
import DashboardPage from './pages/DashboardPage.jsx'
import CoursesPage from './pages/CoursesPage.jsx'
import CoursePage from './pages/CoursePage.jsx'
import ContentPage from './pages/ContentPage.jsx'
import AssignmentsPage from './pages/AssignmentsPage.jsx'
import ForumPage from './pages/ForumPage.jsx'
import ThreadPage from './pages/ThreadPage.jsx'
import CalendarPage from './pages/CalendarPage.jsx'
import GradesPage from './pages/GradesPage.jsx'
import ReportsPage from './pages/ReportsPage.jsx'

function Unauthorised() {
  return (
    <div className="page">
      <h1>Unauthorised</h1>
      <p>You don't have permission to view that page.</p>
    </div>
  )
}

export default function App() {
  const { token } = useAuth()
  return (
    <>
      <Navbar />
      <main>
        <Routes>
          <Route path="/login" element={token ? <Navigate to="/dashboard" replace /> : <LoginPage />} />
          <Route path="/register" element={token ? <Navigate to="/dashboard" replace /> : <RegisterPage />} />
          <Route path="/unauthorised" element={<Unauthorised />} />

          <Route
            path="/dashboard"
            element={<ProtectedRoute><DashboardPage /></ProtectedRoute>}
          />
          <Route
            path="/courses"
            element={<ProtectedRoute><CoursesPage /></ProtectedRoute>}
          />
          <Route
            path="/courses/:courseId"
            element={<ProtectedRoute><CoursePage /></ProtectedRoute>}
          />
          <Route
            path="/courses/:courseId/content"
            element={<ProtectedRoute><ContentPage /></ProtectedRoute>}
          />
          <Route
            path="/courses/:courseId/assignments"
            element={<ProtectedRoute><AssignmentsPage /></ProtectedRoute>}
          />
          <Route
            path="/courses/:courseId/forums"
            element={<ProtectedRoute><ForumPage /></ProtectedRoute>}
          />
          <Route
            path="/forums/:forumId/threads/:threadId"
            element={<ProtectedRoute><ThreadPage /></ProtectedRoute>}
          />
          <Route
            path="/calendar"
            element={<ProtectedRoute><CalendarPage /></ProtectedRoute>}
          />
          <Route
            path="/grades"
            element={
              <ProtectedRoute allowedRoles={['student']}>
                <GradesPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/reports"
            element={
              <ProtectedRoute allowedRoles={['admin']}>
                <ReportsPage />
              </ProtectedRoute>
            }
          />

          <Route path="/" element={<Navigate to={token ? '/dashboard' : '/login'} replace />} />
          <Route path="*" element={<Navigate to={token ? '/dashboard' : '/login'} replace />} />
        </Routes>
      </main>
    </>
  )
}
