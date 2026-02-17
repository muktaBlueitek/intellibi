import React from 'react'
import './TypingIndicator.css'

const TypingIndicator: React.FC = () => {
  return (
    <div className="typing-indicator" aria-label="Assistant is typing">
      <span className="typing-dot" />
      <span className="typing-dot" />
      <span className="typing-dot" />
    </div>
  )
}

export default TypingIndicator
