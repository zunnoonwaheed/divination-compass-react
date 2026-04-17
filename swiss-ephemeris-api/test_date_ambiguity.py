"""
Test if there's a date ambiguity issue
"""

import swisseph as swe
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder

swe.set_ephe_path('./ephe')

def test_date(year, month, day, hour, minute):
    """Test a specific date/time"""
    LATITUDE = 34.0522
    LONGITUDE = -118.2437

    # Get timezone and convert to UTC
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=LATITUDE, lng=LONGITUDE)
    local_tz = pytz.timezone(tz_name)
    naive_dt = datetime(year, month, day, hour, minute, 0)
    local_dt = local_tz.localize(naive_dt)
    utc_dt = local_dt.astimezone(pytz.UTC)

    # Calculate JD
    utc_hours = utc_dt.hour + utc_dt.minute / 60.0
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_hours, swe.GREG_CAL)

    # Get Moon
    moon_lon = swe.calc_ut(jd, swe.MOON)[0][0]

    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    sign_idx = int(moon_lon // 30)
    deg = moon_lon % 30
    min = (deg % 1) * 60

    return {
        'local': f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d} {local_dt.tzname()}",
        'utc': utc_dt.strftime('%Y-%m-%d %H:%M UTC'),
        'jd': jd,
        'moon': f"{int(deg)}°{int(min):02d}' {signs[sign_idx]}",
        'moon_lon': moon_lon,
        'diff_from_expected': moon_lon - 30.0667  # 0°04' Taurus
    }

print("=" * 90)
print("TESTING DIFFERENT DATE/TIME INTERPRETATIONS")
print("=" * 90)
print()

expected_moon = 30.0667  # 0°04' Taurus

tests = [
    ("Dec 3, 00:21", 1987, 12, 3, 0, 21),
    ("Dec 4, 00:21", 1987, 12, 4, 0, 21),
    ("Dec 5, 00:21", 1987, 12, 5, 0, 21),
    ("Dec 3, 12:21 PM", 1987, 12, 3, 12, 21),
    ("Dec 4, 12:21 PM", 1987, 12, 4, 12, 21),
]

print(f"{'Date/Time':<20} {'Local Time':<30} {'UTC Time':<25} {'Moon Position':<20} {'Diff':<10}")
print("-" * 125)

best_match = None
best_diff = float('inf')

for label, year, month, day, hour, minute in tests:
    result = test_date(year, month, day, hour, minute)
    diff = abs(result['diff_from_expected'])

    marker = ""
    if diff < abs(best_diff):
        best_diff = result['diff_from_expected']
        best_match = label
        marker = " ← BEST MATCH"

    print(f"{label:<20} {result['local']:<30} {result['utc']:<25} {result['moon']:<20} {result['diff_from_expected']:+7.2f}°{marker}")

print()
print("=" * 90)
print(f"CONCLUSION: Best match is {best_match} with Moon position difference of {best_diff:+.2f}°")
print("=" * 90)

if abs(best_diff) < 1.0:
    print("✅ FOUND IT! This date/time interpretation matches Astro.com!")
else:
    print("❌ None of these interpretations match. The issue must be something else.")
    print()
    print("Other possibilities to check:")
    print("  1. Different ephemeris data files")
    print("  2. Ayanamsa setting (sidereal vs tropical)")
    print("  3. Different Swiss Ephemeris version")
    print("  4. User may have provided wrong expected values")
