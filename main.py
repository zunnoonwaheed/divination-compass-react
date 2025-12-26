import swisseph as swe
from fastapi import FastAPI

app = FastAPI()

swe.set_ephe_path("./ephe")

@app.get("/")
def root():
    return {"status": "Swiss Ephemeris API running"}

@app.get("/natal")
def natal(jd: float):
    planets = {
        "Sun": swe.calc_ut(jd, swe.SUN)[0][0],
        "Moon": swe.calc_ut(jd, swe.MOON)[0][0],
        "Mercury": swe.calc_ut(jd, swe.MERCURY)[0][0],
        "Venus": swe.calc_ut(jd, swe.VENUS)[0][0],
        "Mars": swe.calc_ut(jd, swe.MARS)[0][0],
        "Jupiter": swe.calc_ut(jd, swe.JUPITER)[0][0],
        "Saturn": swe.calc_ut(jd, swe.SATURN)[0][0],
    }
    return planets
