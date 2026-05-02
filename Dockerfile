# Combined image for single-service deployment (Railway).
# Stage 1 builds the React app; stage 2 runs Flask and serves
# the built SPA as static files.

FROM node:20-slim AS frontend
WORKDIR /build
# Skip the lockfile here on purpose: it pins platform-specific rollup
# binaries from whatever machine first generated it, which trips
# npm/cli#4828 when the build runs on a different OS/arch (e.g. Mac
# arm64 vs. Railway x64). A fresh `npm install` resolves the right
# optional deps for the current platform.
COPY frontend/package.json ./
RUN npm install
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
