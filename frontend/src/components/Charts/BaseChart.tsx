import React from 'react'
import { ChartConfig, ChartData } from '../../types/chart'
import './BaseChart.css'

interface BaseChartProps {
  data: ChartData[]
  config: ChartConfig
  children: React.ReactNode
  className?: string
}

const BaseChart: React.FC<BaseChartProps> = ({
  data,
  config,
  children,
  className = '',
}) => {
  if (!data || data.length === 0) {
    return (
      <div className={`base-chart empty ${className}`}>
        <p>No data available</p>
      </div>
    )
  }

  return (
    <div className={`base-chart ${className}`}>
      {config.title && <h3 className="chart-title">{config.title}</h3>}
      <div className="chart-content">
        {children}
      </div>
    </div>
  )
}

export default BaseChart
