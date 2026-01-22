ARG PYTHON_VERSION=3.13.9
FROM python:${PYTHON_VERSION}-slim as base

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

COPY pyproject.toml poetry.lock ./

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

USER appuser

COPY --chown=appuser:appuser . .

ENTRYPOINT ["/app/entrypoint.sh"]

EXPOSE 8000

CMD gunicorn 'config.wsgi' --bind=0.0.0.0:8000
