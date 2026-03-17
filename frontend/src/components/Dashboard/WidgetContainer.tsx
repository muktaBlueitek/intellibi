import React, { useState } from 'react'
import { Widget } from '../../types/widget'
import { useWidgetData } from '../../hooks/useWidgetData'
import {
  LazyLineChart,
  LazyBarChart,
  LazyPieChart,
  LazyAreaChart,
  LazyHeatmap,
  LazyDataTable,
  LazyChartWrapper,
  ChartLoadingFallback,
} from '../Charts/LazyCharts'
import { exportToCSV, exportChartToPNG } from '../../utils/export'
import './WidgetContainer.css'

interface WidgetContainerProps {
  widget: Widget
  onUpdate: (updates: Partial<Widget>) => void
  onDelete: () => void
  isEditable?: boolean
}

const WidgetContainer: React.FC<WidgetContainerProps> = ({
  widget,
  onUpdate,
  onDelete,
  isEditable = true,
}) => {
  const [isEditing, setIsEditing] = useState(false)
  const { data, columns, loading, error, refetch } = useWidgetData(widget, {
    autoRefresh: widget.config?.autoRefresh || false,
    refreshInterval: widget.config?.refreshInterval || 30000,
  })

  const chartConfig = {
    title: widget.name,
    ...widget.config,
  }

  const handleExportCSV = () => {
    exportToCSV(data, widget.name)
  }

  const handleExportPNG = () => {
    exportChartToPNG(`widget-${widget.id}`, widget.name)
  }

  const renderWidgetContent = () => {
    if (loading) {
      return <div className="widget-loading">Loading...</div>
    }

    if (error) {
      return (
        <div className="widget-error">
          <p>Error: {error}</p>
          <button onClick={refetch} className="widget-retry-btn">Retry</button>
        </div>
      )
    }

    switch (widget.type) {
      case 'line_chart':
        return (
          <div id={`widget-${widget.id}`}>
            <LazyChartWrapper component={LazyLineChart} data={data} config={chartConfig} />
          </div>
        )
      case 'bar_chart':
        return (
          <div id={`widget-${widget.id}`}>
            <LazyChartWrapper component={LazyBarChart} data={data} config={chartConfig} />
          </div>
        )
      case 'pie_chart':
        return (
          <div id={`widget-${widget.id}`}>
            <LazyChartWrapper component={LazyPieChart} data={data} config={chartConfig} />
          </div>
        )
      case 'area_chart':
        return (
          <div id={`widget-${widget.id}`}>
            <LazyChartWrapper component={LazyAreaChart} data={data} config={chartConfig} />
          </div>
        )
      case 'heatmap':
        return (
          <div id={`widget-${widget.id}`}>
            <LazyChartWrapper component={LazyHeatmap} data={data} config={chartConfig} />
          </div>
        )
      case 'table':
        return (
          <LazyChartWrapper
            component={LazyDataTable}
            data={data}
            columns={columns}
            config={{ title: widget.name, ...widget.config }}
          />
        )
      case 'metric':
        // Calculate metric value from first row, first numeric column
        const rawMetric = data.length > 0 && columns.length > 0
          ? data[0][columns.find(col => {
              const val = data[0][col]
              return typeof val === 'number' || (typeof val === 'string' && !isNaN(Number(val)))
            }) || columns[0]]
          : null
        const metricValue = rawMetric != null ? String(rawMetric) : '--'
        return (
          <div className="widget-metric">
            <p className="metric-value">{metricValue}</p>
            <p className="metric-label">{widget.name}</p>
          </div>
        )
      case 'text':
        return (
          <div className="widget-text">
            <p className="text-title">{widget.name}</p>
            {widget.description && <p className="text-content">{widget.description}</p>}
          </div>
        )
      default:
        return (
          <div className="widget-placeholder">
            <p>{widget.name}</p>
            <p className="widget-type">{widget.type}</p>
          </div>
        )
    }
  }

  return (
    <div className="widget-container">
      {isEditable && (
        <div className="widget-header">
          <span className="widget-title">{widget.name}</span>
          <div className="widget-actions">
            {(widget.type === 'line_chart' || widget.type === 'bar_chart' ||
              widget.type === 'pie_chart' || widget.type === 'area_chart' ||
              widget.type === 'heatmap') && (
              <>
                <button
                  className="widget-action-btn"
                  onClick={handleExportPNG}
                  title="Export as PNG"
                >
                  📷
                </button>
                <button
                  className="widget-action-btn"
                  onClick={handleExportCSV}
                  title="Export as CSV"
                >
                  📊
                </button>
              </>
            )}
            {widget.type === 'table' && (
              <button
                className="widget-action-btn"
                onClick={handleExportCSV}
                title="Export as CSV"
              >
                📊
              </button>
            )}
            <button
              className="widget-action-btn"
              onClick={refetch}
              title="Refresh"
            >
              🔄
            </button>
            <button
              className="widget-action-btn"
              onClick={() => setIsEditing(!isEditing)}
              title="Edit"
            >
              ✏️
            </button>
            <button
              className="widget-action-btn delete"
              onClick={onDelete}
              title="Delete"
            >
              🗑️
            </button>
          </div>
        </div>
      )}
      <div className="widget-content">
        {renderWidgetContent()}
      </div>
      {isEditing && (
        <div className="widget-edit-panel">
          <input
            type="text"
            value={widget.name}
            onChange={(e) => onUpdate({ name: e.target.value })}
            placeholder="Widget name"
            className="widget-edit-input"
          />
          <button onClick={() => setIsEditing(false)} className="widget-save-btn">
            Save
          </button>
        </div>
      )}
    </div>
  )
}

export default WidgetContainer
