# IntelliBI – 5-Day Development Plan

**Period:** March 16–20, 2026  
**Goal:** Enhance IntelliBI with high-value features and improvements identified post-20-day development.

---

## Overview

Based on analysis of the codebase, the following gaps and opportunities were identified:

| Gap | Description | Priority |
|-----|-------------|----------|
| API Rate Limiting | ProjectScope lists it; not implemented | High |
| Heatmap Chart | Widget type exists; no UI component | Medium |
| REST API Data Source | Type defined; no connector or UI | Medium |
| Dashboard PDF Export | ProjectScope mentions; only widget-level export exists | Medium |
| E2E Test Coverage | Only 3 basic auth tests; no flows for core features | Medium |

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

## Day 3: REST API Data Source Connector

**Objective:** Enable adding external REST APIs as data sources (type exists, no implementation).

**Tasks:**
- [ ] Backend: Create REST API connector service (HTTP fetch, configurable endpoints)
- [ ] Backend: Add endpoint to create/test REST API data sources
- [ ] Backend: Support JSON array/object response parsing for analytics
- [ ] Frontend: Create `RestApiConnectionForm.tsx` (URL, auth, headers)
- [ ] Frontend: Add REST API option to data source creation flow

**Deliverables:** REST API data source backend + frontend, docs update.

---

## Day 4: Dashboard Export to PDF

**Objective:** Export full dashboard as PDF (ProjectScope lists PDF export).

**Tasks:**
- [ ] Add PDF generation library (e.g., jsPDF + html2canvas, or react-pdf)
- [ ] Create dashboard-to-PDF export service/utility
- [ ] Add "Export as PDF" button to dashboard view
- [ ] Support multi-page layout for large dashboards

**Deliverables:** Dashboard PDF export feature, updated USER_GUIDE.

---

## Day 5: E2E Test Expansion & Documentation

**Objective:** Broaden E2E coverage and keep docs aligned with new features.

**Tasks:**
- [ ] Add E2E: Login flow → create dashboard → add widget
- [ ] Add E2E: Data source upload flow (CSV)
- [ ] Add E2E: Chatbot page load and send message
- [ ] Update BUGS_FIXED.md summary if applicable
- [ ] Update docs/5_DAY_PLAN.md with completion status
- [ ] Update README/ProjectScope with new features

**Deliverables:** Expanded E2E tests, updated documentation.

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
