# Application Pipeline

## Active

```dataview
TABLE company, role, level, applied_date, stage, keyword_coverage, resume_worded_score, source
FROM "applications"
WHERE type = "application" AND status = "active"
SORT applied_date DESC
```

## All Applications

```dataview
TABLE company, role, applied_date, stage, status, cv_version
FROM "applications"
WHERE type = "application"
SORT applied_date DESC
```

## Closed — Outcomes

```dataview
TABLE company, role, applied_date, stage, status
FROM "applications"
WHERE type = "application" AND status = "closed"
SORT applied_date DESC
```
