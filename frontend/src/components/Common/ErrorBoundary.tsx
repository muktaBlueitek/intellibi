import React, { Component, ErrorInfo, ReactNode } from 'react'
import './ErrorBoundary.css'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
    }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null })
  }

  render() {
    if (this.state.hasError && this.state.error) {
      if (this.props.fallback) {
        return this.props.fallback
      }
      return (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <p className="error-boundary-message">
            {this.state.error.message || 'An unexpected error occurred.'}
          </p>
          <button type="button" className="error-boundary-retry" onClick={this.handleRetry}>
            Try again
          </button>
        </div>
      )
    }
    return this.props.children
  }
}

export default ErrorBoundary
