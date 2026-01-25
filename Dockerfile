FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

FROM base AS builder

RUN pip install --upgrade pip wheel

COPY requirements.txt .
RUN pip download --dest /wheelhouse -r requirements.txt

FROM base AS runtime

COPY --from=builder /wheelhouse /wheelhouse

COPY requirements.txt .
RUN pip install --no-index --find-links /wheelhouse -r requirements.txt

COPY . .

RUN mkdir -p /app/data /app/logs

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
