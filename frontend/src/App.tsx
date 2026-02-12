import { Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider } from './components/Common/ThemeProvider'
import Layout from './components/Common/Layout'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ProfilePage from './pages/ProfilePage'
import DashboardPage from './pages/DashboardPage'
import DashboardsListPage from './pages/DashboardsListPage'
import DataSourcesPage from './pages/DataSourcesPage'
import ChatbotPage from './pages/ChatbotPage'
import ProtectedRoute from './components/Common/ProtectedRoute'

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
          <Route index element={<HomePage />} />
          <Route path="profile" element={<ProfilePage />} />
          <Route path="dashboards" element={<DashboardsListPage />} />
          <Route path="dashboards/:id" element={<DashboardPage />} />
          <Route path="datasources" element={<DataSourcesPage />} />
          <Route path="chatbot" element={<ChatbotPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </ThemeProvider>
  )
}

export default App
