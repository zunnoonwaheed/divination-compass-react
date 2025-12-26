FROM python:3.11-slim

# Install system dependencies (THIS FIXES YOUR ERROR)
RUN apt-get update && apt-get install -y \
    sqlite3 \
    libsqlite3-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Railway port
EXPOSE 8080

# Start FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
