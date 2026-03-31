import { useEffect, useState, useCallback, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Layout } from 'react-grid-layout'
import { useAppDispatch, useAppSelector } from '../hooks/redux'
import { dashboardService } from '../services/api/dashboardService'
import { widgetService } from '../services/api/widgetService'
import { Widget, WidgetType } from '../types/widget'
import { setCurrentDashboard, setLoading, setError } from '../store/slices/dashboardSlice'
import { useWebSocket } from '../hooks/useWebSocket'
import DashboardGrid from '../components/Dashboard/DashboardGrid'
import { exportElementToPdf } from '../utils/exportDashboardToPdf'
import './DashboardPage.css'

const DashboardPage = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const dispatch = useAppDispatch()
  const { currentDashboard, loading } = useAppSelector((state) => state.dashboard)
  const [widgets, setWidgets] = useState<Widget[]>([])
  const [isSaving, setIsSaving] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [isExportingPdf, setIsExportingPdf] = useState(false)
  const [showAddWidgetModal, setShowAddWidgetModal] = useState(false)
  const [newWidgetName, setNewWidgetName] = useState('')
  const [newWidgetDescription, setNewWidgetDescription] = useState('')
  const [newWidgetType, setNewWidgetType] = useState<WidgetType>('text')
  const [creatingWidget, setCreatingWidget] = useState(false)
  const pdfExportRef = useRef<HTMLDivElement>(null)
  const { client, subscribe, unsubscribe, isConnected } = useWebSocket()

  useEffect(() => {
    if (id) {
      loadDashboard(parseInt(id))
    }
  }, [id])

  // WebSocket real-time updates
  useEffect(() => {
    if (!id || !client.isConnected()) return

    const dashboardId = parseInt(id)
    client.subscribeToDashboard(dashboardId)

    const handleDashboardUpdate = (message: any) => {
      if (message.update_type === 'dashboard_updated' && message.data) {
        dispatch(setCurrentDashboard(message.data))
      } else if (message.update_type === 'layout_change' && message.data?.layout) {
        // Update layout if we're not currently editing
        if (!isEditing && currentDashboard) {
          dispatch(setCurrentDashboard({ ...currentDashboard, layout_config: message.data.layout }))
        }
      } else if (message.update_type === 'widget_update' && message.data?.widget_data) {
        // Update widget data
        setWidgets((prev) =>
          prev.map((w) =>
            w.id === message.data.widget_id ? { ...w, ...message.data.widget_data } : w
          )
        )
      } else if (message.update_type === 'collaborator_update') {
        // Show collaborator activity (could show a notification)
        console.log('Collaborator update:', message.data)
      }
    }

    subscribe('dashboard_update', handleDashboardUpdate)

    return () => {
      client.unsubscribeFromDashboard(dashboardId)
      unsubscribe('dashboard_update')
    }
  }, [id, client, subscribe, unsubscribe, isConnected, isEditing, currentDashboard, dispatch])

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
    setNewWidgetName('')
    setNewWidgetDescription('')
    setNewWidgetType('text')
    setShowAddWidgetModal(true)
  }

  const handleCreateWidget = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!currentDashboard || !newWidgetName.trim()) return

    const nextY = widgets.reduce(
      (max, w) => Math.max(max, w.position_y + w.height),
      0
    )

    setCreatingWidget(true)
    try {
      const created = await widgetService.createWidget({
        dashboard_id: currentDashboard.id,
        name: newWidgetName.trim(),
        type: newWidgetType,
        description: newWidgetDescription.trim() || undefined,
        position_x: 0,
        position_y: nextY,
        width: 4,
        height: newWidgetType === 'text' ? 2 : 3,
      })
      setWidgets((prev) => [...prev, created])
      setShowAddWidgetModal(false)
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to create widget')
    } finally {
      setCreatingWidget(false)
    }
  }

  const handleExportPdf = async () => {
    if (!pdfExportRef.current || !currentDashboard) return
    if (widgets.length === 0) {
      alert('Add at least one widget before exporting to PDF.')
      return
    }
    setIsExportingPdf(true)
    try {
      const safeName = currentDashboard.name.replace(/[^a-z0-9-_]+/gi, '_').slice(0, 80) || 'dashboard'
      await exportElementToPdf(pdfExportRef.current, `${safeName}_${new Date().toISOString().slice(0, 10)}.pdf`)
    } catch (e) {
      console.error(e)
      alert('Failed to export PDF. Try again or use a shorter dashboard name.')
    } finally {
      setIsExportingPdf(false)
    }
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
            type="button"
            className="export-pdf-btn"
            onClick={handleExportPdf}
            disabled={isExportingPdf || widgets.length === 0}
            title={widgets.length === 0 ? 'Add widgets to export' : 'Download dashboard as PDF'}
          >
            {isExportingPdf ? 'Exporting…' : 'Export as PDF'}
          </button>
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
            <button type="button" className="add-widget-btn" onClick={handleAddWidget}>
              + Add Your First Widget
            </button>
          )}
        </div>
      ) : (
        <div ref={pdfExportRef} className="dashboard-pdf-capture">
          <DashboardGrid
            widgets={widgets}
            onLayoutChange={handleLayoutChange}
            onWidgetUpdate={handleWidgetUpdate}
            onWidgetDelete={handleWidgetDelete}
            isEditable={isEditing}
          />
        </div>
      )}

      {showAddWidgetModal && (
        <div
          className="dashboard-modal-overlay"
          role="presentation"
          onClick={() => !creatingWidget && setShowAddWidgetModal(false)}
        >
          <div
            className="dashboard-modal-content"
            role="dialog"
            aria-labelledby="add-widget-title"
            onClick={(ev) => ev.stopPropagation()}
          >
            <h2 id="add-widget-title">Add Widget</h2>
            <form onSubmit={handleCreateWidget}>
              <div className="form-group">
                <label htmlFor="new-widget-name">Name</label>
                <input
                  id="new-widget-name"
                  type="text"
                  value={newWidgetName}
                  onChange={(e) => setNewWidgetName(e.target.value)}
                  placeholder="Widget title"
                  required
                  autoFocus
                  disabled={creatingWidget}
                />
              </div>
              <div className="form-group">
                <label htmlFor="new-widget-type">Type</label>
                <select
                  id="new-widget-type"
                  value={newWidgetType}
                  onChange={(e) => setNewWidgetType(e.target.value as WidgetType)}
                  disabled={creatingWidget}
                >
                  <option value="text">Text</option>
                  <option value="metric">Metric</option>
                </select>
              </div>
              <div className="form-group">
                <label htmlFor="new-widget-desc">Description (optional)</label>
                <textarea
                  id="new-widget-desc"
                  value={newWidgetDescription}
                  onChange={(e) => setNewWidgetDescription(e.target.value)}
                  placeholder="Shown on text widgets"
                  rows={3}
                  disabled={creatingWidget}
                />
              </div>
              <div className="modal-actions">
                <button
                  type="button"
                  className="cancel-btn"
                  disabled={creatingWidget}
                  onClick={() => setShowAddWidgetModal(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="create-btn" disabled={creatingWidget}>
                  {creatingWidget ? 'Adding…' : 'Add Widget'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default DashboardPage
