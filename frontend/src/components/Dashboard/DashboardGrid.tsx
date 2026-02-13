import React, { useCallback, useEffect, useState } from 'react'
import GridLayout, { Layout } from 'react-grid-layout'
import 'react-grid-layout/css/styles.css'
import 'react-resizable/css/styles.css'
import { Widget } from '../../types/widget'
import WidgetContainer from './WidgetContainer'
import './DashboardGrid.css'

interface DashboardGridProps {
  widgets: Widget[]
  onLayoutChange: (layout: Layout[]) => void
  onWidgetUpdate: (widgetId: number, updates: Partial<Widget>) => void
  onWidgetDelete: (widgetId: number) => void
  isEditable?: boolean
}

const DashboardGrid: React.FC<DashboardGridProps> = ({
  widgets,
  onLayoutChange,
  onWidgetUpdate,
  onWidgetDelete,
  isEditable = true,
}) => {
  const [layout, setLayout] = useState<Layout[]>([])

  // Convert widgets to grid layout format
  useEffect(() => {
    const gridLayout: Layout[] = widgets.map((widget) => ({
      i: widget.id.toString(),
      x: widget.position_x,
      y: widget.position_y,
      w: widget.width,
      h: widget.height,
      minW: 2,
      minH: 2,
      maxW: 12,
      maxH: 10,
    }))
    setLayout(gridLayout)
  }, [widgets])

  const handleLayoutChange = useCallback(
    (newLayout: Layout[]) => {
      setLayout(newLayout)
      
      // Update widget positions
      newLayout.forEach((item) => {
        const widget = widgets.find((w) => w.id.toString() === item.i)
        if (widget) {
          onWidgetUpdate(widget.id, {
            position_x: item.x,
            position_y: item.y,
            width: item.w,
            height: item.h,
          })
        }
      })

      onLayoutChange(newLayout)
    },
    [widgets, onLayoutChange, onWidgetUpdate]
  )

  // Calculate width dynamically for responsiveness
  const [gridWidth, setGridWidth] = useState(1200)

  useEffect(() => {
    const updateWidth = () => {
      const container = document.querySelector('.dashboard-grid')
      if (container) {
        setGridWidth(container.clientWidth - 32) // Account for padding
      }
    }
    updateWidth()
    window.addEventListener('resize', updateWidth)
    return () => window.removeEventListener('resize', updateWidth)
  }, [])

  return (
    <div className="dashboard-grid">
      <GridLayout
        className="layout"
        layout={layout}
        cols={12}
        rowHeight={60}
        width={gridWidth}
        isDraggable={isEditable}
        isResizable={isEditable}
        onLayoutChange={handleLayoutChange}
        margin={[16, 16]}
        containerPadding={[16, 16]}
        useCSSTransforms={true}
      >
        {widgets.map((widget) => (
          <div key={widget.id} className="widget-wrapper">
            <WidgetContainer
              widget={widget}
              onUpdate={(updates) => onWidgetUpdate(widget.id, updates)}
              onDelete={() => onWidgetDelete(widget.id)}
              isEditable={isEditable}
            />
          </div>
        ))}
      </GridLayout>
    </div>
  )
}

export default DashboardGrid
