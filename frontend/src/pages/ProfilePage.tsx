import { useEffect } from 'react'
import { useAppDispatch, useAppSelector } from '../hooks/redux'
import { fetchCurrentUser } from '../store/slices/userSlice'
import { logout } from '../store/slices/authSlice'
import { clearUser } from '../store/slices/userSlice'
import { useNavigate } from 'react-router-dom'
import './ProfilePage.css'

const ProfilePage = () => {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const { currentUser, loading } = useAppSelector((state) => state.user)
  const { isAuthenticated } = useAppSelector((state) => state.auth)

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

  if (loading) {
    return (
      <div className="profile-page">
        <div className="loading">Loading profile...</div>
      </div>
    )
  }

  if (!currentUser) {
    return (
      <div className="profile-page">
        <div className="error">Failed to load user profile</div>
      </div>
    )
  }

  return (
    <div className="profile-page">
      <div className="profile-card">
        <h1>User Profile</h1>
        
        <div className="profile-info">
          <div className="info-row">
            <span className="label">Username:</span>
            <span className="value">{currentUser.username}</span>
          </div>
          
          <div className="info-row">
            <span className="label">Email:</span>
            <span className="value">{currentUser.email}</span>
          </div>
          
          {currentUser.full_name && (
            <div className="info-row">
              <span className="label">Full Name:</span>
              <span className="value">{currentUser.full_name}</span>
            </div>
          )}
          
          <div className="info-row">
            <span className="label">Role:</span>
            <span className="value role-badge">{currentUser.role}</span>
          </div>
          
          <div className="info-row">
            <span className="label">Status:</span>
            <span className={`value status-badge ${currentUser.is_active ? 'active' : 'inactive'}`}>
              {currentUser.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>
          
          <div className="info-row">
            <span className="label">Member Since:</span>
            <span className="value">
              {new Date(currentUser.created_at).toLocaleDateString()}
            </span>
          </div>
        </div>

        <div className="profile-actions">
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </div>
      </div>
    </div>
  )
}

export default ProfilePage
