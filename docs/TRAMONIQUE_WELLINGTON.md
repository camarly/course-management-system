# Tramonique Wellington — Setup & Work Guide

## Your Stream
Forums · Threads · Nested Replies · Postman Collection

---

> **Wait for Camarly to merge Phase 1 to `develop` before writing any code.**
> Pull `develop`, then branch off `tramonique/forums-threads`.

---

## Setup instructions

*(Camarly will fill this in once the environment is confirmed)*

---

## Your files

```
backend/app/routes/forums.py
backend/app/routes/threads.py
backend/app/routes/replies.py

backend/app/services/forum_service.py
backend/app/services/thread_service.py
backend/app/services/reply_service.py

postman/LMS_Collection.postman_collection.json   (shared with Tamarica)
postman/LMS_Environment.postman_environment.json (shared with Tamarica)
```

---

## What you are responsible for

*(Camarly will fill in detailed task instructions here)*

---

## Imports you will use

```python
from app.db.connection import get_connection
from app.middleware.roles import require_role
```

---

## Postman folders you own

- Auth
- Forums
- Threads
- Replies
- Grades
- Reports

---

## Frontend colour / style input

Please bring your suggestions to the group meeting for:
- Forum list and thread card design
- Reply indentation visual style (colours per depth level)
- Accent colour for the discussion / forum section

---
