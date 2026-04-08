# Use slim Python 3.11 base image
FROM python:3.11-slim

# Install system dependencies (Fixes Ephemeris and SQLite issues)
RUN apt-get update && apt-get install -y \
    sqlite3 \
    libsqlite3-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory inside container
WORKDIR /app

# Copy all project files into the image (including ephe/ directory)
COPY . /app

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port Railway uses (dynamic)
EXPOSE ${PORT:-8080}

# Start the FastAPI server
# Note: Railway provides PORT env var dynamically
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080} --log-level info
