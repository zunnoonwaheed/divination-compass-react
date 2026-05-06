# API Response Comparison: Before vs. After

## What Changed in the API Response

---

## BEFORE (Old Response)

```json
{
  "jd_ut": 2447893.208333,
  "input": { ... },
  "timezone_info": { ... },
  "planets": {
    "Sun": { "longitude": 281.0267, ... },
    "Moon": { "longitude": 336.0783, ... },
    "Mercury": { "longitude": 295.6072, ... },
    "Venus": { "longitude": 306.1939, ... },
    "Mars": { "longitude": 250.1467, ... },
    "Jupiter": { "longitude": 95.1208, ... },
    "Saturn": { "longitude": 285.6821, ... },
    "Uranus": { "longitude": 275.7979, ... },
    "Neptune": { "longitude": 282.0460, ... },
    "Pluto": { "longitude": 227.0988, ... }
  },
  "houses": [20.6649, 56.0753, ...],
  "ascendant": 20.6649,
  "mc": 281.1077
}
```

**Planet count:** 10 bodies

**Missing:**
- ❌ Chiron
- ❌ North Node
- ❌ South Node
- ❌ `house_system` field

---

## AFTER (New Response)

```json
{
  "jd_ut": 2447893.208333,
  "input": { ... },
  "timezone_info": { ... },
  "planets": {
    "Sun": { "longitude": 281.0267, ... },
    "Moon": { "longitude": 336.0783, ... },
    "Mercury": { "longitude": 295.6072, ... },
    "Venus": { "longitude": 306.1939, ... },
    "Mars": { "longitude": 250.1467, ... },
    "Jupiter": { "longitude": 95.1208, ... },
    "Saturn": { "longitude": 285.6821, ... },
    "Uranus": { "longitude": 275.7979, ... },
    "Neptune": { "longitude": 282.0460, ... },
    "Pluto": { "longitude": 227.0988, ... },
    "Chiron": { "longitude": 103.7990, ... },       // ✨ NEW
    "North Node": { "longitude": 316.8754, ... },    // ✨ NEW
    "South Node": { "longitude": 136.8754, ... }     // ✨ NEW
  },
  "houses": [20.6649, 56.0753, ...],
  "house_system": "P",    // ✨ NEW
  "ascendant": 20.6649,
  "mc": 281.1077
}
```

**Planet count:** 13 bodies

**Added:**
- ✅ Chiron (asteroid)
- ✅ North Node (lunar node)
- ✅ South Node (calculated as North Node + 180°)
- ✅ `house_system` field (shows which system was used)

---

## Detailed Planet Data Structure

Each planet object includes:

```json
{
  "longitude": 103.7990,    // Ecliptic longitude (0-360°)
  "latitude": -6.8234,      // Ecliptic latitude (-90 to +90°)
  "distance": 12.3456,      // Distance from Earth (AU)
  "speed": 0.0534           // Daily motion (degrees/day)
}
```

### Example: Chiron Data

```json
"Chiron": {
  "longitude": 103.7990,     // Position in zodiac
  "latitude": -6.8234,       // Ecliptic latitude
  "distance": 12.3456,       // Distance from Earth
  "speed": 0.0534            // Speed of movement
}
```

### Example: North Node Data

```json
"North Node": {
  "longitude": 316.8754,     // True node position
  "latitude": 0.0,           // Nodes are on ecliptic
  "distance": 0.0026,        // Very small (Earth-Moon distance)
  "speed": -0.0529           // Retrograde (negative speed)
}
```

### Example: South Node Data

```json
"South Node": {
  "longitude": 136.8754,     // Exactly 180° from North Node
  "latitude": 0.0,           // Opposite of North Node
  "distance": 0.0026,        // Same as North Node
  "speed": -0.0529           // Same as North Node
}
```

---

## New Query Parameter: `house_system`

### Usage

**Default (Placidus):**
```
GET /api/natal-chart?date=1990-01-01&time=12:00:00&latitude=40.7128&longitude=-74.0060
```

**Explicit Placidus:**
```
GET /api/natal-chart?date=1990-01-01&time=12:00:00&latitude=40.7128&longitude=-74.0060&house_system=P
```

**Koch House System:**
```
GET /api/natal-chart?date=1990-01-01&time=12:00:00&latitude=40.7128&longitude=-74.0060&house_system=K
```

**Whole Sign:**
```
GET /api/natal-chart?date=1990-01-01&time=12:00:00&latitude=40.7128&longitude=-74.0060&house_system=W
```

### Supported Values

| Code | House System      | Description                    |
|------|-------------------|--------------------------------|
| `P`  | Placidus          | Default, matches Astro.com     |
| `K`  | Koch              | Popular alternative            |
| `W`  | Whole Sign        | Ancient system                 |
| `E`  | Equal             | 30° per house from ASC         |
| `R`  | Regiomontanus     | Medieval system                |
| `C`  | Campanus          | Space-based division           |
| `A`  | Equal from ASC    | Equal from Ascendant           |
| `V`  | Vehlow Equal      | Equal from middle of 1st house |

---

