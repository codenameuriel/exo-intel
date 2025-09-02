# 🪐 ExoIntel: Exoplanet API & Simulation Platform

A multienvironment Django backend providing REST and GraphQL APIs for the NASA Exoplanet Archive, a developer portal and
an asynchronous simulation engine.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)

---

## ✨ Key Features

* **Dual API Paradigms:**
    * A fully-featured, read-only **REST API** with advanced filtering, searching, and pagination.
    * A powerful, paginated **GraphQL API** for precise, client-driven data queries.

* **Professional API Security:**
    * Tiered access model with **API Key authentication** for programmatic use and **Session authentication** for the
      developer portal.
    * **Dynamic, tiered rate limiting** to protect resources, with different limits for anonymous and authenticated
      users.

* **Asynchronous Simulation Engine:**
    * A robust simulation engine for running complex, long-running scientific calculations (e.g., interstellar travel
      time, planetary seasonality, tidal locking probability).
    * Powered by a **Celery and Redis** background task queue for non-blocking execution.

* **Real-Time Task Tracking:**
    * A persistent, database-backed **simulation history tracker**.
    * A developer dashboard with a **real-time polling UI** to monitor the status of pending and completed jobs.

* **Developer Portal & Tools:**
    * A custom-styled developer portal with a secure login/signup flow and dashboard.
    * A self-service interface for developers to **create and manage their own API keys**.

* **Production-Ready Architecture:**
    * **Containerized** with **Docker** using a `Dockerfile`, ensuring a consistent and reproducible environment.
    * Orchestrated with **Docker Compose** to manage the multi-service application (web, database, cache, workers) for
      local development and
      production environments.
    * **Cloud-Native Deployment** with PaaS provider Render, using a declarative configuration approach via
      `render.yaml` file
    * Professional dependency management with **Poetry**.
    * Environment-specific configurations for seamless local, Docker, and production workflows using `django-environ`.

## 🚀 Live Demo & Documentation

* **Live Portal:** [exo-intel.onrender.com/portal/signup](exo-intel.onrender.com/portal/signup/)
* **REST API Docs (Swagger):** [exo-intel.onrender.com/api/docs](exo-intel.onrender.com/api/docs/)
* **REST API Docs (ReDoc):** [exo-intel.onrender.com/api/redoc](exo-intel.onrender.com/api/redoc/)

## 🛠️ Tech Stack

* **Backend:** Python, Django, Django REST Framework
* **Database:** PostgreSQL (production), SQLite (local)
* **Async Tasks:** Celery, Redis
* **GraphQL:** Graphene-Django
* **Containerization:** Docker, Docker Compose
* **Dependency Management:** Poetry
* **Server:** Gunicorn

## ⚙️ Local Docker Setup & Installation

This project is fully containerized and can be run on any machine with Docker and Docker Compose installed.

**1. Clone the repository via SSH:**

```bash
git clone git@github.com:codenameuriel/exo-intel.git
```

**2. Install the Project Dependencies:**

```bash
poetry install
```

**3. Create the Local Environment File:**

* Create a file named **.env.docker.local** and copy the contents of **.env.example** into it.
* To fill in the **SECRET_KEY** environment variable, you can generate one with the following command:

```bash
poetry shell
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

copy and paste the **SECRET_KEY** into the **.env.docker.local** file and enter **exit** to exit the poetry shell.

**3. Build and Run the Application:**

Use Docker Compose to build the images (only needed the first time) and start all services.

```bash
docker compose -f docker-compose.local.yml -p exo-intel-local build
```

The application will be available at http://localhost:8000/

**4. Enter the Docker Container Shell:**

While the application is running, open a new terminal window to run this command

```bash
docker compose -p exo-intel-local exec -it web bash
```

**5. Migrate the database (while in the container shell):**

```bash
poetry run poe migrate
```

**6. Create a superuser account (while in the container shell):**

```bash
poetry run poe createsuperuser
```

Now you can:

* log into the developer portal http://localhost:8000/portal/login/
* log into the admin panel http://localhost:8000/admin/

**7. Populate the database with NASA data (while in the container shell):**

```bash
poetry run poe import_all_nasa_data
```

📜 License
This project is licensed under the MIT License - see the LICENSE.md file for details.