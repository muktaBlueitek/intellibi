import React, { useState } from 'react'
import { Widget } from '../../types/widget'
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

  const renderWidgetContent = () => {
    switch (widget.type) {
      case 'line_chart':
      case 'bar_chart':
      case 'pie_chart':
      case 'area_chart':
        return (
          <div className="widget-chart-placeholder">
            <p>{widget.type.replace('_', ' ').toUpperCase()}</p>
            <p className="widget-name">{widget.name}</p>
            <p className="widget-note">Chart will be implemented in Day 14</p>
          </div>
        )
      case 'table':
        return (
          <div className="widget-table-placeholder">
            <p>TABLE</p>
            <p className="widget-name">{widget.name}</p>
            <p className="widget-note">Table will be implemented in Day 14</p>
          </div>
        )
      case 'metric':
        return (
          <div className="widget-metric-placeholder">
            <p className="metric-value">--</p>
            <p className="metric-label">{widget.name}</p>
          </div>
        )
      case 'text':
        return (
          <div className="widget-text-placeholder">
            <p>{widget.name}</p>
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
