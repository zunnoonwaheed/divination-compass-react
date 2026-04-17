"""
Test script for Lionel baseline case to verify timezone handling and planet positions.

Expected Astro.com baseline values:
- Birth: December 4, 1987, 12:21 AM PST (Los Angeles)
- Expected UTC: 1987-12-04 08:21:00 UTC
- UTC offset: -8 hours (PST, not PDT)

Planet positions from Astro.com:
- Sun: 11°38' Sagittarius
- Moon: 0°04' Taurus
- Mercury: 1°13' Sagittarius
- Venus: 7°47' Capricorn
- Mars: 6°41' Scorpio
- Jupiter: 19°58' Aries
- Saturn: 22°12' Sagittarius
- Uranus: 25°59' Sagittarius
- Neptune: 6°45' Capricorn
- Pluto: 11°08' Scorpio
- Ascendant: 21°15' Virgo
- MC: 20°27' Gemini
"""

import swisseph as swe
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder

# Set ephemeris path
swe.set_ephe_path('./ephe')

# Test case parameters
YEAR = 1987
MONTH = 12
DAY = 4
HOUR = 0  # 12:21 AM = 00:21
MINUTE = 21
SECOND = 0

# Los Angeles coordinates
LATITUDE = 34.0522
LONGITUDE = -118.2437

print("=" * 80)
print("LIONEL BASELINE TEST CASE")
print("=" * 80)
print(f"Birth Date: December {DAY}, {YEAR}")
print(f"Birth Time: {HOUR:02d}:{MINUTE:02d}:{SECOND:02d} (local)")
print(f"Birth Place: Los Angeles, CA ({LATITUDE}, {LONGITUDE})")
print()

# Step 1: Get timezone from coordinates
tf = TimezoneFinder()
timezone_name = tf.timezone_at(lat=LATITUDE, lng=LONGITUDE)
print(f"📍 Detected timezone: {timezone_name}")

# Step 2: Create timezone-aware datetime
local_tz = pytz.timezone(timezone_name)
naive_local_dt = datetime(YEAR, MONTH, DAY, HOUR, MINUTE, SECOND)
print(f"🕐 Input local datetime: {naive_local_dt}")

# Step 3: Localize to birth location timezone
local_dt = local_tz.localize(naive_local_dt)
print(f"🌍 Localized datetime: {local_dt}")
print(f"   Timezone name: {local_dt.tzname()}")

# Step 4: Get UTC offset
utc_offset_seconds = local_dt.utcoffset().total_seconds()
utc_offset_hours = utc_offset_seconds / 3600
print(f"⏰ UTC offset: {utc_offset_hours:+.1f} hours ({local_dt.tzname()})")

# Step 5: Convert to UTC
utc_dt = local_dt.astimezone(pytz.UTC)
print(f"🌐 Converted UTC datetime: {utc_dt}")
print()

# Expected vs Actual comparison
print("EXPECTED vs ACTUAL:")
print(f"  Expected timezone: PST (Pacific Standard Time)")
print(f"  Actual timezone: {local_dt.tzname()}")
print(f"  Expected UTC offset: -8.0 hours")
print(f"  Actual UTC offset: {utc_offset_hours:+.1f} hours")
print(f"  Expected UTC: 1987-12-04 08:21:00 UTC")
print(f"  Actual UTC: {utc_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
print()

# Step 6: Calculate Julian Day
utc_hours = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
jd_ut = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_hours, swe.GREG_CAL)
print(f"📅 Julian Day (UT): {jd_ut}")
print()

# Step 7: Calculate planets and angles
print("=" * 80)
print("PLANET POSITIONS")
print("=" * 80)

# Helper function to convert longitude to sign notation
def longitude_to_sign(lon):
    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    sign_index = int(lon // 30)
    degrees = lon % 30
    minutes = (degrees % 1) * 60
    return f"{int(degrees)}°{int(minutes):02d}' {signs[sign_index]}"

# Expected values from Astro.com (in decimal degrees)
expected = {
    'Sun': (11 + 38/60) + 240,  # 11°38' Sagittarius (Sagittarius starts at 240°)
    'Moon': (0 + 4/60) + 30,    # 0°04' Taurus (Taurus starts at 30°)
    'Mercury': (1 + 13/60) + 240,  # 1°13' Sagittarius
    'Venus': (7 + 47/60) + 270,    # 7°47' Capricorn (Capricorn starts at 270°)
    'Mars': (6 + 41/60) + 210,     # 6°41' Scorpio (Scorpio starts at 210°)
    'Jupiter': (19 + 58/60) + 0,   # 19°58' Aries (Aries starts at 0°)
    'Saturn': (22 + 12/60) + 240,  # 22°12' Sagittarius
    'Uranus': (25 + 59/60) + 240,  # 25°59' Sagittarius
    'Neptune': (6 + 45/60) + 270,  # 6°45' Capricorn
    'Pluto': (11 + 8/60) + 210,    # 11°08' Scorpio
}

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

print(f"{'Planet':<10} {'Calculated':<25} {'Expected':<25} {'Diff':<10}")
print("-" * 80)

for name, planet_id in planet_ids.items():
    result = swe.calc_ut(jd_ut, planet_id)
    calculated_lon = result[0][0]
    expected_lon = expected[name]
    diff = calculated_lon - expected_lon

    print(f"{name:<10} {longitude_to_sign(calculated_lon):<25} {longitude_to_sign(expected_lon):<25} {diff:+.4f}°")

print()
print("=" * 80)
print("ANGLES (ASCENDANT & MC)")
print("=" * 80)

# Calculate houses for Ascendant and MC
houses, ascmc = swe.houses(jd_ut, LATITUDE, LONGITUDE, b'P')  # Placidus system

ascendant = ascmc[0]
mc = ascmc[1]

# Expected angles from Astro.com
expected_asc = (21 + 15/60) + 150  # 21°15' Virgo (Virgo starts at 150°)
expected_mc = (20 + 27/60) + 60    # 20°27' Gemini (Gemini starts at 60°)

print(f"{'Angle':<10} {'Calculated':<25} {'Expected':<25} {'Diff':<10}")
print("-" * 80)
print(f"{'Ascendant':<10} {longitude_to_sign(ascendant):<25} {longitude_to_sign(expected_asc):<25} {ascendant - expected_asc:+.4f}°")
print(f"{'MC':<10} {longitude_to_sign(mc):<25} {longitude_to_sign(expected_mc):<25} {mc - expected_mc:+.4f}°")

print()
print("=" * 80)
print("ANALYSIS")
print("=" * 80)

# Calculate maximum deviation
all_diffs = [
    abs(swe.calc_ut(jd_ut, planet_ids[name])[0][0] - expected[name])
    for name in planet_ids.keys()
]
all_diffs.append(abs(ascendant - expected_asc))
all_diffs.append(abs(mc - expected_mc))

max_diff = max(all_diffs)
avg_diff = sum(all_diffs) / len(all_diffs)

print(f"Maximum deviation: {max_diff:.4f}°")
print(f"Average deviation: {avg_diff:.4f}°")
print()

if max_diff < 0.1:
    print("✅ EXCELLENT: All positions match within 0.1° (6 arcminutes)")
elif max_diff < 0.5:
    print("✅ GOOD: All positions match within 0.5° (30 arcminutes)")
elif max_diff < 1.0:
    print("⚠️  ACCEPTABLE: Positions match within 1° but should be better")
else:
    print("❌ PROBLEM: Positions deviate by more than 1° - timezone conversion likely incorrect")

print("=" * 80)
