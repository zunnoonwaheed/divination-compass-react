# Railway Deployment Guide

## Overview
This guide explains how to deploy the Swiss Ephemeris API to Railway and connect it to your frontend at https://thedivinatoryreport.com

## Prerequisites
- Railway account
- GitHub repository access
- Mapbox API token

## Deployment Steps

### 1. Connect to Railway

1. Go to [Railway.app](https://railway.app)
2. Create a new project
3. Connect your GitHub repository: `allinonebrandz/swiss-ephemeris-api`
4. Railway will automatically detect it's a Python application

### 2. Configure Environment Variables

In Railway's project settings, add the following environment variable:

```
MAPBOX_TOKEN=pk.eyJ1IjoibnVpbGx1bSIsImEiOiJjbW5leXg4NjYwNGdiMnFvdGNtbmx0eGF5In0.QNGwTpC2JCQuwVAB155qWw
```

**Optional** (only if you want AI-generated readings):
```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 3. Configure Build Settings

Railway should auto-detect Python, but verify:

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 4. Deploy

Railway will automatically deploy when you push to the main branch.

### 5. Get Your API URL

After deployment, Railway will provide a URL like:
```
https://your-app-name.up.railway.app
```

### 6. Update Frontend Configuration

In your Lovable frontend (https://thedivinatoryreport.com), update the API base URL to point to your Railway deployment:

```javascript
const API_BASE_URL = "https://your-app-name.up.railway.app";
```

## API Endpoints

The following endpoints are available:

- **GET** `/` - API status and documentation
- **GET** `/api/natal-chart` - Calculate natal chart positions
- **GET** `/api/astrocartography` - Calculate astrocartography ley lines
- **GET** `/api/mapbox-token` - Get Mapbox token for frontend maps
- **POST** `/api/generate-astrology` - Generate AI readings (optional)

## Testing the Deployment

### Test the API is running:
```bash
curl https://your-app-name.up.railway.app/
```

### Test natal chart endpoint:
```bash
curl "https://your-app-name.up.railway.app/api/natal-chart?date=1990-01-01&time=12:00:00&latitude=40.7128&longitude=-74.0060"
```

### Test Mapbox token:
```bash
curl https://your-app-name.up.railway.app/api/mapbox-token
```

### Test astrocartography:
```bash
curl "https://your-app-name.up.railway.app/api/astrocartography?date=1990-01-01&time=12:00:00&latitude=40.7128&longitude=-74.0060"
```

## CORS Configuration

The API is pre-configured to accept requests from:
- `https://thedivinatoryreport.com`
- `http://localhost:3000` (development)
- `http://localhost:5173` (Vite development)

If you need to add additional domains, edit the `allow_origins` list in `main.py`.

## Troubleshooting

### Issue: Frontend can't connect to backend
- Verify CORS origins in `main.py` include your frontend domain
- Check Railway logs for errors
- Ensure Railway service is running and healthy

### Issue: Mapbox token not working
- Verify `MAPBOX_TOKEN` environment variable is set in Railway
- Check token is valid and not expired

### Issue: Astrocartography map not loading
- Ensure `/api/astrocartography` endpoint returns data
- Verify frontend is making the correct API call
- Check browser console for CORS or network errors

## Support

For issues with:
- **Backend/API**: Check Railway logs and main.py
- **Frontend**: Check Lovable project console
- **Mapbox**: Verify token and map configuration
