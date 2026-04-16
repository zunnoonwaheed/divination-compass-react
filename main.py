import os
import logging
import math
from datetime import datetime
from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import swisseph as swe
from dotenv import load_dotenv
from timezonefinder import TimezoneFinder
import pytz

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Set the path to ephemeris files
swe.set_ephe_path('./ephe')

# Initialize TimezoneFinder for lat/lon to timezone conversion
tf = TimezoneFinder()

def convert_local_to_utc(year, month, day, hour, minute, second, latitude, longitude):
    """
    Convert local birth time to UTC using the timezone at the birth location.

    Args:
        year, month, day, hour, minute, second: Local birth time components
        latitude, longitude: Birth location coordinates

    Returns:
        dict: {
            'utc_datetime': datetime object in UTC,
            'utc_jd': Julian Day in UTC,
            'timezone_name': timezone name (e.g., 'America/Los_Angeles'),
            'utc_offset_hours': UTC offset in hours (e.g., -8 for PST),
            'local_datetime_str': formatted local datetime,
            'utc_datetime_str': formatted UTC datetime
        }
    """
    try:
        # Get timezone name from coordinates
        timezone_name = tf.timezone_at(lat=latitude, lng=longitude)
        if not timezone_name:
            raise ValueError(f"Could not determine timezone for coordinates: {latitude}, {longitude}")

        logger.info(f"📍 Birth location timezone: {timezone_name}")

        # Create timezone-aware local datetime
        local_tz = pytz.timezone(timezone_name)

        # Create naive local datetime
        naive_local_dt = datetime(year, month, day, hour, minute, second)

        # Localize to the birth location timezone (handles DST automatically)
        local_dt = local_tz.localize(naive_local_dt)

        # Convert to UTC
        utc_dt = local_dt.astimezone(pytz.UTC)

        # Calculate UTC offset
        utc_offset_seconds = local_dt.utcoffset().total_seconds()
        utc_offset_hours = utc_offset_seconds / 3600

        # Calculate Julian Day using UTC time
        utc_hours = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
        jd_ut = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_hours, swe.GREG_CAL)

        # Log the conversion
        logger.info(f"🕐 Input local datetime: {naive_local_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"🌍 Detected timezone: {timezone_name}")
        logger.info(f"⏰ UTC offset: {utc_offset_hours:+.1f} hours")
        logger.info(f"🌐 Converted UTC datetime: {utc_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        logger.info(f"📅 Julian Day (UT): {jd_ut}")

        return {
            'utc_datetime': utc_dt,
            'utc_jd': jd_ut,
            'timezone_name': timezone_name,
            'utc_offset_hours': utc_offset_hours,
            'local_datetime_str': naive_local_dt.strftime('%Y-%m-%d %H:%M:%S'),
            'utc_datetime_str': utc_dt.strftime('%Y-%m-%d %H:%M:%S UTC')
        }
    except Exception as e:
        logger.error(f"❌ Timezone conversion error: {str(e)}")
        raise HTTPException(400, detail=f"Timezone conversion failed: {str(e)}")

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

    # Use geocentric positions with speed for all planets (matches Astro.com standard)
    for name, planet_id in planet_ids.items():
        # Calculate with speed flag for accurate speed values
        result = swe.calc_ut(jd_ut, planet_id, swe.FLG_SPEED)

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
    """
    Calculate natal chart with proper timezone conversion.
    Expects LOCAL birth time and converts to UTC internally.
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"🌟 NATAL CHART REQUEST")
    logger.info(f"{'='*60}")
    logger.info(f"Input - Date: {date}, Time: {time}")
    logger.info(f"Input - Location: ({latitude}, {longitude})")

    try:
        date_parts = date.split("-")
        time_parts = time.split(":")
        year, month, day = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
        hour, minute = int(time_parts[0]), int(time_parts[1])
        second = int(time_parts[2]) if len(time_parts) > 2 else 0
    except Exception:
        raise HTTPException(400, detail="Invalid date or time format")

    # Convert local birth time to UTC (this is the critical fix!)
    utc_info = convert_local_to_utc(year, month, day, hour, minute, second, latitude, longitude)

    # Use UTC Julian Day for all calculations
    jd_ut = utc_info['utc_jd']

    # Compute chart using UTC
    chart_data = compute_chart(jd_ut, latitude, longitude, "P")

    logger.info(f"✅ Natal chart calculated successfully")
    logger.info(f"{'='*60}\n")

    return {
        "jd_ut": jd_ut,
        "input": {
            "date": date,
            "time": time,
            "latitude": latitude,
            "longitude": longitude
        },
        "timezone_info": {
            "timezone": utc_info['timezone_name'],
            "utc_offset_hours": utc_info['utc_offset_hours'],
            "local_datetime": utc_info['local_datetime_str'],
            "utc_datetime": utc_info['utc_datetime_str']
        },
        **chart_data
    }

def find_zodiacal_line_longitude(planet_lon, target_angle_offset, jd_ut, latitude, house_system="P"):
    """
    Find longitude where a planet conjuncts a specific angle (ASC/MC/DSC/IC) using Zodiacal method.

    This is the method used by Astro.com - it calculates houses at different longitudes
    to find where the planet's ecliptic longitude matches the angle.

    Args:
        planet_lon: Planet's ecliptic longitude in degrees (0-360)
        target_angle_offset: 0=ASC, 90=MC, 180=DSC, 270=IC (offset from ASC in degrees)
        jd_ut: Julian Day in UTC
        latitude: Observer's latitude
        house_system: House system to use (default "P" for Placidus)

    Returns:
        Longitude where the conjunction occurs, or None if not found
    """
    # Normalize planet longitude to 0-360
    planet_lon = planet_lon % 360

    # Binary search for the longitude where the angle matches the planet position
    # We'll search from -180 to 180 longitude
    left = -180.0
    right = 180.0
    tolerance = 0.01  # 0.01 degree precision

    for _ in range(100):  # Max 100 iterations
        mid = (left + right) / 2.0

        try:
            # Calculate houses at this longitude
            houses, ascmc = swe.houses(jd_ut, latitude, mid, house_system.encode('ascii'))

            # Get the target angle
            if target_angle_offset == 0:  # ASC
                angle = ascmc[0]
            elif target_angle_offset == 90:  # MC
                angle = ascmc[1]
            elif target_angle_offset == 180:  # DSC
                angle = (ascmc[0] + 180) % 360
            else:  # IC
                angle = (ascmc[1] + 180) % 360

            # Normalize angle to 0-360
            angle = angle % 360

            # Calculate difference (accounting for 360-degree wraparound)
            diff = angle - planet_lon
            if diff > 180:
                diff -= 360
            elif diff < -180:
                diff += 360

            # Check if we're close enough
            if abs(diff) < tolerance:
                return mid

            # Adjust search range based on the difference
            # If angle > planet, we need to move west (decrease longitude)
            # If angle < planet, we need to move east (increase longitude)
            if diff > 0:
                right = mid
            else:
                left = mid

            # Check if search range is too small
            if abs(right - left) < tolerance:
                return mid

        except Exception:
            # If houses calculation fails, return None
            return None

    return None

def calculate_zodiacal_line_points(planet_lon, target_angle_offset, jd_ut, num_points=50, house_system="P"):
    """
    Calculate points along an angle line using Zodiacal method (Astro.com style).

    This finds where a planet's ecliptic longitude conjuncts a specific angle (ASC/MC/DSC/IC)
    at different latitudes across the globe.

    Args:
        planet_lon: Planet's ecliptic longitude in degrees (0-360)
        target_angle_offset: 0=ASC, 90=MC, 180=DSC, 270=IC
        jd_ut: Julian Day in UTC
        num_points: Number of points to calculate
        house_system: House system (default "P" for Placidus)

    Returns:
        List of {'latitude': lat, 'longitude': lon} dictionaries
    """
    points = []

    # For MC and IC lines, they are relatively straight (meridians)
    # For ASC and DSC lines, they curve based on latitude
    if target_angle_offset in [90, 270]:  # MC or IC
        # These are simpler - nearly vertical lines
        # Calculate at latitude 0 (equator) as reference
        lon_at_equator = find_zodiacal_line_longitude(planet_lon, target_angle_offset, jd_ut, 0.0, house_system)

        if lon_at_equator is not None:
            # MC/IC lines are nearly vertical, but still need to be calculated at different latitudes
            latitudes = [lat for lat in range(-60, 61, int(120/num_points))]
            for lat in latitudes:
                # Refine the longitude at this specific latitude
                lon = find_zodiacal_line_longitude(planet_lon, target_angle_offset, jd_ut, lat, house_system)
                if lon is not None:
                    points.append({'latitude': lat, 'longitude': lon})
    else:  # ASC or DSC
        # These curve significantly with latitude
        latitudes = [lat for lat in range(-60, 61, int(120/num_points)) if lat != 0]
        for lat in latitudes:
            lon = find_zodiacal_line_longitude(planet_lon, target_angle_offset, jd_ut, lat, house_system)
            if lon is not None:
                points.append({'latitude': lat, 'longitude': lon})

    return points

def calculate_astrocartography_lines_proper(jd_ut, birth_lat=None, birth_lon=None):
    """
    Calculate accurate astrocartography lines using Zodiacal method (Astro.com style).

    This method calculates where each planet conjuncts the ASC/MC/DSC/IC angles
    across different locations on Earth.

    Args:
        jd_ut: Julian Day in UTC
        birth_lat: Birth latitude (optional, used for Moon topocentric correction)
        birth_lon: Birth longitude (optional, used for Moon topocentric correction)

    Returns:
        List of line points for MC, IC, ASC, DSC for each planet
    """
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

    for planet_name, planet_id in planet_ids.items():
        # Get planet position in ECLIPTIC coordinates (longitude/latitude)
        # Use geocentric positions for all planets (matches Astro.com)
        result = swe.calc_ut(jd_ut, planet_id, swe.FLG_SPEED)

        planet_lon = result[0][0]  # Ecliptic longitude in degrees (0-360)
        planet_lat = result[0][1]  # Ecliptic latitude in degrees

        logger.info(f"  {planet_name}: Lon={planet_lon:.2f}°, Lat={planet_lat:.2f}°")

        # Calculate lines using Zodiacal method
        # 1. MC LINE (90° from ASC) - where planet conjuncts MC
        mc_points = calculate_zodiacal_line_points(planet_lon, 90, jd_ut, num_points=25)
        for point in mc_points:
            lines.append({
                'planet': planet_name,
                'line_type': 'MC',
                'latitude': point['latitude'],
                'longitude': point['longitude'],
                'planet_lon': planet_lon,
                'planet_lat': planet_lat
            })

        # 2. IC LINE (270° from ASC) - where planet conjuncts IC
        ic_points = calculate_zodiacal_line_points(planet_lon, 270, jd_ut, num_points=25)
        for point in ic_points:
            lines.append({
                'planet': planet_name,
                'line_type': 'IC',
                'latitude': point['latitude'],
                'longitude': point['longitude'],
                'planet_lon': planet_lon,
                'planet_lat': planet_lat
            })

        # 3. ASC LINE (0° from ASC) - where planet conjuncts ASC
        asc_points = calculate_zodiacal_line_points(planet_lon, 0, jd_ut, num_points=40)
        for point in asc_points:
            lines.append({
                'planet': planet_name,
                'line_type': 'ASC',
                'latitude': point['latitude'],
                'longitude': point['longitude'],
                'planet_lon': planet_lon,
                'planet_lat': planet_lat
            })

        # 4. DSC LINE (180° from ASC) - where planet conjuncts DSC
        dsc_points = calculate_zodiacal_line_points(planet_lon, 180, jd_ut, num_points=40)
        for point in dsc_points:
            lines.append({
                'planet': planet_name,
                'line_type': 'DSC',
                'latitude': point['latitude'],
                'longitude': point['longitude'],
                'planet_lon': planet_lon,
                'planet_lat': planet_lat
            })

    return lines

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
    """
    Calculate astrocartography lines for ley lines map.
    Uses proper UTC conversion to ensure lines are accurate.
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"🗺️  ASTROCARTOGRAPHY REQUEST")
    logger.info(f"{'='*60}")
    logger.info(f"Input - Date: {date}, Time: {time}")
    logger.info(f"Input - Birth Location: ({latitude}, {longitude})")

    try:
        date_parts = date.split("-")
        time_parts = time.split(":")
        year, month, day = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
        hour, minute = int(time_parts[0]), int(time_parts[1])
        second = int(time_parts[2]) if len(time_parts) > 2 else 0
    except Exception:
        raise HTTPException(400, detail="Invalid date or time format")

    # Convert local birth time to UTC (same fix as natal chart!)
    utc_info = convert_local_to_utc(year, month, day, hour, minute, second, latitude, longitude)

    # Use UTC Julian Day for all calculations
    jd_ut = utc_info['utc_jd']

    logger.info(f"🔬 Calculating astrocartography lines using Zodiacal method (Astro.com style)...")

    # Calculate astrocartography lines using Zodiacal method (matching Astro.com)
    lines = calculate_astrocartography_lines_proper(jd_ut, latitude, longitude)

    logger.info(f"✅ Astrocartography calculated: {len(lines)} lines found using Zodiacal method")
    logger.info(f"{'='*60}\n")

    return {
        "jd_ut": jd_ut,
        "input": {
            "date": date,
            "time": time,
            "latitude": latitude,
            "longitude": longitude
        },
        "timezone_info": {
            "timezone": utc_info['timezone_name'],
            "utc_offset_hours": utc_info['utc_offset_hours'],
            "local_datetime": utc_info['local_datetime_str'],
            "utc_datetime": utc_info['utc_datetime_str']
        },
        "lines": lines,
        "birth_location": {"latitude": latitude, "longitude": longitude}
    }