# IntelliBI – 5-Day Development Plan

**Period:** March 16–20, 2026  
**Goal:** Enhance IntelliBI with high-value features and improvements identified post-20-day development.

---

## Overview

Based on analysis of the codebase, the following gaps and opportunities were identified:

| Gap | Description | Status |
|-----|-------------|--------|
| API Rate Limiting | ProjectScope lists it | Done |
| Heatmap Chart | Widget type exists; UI component | Done |
| REST API Data Source | Type defined; connector + UI | Done |
| Dashboard PDF Export | Full dashboard PDF | Done |
| E2E Test Coverage | Core flows beyond basic auth | Done |

---

## Day 1: API Rate Limiting ✅

**Objective:** Add rate limiting to protect the API from abuse and meet ProjectScope requirements.

**Tasks:**
- [x] Add `slowapi` dependency for FastAPI rate limiting
- [x] Create rate limit config (100 req/min general, 10 req/min for auth)
- [x] Apply rate limiting middleware to API routes
- [x] Exempt health check endpoint
- [x] Stricter limits on login/register (10/min)
- [x] Config in settings (RATE_LIMIT_ENABLED, RATE_LIMIT_GENERAL, RATE_LIMIT_AUTH)

**Deliverables:** Rate-limited API, updated requirements.txt, `app/core/rate_limit.py`.

---

## Day 2: Heatmap Chart Component ✅

**Objective:** Implement the missing Heatmap visualization (type exists in widget model).

**Tasks:**
- [x] Create `Heatmap.tsx` using Recharts `Cell` or a heatmap library
- [x] Support pivot data (x-axis, y-axis, color intensity)
- [x] Add to chart exports and `WidgetContainer` type mapping
- [x] Integrate with analytics response format
- [x] Add unit test for Heatmap component

**Deliverables:** Heatmap component, chart index update, widget support.

---

## Day 3: REST API Data Source Connector ✅

**Objective:** Enable adding external REST APIs as data sources (type exists, no implementation).

**Tasks:**
- [x] Backend: Create REST API connector service (HTTP fetch, configurable endpoints)
- [x] Backend: Add endpoint to create/test REST API data sources
- [x] Backend: Support JSON array/object response parsing for analytics
- [x] Frontend: Create `RestApiConnectionForm.tsx` (URL, auth, headers)
- [x] Frontend: Add REST API option to data source creation flow

**Deliverables:** REST API data source backend + frontend (`app/services/rest_api_connector.py`, `app/api/v1/endpoints/rest_api.py`, `RestApiConnectionForm.tsx`).

---

## Day 4: Dashboard Export to PDF ✅

**Objective:** Export full dashboard as PDF (ProjectScope lists PDF export).

**Tasks:**
- [x] Add PDF generation library (e.g., jsPDF + html2canvas, or react-pdf)
- [x] Create dashboard-to-PDF export service/utility
- [x] Add "Export as PDF" button to dashboard view
- [x] Support multi-page layout for large dashboards

**Deliverables:** Dashboard PDF export feature (`exportDashboardToPdf.ts`, DashboardPage button), updated USER_GUIDE.

---

## Day 5: E2E Test Expansion & Documentation ✅

**Objective:** Broaden E2E coverage and keep docs aligned with new features.

**Tasks:**
- [x] Add E2E: Login flow → create dashboard → add widget
- [x] Add E2E: Data source upload flow (CSV)
- [x] Add E2E: Chatbot page load and send message
- [x] Update BUGS_FIXED.md summary if applicable
- [x] Update docs/5_DAY_PLAN.md with completion status
- [x] Update README/ProjectScope with new features

**Deliverables:** `e2e/core-flows.spec.ts`, `e2e/helpers.ts`, fixture CSV; README testing notes; Vitest/TS cleanup for `tsc` passing.

---

## Success Criteria

- All features work end-to-end
- No regressions in existing functionality
- Tests pass (backend pytest, frontend Vitest, Playwright E2E)

---

## Notes

- Adjust scope per day if tasks take longer than expected
- Prioritize correctness over completeness
- Document any deviations in this file
