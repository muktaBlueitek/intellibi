import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import Heatmap from './Heatmap'

const pivotData = [
  { category: 'A', metric: 'X', value: 10 },
  { category: 'A', metric: 'Y', value: 20 },
  { category: 'B', metric: 'X', value: 15 },
  { category: 'B', metric: 'Y', value: 25 },
]

const matrixData = [
  { row: 'R1', col1: 5, col2: 10 },
  { row: 'R2', col1: 15, col2: 20 },
]

describe('Heatmap', () => {
  it('renders pivot-format heatmap with x-axis, y-axis and values', () => {
    render(
      <Heatmap
        data={pivotData}
        config={{
          title: 'Pivot Heatmap',
          xAxisKey: 'metric',
          yAxisKey: 'category',
          valueKey: 'value',
        }}
      />
    )
    expect(screen.getByText('Pivot Heatmap')).toBeInTheDocument()
    expect(screen.getByRole('grid')).toBeInTheDocument()
    expect(screen.getByText('10')).toBeInTheDocument()
    expect(screen.getByText('20')).toBeInTheDocument()
    expect(screen.getByText('15')).toBeInTheDocument()
    expect(screen.getByText('25')).toBeInTheDocument()
  })

  it('renders matrix-format heatmap', () => {
    render(
      <Heatmap
        data={matrixData}
        config={{
          title: 'Matrix Heatmap',
          xAxisKey: 'row',
        }}
      />
    )
    expect(screen.getByText('Matrix Heatmap')).toBeInTheDocument()
    expect(screen.getByRole('grid')).toBeInTheDocument()
  })

  it('shows empty state when no data', () => {
    render(
      <Heatmap data={[]} config={{ title: 'Empty' }} />
    )
    expect(screen.getByText('No data available')).toBeInTheDocument()
  })
})
