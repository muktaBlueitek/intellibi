# IntelliBI - Demo & Presentation

## Overview

**IntelliBI** is an Intelligent Business Intelligence platform that enables organizations to visualize data, generate insights, and interact with data through an AI-powered conversational assistant.

**Duration:** 20-day development cycle  
**Tech Stack:** FastAPI (backend), React + TypeScript (frontend), PostgreSQL, Redis, LangChain/OpenAI

---

## Key Features Demo Flow

### 1. Authentication (2 min)
- **Register** a new user
- **Login** and land on home
- Navigate to Profile

### 2. Dashboards (5 min)
- Create a **new dashboard**
- Add widgets (charts, tables, metrics)
- **Drag-and-drop** layout editing
- Save and share dashboard

### 3. Data Sources (4 min)
- **Upload** CSV/Excel file
- Preview data and validate
- **Connect** PostgreSQL or MySQL
- Test connection and save

### 4. AI Chatbot (5 min)
- Open **Chatbot**
- Select a data source
- Ask natural language questions:
  - "What are total sales by region?"
  - "Show top 10 products"
- View **SQL**, **results table**, **insights**
- Use suggested follow-up queries
- **Export** conversation

### 5. Real-Time (2 min)
- Open same dashboard in two browser tabs
- Edit layout in one tab
- See updates in the other tab
- Chat updates in real time

---

## Talking Points

| Feature | Benefit |
|---------|---------|
| Natural language queries | Non-technical users can query data |
| Multi-source integration | CSV, Excel, PostgreSQL, MySQL |
| Custom dashboards | Drag-and-drop, shareable, versioned |
| Real-time updates | WebSocket for live collaboration |
| AI insights | Summaries, trends, visualization suggestions |
| Role-based access | Share with View or Edit permissions |

---

## Architecture Highlights

```
React Frontend (Vite) → REST API (FastAPI) → PostgreSQL
                    ↘ WebSocket           ↗ Redis Cache
                    ↘ LangChain/OpenAI    ↗ Analytics Engine
```

---

## API Documentation

- **Swagger UI:** `http://localhost:8000/api/v1/docs`
- **ReDoc:** `http://localhost:8000/api/v1/redoc`
- **OpenAPI JSON:** `http://localhost:8000/api/v1/openapi.json`
