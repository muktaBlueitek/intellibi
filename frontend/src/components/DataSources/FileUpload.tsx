import React, { useState, useRef } from 'react'
import { datasourceService } from '../../services/api/datasourceService'
import './FileUpload.css'

interface FileUploadProps {
  onUploadSuccess: (datasource: any) => void
  onCancel: () => void
}

const FileUpload: React.FC<FileUploadProps> = ({ onUploadSuccess, onCancel }) => {
  const [file, setFile] = useState<File | null>(null)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [cleanData, setCleanData] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [preview, setPreview] = useState<any>(null)
  const [previewing, setPreviewing] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (!selectedFile) return

    const validTypes = ['.csv', '.xlsx', '.xls']
    const fileExt = selectedFile.name.toLowerCase().substring(selectedFile.name.lastIndexOf('.'))
    
    if (!validTypes.includes(fileExt)) {
      alert('Please select a CSV or Excel file (.csv, .xlsx, .xls)')
      return
    }

    setFile(selectedFile)
    setName(selectedFile.name.substring(0, selectedFile.name.lastIndexOf('.')))
    handlePreview(selectedFile)
  }

  const handlePreview = async (fileToPreview?: File) => {
    const fileToUse = fileToPreview || file
    if (!fileToUse) return

    setPreviewing(true)
    try {
      const previewData = await datasourceService.previewFile(fileToUse, cleanData, 10)
      setPreview(previewData)
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to preview file')
    } finally {
      setPreviewing(false)
    }
  }

  const handleUpload = async () => {
    if (!file) {
      alert('Please select a file')
      return
    }

    setUploading(true)
    setProgress(0)

    try {
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + 10
        })
      }, 200)

      const datasource = await datasourceService.uploadFile(
        file,
        name || undefined,
        description || undefined,
        cleanData
      )

      clearInterval(progressInterval)
      setProgress(100)
      
      setTimeout(() => {
        onUploadSuccess(datasource)
      }, 500)
    } catch (error: any) {
      setUploading(false)
      setProgress(0)
      alert(error.response?.data?.detail || 'Failed to upload file')
    }
  }

  return (
    <div className="file-upload">
      <h2>Upload File</h2>

      <div className="upload-section">
        <div className="file-input-wrapper">
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv,.xlsx,.xls"
            onChange={handleFileSelect}
            className="file-input"
            disabled={uploading}
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="file-select-btn"
            disabled={uploading}
          >
            {file ? file.name : 'Select File'}
          </button>
        </div>

        {file && (
          <div className="file-info">
            <p><strong>File:</strong> {file.name}</p>
            <p><strong>Size:</strong> {(file.size / 1024).toFixed(2)} KB</p>
          </div>
        )}
      </div>

      <div className="form-group">
        <label>Data Source Name</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Enter name for this data source"
          disabled={uploading}
        />
      </div>

      <div className="form-group">
        <label>Description (Optional)</label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Enter description"
          rows={3}
          disabled={uploading}
        />
      </div>

      <div className="form-group">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={cleanData}
            onChange={(e) => setCleanData(e.target.checked)}
            disabled={uploading}
          />
          Clean data (remove empty rows, normalize formats)
        </label>
      </div>

      {file && !preview && (
        <button
          type="button"
          onClick={() => handlePreview()}
          className="preview-btn"
          disabled={uploading || previewing}
        >
          {previewing ? 'Loading Preview...' : 'Preview File'}
        </button>
      )}

      {preview && (
        <div className="preview-section">
          <h3>Preview</h3>
          <div className="preview-info">
            <p><strong>Columns:</strong> {preview.preview?.columns?.length ?? preview.metadata?.columns?.length ?? 0}</p>
            <p><strong>Rows:</strong> {preview.preview?.total_rows ?? preview.metadata?.row_count ?? 0}</p>
          </div>
          {preview.preview?.data != null && (
            <div className="preview-table">
              <table>
                <thead>
                  <tr>
                    {(preview.preview.columns ?? preview.metadata?.columns ?? []).map((col: string) => (
                      <th key={col}>{col}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {preview.preview.data.slice(0, 10).map((row: any, idx: number) => (
                    <tr key={idx}>
                      {(preview.preview.columns ?? Object.keys(row)).map((col: string, colIdx: number) => (
                        <td key={colIdx}>{String(row[col] ?? '')}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {uploading && (
        <div className="upload-progress">
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p>Uploading... {progress}%</p>
        </div>
      )}

      <div className="upload-actions">
        <button
          type="button"
          onClick={onCancel}
          className="cancel-btn"
          disabled={uploading}
        >
          Cancel
        </button>
        <button
          type="button"
          onClick={handleUpload}
          className="upload-btn"
          disabled={!file || uploading}
        >
          {uploading ? 'Uploading...' : 'Upload'}
        </button>
      </div>
    </div>
  )
}

export default FileUpload
