import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import TypingIndicator from './TypingIndicator'

describe('TypingIndicator', () => {
  it('renders typing indicator', () => {
    render(<TypingIndicator />)
    const container = document.querySelector('.typing-indicator')
    expect(container).toBeInTheDocument()
  })

  it('has three dots for animation', () => {
    render(<TypingIndicator />)
    const dots = document.querySelectorAll('.typing-dot')
    expect(dots).toHaveLength(3)
  })
})
