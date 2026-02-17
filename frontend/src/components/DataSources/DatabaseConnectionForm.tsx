import React, { useState } from 'react'
import { datasourceService } from '../../services/api/datasourceService'
import './DatabaseConnectionForm.css'

interface DatabaseConnectionFormProps {
  onConnectionSuccess: (datasource: any) => void
  onCancel: () => void
}

const DatabaseConnectionForm: React.FC<DatabaseConnectionFormProps> = ({
  onConnectionSuccess,
  onCancel,
}) => {
  const [formData, setFormData] = useState({
    type: 'postgresql',
    name: '',
    description: '',
    host: '',
    port: 5432,
    database_name: '',
    username: '',
    password: '',
  })
  const [testing, setTesting] = useState(false)
  const [creating, setCreating] = useState(false)
  const [testResult, setTestResult] = useState<{ success: boolean; message?: string } | null>(null)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: name === 'port' ? parseInt(value) || 0 : value,
    }))
    setTestResult(null)
  }

  const handleTestConnection = async () => {
    if (!formData.host || !formData.database_name || !formData.username || !formData.password) {
      alert('Please fill in all required fields')
      return
    }

    setTesting(true)
    setTestResult(null)

    try {
      const result = await datasourceService.testDatabaseConnection({
        type: formData.type,
        host: formData.host,
        port: formData.port,
        database_name: formData.database_name,
        username: formData.username,
        password: formData.password,
      })
      setTestResult(result)
    } catch (error: any) {
      setTestResult({
        success: false,
        message: error.response?.data?.detail || 'Connection test failed',
      })
    } finally {
      setTesting(false)
    }
  }

  const handleCreate = async () => {
    if (!formData.name || !formData.host || !formData.database_name || !formData.username || !formData.password) {
      alert('Please fill in all required fields')
      return
    }

    if (!testResult?.success) {
      alert('Please test the connection first')
      return
    }

    setCreating(true)

    try {
      const datasource = await datasourceService.createDatabaseConnection(
        {
          type: formData.type,
          host: formData.host,
          port: formData.port,
          database_name: formData.database_name,
          username: formData.username,
          password: formData.password,
        },
        formData.name,
        formData.description || undefined
      )
      onConnectionSuccess(datasource)
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to create database connection')
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="database-connection-form">
      <h2>Database Connection</h2>

      <div className="form-group">
        <label>Connection Name *</label>
        <input
          type="text"
          name="name"
          value={formData.name}
          onChange={handleChange}
          placeholder="Enter a name for this connection"
          disabled={creating}
        />
      </div>

      <div className="form-group">
        <label>Description (Optional)</label>
        <textarea
          name="description"
          value={formData.description}
          onChange={handleChange}
          placeholder="Enter description"
          rows={2}
          disabled={creating}
        />
      </div>

      <div className="form-group">
        <label>Database Type *</label>
        <select
          name="type"
          value={formData.type}
          onChange={handleChange}
          disabled={creating}
        >
          <option value="postgresql">PostgreSQL</option>
          <option value="mysql">MySQL</option>
        </select>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>Host *</label>
          <input
            type="text"
            name="host"
            value={formData.host}
            onChange={handleChange}
            placeholder="localhost"
            disabled={creating}
          />
        </div>

        <div className="form-group">
          <label>Port *</label>
          <input
            type="number"
            name="port"
            value={formData.port}
            onChange={handleChange}
            placeholder={formData.type === 'postgresql' ? '5432' : '3306'}
            disabled={creating}
          />
        </div>
      </div>

      <div className="form-group">
        <label>Database Name *</label>
        <input
          type="text"
          name="database_name"
          value={formData.database_name}
          onChange={handleChange}
          placeholder="Enter database name"
          disabled={creating}
        />
      </div>

      <div className="form-group">
        <label>Username *</label>
        <input
          type="text"
          name="username"
          value={formData.username}
          onChange={handleChange}
          placeholder="Enter username"
          disabled={creating}
        />
      </div>

      <div className="form-group">
        <label>Password *</label>
        <input
          type="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          placeholder="Enter password"
          disabled={creating}
        />
      </div>

      {testResult && (
        <div className={`test-result ${testResult.success ? 'success' : 'error'}`}>
          {testResult.success ? (
            <p>✓ Connection successful!</p>
          ) : (
            <p>✗ Connection failed: {testResult.message}</p>
          )}
        </div>
      )}

      <div className="form-actions">
        <button
          type="button"
          onClick={handleTestConnection}
          className="test-btn"
          disabled={testing || creating || !formData.host || !formData.database_name}
        >
          {testing ? 'Testing...' : 'Test Connection'}
        </button>
      </div>

      <div className="form-actions">
        <button
          type="button"
          onClick={onCancel}
          className="cancel-btn"
          disabled={creating}
        >
          Cancel
        </button>
        <button
          type="button"
          onClick={handleCreate}
          className="create-btn"
          disabled={creating || !testResult?.success}
        >
          {creating ? 'Creating...' : 'Create Connection'}
        </button>
      </div>
    </div>
  )
}

export default DatabaseConnectionForm
