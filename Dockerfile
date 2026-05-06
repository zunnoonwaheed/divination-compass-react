FROM python:3.11-slim

# System deps
RUN apt-get update && apt-get install -y \
    sqlite3 \
    libsqlite3-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy backend only (keeps image smaller)
COPY swiss-ephemeris-api/ /app/

# Ensure required Swiss Ephemeris files exist (for Chiron + Moon + planets)
RUN chmod +x /app/scripts/fetch_ephe.sh && /app/scripts/fetch_ephe.sh /app/ephe

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE ${PORT:-8080}

ENV EPHE_PATH=/app/ephe

CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080} --log-level info
