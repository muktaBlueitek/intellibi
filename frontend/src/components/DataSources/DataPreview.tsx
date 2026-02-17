import React from 'react'
import { ChartData } from '../../types/chart'
import DataTable from '../Charts/DataTable'
import './DataPreview.css'

interface DataPreviewProps {
  data: ChartData[]
  columns: string[]
  metadata?: {
    row_count?: number
    columns?: string[]
    file_name?: string
    file_size?: number
  }
  onClose?: () => void
}

const DataPreview: React.FC<DataPreviewProps> = ({ data, columns, metadata, onClose }) => {
  if (!data || data.length === 0) {
    return (
      <div className="data-preview empty">
        <p>No data to preview</p>
        {onClose && (
          <button onClick={onClose} className="close-btn">
            Close
          </button>
        )}
      </div>
    )
  }

  return (
    <div className="data-preview">
      {onClose && (
        <div className="preview-header">
          <h3>Data Preview</h3>
          <button onClick={onClose} className="close-btn">
            ×
          </button>
        </div>
      )}
      
      {metadata && (
        <div className="preview-metadata">
          {metadata.file_name && (
            <p><strong>File:</strong> {metadata.file_name}</p>
          )}
          {metadata.file_size && (
            <p><strong>Size:</strong> {(metadata.file_size / 1024).toFixed(2)} KB</p>
          )}
          {metadata.row_count !== undefined && (
            <p><strong>Rows:</strong> {metadata.row_count.toLocaleString()}</p>
          )}
          {columns.length > 0 && (
            <p><strong>Columns:</strong> {columns.length}</p>
          )}
        </div>
      )}

      <div className="preview-content">
        <DataTable
          data={data}
          columns={columns}
          config={{
            pageSize: 20,
            sortable: true,
            searchable: true,
          }}
        />
      </div>
    </div>
  )
}

export default DataPreview
