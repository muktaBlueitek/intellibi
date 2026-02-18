import { lazy, Suspense } from 'react'

// Lazy load chart components for better performance
export const LazyLineChart = lazy(() => import('./LineChart'))
export const LazyBarChart = lazy(() => import('./BarChart'))
export const LazyPieChart = lazy(() => import('./PieChart'))
export const LazyAreaChart = lazy(() => import('./AreaChart'))
export const LazyDataTable = lazy(() => import('./DataTable'))

// Loading fallback component
export const ChartLoadingFallback = () => (
  <div style={{ 
    display: 'flex', 
    alignItems: 'center', 
    justifyContent: 'center', 
    minHeight: '200px',
    color: 'var(--text-secondary)'
  }}>
    Loading chart...
  </div>
)

// Wrapper component for lazy-loaded charts
export const LazyChartWrapper: React.FC<{
  component: React.LazyExoticComponent<React.ComponentType<any>>
  fallback?: React.ReactNode
  [key: string]: any
}> = ({ component: Component, fallback = <ChartLoadingFallback />, ...props }) => {
  return (
    <Suspense fallback={fallback}>
      <Component {...props} />
    </Suspense>
  )
}
