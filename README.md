# Swiss Ephemeris API

A REST API for calculating natal charts and astrocartography using the Swiss Ephemeris library.

**Live API:** https://swiss-ephemeris-api-production-e398.up.railway.app
**Documentation:** https://swiss-ephemeris-api-production-e398.up.railway.app/docs

## Features

- Natal chart calculations with planetary positions and house cusps
- Astrocartography ley line calculations
- AI-powered astrology readings (optional)
- CORS-enabled for frontend integration
- Docker and Railway ready

## Quick Start

```bash
# Clone and install
git clone https://github.com/allinonebrandz/swiss-ephemeris-api.git
cd swiss-ephemeris-api
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your tokens

# Run server
uvicorn main:app --reload
```

Visit http://localhost:8000/docs for interactive documentation.

## API Endpoints

### GET /api/natal-chart

Calculate natal chart positions.

**Parameters:**
- `date` - Birth date (YYYY-MM-DD)
- `time` - Birth time (HH:MM:SS)
- `latitude` - Latitude in decimal degrees
- `longitude` - Longitude in decimal degrees

**Example:**
```bash
curl "https://swiss-ephemeris-api-production-e398.up.railway.app/api/natal-chart?date=1990-01-01&time=12:00:00&latitude=40.7128&longitude=-74.0060"
```

**Response:**
```json
{
  "planets": {
    "Sun": {"longitude": 280.81, "speed": 1.02},
    "Moon": {...}
  },
  "houses": [99.56, 121.51, ...],
  "ascendant": 99.56,
  "mc": 354.80
}
```

### GET /api/astrocartography

Calculate astrocartography ley lines.

**Parameters:** Same as natal chart endpoint

**Response:**
```json
{
  "lines": [
    {"planet": "Sun", "line_type": "ASC", "latitude": 40.0, "longitude": -75.0}
  ],
  "birth_location": {"latitude": 40.7128, "longitude": -74.0060}
}
```

### GET /api/mapbox-token

Returns Mapbox token for frontend map rendering.

### POST /api/generate-astrology

Generate AI astrology readings. Requires `ANTHROPIC_API_KEY`.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `MAPBOX_TOKEN` | Yes | Mapbox API token |
| `ANTHROPIC_API_KEY` | No | Claude API key for AI readings |

Create a `.env` file:
```
MAPBOX_TOKEN=pk.eyJ1...
ANTHROPIC_API_KEY=sk-ant-api03-...
```

## Deployment

### Railway

1. Connect GitHub repository to Railway
2. Add environment variables in Railway dashboard
3. Push to main branch to deploy

Railway auto-detects the Dockerfile and deploys automatically.

### Docker

```bash
docker build -t swiss-ephemeris-api .
docker run -p 8080:8080 -e MAPBOX_TOKEN=your_token swiss-ephemeris-api
```

## Usage Examples

### Python

```python
import requests

response = requests.get(
    "https://swiss-ephemeris-api-production-e398.up.railway.app/api/natal-chart",
    params={"date": "1990-01-01", "time": "12:00:00", "latitude": 40.7128, "longitude": -74.0060}
)

chart = response.json()
print(f"Ascendant: {chart['ascendant']}°")
```

### JavaScript

```javascript
const response = await fetch(
  'https://swiss-ephemeris-api-production-e398.up.railway.app/api/natal-chart?' +
  new URLSearchParams({date: '1990-01-01', time: '12:00:00', latitude: 40.7128, longitude: -74.0060})
);

const chart = await response.json();
console.log('Ascendant:', chart.ascendant);
```

## Project Structure

```
swiss-ephemeris-api/
├── main.py              # FastAPI application
├── requirements.txt     # Dependencies
├── Dockerfile          # Container config
├── ephe/               # Ephemeris data files
└── .env                # Environment variables
```

## CORS Configuration

Allowed origins:
- https://thedivinatoryreport.com
- http://localhost:3000
- http://localhost:5173

Edit `allow_origins` in `main.py` to add domains.

## License

MIT License

## Author

[allinonebrandz](https://github.com/allinonebrandz)
