import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { Provider } from 'react-redux'
import { configureStore } from '@reduxjs/toolkit'
import ProtectedRoute from './ProtectedRoute'
import authReducer from '../../store/slices/authSlice'

const renderWithStore = (isAuthenticated: boolean, children: React.ReactNode) => {
  const store = configureStore({
    reducer: {
      auth: authReducer,
    },
    preloadedState: {
      auth: {
        token: isAuthenticated ? 'fake-token' : null,
        isAuthenticated,
        loading: false,
        error: null,
      },
    },
  })
  return render(
    <Provider store={store}>
      <MemoryRouter>
        <ProtectedRoute>{children}</ProtectedRoute>
      </MemoryRouter>
    </Provider>
  )
}

describe('ProtectedRoute', () => {
  it('renders children when authenticated', () => {
    renderWithStore(true, <div>Protected content</div>)
    expect(screen.getByText('Protected content')).toBeInTheDocument()
  })

  it('does not render children when not authenticated', () => {
    renderWithStore(false, <div>Protected content</div>)
    expect(screen.queryByText('Protected content')).not.toBeInTheDocument()
  })
})
