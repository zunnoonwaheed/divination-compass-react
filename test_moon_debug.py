"""
Debug Moon calculation issue
"""

import sys
sys.path.insert(0, './swiss-ephemeris-api')

import swisseph as swe
from datetime import datetime
import pytz

# Set ephemeris path
swe.set_ephe_path('./swiss-ephemeris-api/ephe')

# Lionel's data
LATITUDE = 34.0522
LONGITUDE = -118.2437

# UTC datetime: 1987-12-04 08:21:00 UTC
utc_dt = datetime(1987, 12, 4, 8, 21, 0, tzinfo=pytz.UTC)
utc_hours = utc_dt.hour + utc_dt.minute / 60.0
jd_ut = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_hours, swe.GREG_CAL)

print(f"Julian Day: {jd_ut}")
print(f"Expected from Astro.com: 0°04' Taurus = 30.067°")
print()

# Test different calculation methods
print("Moon calculations:")
print("-" * 60)

# 1. Geocentric (default)
result_geo = swe.calc_ut(jd_ut, swe.MOON)
print(f"Geocentric (default):     {result_geo[0][0]:.4f}°")

# 2. With SWIEPH flag
result_swe_flag = swe.calc_ut(jd_ut, swe.MOON, swe.FLG_SWIEPH)
print(f"With SWIEPH flag:         {result_swe_flag[0][0]:.4f}°")

# 3. Topocentric
swe.set_topo(LONGITUDE, LATITUDE, 0)
result_topo = swe.calc_ut(jd_ut, swe.MOON, swe.FLG_TOPOCTR)
print(f"Topocentric:              {result_topo[0][0]:.4f}°")

# 4. Without topocentric flag after set_topo
result_after_topo = swe.calc_ut(jd_ut, swe.MOON)
print(f"After set_topo (no flag): {result_after_topo[0][0]:.4f}°")

print()
print("Analysis:")
print("-" * 60)

def get_sign_notation(lon):
    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    sign_index = int(lon // 30)
    degrees = lon % 30
    minutes = (degrees % 1) * 60
    return f"{int(degrees)}°{int(minutes):02d}' {signs[sign_index]}"

print(f"Geocentric:     {get_sign_notation(result_geo[0][0])}")
print(f"Topocentric:    {get_sign_notation(result_topo[0][0])}")
print(f"Expected:       0°04' Taurus")
print()

# Check difference
geo_diff = result_geo[0][0] - 30.067
topo_diff = result_topo[0][0] - 30.067
print(f"Geocentric difference:  {geo_diff:+.4f}°")
print(f"Topocentric difference: {topo_diff:+.4f}°")
