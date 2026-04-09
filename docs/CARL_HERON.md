# Carl Heron — Setup & Work Guide

## Your Stream
Assignments · Submissions · Grades · Reports

---

> **Wait for Camarly to merge Phase 1 to `develop` before writing any code.**
> Pull `develop`, then branch off `carl/assignments-grades`.

---

## Setup instructions

*(Camarly will fill this in once the environment is confirmed)*

---

## Your files

```
backend/app/routes/assignments.py
backend/app/routes/submissions.py
backend/app/routes/grades.py
backend/app/routes/reports.py

backend/app/services/assignment_service.py
backend/app/services/submission_service.py
backend/app/services/grade_service.py
backend/app/services/report_service.py
```

---

## What you are responsible for

*(Camarly will fill in detailed task instructions here)*

---

## Imports you will use

```python
from app.db.connection import get_connection
from app.middleware.roles import require_role
from app.cache.client import cache_get, cache_set, cache_del
```

---

## Frontend colour / style input

Please bring your suggestions to the group meeting for:
- Grade table colour scheme (row colours, score badge colours for grade ranges)
- Report page table styles and chart palette

---
