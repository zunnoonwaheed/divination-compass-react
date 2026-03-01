from fastapi import Request
from anthropic import Anthropic

anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

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
```

**Then in Railway**, make sure you have these environment variables set:
- `MAPBOX_TOKEN` — your Mapbox key
- `ANTHROPIC_API_KEY` — your Anthropic key (needed for `/api/generate-astrology`)

Also add `anthropic` to your `requirements.txt` in GitHub:
```
anthropic
