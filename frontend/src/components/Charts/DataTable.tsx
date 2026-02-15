import React, { useState, useMemo } from 'react'
import { ChartData } from '../../types/chart'
import './DataTable.css'

interface DataTableProps {
  data: ChartData[]
  columns?: string[]
  config?: {
    title?: string
    pageSize?: number
    sortable?: boolean
    searchable?: boolean
  }
}

const DataTable: React.FC<DataTableProps> = ({ data, columns, config = {} }) => {
  const [currentPage, setCurrentPage] = useState(1)
  const [sortColumn, setSortColumn] = useState<string | null>(null)
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc')
  const [searchTerm, setSearchTerm] = useState('')
  
  const pageSize = config.pageSize || 10
  const sortable = config.sortable !== false
  const searchable = config.searchable !== false

  // Get columns from data if not provided
  const tableColumns = useMemo(() => {
    if (columns && columns.length > 0) {
      return columns
    }
    if (data.length > 0) {
      return Object.keys(data[0])
    }
    return []
  }, [columns, data])

  // Filter and sort data
  const processedData = useMemo(() => {
    let result = [...data]

    // Apply search filter
    if (searchable && searchTerm) {
      result = result.filter(row =>
        tableColumns.some(col => {
          const value = row[col]
          return value !== null && value !== undefined && 
                 String(value).toLowerCase().includes(searchTerm.toLowerCase())
        })
      )
    }

    // Apply sorting
    if (sortable && sortColumn) {
      result.sort((a, b) => {
        const aVal = a[sortColumn]
        const bVal = b[sortColumn]
        
        if (aVal === null || aVal === undefined) return 1
        if (bVal === null || bVal === undefined) return -1
        
        const comparison = aVal < bVal ? -1 : aVal > bVal ? 1 : 0
        return sortDirection === 'asc' ? comparison : -comparison
      })
    }

    return result
  }, [data, searchTerm, sortColumn, sortDirection, tableColumns, sortable, searchable])

  // Paginate data
  const paginatedData = useMemo(() => {
    const startIndex = (currentPage - 1) * pageSize
    return processedData.slice(startIndex, startIndex + pageSize)
  }, [processedData, currentPage, pageSize])

  const totalPages = Math.ceil(processedData.length / pageSize)

  const handleSort = (column: string) => {
    if (!sortable) return
    
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortColumn(column)
      setSortDirection('asc')
    }
  }

  if (!data || data.length === 0) {
    return (
      <div className="data-table empty">
        <p>No data available</p>
      </div>
    )
  }

  return (
    <div className="data-table">
      {config.title && <h3 className="table-title">{config.title}</h3>}
      
      {searchable && (
        <div className="table-search">
          <input
            type="text"
            placeholder="Search..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value)
              setCurrentPage(1)
            }}
            className="search-input"
          />
        </div>
      )}

      <div className="table-container">
        <table>
          <thead>
            <tr>
              {tableColumns.map((col) => (
                <th
                  key={col}
                  onClick={() => handleSort(col)}
                  className={sortable ? 'sortable' : ''}
                >
                  {col}
                  {sortable && sortColumn === col && (
                    <span className="sort-indicator">
                      {sortDirection === 'asc' ? ' ↑' : ' ↓'}
                    </span>
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paginatedData.map((row, index) => (
              <tr key={index}>
                {tableColumns.map((col) => (
                  <td key={col}>
                    {row[col] !== null && row[col] !== undefined 
                      ? String(row[col])
                      : '-'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="table-pagination">
          <button
            onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
            disabled={currentPage === 1}
            className="pagination-btn"
          >
            Previous
          </button>
          <span className="pagination-info">
            Page {currentPage} of {totalPages} ({processedData.length} total rows)
          </span>
          <button
            onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
            disabled={currentPage === totalPages}
            className="pagination-btn"
          >
            Next
          </button>
        </div>
      )}
    </div>
  )
}

export default DataTable
