#!/usr/bin/env python3
"""
Test script to verify timezone conversion fix
Test case: Lionel, born December 4, 1987, 12:21 AM, Los Angeles, CA

Expected UTC: 1987-12-04 08:21:00 (PST is UTC-8)
Expected results should match Astro.com baseline
"""

from datetime import datetime
from timezonefinder import TimezoneFinder
import pytz
import swisseph as swe

# Set ephemeris path
swe.set_ephe_path('./ephe')

# Test case data
test_case = {
    'name': 'Lionel',
    'birth_date': '1987-12-04',
    'birth_time': '00:21:00',  # 12:21 AM
    'birth_place': 'Los Angeles, California, USA',
    'latitude': 34.0522,
    'longitude': -118.2437
}

# Expected Astro.com baseline values (in absolute longitude 0-360°)
# Sign positions: Aries=0°, Taurus=30°, Gemini=60°, Cancer=90°, Leo=120°, Virgo=150°
#                 Libra=180°, Scorpio=210°, Sagittarius=240°, Capricorn=270°, Aquarius=300°, Pisces=330°
expected_values = {
    'Sun': 240 + 11.63,        # 11°38' Sagittarius = 251.63°
    'Moon': 30 + 0.07,         # 0°04' Taurus = 30.07°
    'Mercury': 240 + 1.22,     # 1°13' Sagittarius = 241.22°
    'Venus': 270 + 7.78,       # 7°47' Capricorn = 277.78°
    'Mars': 210 + 6.68,        # 6°41' Scorpio = 216.68°
    'Jupiter': 0 + 19.97,      # 19°58' Aries = 19.97°
    'Saturn': 240 + 22.20,     # 22°12' Sagittarius = 262.20°
    'Uranus': 240 + 25.98,     # 25°59' Sagittarius = 265.98°
    'Neptune': 270 + 6.75,     # 6°45' Capricorn = 276.75°
    'Pluto': 210 + 11.13,      # 11°08' Scorpio = 221.13°
    'Ascendant': 150 + 21.25,  # 21°15' Virgo = 171.25°
    'MC': 60 + 20.45           # 20°27' Gemini = 80.45°
}

print("="*70)
print(f"🧪 TESTING TIMEZONE FIX")
print("="*70)
print(f"Test case: {test_case['name']}")
print(f"Birth: {test_case['birth_date']} at {test_case['birth_time']}")
print(f"Location: {test_case['birth_place']}")
print(f"Coordinates: ({test_case['latitude']}, {test_case['longitude']})")
print()

# Parse date/time
date_parts = test_case['birth_date'].split('-')
time_parts = test_case['birth_time'].split(':')
year, month, day = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
hour, minute, second = int(time_parts[0]), int(time_parts[1]), int(time_parts[2])

# Get timezone
tf = TimezoneFinder()
timezone_name = tf.timezone_at(lat=test_case['latitude'], lng=test_case['longitude'])
print(f"📍 Detected timezone: {timezone_name}")

# Create timezone-aware local datetime
local_tz = pytz.timezone(timezone_name)
naive_local_dt = datetime(year, month, day, hour, minute, second)
local_dt = local_tz.localize(naive_local_dt)

# Convert to UTC
utc_dt = local_dt.astimezone(pytz.UTC)
utc_offset_hours = local_dt.utcoffset().total_seconds() / 3600

print(f"🕐 Local datetime: {naive_local_dt.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"⏰ UTC offset: {utc_offset_hours:+.1f} hours ({timezone_name})")
print(f"🌐 UTC datetime: {utc_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
print(f"✅ Expected UTC: 1987-12-04 08:21:00 UTC")
print(f"   Match: {'✓ YES' if utc_dt.strftime('%Y-%m-%d %H:%M:%S') == '1987-12-04 08:21:00' else '✗ NO'}")
print()

# Calculate Julian Day
utc_hours = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
jd_ut = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_hours, swe.GREG_CAL)
print(f"📅 Julian Day (UT): {jd_ut}")
print()

# Calculate houses
houses, ascmc = swe.houses(jd_ut, test_case['latitude'], test_case['longitude'], b'P')
asc = ascmc[0]
mc = ascmc[1]

# Calculate planets
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

def degrees_to_dms(degrees):
    """Convert decimal degrees to degrees, minutes, seconds"""
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = int(((degrees - d) * 60 - m) * 60)
    return f"{d}°{m:02d}'{s:02d}\""

def get_zodiac_sign(degrees):
    """Get zodiac sign and position"""
    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    normalized = degrees % 360
    sign_index = int(normalized / 30)
    sign_degrees = normalized % 30
    return f"{signs[sign_index]} {degrees_to_dms(sign_degrees)}"

print("="*70)
print("🌟 CALCULATED PLANETARY POSITIONS")
print("="*70)

results = {}
for name, planet_id in planet_ids.items():
    result = swe.calc_ut(jd_ut, planet_id)
    longitude = result[0][0]
    results[name] = longitude

    expected = expected_values.get(name, 0)
    diff = abs(longitude - expected)
    match = "✓" if diff < 0.5 else "✗"  # Within 0.5 degree tolerance

    print(f"{name:10s}: {longitude:7.2f}° = {get_zodiac_sign(longitude):25s} | Expected: {expected:7.2f}° | Diff: {diff:5.2f}° {match}")

print()
print("="*70)
print("📐 CALCULATED ANGLES")
print("="*70)

# Check Ascendant
asc_diff = abs(asc - expected_values['Ascendant'])
asc_match = "✓" if asc_diff < 0.5 else "✗"
print(f"Ascendant : {asc:7.2f}° = {get_zodiac_sign(asc):25s} | Expected: {expected_values['Ascendant']:7.2f}° | Diff: {asc_diff:5.2f}° {asc_match}")

# Check MC
mc_diff = abs(mc - expected_values['MC'])
mc_match = "✓" if mc_diff < 0.5 else "✗"
print(f"MC        : {mc:7.2f}° = {get_zodiac_sign(mc):25s} | Expected: {expected_values['MC']:7.2f}° | Diff: {mc_diff:5.2f}° {mc_match}")

print()
print("="*70)
print("📊 SUMMARY")
print("="*70)

# Count matches
total_checks = len(planet_ids) + 2  # planets + ASC + MC
matches = sum(1 for name in planet_ids if abs(results[name] - expected_values[name]) < 0.5)
matches += 1 if asc_diff < 0.5 else 0
matches += 1 if mc_diff < 0.5 else 0

print(f"Timezone conversion: {'✓ CORRECT' if utc_dt.strftime('%Y-%m-%d %H:%M:%S') == '1987-12-04 08:21:00' else '✗ FAILED'}")
print(f"Planetary positions: {matches}/{total_checks} match Astro.com baseline (within 0.5°)")

if matches == total_checks:
    print("\n🎉 SUCCESS! All calculations match Astro.com baseline!")
    print("The timezone fix is working correctly.")
else:
    print(f"\n⚠️  Warning: {total_checks - matches} values don't match.")
    print("Note: Small differences may be due to different ephemeris data or house systems.")

print("="*70)
