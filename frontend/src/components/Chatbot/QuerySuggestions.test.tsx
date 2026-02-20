import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import QuerySuggestions from './QuerySuggestions'

describe('QuerySuggestions', () => {
  it('renders nothing when suggestions is empty', () => {
    const { container } = render(
      <QuerySuggestions suggestions={[]} onSelect={vi.fn()} />
    )
    expect(container.firstChild).toBeNull()
  })

  it('renders suggestion buttons', () => {
    const onSelect = vi.fn()
    render(
      <QuerySuggestions
        suggestions={['Query 1', 'Query 2']}
        onSelect={onSelect}
      />
    )
    expect(screen.getByText('Query 1')).toBeInTheDocument()
    expect(screen.getByText('Query 2')).toBeInTheDocument()
  })

  it('calls onSelect when a suggestion is clicked', () => {
    const onSelect = vi.fn()
    render(
      <QuerySuggestions
        suggestions={['Click me']}
        onSelect={onSelect}
      />
    )
    fireEvent.click(screen.getByText('Click me'))
    expect(onSelect).toHaveBeenCalledWith('Click me')
  })
})
