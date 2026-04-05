import os
from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import swisseph as swe
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set the path to ephemeris files
swe.set_ephe_path('./ephe')

app = FastAPI()

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://thedivinatoryreport.com",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Anthropic client only if API key is available
anthropic_client = None
try:
    from anthropic import Anthropic
    if os.getenv("ANTHROPIC_API_KEY"):
        anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
except ImportError:
    pass

@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "name": "Swiss Ephemeris API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "natal_chart": {
                "path": "/api/natal-chart",
                "method": "GET",
                "description": "Calculate natal chart positions",
                "parameters": {
                    "date": "YYYY-MM-DD format",
                    "time": "HH:MM:SS format",
                    "latitude": "decimal degrees",
                    "longitude": "decimal degrees"
                },
                "example": "/api/natal-chart?date=1990-01-01&time=12:00:00&latitude=40.7128&longitude=-74.0060"
            },
            "astrocartography": {
                "path": "/api/astrocartography",
                "method": "GET",
                "description": "Calculate astrocartography ley lines for mapping",
                "parameters": {
                    "date": "YYYY-MM-DD format",
                    "time": "HH:MM:SS format",
                    "latitude": "decimal degrees (birth location)",
                    "longitude": "decimal degrees (birth location)"
                },
                "example": "/api/astrocartography?date=1990-01-01&time=12:00:00&latitude=40.7128&longitude=-74.0060"
            },
            "mapbox_token": {
                "path": "/api/mapbox-token",
                "method": "GET",
                "description": "Get Mapbox API token"
            },
            "generate_astrology": {
                "path": "/api/generate-astrology",
                "method": "POST",
                "description": "Generate AI astrology reading using Claude (optional)",
                "body": {
                    "prompt": "Custom prompt (optional)",
                    "chart_data": "Chart data object"
                }
            }
        },
        "docs": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }

def compute_chart(jd_ut, latitude, longitude, house_system="P"):
    """Compute astrological chart data using Swiss Ephemeris"""

    # Calculate houses
    houses, ascmc = swe.houses(jd_ut, latitude, longitude, house_system.encode('ascii'))

    # Planet calculations
    planets = {}
    planet_ids = {
        'Sun': swe.SUN,
        'Moon': swe.MOON,
        'Mercury': swe.MERCURY,
        'Venus': swe.VENUS,
        'Mars': swe.MARS,
        'Jupiter': swe.JUPITER,
        'Saturn': swe.SATURN,
        'Uranus': swe.URANUS,
        'Neptune': swe.NEPTUNE,
        'Pluto': swe.PLUTO,
    }

    for name, planet_id in planet_ids.items():
        result = swe.calc_ut(jd_ut, planet_id)
        planets[name] = {
            'longitude': result[0][0],
            'latitude': result[0][1],
            'distance': result[0][2],
            'speed': result[0][3]
        }

    return {
        'planets': planets,
        'houses': list(houses),
        'ascendant': ascmc[0],
        'mc': ascmc[1]
    }

@app.get("/api/natal-chart")
def natal_chart_alias(
    date: str = Query(...),
    time: str = Query(...),
    latitude: float = Query(...),
    longitude: float = Query(...)
):
    try:
        date_parts = date.split("-")
        time_parts = time.split(":")
        year, month, day = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
        hour, minute = int(time_parts[0]), int(time_parts[1])
        second = int(time_parts[2]) if len(time_parts) > 2 else 0
    except Exception:
        raise HTTPException(400, detail="Invalid date or time format")
    
    local_hours = hour + minute / 60.0 + second / 3600.0
    jd_ut = swe.julday(year, month, day, local_hours, swe.GREG_CAL)
    chart_data = compute_chart(jd_ut, latitude, longitude, "P")
    return {
        "jd_ut": jd_ut,
        "input": {"date": date, "time": time, "latitude": latitude, "longitude": longitude},
        **chart_data
    }

@app.get("/api/mapbox-token")
def get_mapbox_token():
    token = os.getenv("MAPBOX_TOKEN")
    if not token:
        raise HTTPException(500, detail="MAPBOX_TOKEN not set")
    return {"token": token}

@app.post("/api/generate-astrology")
async def generate_astrology(request: Request):
    if not anthropic_client:
        raise HTTPException(500, detail="AI reading feature not configured. ANTHROPIC_API_KEY required.")

    body = await request.json()
    prompt = body.get("prompt", "Generate a brief astrology reading based on this chart data.")
    chart_data = body.get("chart_data", {})

    message = anthropic_client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": f"{prompt}\n\nChart data: {chart_data}"}
        ]
    )
    return {"reading": message.content[0].text}

@app.get("/api/astrocartography")
def astrocartography(
    date: str = Query(...),
    time: str = Query(...),
    latitude: float = Query(...),
    longitude: float = Query(...)
):
    """Calculate astrocartography lines for ley lines map"""
    try:
        date_parts = date.split("-")
        time_parts = time.split(":")
        year, month, day = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
        hour, minute = int(time_parts[0]), int(time_parts[1])
        second = int(time_parts[2]) if len(time_parts) > 2 else 0
    except Exception:
        raise HTTPException(400, detail="Invalid date or time format")

    local_hours = hour + minute / 60.0 + second / 3600.0
    jd_ut = swe.julday(year, month, day, local_hours, swe.GREG_CAL)

    # Get planetary positions
    planet_ids = {
        'Sun': swe.SUN,
        'Moon': swe.MOON,
        'Mercury': swe.MERCURY,
        'Venus': swe.VENUS,
        'Mars': swe.MARS,
        'Jupiter': swe.JUPITER,
        'Saturn': swe.SATURN,
        'Uranus': swe.URANUS,
        'Neptune': swe.NEPTUNE,
        'Pluto': swe.PLUTO,
    }

    lines = []

    # Calculate lines for each planet at different latitudes
    for planet_name, planet_id in planet_ids.items():
        result = swe.calc_ut(jd_ut, planet_id)
        planet_lon = result[0][0]

        # Calculate longitude lines where planet is on angles
        # ASC line: where planet rises
        # MC line: where planet culminates
        # DSC line: where planet sets
        # IC line: where planet is at lower culmination

        for lat in range(-80, 81, 10):  # Sample latitudes
            try:
                # Calculate houses for this latitude at different longitudes
                for lon in range(-180, 181, 5):
                    houses, ascmc = swe.houses(jd_ut, lat, lon, b'P')
                    asc = ascmc[0]
                    mc = ascmc[1]
                    dsc = (asc + 180) % 360
                    ic = (mc + 180) % 360

                    # Check if planet is within 1 degree of any angle
                    tolerance = 1.0
                    if abs(planet_lon - asc) < tolerance or abs(planet_lon - asc - 360) < tolerance:
                        lines.append({
                            'planet': planet_name,
                            'line_type': 'ASC',
                            'latitude': lat,
                            'longitude': lon,
                            'planet_longitude': planet_lon
                        })
                    if abs(planet_lon - mc) < tolerance or abs(planet_lon - mc - 360) < tolerance:
                        lines.append({
                            'planet': planet_name,
                            'line_type': 'MC',
                            'latitude': lat,
                            'longitude': lon,
                            'planet_longitude': planet_lon
                        })
            except Exception:
                continue

    return {
        "jd_ut": jd_ut,
        "input": {"date": date, "time": time, "latitude": latitude, "longitude": longitude},
        "lines": lines,
        "birth_location": {"latitude": latitude, "longitude": longitude}
    }