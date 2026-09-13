# ExoIntel

ExoIntel is a Django backend for exploring exoplanet and star-system data. It provides REST and GraphQL APIs, API-key authentication, a developer portal, and background simulation jobs powered by Celery and Redis.

ExoIntel is also the backend data source for [ExoView](https://github.com/codenameuriel/exo-view).

## Features

- Read-only REST API for planets, stars, and star systems
- GraphQL API for client-driven queries
- API-key authentication and rate limiting
- Developer portal for account and API-key management
- Background simulation jobs with Celery and Redis
- Simulation history and task tracking
- Docker-based local and production workflows

## Tech Stack

- Python 3.10+
- Django 5.2
- Django REST Framework
- Graphene-Django
- Celery
- Redis
- SQLite for local development
- PostgreSQL for production
- Docker and Docker Compose
- Poetry
- Gunicorn

## Getting Started

The simplest local setup uses Docker Compose.

### 1. Clone the repository

```bash
git clone https://github.com/codenameuriel/exo-intel.git
cd exo-intel
```

### 2. Create the local environment file

```bash
cp .env.example .env.docker.local
python3 -c 'import secrets; print(secrets.token_urlsafe(50))'
```

Add the generated value to `SECRET_KEY` in `.env.docker.local`.

### 3. Start the application

```bash
docker compose -f docker-compose.local.yml -p exo-intel-local up --build
```

The local application runs at:

```text
http://localhost:8000
```

### 4. Create an administrator

```bash
docker compose -f docker-compose.local.yml -p exo-intel-local exec web \
  poetry run python3 manage.py createsuperuser
```

### 5. Load exoplanet data

```bash
docker compose -f docker-compose.local.yml -p exo-intel-local exec web \
  poetry run python3 manage.py import_canonical_data
```

## Main Endpoints

```text
Portal:     http://localhost:8000/portal/login/
Admin:      http://localhost:8000/admin/
REST API:   http://localhost:8000/api/rest/
GraphQL:    http://localhost:8000/api/graphql/
API Docs:   http://localhost:8000/api/docs/
Health:     http://localhost:8000/health/
```

API documentation requires an authenticated session.

## Host Development

For development outside Docker, install Python 3.10+, Poetry, and Redis.

```bash
cp .env.local.example .env.local
poetry install
poetry run poe migrate
poetry run poe runserver
```

The host development server runs at:

```text
http://localhost:7000
```

Start the Celery worker and scheduler separately:

```bash
poetry run poe celery:start
```

Useful commands:

```bash
poetry run poe celery:logs
poetry run poe celery:stop
poetry run poe lint
```

## Project Structure

```text
api/           REST and GraphQL API layer
api_keys/      API-key management
config/        Django settings, URLs, and application configuration
portal/        Developer portal
simulations/   Simulation engine and domain logic
tasks/         Background task tracking and Celery workflows
data/          Bundled exoplanet data
scripts/       Development and runtime scripts
```

## ExoView Integration

[ExoView](https://github.com/codenameuriel/exo-view) consumes ExoIntel through the GraphQL API using a server-side API key.

For local integration, ExoView needs an ExoIntel GraphQL endpoint and API key configured in its environment.

## License

This repository is source-available for personal, non-commercial, and educational use. Modification, redistribution, public forks, and commercial use are restricted.

See [LICENSE.md](LICENSE.md) for the complete license terms.
