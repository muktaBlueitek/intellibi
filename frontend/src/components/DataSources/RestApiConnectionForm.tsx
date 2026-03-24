import React, { useState } from 'react'
import { datasourceService } from '../../services/api/datasourceService'
import './RestApiConnectionForm.css'

interface RestApiConnectionFormProps {
  onConnectionSuccess: (datasource: any) => void
  onCancel: () => void
}

const RestApiConnectionForm: React.FC<RestApiConnectionFormProps> = ({
  onConnectionSuccess,
  onCancel,
}) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    url: '',
    auth_type: 'bearer',
    api_key: '',
    data_path: '',
  })
  const [headers, setHeaders] = useState<{ name: string; value: string }[]>([{ name: '', value: '' }])
  const [testing, setTesting] = useState(false)
  const [creating, setCreating] = useState(false)
  const [testResult, setTestResult] = useState<{ success: boolean; message?: string } | null>(null)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    setTestResult(null)
  }

  const handleHeaderChange = (index: number, field: 'name' | 'value', value: string) => {
    setHeaders(prev => {
      const next = [...prev]
      next[index] = { ...next[index], [field]: value }
      return next
    })
    setTestResult(null)
  }

  const addHeader = () => setHeaders(prev => [...prev, { name: '', value: '' }])
  const removeHeader = (index: number) => setHeaders(prev => prev.filter((_, i) => i !== index))

  const buildHeaders = (): Record<string, string> | undefined => {
    const h: Record<string, string> = {}
    headers.forEach(({ name, value }) => {
      if (name.trim()) h[name.trim()] = value
    })
    return Object.keys(h).length ? h : undefined
  }

  const handleTestConnection = async () => {
    if (!formData.url?.trim()) {
      alert('Please enter the API URL')
      return
    }

    setTesting(true)
    setTestResult(null)

    try {
      const result = await datasourceService.testRestApiConnection({
        url: formData.url.trim(),
        auth_type: formData.auth_type,
        api_key: formData.api_key || undefined,
        headers: buildHeaders(),
        data_path: formData.data_path?.trim() || undefined,
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
    if (!formData.name?.trim()) {
      alert('Please enter a connection name')
      return
    }
    if (!formData.url?.trim()) {
      alert('Please enter the API URL')
      return
    }

    if (!testResult?.success) {
      alert('Please test the connection first')
      return
    }

    setCreating(true)

    try {
      const datasource = await datasourceService.createRestApiConnection(
        {
          url: formData.url.trim(),
          auth_type: formData.auth_type,
          api_key: formData.api_key || undefined,
          headers: buildHeaders(),
          data_path: formData.data_path?.trim() || undefined,
        },
        formData.name.trim(),
        formData.description?.trim() || undefined
      )
      onConnectionSuccess(datasource)
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to create REST API connection')
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="rest-api-connection-form">
      <h2>REST API Connection</h2>

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
        <label>API URL *</label>
        <input
          type="url"
          name="url"
          value={formData.url}
          onChange={handleChange}
          placeholder="https://api.example.com/data"
          disabled={creating}
        />
      </div>

      <div className="form-group">
        <label>Data Path (Optional)</label>
        <input
          type="text"
          name="data_path"
          value={formData.data_path}
          onChange={handleChange}
          placeholder="e.g. data, results.items"
          disabled={creating}
        />
        <small>JSON path to array in response (e.g. &quot;data&quot; for &#123;&quot;data&quot;: [...]&#125;)</small>
      </div>

      <div className="form-group">
        <label>Authentication</label>
        <select
          name="auth_type"
          value={formData.auth_type}
          onChange={handleChange}
          disabled={creating}
        >
          <option value="none">None</option>
          <option value="bearer">Bearer Token</option>
          <option value="api_key">API Key</option>
        </select>
      </div>

      {(formData.auth_type === 'bearer' || formData.auth_type === 'api_key') && (
        <div className="form-group">
          <label>{formData.auth_type === 'bearer' ? 'Bearer Token' : 'API Key'} *</label>
          <input
            type="password"
            name="api_key"
            value={formData.api_key}
            onChange={handleChange}
            placeholder={formData.auth_type === 'bearer' ? 'Enter token' : 'Enter API key'}
            disabled={creating}
          />
        </div>
      )}

      <div className="form-group">
        <label>Custom Headers (Optional)</label>
        {headers.map((h, i) => (
          <div key={i} className="header-row">
            <input
              type="text"
              placeholder="Header name"
              value={h.name}
              onChange={e => handleHeaderChange(i, 'name', e.target.value)}
              disabled={creating}
            />
            <input
              type="text"
              placeholder="Value"
              value={h.value}
              onChange={e => handleHeaderChange(i, 'value', e.target.value)}
              disabled={creating}
            />
            <button
              type="button"
              onClick={() => removeHeader(i)}
              disabled={creating || headers.length <= 1}
              className="remove-header"
            >
              ×
            </button>
          </div>
        ))}
        <button type="button" onClick={addHeader} disabled={creating} className="add-header">
          + Add Header
        </button>
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
          disabled={testing || creating || !formData.url?.trim()}
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

export default RestApiConnectionForm
