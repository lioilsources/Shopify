FROM python:3.12-slim
WORKDIR /app
# DejaVu for the preview watermark (previews.py); slim has no fonts.
RUN apt-get update && apt-get install -y --no-install-recommends fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml .
COPY brain ./brain
COPY alembic.ini .
COPY alembic ./alembic
RUN pip install --no-cache-dir .
EXPOSE 8000
# Migrace se spustí při startu, pak server.
CMD ["sh", "-c", "alembic upgrade head && uvicorn brain.main:app --host 0.0.0.0 --port 8000"]
