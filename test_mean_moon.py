"""
Test Mean Moon vs True Moon
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

# Test True Moon vs Mean Moon
print("Moon calculations:")
print("-" * 60)

# True Moon (default)
result_true = swe.calc_ut(jd_ut, swe.MOON)
print(f"True Moon (SE_MOON):      {result_true[0][0]:.4f}°")

# Try Mean Moon
# MEAN_NODE is 10, MEAN_APOG is 11, but there's no direct MEAN_MOON constant
# Let's try different Moon calculations

# Try with interpolated Moon
result_interp = swe.calc_ut(jd_ut, swe.MOON, swe.FLG_TRUEPOS)
print(f"With TRUEPOS flag:        {result_interp[0][0]:.4f}°")

# Try with speed
result_speed = swe.calc_ut(jd_ut, swe.MOON, swe.FLG_SPEED)
print(f"With SPEED flag:          {result_speed[0][0]:.4f}°")

# Check if maybe we need to subtract 30 degrees?
print()
print("If we subtract 30 degrees:")
print(f"True Moon - 30°:          {result_true[0][0] - 30:.4f}° = {int((result_true[0][0] - 30) % 30)}°{int(((result_true[0][0] - 30) % 30 % 1) * 60):02d}' Taurus")

# Could the coordinate system be wrong? Let's check sidereal
result_sidereal = swe.calc_ut(jd_ut, swe.MOON, swe.FLG_SIDEREAL)
print()
print("Sidereal calculation:")
print(f"Sidereal Moon:            {result_sidereal[0][0]:.4f}°")