## Breaking Changes

**✅ NONE!** This is a **non-breaking change**.

- Existing API calls continue to work
- Default behavior is unchanged (Placidus)
- Only new fields added (backward compatible)
- Frontend can ignore new fields if not ready

---

## Migration Guide for Frontend

### Step 1: Update TypeScript Types (Optional but Recommended)

```typescript
// Before
interface PlanetPositions {
  Sun: PlanetData;
  Moon: PlanetData;
  Mercury: PlanetData;
  Venus: PlanetData;
  Mars: PlanetData;
  Jupiter: PlanetData;
  Saturn: PlanetData;
  Uranus: PlanetData;
  Neptune: PlanetData;
  Pluto: PlanetData;
}

// After
interface PlanetPositions {
  Sun: PlanetData;
  Moon: PlanetData;
  Mercury: PlanetData;
  Venus: PlanetData;
  Mars: PlanetData;
  Jupiter: PlanetData;
  Saturn: PlanetData;
  Uranus: PlanetData;
  Neptune: PlanetData;
  Pluto: PlanetData;
  Chiron: PlanetData;         // ← NEW
  'North Node': PlanetData;   // ← NEW
  'South Node': PlanetData;   // ← NEW
}

interface NatalChartResponse {
  // ... existing fields
  house_system: string;  // ← NEW
}
```

### Step 2: Add Glyphs for New Bodies

```typescript
const PLANET_GLYPHS = {
  'Sun': '☉',
  'Moon': '☽',
  'Mercury': '☿',
  'Venus': '♀',
  'Mars': '♂',
  'Jupiter': '♃',
  'Saturn': '♄',
  'Uranus': '♅',
  'Neptune': '♆',
  'Pluto': '♇',
  'Chiron': '⚷',      // ← NEW
  'North Node': '☊',   // ← NEW
  'South Node': '☋'    // ← NEW
};
```

### Step 3: Update Rendering Logic

```typescript
// Before
const planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars',
                 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto'];

// After
const planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars',
                 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto',
                 'Chiron', 'North Node', 'South Node'];  // ← ADDED

planets.forEach(planet => {
  const data = chartData.planets[planet];
  renderPlanet(planet, data);
});
```

### Step 4: Display House System (Optional)

```typescript
// Show which house system was used
const houseSystemNames = {
  'P': 'Placidus',
  'K': 'Koch',
  'W': 'Whole Sign',
  'E': 'Equal',
  'R': 'Regiomontanus'
};

const systemName = houseSystemNames[chartData.house_system] || chartData.house_system;
console.log(`House system: ${systemName}`);
```

---

## Testing the Changes

### Test Request

```bash
curl "http://localhost:8000/api/natal-chart?date=1990-01-01&time=12:00:00&latitude=40.7128&longitude=-74.0060" \
  | python3 -m json.tool
```

### Verification Checklist

Check the response includes:

- [ ] `"Chiron"` object with longitude, latitude, distance, speed
- [ ] `"North Node"` object with data
- [ ] `"South Node"` object with data
- [ ] `"house_system": "P"` field
- [ ] South Node longitude = (North Node longitude + 180) % 360

### Quick Verification Script

```javascript
// In browser console or Node.js
fetch('http://localhost:8000/api/natal-chart?date=1990-01-01&time=12:00:00&latitude=40.7128&longitude=-74.0060')
  .then(r => r.json())
  .then(data => {
    console.log('Chiron:', data.planets.Chiron ? '✅' : '❌');
    console.log('North Node:', data.planets['North Node'] ? '✅' : '❌');
    console.log('South Node:', data.planets['South Node'] ? '✅' : '❌');
    console.log('House System:', data.house_system || '❌');

    // Verify South Node is 180° from North Node
    const northLon = data.planets['North Node'].longitude;
    const southLon = data.planets['South Node'].longitude;
    const expected = (northLon + 180) % 360;
    const diff = Math.abs(southLon - expected);
    console.log('South Node 180° check:', diff < 0.01 ? '✅' : `❌ (off by ${diff}°)`);
  });
```

---

## Expected Output

```
Chiron: ✅
North Node: ✅
South Node: ✅
House System: P
South Node 180° check: ✅
```

---

## Astrocartography Changes

The `/api/astrocartography` endpoint now also includes ley lines for:

- Chiron ASC/DSC/MC/IC lines
- North Node ASC/DSC/MC/IC lines

**Note:** South Node lines are not typically used in astrocartography, so they are not included in the map lines.

---

## Summary

| Feature | Before | After | Impact |
|---------|--------|-------|--------|
| Planet count | 10 | 13 | ✨ Added 3 bodies |
| Chiron | ❌ Missing | ✅ Included | New data |
| North Node | ❌ Missing | ✅ Included | New data |
| South Node | ❌ Missing | ✅ Calculated | New data |
| House system in response | ❌ Missing | ✅ Included | Transparency |
| House system parameter | ❌ No | ✅ Yes | Flexibility |
| Breaking changes | - | - | ✅ None |

---

**All changes are backward compatible and ready for production!** 🚀
