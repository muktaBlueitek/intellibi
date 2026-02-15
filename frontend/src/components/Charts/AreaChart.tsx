import React from 'react'
import { AreaChart as RechartsAreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { ChartData, ChartConfig } from '../../types/chart'
import BaseChart from './BaseChart'

interface AreaChartProps {
  data: ChartData[]
  config: ChartConfig
}

const AreaChart: React.FC<AreaChartProps> = ({ data, config }) => {
  const xAxisKey = config.xAxisKey || (data.length > 0 ? Object.keys(data[0])[0] : '')
  const dataKeys = config.dataKey 
    ? [config.dataKey]
    : Object.keys(data[0] || {}).filter(key => key !== xAxisKey)
  
  const colors = config.colors || ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#00ff00']
  const strokeWidth = config.strokeWidth || 2

  return (
    <BaseChart data={data} config={config}>
      <ResponsiveContainer width="100%" height="100%">
        <RechartsAreaChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          {config.showGrid !== false && <CartesianGrid strokeDasharray="3 3" />}
          <XAxis 
            dataKey={xAxisKey} 
            tick={{ fontSize: 12 }}
            angle={data.length > 10 ? -45 : 0}
            textAnchor={data.length > 10 ? 'end' : 'middle'}
            height={data.length > 10 ? 60 : 30}
          />
          <YAxis tick={{ fontSize: 12 }} />
          {config.showTooltip !== false && <Tooltip />}
          {config.showLegend !== false && <Legend />}
          {dataKeys.map((key, index) => (
            <Area
              key={key}
              type="monotone"
              dataKey={key}
              stackId={dataKeys.length > 1 ? "1" : undefined}
              stroke={colors[index % colors.length]}
              fill={colors[index % colors.length]}
              fillOpacity={0.6}
              strokeWidth={strokeWidth}
            />
          ))}
        </RechartsAreaChart>
      </ResponsiveContainer>
    </BaseChart>
  )
}

export default AreaChart
