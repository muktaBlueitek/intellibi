import { useEffect, useState } from 'react'
import { useAppDispatch, useAppSelector } from '../hooks/redux'
import { datasourceService } from '../services/api/datasourceService'
import { DataSource } from '../types/datasource'
import { setDataSources, setLoading, setError } from '../store/slices/datasourceSlice'
import FileUpload from '../components/DataSources/FileUpload'
import DatabaseConnectionForm from '../components/DataSources/DatabaseConnectionForm'
import DataPreview from '../components/DataSources/DataPreview'
import { ChartData } from '../types/chart'
import './DataSourcesPage.css'

type ViewMode = 'list' | 'upload' | 'database' | 'preview'

const DataSourcesPage = () => {
  const dispatch = useAppDispatch()
  const { datasources, loading, error } = useAppSelector((state) => state.datasource)
  const [viewMode, setViewMode] = useState<ViewMode>('list')
  const [previewData, setPreviewData] = useState<{ data: ChartData[]; columns: string[]; metadata?: any } | null>(null)

  useEffect(() => {
    loadDataSources()
  }, [])

  const loadDataSources = async () => {
    try {
      dispatch(setLoading(true))
      const data = await datasourceService.getDataSources()
      dispatch(setDataSources(data))
    } catch (err: any) {
      dispatch(setError(err.response?.data?.detail || 'Failed to load data sources'))
    } finally {
      dispatch(setLoading(false))
    }
  }

  const handleUploadSuccess = () => {
    setViewMode('list')
    loadDataSources()
  }

  const handleDatabaseSuccess = () => {
    setViewMode('list')
    loadDataSources()
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this data source?')) return

    try {
      await datasourceService.deleteDataSource(id)
      loadDataSources()
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete data source')
    }
  }

  const handleToggleActive = async (datasource: DataSource) => {
    try {
      await datasourceService.updateDataSource(datasource.id, {
        is_active: !datasource.is_active,
      })
      loadDataSources()
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to update data source')
    }
  }

  const handlePreview = async (datasource: DataSource) => {
    try {
      // For file datasources, get preview from connection_config
      if (datasource.type === 'file' && datasource.connection_config?.preview) {
        const preview = datasource.connection_config.preview
        const columns = datasource.connection_config.metadata?.columns || []
        setPreviewData({
          data: preview,
          columns,
          metadata: {
            file_name: datasource.file_name,
            file_size: datasource.file_size,
            row_count: datasource.connection_config.metadata?.row_count,
          },
        })
        setViewMode('preview')
      } else {
        // For database datasources, would need to execute a query
        alert('Preview for database connections will be available after connecting')
      }
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to preview data source')
    }
  }

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      file: 'File',
      postgresql: 'PostgreSQL',
      mysql: 'MySQL',
      mongodb: 'MongoDB',
      rest_api: 'REST API',
    }
    return labels[type] || type
  }

  if (loading && datasources.length === 0) {
    return (
      <div className="datasources-page">
        <div className="loading">Loading data sources...</div>
      </div>
    )
  }

  if (viewMode === 'upload') {
    return (
      <div className="datasources-page">
        <FileUpload
          onUploadSuccess={handleUploadSuccess}
          onCancel={() => setViewMode('list')}
        />
      </div>
    )
  }

  if (viewMode === 'database') {
    return (
      <div className="datasources-page">
        <DatabaseConnectionForm
          onConnectionSuccess={handleDatabaseSuccess}
          onCancel={() => setViewMode('list')}
        />
      </div>
    )
  }

  if (viewMode === 'preview' && previewData) {
    return (
      <div className="datasources-page">
        <DataPreview
          data={previewData.data}
          columns={previewData.columns}
          metadata={previewData.metadata}
          onClose={() => setViewMode('list')}
        />
      </div>
    )
  }

  return (
    <div className="datasources-page">
      <div className="datasources-header">
        <h1>Data Sources</h1>
        <div className="header-actions">
          <button
            className="action-btn primary"
            onClick={() => setViewMode('upload')}
          >
            + Upload File
          </button>
          <button
            className="action-btn primary"
            onClick={() => setViewMode('database')}
          >
            + Database Connection
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {datasources.length === 0 ? (
        <div className="empty-state">
          <p>No data sources yet. Upload a file or create a database connection to get started!</p>
        </div>
      ) : (
        <div className="datasources-table">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Description</th>
                <th>Status</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {datasources.map((ds) => (
                <tr key={ds.id}>
                  <td>
                    <strong>{ds.name}</strong>
                    {ds.file_name && (
                      <div className="file-name">{ds.file_name}</div>
                    )}
                    {ds.host && (
                      <div className="connection-info">
                        {ds.host}:{ds.port}/{ds.database_name}
                      </div>
                    )}
                  </td>
                  <td>
                    <span className={`type-badge ${ds.type}`}>
                      {getTypeLabel(ds.type)}
                    </span>
                  </td>
                  <td>{ds.description || '-'}</td>
                  <td>
                    <button
                      className={`status-btn ${ds.is_active ? 'active' : 'inactive'}`}
                      onClick={() => handleToggleActive(ds)}
                    >
                      {ds.is_active ? 'Active' : 'Inactive'}
                    </button>
                  </td>
                  <td>{new Date(ds.created_at).toLocaleDateString()}</td>
                  <td>
                    <div className="action-buttons">
                      {ds.type === 'file' && (
                        <button
                          className="action-btn small"
                          onClick={() => handlePreview(ds)}
                          title="Preview"
                        >
                          👁️
                        </button>
                      )}
                      <button
                        className="action-btn small delete"
                        onClick={() => handleDelete(ds.id)}
                        title="Delete"
                      >
                        🗑️
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default DataSourcesPage
