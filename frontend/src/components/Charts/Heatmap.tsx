import React, { useMemo } from 'react'
import { ChartData, ChartConfig } from '../../types/chart'
import BaseChart from './BaseChart'
import './Heatmap.css'

interface HeatmapProps {
  data: ChartData[]
  config: ChartConfig
}

/** Get numeric value from a cell, handling string numbers */
function toNumber(v: string | number | Date | null | undefined): number {
  if (v == null) return 0
  if (typeof v === 'number' && !Number.isNaN(v)) return v
  const n = Number(v)
  return Number.isNaN(n) ? 0 : n
}

/**
 * Interpolate color from low (light) to high (dark) based on value in [min, max]
 */
function interpolateColor(
  value: number,
  min: number,
  max: number,
  lowColor: string = '#e3f2fd',
  highColor: string = '#1565c0'
): string {
  if (min === max) return lowColor
  const t = (value - min) / (max - min)
  const clamp = (n: number) => Math.max(0, Math.min(255, Math.round(n)))

  const parseHex = (hex: string) => {
    const m = hex.match(/^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i)
    return m ? [parseInt(m[1], 16), parseInt(m[2], 16), parseInt(m[3], 16)] : [0, 0, 0]
  }

  const [r1, g1, b1] = parseHex(lowColor)
  const [r2, g2, b2] = parseHex(highColor)

  const r = clamp(r1 + (r2 - r1) * t)
  const g = clamp(g1 + (g2 - g1) * t)
  const b = clamp(b1 + (b2 - b1) * t)

  return `rgb(${r}, ${g}, ${b})`
}

const Heatmap: React.FC<HeatmapProps> = ({ data, config }) => {
  const { grid, xLabels, yLabels, minVal, maxVal } = useMemo(() => {
    if (!data || data.length === 0) {
      return { grid: [], xLabels: [], yLabels: [], minVal: 0, maxVal: 0 }
    }

    const cols = Object.keys(data[0])
    const xKey = config.xAxisKey || cols[0]
    const yKey = config.yAxisKey || (cols.length > 1 ? cols[1] : cols[0])
    const valueKey = config.valueKey || config.dataKey || (cols.length > 2 ? cols[2] : cols.find(c => c !== xKey && c !== yKey) || cols[0])

    const isPivotFormat =
      cols.length >= 3 &&
      data.some(row => typeof toNumber(row[valueKey]) === 'number' || !Number.isNaN(Number(row[valueKey])))

    if (isPivotFormat) {
      const xSet = new Set<string>()
      const ySet = new Set<string>()
      const valueMap = new Map<string, number>()

      for (const row of data) {
        const x = String(row[xKey] ?? '')
        const y = String(row[yKey] ?? '')
        const v = toNumber(row[valueKey])
        xSet.add(x)
        ySet.add(y)
        valueMap.set(`${y}::${x}`, v)
      }

      const xLabels = Array.from(xSet)
      const yLabels = Array.from(ySet)
      const grid: number[][] = yLabels.map(y =>
        xLabels.map(x => valueMap.get(`${y}::${x}`) ?? 0)
      )
      const flat = grid.flat()
      const minVal = flat.length ? Math.min(...flat) : 0
      const maxVal = flat.length ? Math.max(...flat) : 0
      return { grid, xLabels, yLabels, minVal, maxVal }
    }

    // Matrix format: first col = row label, rest = column values
    const yLabelsMatrix = data.map(row => String(row[xKey] ?? row[cols[0]] ?? ''))
    const valueCols = cols.filter(c => c !== xKey && c !== yKey)
    const xLabelsMatrix = valueCols.length ? valueCols : cols.filter(c => c !== xKey)
    const gridMatrix: number[][] = data.map(row =>
      xLabelsMatrix.map(c => toNumber(row[c]))
    )
    const flatM = gridMatrix.flat()
    const minM = flatM.length ? Math.min(...flatM) : 0
    const maxM = flatM.length ? Math.max(...flatM) : 0
    return {
      grid: gridMatrix,
      xLabels: xLabelsMatrix,
      yLabels: yLabelsMatrix,
      minVal: minM,
      maxVal: maxM,
    }
  }, [data, config.xAxisKey, config.yAxisKey, config.valueKey, config.dataKey])

  const colors = config.colors
  const lowColor = colors?.[0] ?? '#e3f2fd'
  const highColor = colors?.[1] ?? '#1565c0'

  return (
    <BaseChart data={data} config={config}>
      <div className="heatmap-container">
        {grid.length === 0 ? null : (
          <table className="heatmap-table" role="grid">
            <thead>
              <tr>
                <th className="heatmap-corner" />
                {xLabels.map((x, i) => (
                  <th key={i} className="heatmap-x-label">
                    {x}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {grid.map((row, rowIdx) => (
                <tr key={rowIdx}>
                  <td className="heatmap-y-label">{yLabels[rowIdx]}</td>
                  {row.map((val, colIdx) => (
                    <td
                      key={colIdx}
                      className="heatmap-cell"
                      style={{
                        backgroundColor: interpolateColor(val, minVal, maxVal, lowColor, highColor),
                        color: (minVal !== maxVal && (val - minVal) / (maxVal - minVal) < 0.5) ? '#333' : '#fff',
                      }}
                      title={`${yLabels[rowIdx]} × ${xLabels[colIdx]}: ${val}`}
                    >
                      {val}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </BaseChart>
  )
}

export default Heatmap
