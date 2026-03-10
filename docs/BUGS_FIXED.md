# IntelliBI – Bugs Found and Fixed

This document captures additional bugs found during code review and their fixes.

---

## 1. FileUpload Preview Structure Mismatch

**Location:** `frontend/src/components/DataSources/FileUpload.tsx`

**Severity:** High – Causes runtime crash when previewing uploaded files

**Problem:**
The backend preview API returns:
```json
{
  "metadata": { "row_count", "column_count", "columns", ... },
  "preview": {
    "columns": ["col1", "col2", ...],
    "data": [ { "col1": "val1", ... }, ... ],
    "total_rows": 100,
    "preview_rows": 10
  }
}
```

The frontend treated `preview.preview` as an **array of row objects**, but it is actually an **object** with a `data` property containing the rows. As a result:

- `preview.preview[0]` is `undefined` (objects have no numeric index)
- `Object.keys(preview.preview[0])` throws `TypeError`
- `preview.preview.slice(0, 10)` fails (objects don’t have `slice`)
- `preview.preview.length > 0` is always false (objects don’t have `length`)

**Fix:**
- Use `preview.preview.data` for the row array.
- Use `preview.preview.columns` or `preview.metadata.columns` for column headers.
- Add a check for empty data so the preview table still shows headers when there are no rows.

---

## 2. Dashboard Shared Query – Redundant SQLAlchemy Wrapper

**Location:** `backend/app/api/v1/endpoints/dashboards.py` (lines 71–75)

**Severity:** Medium – Potential compatibility and clarity issues

**Problem:**
```python
shared_dashboard_ids = db.query(DashboardShare.dashboard_id).filter(
    DashboardShare.user_id == current_user.id
).subquery()
conditions.append(Dashboard.id.in_(db.query(shared_dashboard_ids)))
```

- `shared_dashboard_ids` is already a subquery object.
- `db.query(shared_dashboard_ids)` wraps it in another query, which is unnecessary.
- `in_()` accepts a subquery/selectable directly.
- The extra wrapping can cause compatibility issues across SQLAlchemy versions and hurts readability.

**Fix:**
```python
shared_dashboard_ids = db.query(DashboardShare.dashboard_id).filter(
    DashboardShare.user_id == current_user.id
).subquery()
conditions.append(Dashboard.id.in_(shared_dashboard_ids))
```

Pass the subquery directly to `in_()` instead of wrapping it with `db.query()`.

---

## Summary

| Bug                           | Component | Severity | Fix                          |
|------------------------------|-----------|----------|------------------------------|
| FileUpload preview structure | Frontend  | High     | Use `preview.data` and `preview.columns` |
| Dashboard shared query       | Backend   | Medium   | Pass subquery directly to `in_()` |
