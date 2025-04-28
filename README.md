Task Management System - Architecture Design Document

📅 Application Overview
A FastAPI-based Task Management System with the following capabilities:
CRUD operations on tasks (title, description, status).


PostgreSQL for persistent data storage.


Redis for caching frequently accessed data.


Celery + Redis for background task processing.


Keycloak for authentication & role-based access control (RBAC).


Logging (to file and Graylog), monitoring, and pre-commit for code consistency.



📊 Application Architecture
![Diagram:](jasper-colin/app_arch.png)


Tasks Table:


id: UUID (Primary Key)


title: String (Required)


description: String (Optional)


status: Enum (pending, in-progress, completed)


created_at: Timestamp (default=now)


updated_at: Timestamp (auto-update on modify)


Migration handled via Alembic.
2. API Scalability
FastAPI with ASGI server (e.g., Uvicorn/Gunicorn) for async support.


Stateless APIs deployed in containers (Docker), orchestrated via Docker Compose or Kubernetes for high availability.


Connection pooling with SQLAlchemy + PostgreSQL.


Redis caching to reduce database load.


Horizontal scaling of API pods for handling concurrent traffic.


3. Authentication Setup
Keycloak as Identity Provider.


Integrated using OpenID Connect.


Protect routes using Keycloak token validation.


Role-based access enforced at route level (e.g., admin, user).


Tokens validated via FastAPI dependency that decodes and checks scopes/roles.

               +---------------------------+
               |       Users / Clients      |
               +------------+---------------+
                            |
                            v
               +------------+---------------+
               |         FastAPI App         |  <---------------------+
               | (Keycloak, RBAC, Caching)   |                        |
               +------------+---------------+                        |
                            |                                        |
    +-----------------------+-----------------------+              |
    |                       |                       |              |
    v                       v                       v              |
+-------------+      +---------------+       +----------------+    |
| PostgreSQL  |      | Redis (cache)  |       | Celery Worker  |    |
| (Main DB)   |      +---------------+       +----------------+    |
+-------------+                                             |        |
        ^                                                   |        |
        |                                                   v        |
+-------------+                                   +------------------+
| Alembic     |                                   | Redis (broker)    |
| (Migrations)|                                   +------------------+
+-------------+


🌐 Caching Strategy
Tool: Redis


Strategy:


Frequently accessed endpoints (e.g., get_task, filtered get_tasks) use cached responses.


Key format: task:{id} or hash-based key for query filters.


TTL (time-to-live): e.g., 300 seconds.


Invalidated automatically on updates/deletes.


# Sample usage
key = f"task:{task_id}"
cached = await get_cached_response(key)
if not cached:
    task = await get_task_from_db()
    await set_cached_response(key, task)


⏳ Message Queuing & Background Tasks
Tools: Celery + Redis (broker)


Use Cases:


Sending emails/notifications on task creation.


Asynchronous logging or analytics processing.


Design:


Tasks are offloaded to Celery.


Redis broker manages task queue.


Celery workers consume and process background tasks.


# Example
@app.post("/tasks")
async def create_task(...):
    task = await save_task_to_db(...)
    send_notification.delay(task.id)  # Background task via Celery


📉 Monitoring, Logging, Pre-commit
Logging:


.ini based config


Logs written to file and sent to Graylog.


Monitoring:


Health check endpoint


Redis/ping + PostgreSQL test


Pre-commit hooks:


Ensures linting, formatting, and type checking before commits.



✅ Summary
This architecture ensures:
High scalability (async FastAPI, Redis caching, container orchestration).


Security (RBAC with Keycloak).


Observability (logging + monitoring).


Performance (background jobs via Celery).


The system is production-grade and designed for handling scale and complexity in a clean, modular way.

