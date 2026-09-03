FROM node:22-alpine AS frontend
WORKDIR /build/italy-trip-2026
COPY italy-trip-2026/package.json italy-trip-2026/package-lock.json ./
RUN npm ci
COPY italy-trip-2026/index.html italy-trip-2026/vite.config.js ./
COPY italy-trip-2026/src ./src
RUN npm run build

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_URL=sqlite:////data/trip_planner.db \
    ENABLE_LEGACY_FARE_API=false \
    PORT=8080
WORKDIR /app
RUN pip install --no-cache-dir \
    "fastapi>=0.115" "uvicorn[standard]>=0.32" "sqlalchemy>=2.0" \
    "alembic>=1.13" "jinja2>=3.1" "pydantic-settings>=2.6" \
    "python-dotenv>=1.0" "typer>=0.15" "rich>=13" "json5>=0.9" \
    "httpx>=0.28" "python-multipart>=0.0.20"
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini
COPY italy-trip-2026/public ./italy-trip-2026/public
COPY italy-trip-2026/tools/activities-seed.csv ./italy-trip-2026/tools/activities-seed.csv
COPY italy-trip-2026/tools/activity-coordinates.json ./italy-trip-2026/tools/activity-coordinates.json
COPY --from=frontend /build/app/static/wiki-dist ./app/static/wiki-dist
EXPOSE 8080
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
