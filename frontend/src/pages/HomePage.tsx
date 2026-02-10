import { Link } from 'react-router-dom'
import './HomePage.css'

const HomePage = () => {
  return (
    <div className="home-page">
      <div className="hero">
        <h1>Welcome to IntelliBI</h1>
        <p>Your intelligent business intelligence platform</p>
      </div>
      <div className="features">
        <Link to="/dashboards" className="feature-card">
          <h2>Dashboards</h2>
          <p>Create and manage interactive dashboards</p>
        </Link>
        <Link to="/datasources" className="feature-card">
          <h2>Data Sources</h2>
          <p>Connect and manage your data sources</p>
        </Link>
        <Link to="/chatbot" className="feature-card">
          <h2>AI Chatbot</h2>
          <p>Query your data with natural language</p>
        </Link>
      </div>
    </div>
  )
}

export default HomePage
