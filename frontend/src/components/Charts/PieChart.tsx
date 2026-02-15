import React from 'react'
import { PieChart as RechartsPieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { ChartData, ChartConfig } from '../../types/chart'
import BaseChart from './BaseChart'

interface PieChartProps {
  data: ChartData[]
  config: ChartConfig
}

const PieChart: React.FC<PieChartProps> = ({ data, config }) => {
  const labelKey = config.labelKey || config.xAxisKey || (data.length > 0 ? Object.keys(data[0])[0] : '')
  const valueKey = config.valueKey || config.dataKey || config.yAxisKey || (data.length > 0 ? Object.keys(data[0])[1] : '')
  
  const colors = config.colors || [
    '#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#00ff00',
    '#0088fe', '#00c49f', '#ffbb28', '#ff8042', '#8884d8'
  ]
  const innerRadius = config.innerRadius || 0
  const outerRadius = config.outerRadius || 80

  return (
    <BaseChart data={data} config={config}>
      <ResponsiveContainer width="100%" height="100%">
        <RechartsPieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            outerRadius={outerRadius}
            innerRadius={innerRadius}
            fill="#8884d8"
            dataKey={valueKey}
            nameKey={labelKey}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
            ))}
          </Pie>
          {config.showTooltip !== false && <Tooltip />}
          {config.showLegend !== false && <Legend />}
        </RechartsPieChart>
      </ResponsiveContainer>
    </BaseChart>
  )
}

export default PieChart
