from fastapi import FastAPI, Query, HTTPException
import os
import logging
import requests
import swisseph as swe

logging.basicConfig(level=logging.DEBUG)

# Initialise FastAPI and Swiss Ephemeris
app = FastAPI(debug=True)
swe.set_ephe_path("./ephe")
FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED

# Define constants for planets, points and asteroids
PLANETS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY,
    "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN, "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
}
POINTS = {
    "MeanNode": swe.MEAN_NODE, "TrueNode": swe.TRUE_NODE,
    "Chiron": swe.CHIRON, "LilithMeanApogee": swe.MEAN_APOG,
    "LilithOscApogee": swe.OSCU_APOG,
}
MAJOR_ASTEROIDS = {
    "Ceres": swe.CERES, "Pallas": swe.PALLAS,
    "Juno": swe.JUNO, "Vesta": swe.VESTA,
}
MINOR_PLANETS_BY_NUMBER = {
    "Lilith_1181": 1181, "Eros_433": 433, "Psyche_16": 16, "Hygiea_10": 10,
    "Pholus_5145": 5145, "Nessus_7066": 7066, "Chariklo_10199": 10199,
    "Sappho_80": 80, "Amor_1221": 1221, "Valentine_447": 447,
    "Cupido_763": 763, "Eris_136199": 136199,
}
SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

@app.get("/")
def root():
    """Health-check endpoint listing available routes and environment status."""
    return {
        "status": "running",
        "endpoints": ["/chart", "/api/natalchart-city", "/api/natalchart-latlon"],
        "env": {"MAPBOX_TOKEN_SET": bool(os.getenv("MAPBOX_TOKEN"))},
    }

def norm360(x: float) -> float:
    """Normalize an angle to the 0–360° range."""
    x %= 360.0
    return x + 360.0 if x < 0 else x

