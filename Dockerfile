# Combined image for single-service deployment (Railway).
# Stage 1 builds the React app; stage 2 runs Flask and serves
# the built SPA as static files.

FROM node:20-alpine AS frontend
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci || npm install
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./
COPY --from=frontend /build/dist ./static_frontend

EXPOSE 5000

CMD gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 4 --timeout 120 run:app
