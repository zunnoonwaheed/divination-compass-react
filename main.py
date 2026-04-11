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

def calculate_mc_line_longitude(planet_ra, jd_ut):
    """
    Calculate longitude where planet is on MC (Midheaven).

    MC line formula: Longitude = (Planet RA - RAMC at Greenwich) * 15
    where RAMC = Right Ascension of MC

    Args:
        planet_ra: Planet's Right Ascension in degrees
        jd_ut: Julian Day in UTC

    Returns:
        Longitude in degrees (-180 to 180)
    """
    # Get sidereal time at Greenwich
    # swe.sidtime returns sidereal time in hours
    gmst_hours = swe.sidtime(jd_ut)  # Greenwich Mean Sidereal Time in hours
    gmst_degrees = gmst_hours * 15.0  # Convert hours to degrees

    # MC line: where planet's RA equals RAMC
    # Longitude = Planet RA - RAMC (in degrees)
    mc_longitude = planet_ra - gmst_degrees

    # Normalize to -180 to 180
    while mc_longitude > 180:
        mc_longitude -= 360
    while mc_longitude < -180:
        mc_longitude += 360

    return mc_longitude

def calculate_asc_line_points(planet_ra, planet_dec, jd_ut, num_points=50):
    """
    Calculate points along the Ascendant line for a planet.

    ASC line is where the planet is rising on the eastern horizon.
    This requires solving for longitude at each latitude using oblique ascension.

    Args:
        planet_ra: Planet's Right Ascension in degrees
        planet_dec: Planet's Declination in degrees
        jd_ut: Julian Day in UTC
        num_points: Number of points to calculate along the line

    Returns:
        List of (latitude, longitude) tuples
    """
    points = []

    # Get obliquity of ecliptic (Earth's axial tilt)
    obliquity = swe.calc_ut(jd_ut, swe.ECL_NUT)[0][0]  # Mean obliquity

    # Calculate for latitudes from -60 to 60 (beyond this, calculations get unreliable)
    latitudes = [lat for lat in range(-60, 61, int(120/num_points)) if lat != 0]

    for lat in latitudes:
        try:
            # For ASC line, we need to find longitude where planet is on eastern horizon
            # This involves calculating the Local Sidereal Time when planet rises

            # Calculate oblique ascension (OA) for this planet at this latitude
            # OA depends on planet's RA, Dec, and observer's latitude

            lat_rad = math.radians(lat)
            dec_rad = math.radians(planet_dec)

            # Check if planet is circumpolar or never rises at this latitude
            if abs(planet_dec) + abs(lat) > 90:
                # Planet may be circumpolar (always up) or never visible
                if (planet_dec > 0 and lat > 0) or (planet_dec < 0 and lat < 0):
                    # Similar hemisphere - might be circumpolar
                    if abs(lat) + abs(planet_dec) > 90:
                        continue  # Skip this latitude

            # Calculate hour angle when planet is on horizon
            # cos(H) = -tan(lat) * tan(dec)
            cos_h = -math.tan(lat_rad) * math.tan(dec_rad)

            if abs(cos_h) > 1:
                # Planet never rises or never sets at this latitude
                continue

            # Hour angle in degrees
            hour_angle = math.degrees(math.acos(cos_h))

            # Local Sidereal Time when planet rises = RA - Hour Angle
            lst_rise = planet_ra - hour_angle

            # Get Greenwich Sidereal Time
            gmst_hours = swe.sidtime(jd_ut)
            gmst_degrees = gmst_hours * 15.0

            # Longitude = LST - GST (when planet is rising)
            longitude = lst_rise - gmst_degrees

            # Normalize to -180 to 180
            while longitude > 180:
                longitude -= 360
            while longitude < -180:
                longitude += 360

            points.append({'latitude': lat, 'longitude': longitude})

        except (ValueError, ZeroDivisionError):
            # Skip problematic latitudes
            continue

    return points

def calculate_astrocartography_lines_proper(jd_ut):
    """
    Calculate accurate astrocartography lines using spherical astronomy.

    Returns lines for MC, IC, ASC, DSC for each planet.
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
        # Get planet position in EQUATORIAL coordinates (RA/Dec)
        # SEFLG_EQUATORIAL = 2048
        result_eq = swe.calc_ut(jd_ut, planet_id, swe.FLG_EQUATORIAL)

        planet_ra = result_eq[0][0]   # Right Ascension in degrees (0-360)
        planet_dec = result_eq[0][1]  # Declination in degrees (-90 to +90)

        logger.info(f"  {planet_name}: RA={planet_ra:.2f}°, Dec={planet_dec:.2f}°")

        # 1. MC LINE (Midheaven) - vertical line where planet culminates
        mc_lon = calculate_mc_line_longitude(planet_ra, jd_ut)

        # MC line is a meridian (vertical line) - generate points at different latitudes
        for lat in range(-60, 61, 5):
            lines.append({
                'planet': planet_name,
                'line_type': 'MC',
                'latitude': lat,
                'longitude': mc_lon,
                'planet_ra': planet_ra,
                'planet_dec': planet_dec
            })

        # 2. IC LINE (Imum Coeli) - opposite of MC (180° away)
        ic_lon = mc_lon + 180 if mc_lon < 0 else mc_lon - 180

        for lat in range(-60, 61, 5):
            lines.append({
                'planet': planet_name,
                'line_type': 'IC',
                'latitude': lat,
                'longitude': ic_lon,
                'planet_ra': planet_ra,
                'planet_dec': planet_dec
            })

        # 3. ASC LINE (Ascendant) - curved line where planet rises
        asc_points = calculate_asc_line_points(planet_ra, planet_dec, jd_ut)
        for point in asc_points:
            lines.append({
                'planet': planet_name,
                'line_type': 'ASC',
                'latitude': point['latitude'],
                'longitude': point['longitude'],
                'planet_ra': planet_ra,
                'planet_dec': planet_dec
            })

        # 4. DSC LINE (Descendant) - opposite of ASC (where planet sets)
        # DSC is 180° opposite in longitude from ASC
        for point in asc_points:
            dsc_lon = point['longitude'] + 180 if point['longitude'] < 0 else point['longitude'] - 180
            lines.append({
                'planet': planet_name,
                'line_type': 'DSC',
                'latitude': point['latitude'],
                'longitude': dsc_lon,
                'planet_ra': planet_ra,
                'planet_dec': planet_dec
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

    logger.info(f"🔬 Calculating planetary RA/Dec for astrocartography...")

    # Calculate proper astrocartography lines using spherical astronomy
    lines = calculate_astrocartography_lines_proper(jd_ut)

    logger.info(f"✅ Astrocartography calculated: {len(lines)} lines found using proper spherical astronomy")
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