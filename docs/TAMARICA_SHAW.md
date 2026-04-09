# Tamarica Shaw — Setup & Work Guide

## Your Stream
Courses · Enrollment · Calendar Events · Course Content · Postman Collection

---

> **Wait for Camarly to merge Phase 1 to `develop` before writing any code.**
> Pull `develop`, then branch off `tamarica/courses-enrollment`.

---

## Setup instructions

*(Camarly will fill this in once the environment is confirmed)*

---

## Your files

```
backend/app/routes/courses.py
backend/app/routes/enrollments.py
backend/app/routes/calendar_events.py
backend/app/routes/content.py

backend/app/services/course_service.py
backend/app/services/enrollment_service.py
backend/app/services/calendar_service.py
backend/app/services/content_service.py

postman/LMS_Collection.postman_collection.json   (shared with Tramonique)
postman/LMS_Environment.postman_environment.json (shared with Tramonique)
```

---

## What you are responsible for

*(Camarly will fill in detailed task instructions here)*

---

## Business rules you must enforce in your service code

| Rule | Where |
|---|---|
| A student cannot enroll in more than **6 courses** | `enrollment_service.py` → return 403 |
| A lecturer cannot be assigned to more than **5 courses** | `course_service.py` → return 403 |
| A course can have only **one lecturer** at a time | `course_service.py` → replace, not append |
| Duplicate enrollment returns **409** | `enrollment_service.py` |

---

## Imports you will use

```python
from app.db.connection import get_connection
from app.middleware.roles import require_role
from app.cache.client import cache_get, cache_set, cache_del
```

---

## Postman folders you own

- Courses
- Enrollment
- Calendar Events
- Content
- Assignments
- Submissions

---

## Frontend colour / style input

Please bring your suggestions to the group meeting for:
- Course card layout and colour palette
- Calendar event chip / badge colours
- Enrollment status indicator styles (enrolled vs. available)

---
