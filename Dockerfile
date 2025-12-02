# ============ STAGE 1: Build Frontend ============
FROM node:20-alpine AS frontend-builder

WORKDIR /web-dev-project/frontend

# Copy package files for dependency installation
COPY frontend/package.json frontend/package-lock.json ./

# Install dependencies
RUN npm ci

# Copy frontend source code
COPY frontend/ .

# Build Next.js application (outputs to out/ directory with export)
ARG NEXT_PUBLIC_API_BASE_URL=http://localhost:5000
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL
RUN NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL npm run build

# Validate that 'out' directory exists and contains expected files
RUN test -d out || (echo "Frontend build failed: 'out' directory not found" && exit 1)
RUN test -f out/index.html || (echo "Frontend build failed: 'index.html' not found" && exit 1)

# ============ STAGE 2: Build Backend with Embedded Frontend ============
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /inner-app

# Install system dependencies required for mysql-connector-python
RUN apt-get update && apt-get install -y default-libmysqlclient-dev build-essential && rm -rf /var/lib/apt/lists/*

# Copy the backend requirements file into the container
COPY backend/requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend application code into the container
COPY backend/ .

# Copy the compiled frontend from Stage 1 into backend's static directory
# The 'out' directory contains static-exported Next.js files ready to be served
RUN mkdir -p static
COPY --from=frontend-builder /web-dev-project/frontend/out ./static/frontend

# Validate frontend files are present
RUN test -f static/frontend/index.html || (echo "Frontend deployment failed: 'index.html' not found in static directory" && exit 1)

# Command to run the application
CMD ["sh", "-c", "if [ \"$FLASK_ENV\" = \"production\" ]; then gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 4 run:app; else python run.py; fi"]
