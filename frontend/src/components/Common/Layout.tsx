import { Outlet, Link, useNavigate } from 'react-router-dom'
import { useEffect } from 'react'
import { useAppDispatch, useAppSelector } from '../../hooks/redux'
import { logout } from '../../store/slices/authSlice'
import { clearUser, fetchCurrentUser } from '../../store/slices/userSlice'
import './Layout.css'

const Layout = () => {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const { isAuthenticated } = useAppSelector((state) => state.auth)
  const { currentUser } = useAppSelector((state) => state.user)

  useEffect(() => {
    if (isAuthenticated && !currentUser) {
      dispatch(fetchCurrentUser())
    }
  }, [dispatch, isAuthenticated, currentUser])

  const handleLogout = () => {
    dispatch(logout())
    dispatch(clearUser())
    navigate('/login')
  }

  return (
    <div className="layout">
      <header className="header">
        <div className="header-content">
          <Link to="/" className="logo">
            <h1>IntelliBI</h1>
          </Link>
          <nav className="nav">
            <Link to="/dashboards">Dashboards</Link>
            <Link to="/datasources">Data Sources</Link>
            <Link to="/chatbot">Chatbot</Link>
          </nav>
          <div className="header-actions">
            {currentUser && (
              <Link to="/profile" className="user-name">
                {currentUser.username}
              </Link>
            )}
            {isAuthenticated && (
              <button onClick={handleLogout} className="logout-btn">
                Logout
              </button>
            )}
          </div>
        </div>
      </header>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}

export default Layout
