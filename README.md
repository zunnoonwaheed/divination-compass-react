# Swiss Ephemeris API

A FastAPI-based REST API for calculating natal charts and astrocartography using the Swiss Ephemeris library. Deployed on Railway and integrated with a Lovable frontend at [thedivinatoryreport.com](https://thedivinatoryreport.com).

[![Railway Deploy](https://img.shields.io/badge/Railway-Deploy-blueviolet)](https://railway.app)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)

## 🌟 Features

- **Natal Chart Calculations** - Accurate planetary positions, houses, and chart angles
- **Astrocartography** - Calculate ley lines for location-based astrology
- **Swiss Ephemeris** - Professional-grade astronomical calculations
- **AI Readings** (Optional) - Generate personalized astrology readings with Claude AI
- **CORS Enabled** - Ready for frontend integration
- **Docker Ready** - Containerized for easy deployment
- **Railway Optimized** - Configured for Railway deployment

## 🚀 Live Demo

**API URL:** https://swiss-ephemeris-api-production-e398.up.railway.app

**Frontend:** https://thedivinatoryreport.com/full-report

## 📋 Table of Contents

- [Installation](#installation)
- [API Endpoints](#api-endpoints)
- [Deployment](#deployment)
- [Environment Variables](#environment-variables)
- [Usage Examples](#usage-examples)
- [Development](#development)
- [License](#license)

## 🔧 Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/allinonebrandz/swiss-ephemeris-api.git
   cd swiss-ephemeris-api
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your tokens
   ```

5. **Run the server**
   ```bash
   uvicorn main:app --reload
   ```

6. **Visit the API docs**
   ```
   http://localhost:8000/docs
   ```

## 📡 API Endpoints

### Root Endpoint

```http
GET /
```

Returns API information and available endpoints.

**Response:**
```json
{
  "name": "Swiss Ephemeris API",
  "version": "1.0.0",
  "status": "running",
  "endpoints": { ... }
}
```

### Natal Chart

```http
GET /api/natal-chart
```

Calculate natal chart positions for a given birth date, time, and location.

**Parameters:**
- `date` (string, required) - Birth date in YYYY-MM-DD format
- `time` (string, required) - Birth time in HH:MM:SS format
- `latitude` (float, required) - Birth latitude in decimal degrees
- `longitude` (float, required) - Birth longitude in decimal degrees

**Example:**
```bash
curl "https://swiss-ephemeris-api-production-e398.up.railway.app/api/natal-chart?date=1990-01-01&time=12:00:00&latitude=40.7128&longitude=-74.0060"
```

**Response:**
```json
{
  "jd_ut": 2447893.0,
  "input": {
    "date": "1990-01-01",
    "time": "12:00:00",
    "latitude": 40.7128,
    "longitude": -74.0060
  },
  "planets": {
    "Sun": {
      "longitude": 280.81,
      "latitude": 0.0,
      "distance": 0.983,
      "speed": 1.019
    },
    "Moon": { ... },
    ...
  },
  "houses": [99.56, 121.51, ...],
  "ascendant": 99.56,
  "mc": 354.80
}
```

### Astrocartography

```http
GET /api/astrocartography
```

Calculate astrocartography ley lines for mapping planetary influences across the globe.

**Parameters:**
- `date` (string, required) - Birth date in YYYY-MM-DD format
- `time` (string, required) - Birth time in HH:MM:SS format
- `latitude` (float, required) - Birth latitude in decimal degrees
- `longitude` (float, required) - Birth longitude in decimal degrees

**Example:**
```bash
curl "https://swiss-ephemeris-api-production-e398.up.railway.app/api/astrocartography?date=1990-01-01&time=12:00:00&latitude=40.7128&longitude=-74.0060"
```

**Response:**
```json
{
  "jd_ut": 2447893.0,
  "input": { ... },
  "lines": [
    {
      "planet": "Sun",
      "line_type": "ASC",
      "latitude": 40.0,
      "longitude": -75.0,
      "planet_longitude": 280.81
    },
    ...
  ],
  "birth_location": {
    "latitude": 40.7128,
    "longitude": -74.0060
  }
}
```

### Mapbox Token

```http
GET /api/mapbox-token
```

Returns the Mapbox token for frontend map rendering.

**Response:**
```json
{
  "token": "pk.eyJ1..."
}
```

### AI Astrology Reading (Optional)

```http
POST /api/generate-astrology
```

Generate AI-powered astrology readings using Claude.

**Requires:** `ANTHROPIC_API_KEY` environment variable

**Request Body:**
```json
{
  "prompt": "Generate a brief astrology reading",
  "chart_data": {
    "sun": "280.5",
    "moon": "45.2"
  }
}
```

**Response:**
```json
{
  "reading": "Based on your chart..."
}
```

## 🚢 Deployment

### Railway Deployment

This API is configured for Railway deployment.

1. **Connect to Railway**
   - Go to [Railway.app](https://railway.app)
   - Create a new project
   - Connect your GitHub repository

2. **Set Environment Variables**

   In Railway dashboard → Variables:
   ```
   MAPBOX_TOKEN=your_mapbox_token_here
   ANTHROPIC_API_KEY=your_anthropic_key_here (optional)
   ```

3. **Deploy**
   - Railway automatically detects the Dockerfile
   - Push to `main` branch to trigger deployment
   - Railway provides a public URL

### Docker Deployment

```bash
# Build the image
docker build -t swiss-ephemeris-api .

# Run the container
docker run -p 8080:8080 \
  -e MAPBOX_TOKEN=your_token \
  -e ANTHROPIC_API_KEY=your_key \
  swiss-ephemeris-api
```

## 🔐 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `MAPBOX_TOKEN` | Yes | Mapbox API token for frontend maps |
| `ANTHROPIC_API_KEY` | No | Claude API key for AI readings |
| `PORT` | No | Port number (default: 8080, Railway auto-sets) |

**Create a `.env` file:**
```bash
MAPBOX_TOKEN=pk.eyJ1...
ANTHROPIC_API_KEY=sk-ant-api03-...
```

## 📖 Usage Examples

### Python

```python
import requests

# Get natal chart
response = requests.get(
    "https://swiss-ephemeris-api-production-e398.up.railway.app/api/natal-chart",
    params={
        "date": "1990-01-01",
        "time": "12:00:00",
        "latitude": 40.7128,
        "longitude": -74.0060
    }
)

chart_data = response.json()
print(f"Ascendant: {chart_data['ascendant']}°")
print(f"Sun: {chart_data['planets']['Sun']['longitude']}°")
```

### JavaScript

```javascript
// Fetch natal chart
const response = await fetch(
  'https://swiss-ephemeris-api-production-e398.up.railway.app/api/natal-chart?' +
  new URLSearchParams({
    date: '1990-01-01',
    time: '12:00:00',
    latitude: 40.7128,
    longitude: -74.0060
  })
);

const chartData = await response.json();
console.log('Ascendant:', chartData.ascendant);
console.log('Sun:', chartData.planets.Sun.longitude);
```

### cURL

```bash
# Get natal chart
curl "https://swiss-ephemeris-api-production-e398.up.railway.app/api/natal-chart?date=1990-01-01&time=12:00:00&latitude=40.7128&longitude=-74.0060"

# Get astrocartography
curl "https://swiss-ephemeris-api-production-e398.up.railway.app/api/astrocartography?date=1990-01-01&time=12:00:00&latitude=40.7128&longitude=-74.0060"

# Get Mapbox token
curl "https://swiss-ephemeris-api-production-e398.up.railway.app/api/mapbox-token"
```

## 🛠️ Development

### Project Structure

```
swiss-ephemeris-api/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker configuration
├── .env               # Environment variables (not in git)
├── .gitignore         # Git ignore rules
├── ephe/              # Swiss Ephemeris data files
└── README.md          # This file
```

### Dependencies

- **FastAPI** - Modern web framework
- **Uvicorn** - ASGI server
- **pyswisseph** - Swiss Ephemeris Python wrapper
- **python-dotenv** - Environment variable management
- **anthropic** - Claude AI integration (optional)

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### API Documentation

Interactive API documentation is available at:

- **Swagger UI:** `https://swiss-ephemeris-api-production-e398.up.railway.app/docs`
- **ReDoc:** `https://swiss-ephemeris-api-production-e398.up.railway.app/redoc`

## 🌐 CORS Configuration

The API allows requests from:
- `https://thedivinatoryreport.com`
- `http://localhost:3000` (development)
- `http://localhost:5173` (Vite development)

To add more domains, edit the `allow_origins` list in `main.py`.

## 🔍 Troubleshooting

### Issue: "MAPBOX_TOKEN not set"

**Solution:** Add `MAPBOX_TOKEN` to your environment variables in Railway or `.env` file.

### Issue: "AI reading feature not configured"

**Solution:** This is optional. Add `ANTHROPIC_API_KEY` if you want AI readings, or ignore this endpoint.

### Issue: CORS errors

**Solution:** Ensure your frontend domain is in the `allow_origins` list in `main.py`.

### Issue: Port not binding

**Solution:** Railway automatically sets the `PORT` environment variable. The Dockerfile is configured to use it.

## 📚 Resources

- **Swiss Ephemeris:** https://www.astro.com/swisseph/
- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **Railway Docs:** https://docs.railway.app/
- **Mapbox API:** https://docs.mapbox.com/

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👤 Author

**allinonebrandz**

- GitHub: [@allinonebrandz](https://github.com/allinonebrandz)
- Website: [thedivinatoryreport.com](https://thedivinatoryreport.com)

## 🙏 Acknowledgments

- Swiss Ephemeris by Astrodienst AG
- FastAPI by Sebastián Ramírez
- Railway for hosting
- Claude AI for assistance

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check the API documentation at `/docs`
- Visit the live demo

---

**Built with ❤️ for accurate astrological calculations**
