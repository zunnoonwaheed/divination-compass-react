"""
Test different Swiss Ephemeris calculation methods to match Astro.com
"""

import swisseph as swe
from datetime import datetime
import pytz

# Set ephemeris path
swe.set_ephe_path('./ephe')

# Test case: Lionel, Dec 4 1987, 00:21 AM PST (Los Angeles)
# Expected UTC: 1987-12-04 08:21:00 UTC

LATITUDE = 34.0522   # Los Angeles
LONGITUDE = -118.2437
utc_dt = datetime(1987, 12, 4, 8, 21, 0, tzinfo=pytz.UTC)

# Calculate Julian Day
utc_hours = utc_dt.hour + utc_dt.minute / 60.0
jd_ut = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_hours, swe.GREG_CAL)

print("=" * 80)
print("TESTING DIFFERENT CALCULATION METHODS")
print("=" * 80)
print(f"UTC: {utc_dt}")
print(f"Julian Day: {jd_ut}")
print(f"Location: {LATITUDE}°N, {LONGITUDE}°E")
print()

# Helper function
def deg_to_dms(deg):
    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    sign_num = int(deg // 30)
    deg_in_sign = deg % 30
    minutes = (deg_in_sign % 1) * 60
    return f"{int(deg_in_sign)}°{int(minutes):02d}' {signs[sign_num]} ({deg:.4f}°)"

# Expected values from Astro.com
expected = {
    'Sun': 240 + 11 + 38/60,      # 11°38' Sagittarius
    'Moon': 30 + 0 + 4/60,         # 0°04' Taurus
    'Mercury': 240 + 1 + 13/60,    # 1°13' Sagittarius
    'Ascendant': 150 + 21 + 15/60, # 21°15' Virgo
    'MC': 60 + 20 + 27/60,         # 20°27' Gemini
}

print("EXPECTED VALUES FROM ASTRO.COM:")
print("-" * 80)
for name, value in expected.items():
    print(f"{name:<12} {deg_to_dms(value)}")
print()

# Test 1: Default geocentric
print("METHOD 1: GEOCENTRIC (DEFAULT)")
print("-" * 80)
sun_geo = swe.calc_ut(jd_ut, swe.SUN)[0][0]
moon_geo = swe.calc_ut(jd_ut, swe.MOON)[0][0]
mercury_geo = swe.calc_ut(jd_ut, swe.MERCURY)[0][0]
houses_geo, ascmc_geo = swe.houses(jd_ut, LATITUDE, LONGITUDE, b'P')

print(f"Sun          {deg_to_dms(sun_geo)}")
print(f"Moon         {deg_to_dms(moon_geo)}")
print(f"Mercury      {deg_to_dms(mercury_geo)}")
print(f"Ascendant    {deg_to_dms(ascmc_geo[0])}")
print(f"MC           {deg_to_dms(ascmc_geo[1])}")
print()
print(f"Sun diff:    {sun_geo - expected['Sun']:+.4f}°")
print(f"Moon diff:   {moon_geo - expected['Moon']:+.4f}°")
print(f"Mercury diff: {mercury_geo - expected['Mercury']:+.4f}°")
print()

# Test 2: Topocentric for planets
print("METHOD 2: TOPOCENTRIC FOR PLANETS")
print("-" * 80)
swe.set_topo(LONGITUDE, LATITUDE, 0)  # longitude, latitude, altitude
sun_topo = swe.calc_ut(jd_ut, swe.SUN, swe.FLG_TOPOCTR)[0][0]
moon_topo = swe.calc_ut(jd_ut, swe.MOON, swe.FLG_TOPOCTR)[0][0]
mercury_topo = swe.calc_ut(jd_ut, swe.MERCURY, swe.FLG_TOPOCTR)[0][0]

print(f"Sun          {deg_to_dms(sun_topo)}")
print(f"Moon         {deg_to_dms(moon_topo)}")
print(f"Mercury      {deg_to_dms(mercury_topo)}")
print()
print(f"Sun diff:    {sun_topo - expected['Sun']:+.4f}°")
print(f"Moon diff:   {moon_topo - expected['Moon']:+.4f}°")
print(f"Mercury diff: {mercury_topo - expected['Mercury']:+.4f}°")
print()

# Test 3: Check if it's a date/time issue - try PST local time instead
print("METHOD 3: TRYING LOCAL PST TIME (IN CASE OF CONVERSION ERROR)")
print("-" * 80)
# Try using local time 00:21 directly
local_hours = 0 + 21/60.0
jd_local = swe.julday(1987, 12, 4, local_hours, swe.GREG_CAL)
moon_local = swe.calc_ut(jd_local, swe.MOON)[0][0]
print(f"JD (local):  {jd_local}")
print(f"Moon         {deg_to_dms(moon_local)}")
print(f"Moon diff:   {moon_local - expected['Moon']:+.4f}°")
print()

# Test 4: Try different timezone offsets
print("METHOD 4: TESTING DIFFERENT TIME OFFSETS")
print("-" * 80)
for offset in [-10, -9, -8, -7, -6]:
    test_hour = 0 + 21/60.0 - offset  # local 00:21 + offset
    test_jd = swe.julday(1987, 12, 4 + (1 if test_hour >= 24 else 0),
                          test_hour % 24, swe.GREG_CAL)
    moon_test = swe.calc_ut(test_jd, swe.MOON)[0][0]
    diff = abs(moon_test - expected['Moon'])
    marker = " ← CLOSEST" if diff < 1.0 else ""
    print(f"Offset {offset:+3}h: Moon = {deg_to_dms(moon_test)}, diff = {diff:+.4f}°{marker}")

print()

# Test 5: Try with accurate UTC but different house system
print("METHOD 5: DIFFERENT HOUSE SYSTEMS")
print("-" * 80)
house_systems = {
    'P': 'Placidus',
    'K': 'Koch',
    'O': 'Porphyrius',
    'R': 'Regiomontanus',
    'C': 'Campanus',
    'E': 'Equal',
    'W': 'Whole Sign',
    'T': 'Topocentric (Polich/Page)'
}

for code, name in house_systems.items():
    try:
        houses, ascmc = swe.houses(jd_ut, LATITUDE, LONGITUDE, code.encode('ascii'))
        asc_diff = abs(ascmc[0] - expected['Ascendant'])
        mc_diff = abs(ascmc[1] - expected['MC'])
        total_diff = asc_diff + mc_diff
        marker = " ← BEST MATCH" if total_diff < 0.1 else ""
        print(f"{code} ({name:<25}): ASC={ascmc[0]:7.3f}° (diff {asc_diff:+.3f}°), MC={ascmc[1]:7.3f}° (diff {mc_diff:+.3f}°){marker}")
    except:
        print(f"{code} ({name:<25}): ERROR")

print()
print("=" * 80)
print("CONCLUSION")
print("=" * 80)
print(f"Best Moon match: geocentric with local PST time gives {deg_to_dms(moon_local)}")
print(f"This suggests the issue is: ", end="")

if abs(moon_local - expected['Moon']) < 1.0:
    print("❌ TIME CONVERSION PROBLEM - using wrong UTC offset or treating local as UTC")
elif abs(moon_topo - expected['Moon']) < 1.0:
    print("⚠️  COORDINATE SYSTEM - need topocentric for Moon")
else:
    print("❓ UNKNOWN - requires further investigation")
