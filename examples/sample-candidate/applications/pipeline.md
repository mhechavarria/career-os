# Application Pipeline

<!-- Lifecycle is tracked by the `stage` field, updated in each application's
frontmatter as it progresses (applied → screening stages → offer, or one of the
terminal stages rejected / ghosted / withdrawn). The terminal stages are what
`pipeline_report.py` treats as closed; the tables below mirror that, so an
application moves from Active to Closed purely by advancing its `stage`. -->

## Active

```dataview
TABLE company, role, level, applied_date, stage, keyword_coverage, resume_worded_score, source
FROM "applications"
WHERE type = "application" AND !contains(list("rejected", "ghosted", "withdrawn"), stage)
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
TABLE company, role, applied_date, stage
FROM "applications"
WHERE type = "application" AND contains(list("rejected", "ghosted", "withdrawn"), stage)
SORT applied_date DESC
```
