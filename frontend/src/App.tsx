import { Routes, Route, Navigate } from 'react-router-dom'
import { lazy, Suspense } from 'react'
import { ThemeProvider } from './components/Common/ThemeProvider'
import Layout from './components/Common/Layout'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ProtectedRoute from './components/Common/ProtectedRoute'

// Lazy load pages for code splitting
const HomePage = lazy(() => import('./pages/HomePage'))
const ProfilePage = lazy(() => import('./pages/ProfilePage'))
const DashboardPage = lazy(() => import('./pages/DashboardPage'))
const DashboardsListPage = lazy(() => import('./pages/DashboardsListPage'))
const DataSourcesPage = lazy(() => import('./pages/DataSourcesPage'))
const ChatbotPage = lazy(() => import('./pages/ChatbotPage'))

const PageLoadingFallback = () => (
  <div style={{ 
    display: 'flex', 
    alignItems: 'center', 
    justifyContent: 'center', 
    minHeight: '50vh',
    color: 'var(--text-secondary)'
  }}>
    Loading...
  </div>
)

function App() {
  return (
    <ThemeProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Suspense fallback={<PageLoadingFallback />}><HomePage /></Suspense>} />
          <Route path="profile" element={<Suspense fallback={<PageLoadingFallback />}><ProfilePage /></Suspense>} />
          <Route path="dashboards" element={<Suspense fallback={<PageLoadingFallback />}><DashboardsListPage /></Suspense>} />
          <Route path="dashboards/:id" element={<Suspense fallback={<PageLoadingFallback />}><DashboardPage /></Suspense>} />
          <Route path="datasources" element={<Suspense fallback={<PageLoadingFallback />}><DataSourcesPage /></Suspense>} />
          <Route path="chatbot" element={<Suspense fallback={<PageLoadingFallback />}><ChatbotPage /></Suspense>} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </ThemeProvider>
  )
}

export default App
