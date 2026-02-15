import { ChartData } from '../types/chart'

/**
 * Export chart data to CSV
 */
export const exportToCSV = (data: ChartData[], filename: string = 'chart-data'): void => {
  if (!data || data.length === 0) {
    alert('No data to export')
    return
  }

  const columns = Object.keys(data[0])
  const csvContent = [
    columns.join(','),
    ...data.map(row => 
      columns.map(col => {
        const value = row[col]
        // Escape commas and quotes in CSV
        if (value === null || value === undefined) return ''
        const stringValue = String(value)
        if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
          return `"${stringValue.replace(/"/g, '""')}"`
        }
        return stringValue
      }).join(',')
    )
  ].join('\n')

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  
  link.setAttribute('href', url)
  link.setAttribute('download', `${filename}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

/**
 * Export chart as PNG image
 */
export const exportChartToPNG = (chartId: string, filename: string = 'chart'): void => {
  const chartElement = document.getElementById(chartId)
  if (!chartElement) {
    alert('Chart element not found')
    return
  }

  // Use html2canvas if available, otherwise fallback to basic screenshot
  import('html2canvas').then(html2canvas => {
    html2canvas.default(chartElement, {
      backgroundColor: '#ffffff',
      scale: 2,
    }).then(canvas => {
      const link = document.createElement('a')
      link.download = `${filename}.png`
      link.href = canvas.toDataURL('image/png')
      link.click()
    }).catch(err => {
      console.error('Failed to export chart:', err)
      alert('Failed to export chart as image')
    })
  }).catch(() => {
    // Fallback: try to use canvas if it's a canvas element
    if (chartElement instanceof HTMLCanvasElement) {
      const link = document.createElement('a')
      link.download = `${filename}.png`
      link.href = chartElement.toDataURL('image/png')
      link.click()
    } else {
      alert('Chart export not supported. Please install html2canvas for full export functionality.')
    }
  })
}

/**
 * Export table data to Excel (CSV format)
 */
export const exportTableToExcel = (data: ChartData[], filename: string = 'table-data'): void => {
  exportToCSV(data, filename)
}
