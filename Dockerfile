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

# Expose port Railway uses
EXPOSE 8080

# Start the FastAPI server with auto-reload and debug logging
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload", "--log-level", "debug"]
