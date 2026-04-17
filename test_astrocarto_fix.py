"""
Test the corrected astrocartography calculations
"""

import sys
sys.path.insert(0, './swiss-ephemeris-api')

from main import convert_local_to_utc, calculate_astrocartography_lines_proper, compute_chart

# Lionel's birth data (from test_lionel_baseline.py)
YEAR = 1987
MONTH = 12
DAY = 4
HOUR = 0  # 12:21 AM
MINUTE = 21
SECOND = 0
LATITUDE = 34.0522  # Los Angeles
LONGITUDE = -118.2437

print("=" * 80)
print("TESTING CORRECTED ASTROCARTOGRAPHY CALCULATIONS")
print("=" * 80)
print(f"Birth: December {DAY}, {YEAR} at {HOUR:02d}:{MINUTE:02d}:{SECOND:02d}")
print(f"Location: Los Angeles ({LATITUDE}, {LONGITUDE})")
print()

# Convert to UTC
utc_info = convert_local_to_utc(YEAR, MONTH, DAY, HOUR, MINUTE, SECOND, LATITUDE, LONGITUDE)
jd_ut = utc_info['utc_jd']

print(f"Julian Day: {jd_ut}")
print(f"UTC Time: {utc_info['utc_datetime_str']}")
print()

# Test natal chart first (to verify Moon position)
print("=" * 80)
print("NATAL CHART (testing Moon topocentric correction)")
print("=" * 80)

chart = compute_chart(jd_ut, LATITUDE, LONGITUDE)

def longitude_to_sign(lon):
    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    sign_index = int(lon // 30)
    degrees = lon % 30
    minutes = (degrees % 1) * 60
    return f"{int(degrees)}°{int(minutes):02d}' {signs[sign_index]}"

print(f"Moon: {longitude_to_sign(chart['planets']['Moon']['longitude'])}")
print(f"  Expected: 0°04' Taurus")
print(f"  Calculated: {chart['planets']['Moon']['longitude']:.4f}°")
print()

# Test astrocartography lines
print("=" * 80)
print("ASTROCARTOGRAPHY LINES (sample points)")
print("=" * 80)

lines = calculate_astrocartography_lines_proper(jd_ut, LATITUDE, LONGITUDE)

# Show sample lines for Jupiter and Mars
print("\nJupiter lines (first 5 points of each type):")
jupiter_lines = [l for l in lines if l['planet'] == 'Jupiter']
for line_type in ['MC', 'IC', 'ASC', 'DSC']:
    points = [l for l in jupiter_lines if l['line_type'] == line_type][:5]
    if points:
        print(f"  {line_type}:")
        for p in points:
            print(f"    Lat {p['latitude']:6.1f}°, Lon {p['longitude']:7.2f}°")

print("\nMars lines (first 5 points of each type):")
mars_lines = [l for l in lines if l['planet'] == 'Mars']
for line_type in ['MC', 'IC', 'ASC', 'DSC']:
    points = [l for l in mars_lines if l['line_type'] == line_type][:5]
    if points:
        print(f"  {line_type}:")
        for p in points:
            print(f"    Lat {p['latitude']:6.1f}°, Lon {p['longitude']:7.2f}°")

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total lines generated: {len(lines)}")
print("Lines per planet:")
for planet in ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']:
    count = len([l for l in lines if l['planet'] == planet])
    print(f"  {planet}: {count} points")

print()
print("✅ Test completed successfully!")
