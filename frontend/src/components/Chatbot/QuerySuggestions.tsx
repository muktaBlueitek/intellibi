import React from 'react'
import './QuerySuggestions.css'

interface QuerySuggestionsProps {
  suggestions: string[]
  onSelect: (query: string) => void
  disabled?: boolean
}

const QuerySuggestions: React.FC<QuerySuggestionsProps> = ({
  suggestions,
  onSelect,
  disabled = false,
}) => {
  if (!suggestions || suggestions.length === 0) return null

  return (
    <div className="query-suggestions">
      <span className="query-suggestions-label">Try asking:</span>
      <div className="query-suggestions-list">
        {suggestions.map((q, i) => (
          <button
            key={i}
            type="button"
            className="query-suggestion-btn"
            onClick={() => onSelect(q)}
            disabled={disabled}
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  )
}

export default QuerySuggestions
