# 🪐 ExoIntel: Exoplanet API & Simulation Platform

A multienvironment Django backend providing REST and GraphQL APIs for the NASA Exoplanet Archive, a developer portal and
an asynchronous simulation engine.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)

---

## ✨ Key Features

- **Dual API Paradigms:**
  - A fully-featured, read-only **REST API** with advanced filtering, searching, and pagination.
  - A powerful, paginated **GraphQL API** for precise, client-driven data queries.

- **Professional API Security:**
  - Tiered access model with **API Key authentication** for programmatic use and **Session authentication** for the
    developer portal.
  - **Dynamic, tiered rate limiting** to protect resources, with different limits for anonymous and authenticated
    users.

- **Asynchronous Simulation Engine:**
  - A robust simulation engine for running complex, long-running scientific calculations (e.g., interstellar travel
    time, planetary seasonality, tidal locking probability).
  - Powered by a **Celery and Redis** background task queue for non-blocking execution.

- **Real-Time Task Tracking:**
  - A persistent, database-backed **simulation history tracker**.
  - A developer dashboard with a **real-time polling UI** to monitor the status of pending and completed jobs.

- **Developer Portal & Tools:**
  - A custom-styled developer portal with a secure login/signup flow and dashboard.
  - A self-service interface for developers to **create and manage their own API keys**.

- **Production-Ready Architecture:**
  - **Containerized** with **Docker** using a `Dockerfile`, ensuring a consistent and reproducible environment.
  - Orchestrated with **Docker Compose** to manage the multi-service application (web, database, cache, workers) for
    local development and
    production environments.
  - **Cloud-Native Deployment** with PaaS provider Render, using a declarative configuration approach via
    `render.yaml` file
  - Professional dependency management with **Poetry**.
  - Environment-specific configurations for seamless local, Docker, and production workflows using `django-environ`.

## 🚀 Live Demo & Documentation

- **Live Portal:** [exo-intel.onrender.com/portal/signup](exo-intel.onrender.com/portal/signup/)
- **REST API Docs (Swagger):** [exo-intel.onrender.com/api/docs](exo-intel.onrender.com/api/docs/)
- **REST API Docs (ReDoc):** [exo-intel.onrender.com/api/redoc](exo-intel.onrender.com/api/redoc/)

## 🛠️ Tech Stack

- **Backend:** Python, Django, Django REST Framework
- **Database:** PostgreSQL (production), SQLite (local)
- **Async Tasks:** Celery, Redis
- **GraphQL:** Graphene-Django
- **Containerization:** Docker, Docker Compose
- **Dependency Management:** Poetry
- **Server:** Gunicorn

## Local Docker setup

Docker Compose runs Django, Redis, a Celery worker, and Celery Beat. Django uses SQLite locally. You do not need Poetry installed on the host.

1. Create the local environment file on a fresh checkout:

```bash
cp .env.example .env.docker.local
python3 -c 'import secrets; print(secrets.token_urlsafe(50))'
```

Put the generated value in `SECRET_KEY` inside `.env.docker.local`. This file is ignored by Git.

1. Build and start the stack:

```bash
docker compose -f docker-compose.local.yml -p exo-intel-local up --build
```

The migration service runs before the web and Celery services. When startup finishes, open <http://localhost:8000/>.

1. Create an administrator in another terminal:

```bash
docker compose -f docker-compose.local.yml -p exo-intel-local exec web \
  poetry run python3 manage.py createsuperuser
```

1. Load the bundled canonical NASA data if you want a populated API:

```bash
docker compose -f docker-compose.local.yml -p exo-intel-local exec web \
  poetry run python3 manage.py import_canonical_data
```

The portal is at <http://localhost:8000/portal/login/> and the default admin is at <http://localhost:8000/admin/>.

Useful local commands:

```bash
# Follow logs
docker compose -f docker-compose.local.yml -p exo-intel-local logs -f

# Open a shell in the web container
docker compose -f docker-compose.local.yml -p exo-intel-local exec web bash

# Stop and remove the containers
docker compose -f docker-compose.local.yml -p exo-intel-local down
```

## Host development setup

Host development requires Python 3.10 or newer, Poetry, and Redis. The web server and Celery use `.env.local`.

```bash
cp .env.local.example .env.local
poetry install
poetry run poe migrate
poetry run poe runserver
```

The host web server listens at <http://localhost:7000/>. Start the Celery worker and Beat in another terminal:

```bash
poetry run poe celery:start
```

Use `poetry run poe celery:logs` and `poetry run poe celery:stop` to inspect or stop those background processes.

## Production Docker setup

The production stack runs PostgreSQL, Redis, Gunicorn, a Celery worker, and Celery Beat. Its one-shot preparation service waits for PostgreSQL, applies migrations, and imports the bundled canonical data before the application starts.

```bash
cp .env.docker.production.example .env.docker.production
python3 -c 'import secrets; print(f"SECRET_KEY={secrets.token_urlsafe(50)}"); print(f"DATABASE_PASSWORD={secrets.token_urlsafe(32)}")'
```

Put the generated `SECRET_KEY` value in `SECRET_KEY`. Put the generated URL-safe database password in both `POSTGRES_PASSWORD` and `DATABASE_URL`. Before exposing the service publicly, set the real hostnames and HTTPS origins and change `SECURE_COOKIES` to `True`. Then start it:

```bash
docker compose -f docker-compose.production.yml up --build -d
```

Gunicorn listens at <http://localhost:9000/>. Stop the stack without deleting PostgreSQL data with:

```bash
docker compose -f docker-compose.production.yml down
```

📜 License

This project is under a proprietary license. You are welcome to view the source code and run the application locally for
personal and educational purposes. However, you are not permitted to modify, redistribute, or use the code for any
commercial purpose. Please see the `LICENSE.md` file for full details.
