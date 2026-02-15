import React from 'react'
import { BarChart as RechartsBarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { ChartData, ChartConfig } from '../../types/chart'
import BaseChart from './BaseChart'

interface BarChartProps {
  data: ChartData[]
  config: ChartConfig
}

const BarChart: React.FC<BarChartProps> = ({ data, config }) => {
  const xAxisKey = config.xAxisKey || (data.length > 0 ? Object.keys(data[0])[0] : '')
  const dataKeys = config.dataKey 
    ? [config.dataKey]
    : Object.keys(data[0] || {}).filter(key => key !== xAxisKey)
  
  const colors = config.colors || ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#00ff00']
  const barSize = config.barSize || undefined
  const layout = config.layout || 'vertical'

  return (
    <BaseChart data={data} config={config}>
      <ResponsiveContainer width="100%" height="100%">
        <RechartsBarChart 
          data={data} 
          layout={layout}
          margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
        >
          {config.showGrid !== false && <CartesianGrid strokeDasharray="3 3" />}
          {layout === 'vertical' ? (
            <>
              <XAxis 
                dataKey={xAxisKey} 
                tick={{ fontSize: 12 }}
                angle={data.length > 10 ? -45 : 0}
                textAnchor={data.length > 10 ? 'end' : 'middle'}
                height={data.length > 10 ? 60 : 30}
              />
              <YAxis tick={{ fontSize: 12 }} />
            </>
          ) : (
            <>
              <XAxis type="number" tick={{ fontSize: 12 }} />
              <YAxis 
                type="category" 
                dataKey={xAxisKey} 
                tick={{ fontSize: 12 }}
                width={100}
              />
            </>
          )}
          {config.showTooltip !== false && <Tooltip />}
          {config.showLegend !== false && <Legend />}
          {dataKeys.map((key, index) => (
            <Bar
              key={key}
              dataKey={key}
              fill={colors[index % colors.length]}
              barSize={barSize}
            />
          ))}
        </RechartsBarChart>
      </ResponsiveContainer>
    </BaseChart>
  )
}

export default BarChart
