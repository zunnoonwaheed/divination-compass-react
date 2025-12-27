from fastapi import FastAPI, Query, HTTPException
import os
import math
import requests
import swisseph as swe

app = FastAPI()
swe.set_ephe_path("./ephe")

FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED

PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
}

POINTS = {
    "MeanNode": swe.MEAN_NODE,
    "TrueNode": swe.TRUE_NODE,
    "Chiron": swe.CHIRON,
    "LilithMeanApogee": swe.MEAN_APOG,
    "LilithOscApogee": swe.OSCU_APOG,
}

MAJOR_ASTEROIDS = {
    "Ceres": swe.CERES,
    "Pallas": swe.PALLAS,
    "Juno": swe.JUNO,
    "Vesta": swe.VESTA,
}

MINOR_PLANETS_BY_NUMBER = {
    "Lilith_1181": 1181,
    "Eros_433": 433,
    "Psyche_16": 16,
    "Hygiea_10": 10,
    "Pholus_5145": 5145,
    "Nessus_7066": 7066,
    "Chariklo_10199": 10199,
    "Sappho_80": 80,
    "Amor_1221": 1221,
    "Valentine_447": 447,
    "Cupido_763": 763,
    "Eris_136199": 136199,
}

SIGNS = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"
]

@app.get("/")
def root():
    return {"status": "running", "endpoints": ["/chart", "/docs"]}

def norm360(x: float) -> float:
    x = x % 360.0
    return x + 360.0 if x < 0 else x

def lon_to_sign_deg(lon: float) -> dict:
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
    pos = swe.calc_ut(jd_ut, body_id, FLAGS)[0]
    lon = float(pos[0])
    spd = float(pos[3])
    out = lon_to_sign_deg(lon)
    out["speed"] = spd
    return out

def calc_minor_planet(jd_ut: float, number: int) -> dict:
    body_id = swe.AST_OFFSET + number
    pos = swe.calc_ut(jd_ut, body_id, FLAGS)[0]
    lon = float(pos[0])
    spd = float(pos[3])
    out = lon_to_sign_deg(lon)
    out["speed"] = spd
    out["number"] = number
    return out

def mapbox_geocode(city: str, state: str | None, country: str) -> tuple[float, float, str]:
    token = os.getenv("MAPBOX_TOKEN")
    if not token:
        raise HTTPException(status_code=500, detail="MAPBOX_TOKEN is not set in environment variables")

    query = f"{city}, {country}" if not state else f"{city}, {state}, {country}"
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{query}.json"
    try:
        r = requests.get(url, params={"access_token": token, "limit": 1}, timeout=10)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Mapbox request failed: {e}")

    if r.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Mapbox error {r.status_code}: {r.text[:200]}")

    data = r.json()
    features = data.get("features", [])
    if not features:
        raise HTTPException(status_code=404, detail=f"Location not found: {query}")

    center = features[0].get("center")
    place_name = features[0].get("place_name", query)

    if not center or len(center) != 2:
        raise HTTPException(status_code=502, detail="Mapbox response missing center coordinates")

    lon = float(center[0])
    lat = float(center[1])
    return lat, lon, place_name

@app.get("/chart")
def chart(
    year: int,
    month: int,
    day: int,
    hour: int = Query(0, ge=0, le=23),
    minute: int = Query(0, ge=0, le=59),
    second: int = Query(0, ge=0, le=59),
    tz_offset_hours: float = Query(0.0, description="Example: -5 for EST, -4 for EDT"),

    city: str = Query(..., description="Birth city, ex Los Angeles"),
    state: str | None = Query(None, description="Birth state/region, ex CA"),
    country: str = Query(..., description="Birth country, ex US or United States"),

    house_system: str = Query("P", description="P=Placidus, W=Whole Sign, K=Koch, O=Porphyry, R=Regiomontanus, C=Campanus, E=Equal"),
):
    lat, lon, place_name = mapbox_geocode(city=city, state=state, country=country)

    local_hours = hour + (minute / 60.0) + (second / 3600.0)
    ut_hours = local_hours - tz_offset_hours
    jd_ut = swe.julday(year, month, day, ut_hours, swe.GREG_CAL)

    hs = house_system[:1].upper()
    cusps, ascmc = swe.houses_ex(jd_ut, lat, lon, hs)

    houses = {f"House{i}": lon_to_sign_deg(float(cusps[i])) for i in range(1, 13)}
    angles = {
    "ASC": lon_to_sign_deg(float(ascmc[0])),
    "MC": lon_to_sign_deg(float(ascmc[1])),
    "DC": lon_to_sign_deg((float(ascmc[0]) + 180.0) % 360.0),
    "IC": lon_to_sign_deg((float(ascmc[1]) + 180.0) % 360.0),
    "Vertex": lon_to_sign_deg(float(ascmc[3])),
}


    bodies = {}
    for name, pid in PLANETS.items():
        bodies[name] = calc_body(jd_ut, pid)

    for name, pid in POINTS.items():
        bodies[name] = calc_body(jd_ut, pid)

    for name, pid in MAJOR_ASTEROIDS.items():
        bodies[name] = calc_body(jd_ut, pid)

    minor = {}
    for name, number in MINOR_PLANETS_BY_NUMBER.items():
        minor[name] = calc_minor_planet(jd_ut, number)

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
        "angles": angles,
        "houses": houses,
        "house12": houses["House12"],
        "bodies": bodies,
        "asteroids": minor,
    }
