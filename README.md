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

4. Configure environment:
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# Edit .env files with your values
```

5. Run with Docker Compose:
```bash
docker-compose up -d
```

### Production Deployment

```bash
cp .env.example .env
# Set SECRET_KEY, POSTGRES_PASSWORD, OPENAI_API_KEY in .env
docker-compose -f docker-compose.prod.yml up -d
# Or: ./scripts/deploy.sh prod
```

See [docs/USER_GUIDE.md](docs/USER_GUIDE.md) and [docs/DEMO.md](docs/DEMO.md) for more.

### End-to-end tests (Playwright)

From `frontend/`, with the API running on `http://localhost:8000` (and seed user `admin` / `admin123` or set `E2E_ADMIN_USER` / `E2E_ADMIN_PASSWORD`):

```bash
npm run test:e2e
```

Core flows live in `e2e/core-flows.spec.ts`. Tests call `GET /api/v1/health` first and skip if the backend is unreachable. Override the API base with `PLAYWRIGHT_API_BASE_URL` if needed.

## Development Status

✅ **20-day development plan complete.** See [ProjectScope.md](ProjectScope.md).

## Features

- ✅ Project setup and architecture
- ✅ Backend foundation (FastAPI, PostgreSQL, Redis, Docker)
- ✅ Authentication & User Management (JWT, RBAC)
- ✅ Dashboards (CRUD, layout, sharing, versioning)
- ✅ Data Sources (CSV/Excel upload, PostgreSQL, MySQL, REST API connectors)
- ✅ Analytics Engine (query processing, aggregations)
- ✅ AI Chatbot (natural language to SQL, insights)
- ✅ Frontend (React, dashboards, data sources, chatbot)
- ✅ Real-time (WebSocket, notifications)
- ✅ Testing (pytest, Vitest, Playwright — including dashboard/CSV/chatbot flows when API is up)
- ✅ Documentation & Deployment (Swagger, user guide, docker-compose.prod)

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


