# IntelliBI - Intelligent Business Intelligence Platform

A comprehensive full-stack business intelligence platform that enables organizations to visualize data, generate insights, and interact with their data through an AI-powered conversational assistant.

## Project Overview

IntelliBI is a modern BI platform featuring:
- **Real-time Analytics Dashboards** - Multi-widget dashboards with customizable layouts
- **AI-Powered Chatbot** - Natural language query interface for data insights
- **Data Integration** - Support for CSV/Excel uploads, database connectors, and REST APIs
- **User Management** - Role-based access control and team collaboration
- **Performance & Scalability** - Built with distributed systems architecture

## Technology Stack

### Backend
- **Framework:** Python FastAPI (async, high-performance)
- **Database:** PostgreSQL (primary), Redis (caching)
- **AI/ML:** Python (LangChain, OpenAI API or open-source LLM)
- **Data Processing:** Pandas, NumPy, SQLAlchemy
- **APIs:** RESTful APIs, WebSocket for real-time updates
- **Authentication:** JWT tokens, OAuth2

### Frontend
- **Framework:** React 18 with TypeScript
- **UI Library:** Material-UI or Ant Design
- **Charts:** Recharts, D3.js, Chart.js
- **State Management:** Redux Toolkit or Zustand
- **Real-time:** Socket.io-client

### Infrastructure
- **Containerization:** Docker, Docker Compose
- **API Gateway:** Kong or Nginx
- **Message Queue:** RabbitMQ or Apache Kafka
- **Monitoring:** Prometheus, Grafana (optional)

## Project Structure

```
intellibi/
├── backend/          # FastAPI backend application
├── frontend/         # React frontend application
├── docker-compose.yml
├── README.md
└── ProjectScope.md
```

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker and Docker Compose
- PostgreSQL 14+
- Redis 6+

### Installation

1. Clone the repository:
```bash
git clone https://github.com/muktaBlueitek/intellibi.git
cd intellibi
```

2. Set up backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up frontend:
```bash
cd frontend
npm install
```

4. Run with Docker Compose:
```bash
docker-compose up -d
```

## Development Status

This project is currently in active development. See [ProjectScope.md](ProjectScope.md) for the complete 20-day development plan.

## Features

- ✅ Project setup and architecture
- ✅ Backend foundation (FastAPI skeleton, DB config, Docker, health endpoint)
- ✅ Authentication & User Management (JWT, RBAC, user endpoints)
- 🚧 Frontend foundation (in progress)
- 🚧 AI chatbot integration (planned)
- 🚧 Data analytics dashboards (planned)

## Contributing

This is a personal project for demonstrating full-stack development capabilities including:
- Modern web application development
- Data analytics and visualization
- AI/ML integration
- Distributed systems architecture
- System design and software engineering principles

## License

This project is for demonstration purposes.

## Contact

For questions or inquiries, please open an issue on GitHub.


