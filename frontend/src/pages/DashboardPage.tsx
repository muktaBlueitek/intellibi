import { useEffect, useState, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Layout } from 'react-grid-layout'
import { useAppDispatch, useAppSelector } from '../hooks/redux'
import { dashboardService } from '../services/api/dashboardService'
import { widgetService } from '../services/api/widgetService'
import { Dashboard } from '../types/dashboard'
import { Widget } from '../types/widget'
import { setCurrentDashboard, setLoading, setError } from '../store/slices/dashboardSlice'
import DashboardGrid from '../components/Dashboard/DashboardGrid'
import './DashboardPage.css'

const DashboardPage = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const dispatch = useAppDispatch()
  const { currentDashboard, loading } = useAppSelector((state) => state.dashboard)
  const [widgets, setWidgets] = useState<Widget[]>([])
  const [isSaving, setIsSaving] = useState(false)
  const [isEditing, setIsEditing] = useState(false)

  useEffect(() => {
    if (id) {
      loadDashboard(parseInt(id))
    }
  }, [id])

  const loadDashboard = async (dashboardId: number) => {
    try {
      dispatch(setLoading(true))
      const dashboard = await dashboardService.getDashboard(dashboardId)
      dispatch(setCurrentDashboard(dashboard))
      
      // Load widgets if not included in dashboard response
      if (dashboard.widgets && dashboard.widgets.length > 0) {
        setWidgets(dashboard.widgets)
      } else {
        const widgetsData = await widgetService.getWidgets(dashboardId)
        setWidgets(widgetsData)
      }
    } catch (err: any) {
      dispatch(setError(err.response?.data?.detail || 'Failed to load dashboard'))
      if (err.response?.status === 404) {
        navigate('/dashboards')
      }
    } finally {
      dispatch(setLoading(false))
    }
  }

  const handleLayoutChange = useCallback(
    async (layout: Layout[]) => {
      if (!currentDashboard || !isEditing) return

      // Debounce save
      setIsSaving(true)
      try {
        await dashboardService.updateLayout(currentDashboard.id, {
          widgets: layout.map((item) => ({
            i: item.i,
            x: item.x,
            y: item.y,
            w: item.w,
            h: item.h,
          })),
        })
      } catch (err) {
        console.error('Failed to save layout:', err)
      } finally {
        setIsSaving(false)
      }
    },
    [currentDashboard, isEditing]
  )

  const handleWidgetUpdate = useCallback(
    async (widgetId: number, updates: Partial<Widget>) => {
      try {
        await widgetService.updateWidget(widgetId, updates)
        setWidgets((prev) =>
          prev.map((w) => (w.id === widgetId ? { ...w, ...updates } : w))
        )
      } catch (err: any) {
        alert(err.response?.data?.detail || 'Failed to update widget')
      }
    },
    []
  )

  const handleWidgetDelete = useCallback(
    async (widgetId: number) => {
      try {
        await widgetService.deleteWidget(widgetId)
        setWidgets((prev) => prev.filter((w) => w.id !== widgetId))
      } catch (err: any) {
        alert(err.response?.data?.detail || 'Failed to delete widget')
      }
    },
    []
  )

  const handleAddWidget = () => {
    // Widget creation will be implemented in Day 14
    alert('Widget creation will be implemented in Day 14')
  }

  if (loading) {
    return (
      <div className="dashboard-page">
        <div className="loading">Loading dashboard...</div>
      </div>
    )
  }

  if (!currentDashboard) {
    return (
      <div className="dashboard-page">
        <div className="error">Dashboard not found</div>
      </div>
    )
  }

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <div>
          <h1>{currentDashboard.name}</h1>
          {currentDashboard.description && (
            <p className="dashboard-description">{currentDashboard.description}</p>
          )}
        </div>
        <div className="dashboard-actions">
          <button
            className={`edit-btn ${isEditing ? 'active' : ''}`}
            onClick={() => setIsEditing(!isEditing)}
          >
            {isEditing ? '✓ Done Editing' : '✏️ Edit Layout'}
          </button>
          {isEditing && (
            <button className="add-widget-btn" onClick={handleAddWidget}>
              + Add Widget
            </button>
          )}
          {isSaving && <span className="saving-indicator">Saving...</span>}
        </div>
      </div>

      {widgets.length === 0 ? (
        <div className="empty-dashboard">
          <p>This dashboard is empty.</p>
          {isEditing && (
            <button className="add-widget-btn" onClick={handleAddWidget}>
              + Add Your First Widget
            </button>
          )}
        </div>
      ) : (
        <DashboardGrid
          widgets={widgets}
          onLayoutChange={handleLayoutChange}
          onWidgetUpdate={handleWidgetUpdate}
          onWidgetDelete={handleWidgetDelete}
          isEditable={isEditing}
        />
      )}
    </div>
  )
}

export default DashboardPage
