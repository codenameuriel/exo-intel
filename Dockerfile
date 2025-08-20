FROM python:3.10-slim

# default build argument
ARG ENVIRONMENT=local

ENV ENVIRONMENT=${ENVIRONMENT} \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.1.4 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=0 \
    POETRY_VIRTUALENVS_PATH=/venv \
    DJANGO_SETTINGS_MODULE=config.settings.${ENVIRONMENT}

WORKDIR /app
RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

COPY pyproject.toml poetry.lock ./
RUN if [ "$ENVIRONMENT" = "production" ]; then \
      poetry install --only main --no-root --no-ansi; \
    else \
      poetry install --no-root --no-ansi; \
    fi

COPY . .

COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh

RUN chmod +x /usr/local/bin/entrypoint.sh

# collect static files at build time
RUN if [ "$ENVIRONMENT" = "production" ]; then \
      poetry run python3 manage.py collectstatic --noinput; \
    fi

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]