def lon_to_sign_deg(lon: float) -> dict:
    """
    Convert an ecliptic longitude into zodiac sign and degree information.
    Returns a dict with total longitude, sign name, degrees within the sign and minutes.
    """
    lon = norm360(lon)
    sign_index = int(lon // 30)
    deg_in_sign = lon - (sign_index * 30)
    deg = int(deg_in_sign)
    minutes = int(round((deg_in_sign - deg) * 60))
    if minutes == 60:
        minutes = 0
        deg += 1
        if deg == 30:
            deg = 0
            sign_index = (sign_index + 1) % 12
    return {"lon": lon, "sign": SIGNS[sign_index], "deg": deg, "min": minutes}

def calc_body(jd_ut: float, body_id: int) -> dict:
    """
    Compute longitude and speed for a given celestial body.
    Some objects do not have speed data; in that case speed is set to 0.0.
    """
    try:
        xx, _flags = swe.calc_ut(jd_ut, body_id, FLAGS)
        lon = float(xx[0])
        speed = float(xx[3]) if len(xx) > 3 else 0.0
        out = lon_to_sign_deg(lon)
        out["speed"] = speed
        return out
    except Exception as e:
        logging.error(f"calc_body error for body_id {body_id}: {e}")
        raise HTTPException(500, detail=f"Ephemeris error for body_id {body_id}")

def calc_minor_planet(jd_ut: float, number: int) -> dict:
    """
    Compute longitude and speed for a minor planet.
    Some minor planets may not have speed data; in that case speed is set to 0.0.
    """
    try:
        body_id = swe.AST_OFFSET + number
        xx, _flags = swe.calc_ut(jd_ut, body_id, FLAGS)
        lon = float(xx[0])
        speed = float(xx[3]) if len(xx) > 3 else 0.0
        out = lon_to_sign_deg(lon)
        out["speed"] = speed
        out["number"] = number
        return out
    except Exception as e:
        logging.error(f"calc_minor_planet error for number {number}: {e}")
        raise HTTPException(500, detail=f"Ephemeris error for minor planet {number}")

def mapbox_geocode(city: str, state: str | None, country: str) -> tuple[float, float, str]:
    """
    Use the Mapbox Geocoding API to convert a city/state/country into lat/lon coordinates.
    Requires a MAPBOX_TOKEN environment variable.
    """
    token = os.getenv("MAPBOX_TOKEN")
    if not token:
        raise HTTPException(status_code=500, detail="MAPBOX_TOKEN is not set in environment variables")
    query = f"{city}, {country}" if not state else f"{city}, {state}, {country}"
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{query}.json"
    try:
        r = requests.get(url, params={"access_token": token, "limit": 1}, timeout=10)
    except requests.RequestException as e:
        logging.error(f"Mapbox request failed: {e}")
        raise HTTPException(502, detail=f"Mapbox request failed: {e}")
    if r.status_code != 200:
        raise HTTPException(502, detail=f"Mapbox error {r.status_code}: {r.text[:200]}")
    data = r.json()
    features = data.get("features", [])
    if not features:
        raise HTTPException(404, detail=f"Location not found: {query}")
    center = features[0].get("center")
    place_name = features[0].get("place_name", query)
    if not center or len(center) != 2:
        raise HTTPException(502, detail="Mapbox response missing center coordinates")
    lon = float(center[0])
    lat = float(center[1])
    return lat, lon, place_name

def compute_chart(jd_ut: float, lat: float, lon: float, hs: str) -> dict:
    """
    Compute houses, angles, planet and asteroid positions for a given Julian Day and location.
    `hs` is the house system code (e.g. 'P' for Placidus) and is converted to a one‑byte ASCII string:contentReference[oaicite:1]{index=1}.
    """
    # Ensure a single uppercase character and convert to bytes
    hs_byte = hs[:1].upper().encode("ascii")
    cusps, ascmc = swe.houses_ex(jd_ut, lat, lon, hs_byte)
    houses = {f"House{i}": lon_to_sign_deg(float(cusps[i])) for i in range(1, 13)}
    angles = {
        "ASC": lon_to_sign_deg(float(ascmc[0])),
        "MC":  lon_to_sign_deg(float(ascmc[1])),
        "DC":  lon_to_sign_deg((float(ascmc[0]) + 180.0) % 360.0),
        "IC":  lon_to_sign_deg((float(ascmc[1]) + 180.0) % 360.0),
        "Vertex": lon_to_sign_deg(float(ascmc[3])),
    }
    bodies = {
        **{k: calc_body(jd_ut, v) for k, v in PLANETS.items()},
        **{k: calc_body(jd_ut, v) for k, v in POINTS.items()},
        **{k: calc_body(jd_ut, v) for k, v in MAJOR_ASTEROIDS.items()},
    }
    minor = {k: calc_minor_planet(jd_ut, v) for k, v in MINOR_PLANETS_BY_NUMBER.items()}
    return {
        "angles": angles,
        "houses": houses,
        "house12": houses["House12"],
        "bodies": bodies,
        "asteroids": minor,
    }

@app.get("/chart")
def chart(
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
    tz_offset_hours: float = 0.0,
    city: str = Query(...),
    state: str | None = None,
    country: str = Query(...),
    house_system: str = Query("P"),
):
    """Compute a natal chart using a location string.  Returns a full chart dict with input metadata."""
    lat, lon, place_name = mapbox_geocode(city, state, country)
    local_hours = hour + minute / 60.0 + second / 3600.0
    ut_hours = local_hours - tz_offset_hours
    jd_ut = swe.julday(year, month, day, ut_hours, swe.GREG_CAL)
    hs = house_system[:1].upper()
    chart_data = compute_chart(jd_ut, lat, lon, hs)
    return {
        "jd_ut": jd_ut,
        "input": {
            "date": f"{year:04d}-{month:02d}-{day:02d}",
            "time_local": f"{hour:02d}:{minute:02d}:{second:02d}",
            "tz_offset_hours": tz_offset_hours,
            "birth_place_input": {"city": city, "state": state, "country": country},
            "birth_place_resolved": {"place_name": place_name, "lat": lat, "lon": lon},
            "house_system": hs,
        },
        **chart_data,
    }

@app.get("/api/natalchart-city")
def natalchart_city(
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
    tz_offset_hours: float = 0.0,
    city: str = Query(...),
    state: str | None = None,
    country: str = Query(...),
    house_system: str = Query("P"),
):
    """Proxy endpoint forwarding parameters to /chart for clients that prefer flat URLs."""
    return chart(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        second=second,
        tz_offset_hours=tz_offset_hours,
        city=city,
        state=state,
        country=country,
        house_system=house_system,
    )

@app.get("/api/natalchart-latlon")
def natalchart_latlon(
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
    tz_offset_hours: float = 0.0,
    lat: float = Query(...),
    lon: float = Query(...),
    house_system: str = Query("P"),
):
    """Compute a chart directly from latitude and longitude without geocoding."""
    local_hours = hour + minute / 60.0 + second / 3600.0
    ut_hours = local_hours - tz_offset_hours
    jd_ut = swe.julday(year, month, day, ut_hours, swe.GREG_CAL)
    hs = house_system[:1].upper()
    chart_data = compute_chart(jd_ut, lat, lon, hs)
    return {
        "jd_ut": jd_ut,
        "input": {
            "date": f"{year:04d}-{month:02d}-{day:02d}",
            "time_local": f"{hour:02d}:{minute:02d}:{second:02d}",
            "tz_offset_hours": tz_offset_hours,
            "lat": lat,
            "lon": lon,
            "house_system": hs,
        },
        **chart_data,
    }

if __name__ == "__main__":
    # Local development server entrypoint. Railway will use uvicorn automatically.
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True, log_level="debug")
