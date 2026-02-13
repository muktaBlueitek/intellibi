import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAppDispatch, useAppSelector } from '../hooks/redux'
import { dashboardService } from '../services/api/dashboardService'
import { Dashboard } from '../types/dashboard'
import { setDashboards, setLoading, setError } from '../store/slices/dashboardSlice'
import './DashboardsListPage.css'

const DashboardsListPage = () => {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const { dashboards, loading, error } = useAppSelector((state) => state.dashboard)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newDashboardName, setNewDashboardName] = useState('')
  const [newDashboardDesc, setNewDashboardDesc] = useState('')

  useEffect(() => {
    loadDashboards()
  }, [])

  const loadDashboards = async () => {
    try {
      dispatch(setLoading(true))
      const data = await dashboardService.getDashboards()
      dispatch(setDashboards(data))
    } catch (err: any) {
      dispatch(setError(err.response?.data?.detail || 'Failed to load dashboards'))
    } finally {
      dispatch(setLoading(false))
    }
  }

  const handleCreateDashboard = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newDashboardName.trim()) return

    try {
      const dashboard = await dashboardService.createDashboard({
        name: newDashboardName,
        description: newDashboardDesc || undefined,
      })
      navigate(`/dashboards/${dashboard.id}`)
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to create dashboard')
    }
  }

  const handleDeleteDashboard = async (id: number, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    if (!confirm('Are you sure you want to delete this dashboard?')) return

    try {
      await dashboardService.deleteDashboard(id)
      loadDashboards()
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete dashboard')
    }
  }

  if (loading) {
    return (
      <div className="dashboards-page">
        <div className="loading">Loading dashboards...</div>
      </div>
    )
  }

  return (
    <div className="dashboards-page">
      <div className="dashboards-header">
        <h1>My Dashboards</h1>
        <button
          className="create-dashboard-btn"
          onClick={() => setShowCreateModal(true)}
        >
          + Create Dashboard
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {dashboards.length === 0 ? (
        <div className="empty-state">
          <p>No dashboards yet. Create your first dashboard to get started!</p>
        </div>
      ) : (
        <div className="dashboards-grid">
          {dashboards.map((dashboard) => (
            <Link
              key={dashboard.id}
              to={`/dashboards/${dashboard.id}`}
              className="dashboard-card"
            >
              <div className="dashboard-card-header">
                <h3>{dashboard.name}</h3>
                <button
                  className="delete-btn"
                  onClick={(e) => handleDeleteDashboard(dashboard.id, e)}
                >
                  ×
                </button>
              </div>
              {dashboard.description && (
                <p className="dashboard-description">{dashboard.description}</p>
              )}
              <div className="dashboard-meta">
                <span>{dashboard.widgets?.length || 0} widgets</span>
                <span>
                  {new Date(dashboard.updated_at || dashboard.created_at).toLocaleDateString()}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}

      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Create New Dashboard</h2>
            <form onSubmit={handleCreateDashboard}>
              <div className="form-group">
                <label>Dashboard Name</label>
                <input
                  type="text"
                  value={newDashboardName}
                  onChange={(e) => setNewDashboardName(e.target.value)}
                  placeholder="Enter dashboard name"
                  required
                  autoFocus
                />
              </div>
              <div className="form-group">
                <label>Description (Optional)</label>
                <textarea
                  value={newDashboardDesc}
                  onChange={(e) => setNewDashboardDesc(e.target.value)}
                  placeholder="Enter dashboard description"
                  rows={3}
                />
              </div>
              <div className="modal-actions">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="cancel-btn"
                >
                  Cancel
                </button>
                <button type="submit" className="create-btn">
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default DashboardsListPage
