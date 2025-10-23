# backend/Dockerfile
FROM python:3.11-slim AS base

# install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev curl \
  && rm -rf /var/lib/apt/lists/*

# create app user
ENV APP_HOME=/app
RUN useradd --create-home --home-dir $APP_HOME appuser

WORKDIR $APP_HOME

# copy requirements first for better layer caching
COPY requirements.txt .

# install python deps
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# copy app
COPY . $APP_HOME

# chown to non-root
RUN chown -R appuser:appuser $APP_HOME
USER appuser

ENV PYTHONPATH=$APP_HOME

# production command: uvicorn (replace host/port with compose env)
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
