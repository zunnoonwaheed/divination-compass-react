"""
Debug Moon calculation to understand the 30° discrepancy
"""

import swisseph as swe
from datetime import datetime
import pytz

# Set ephemeris path
swe.set_ephe_path('./ephe')

# Test case parameters
YEAR = 1987
MONTH = 12
DAY = 4
HOUR = 0
MINUTE = 21
SECOND = 0

# Los Angeles coordinates
LATITUDE = 34.0522
LONGITUDE = -118.2437

# Create UTC datetime
utc_dt = datetime(1987, 12, 4, 8, 21, 0, tzinfo=pytz.UTC)
utc_hours = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
jd_ut = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_hours, swe.GREG_CAL)

print(f"Julian Day: {jd_ut}")
print()

# Calculate Moon with different flags
print("Moon calculation with different settings:")
print("-" * 60)

# Default calculation
result_default = swe.calc_ut(jd_ut, swe.MOON)
print(f"calc_ut (default):          {result_default[0][0]:.6f}°")

# With SEFLG_SWIEPH (Swiss Ephemeris)
result_swieph = swe.calc_ut(jd_ut, swe.MOON, swe.FLG_SWIEPH)
print(f"calc_ut (SWIEPH):           {result_swieph[0][0]:.6f}°")

# With topocentric correction
swe.set_topo(LONGITUDE, LATITUDE, 0)  # Set topocentric location
result_topo = swe.calc_ut(jd_ut, swe.MOON, swe.FLG_TOPOCTR)
print(f"calc_ut (TOPOCTR):          {result_topo[0][0]:.6f}°")

# Check if Astro.com uses topocentric or geocentric
print()
print("Interpretation:")
print("-" * 60)
print(f"Geocentric (default): {result_default[0][0]:.6f}° = {int(result_default[0][0] % 30)}°{int((result_default[0][0] % 30 % 1) * 60):02d}' {['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'][int(result_default[0][0] // 30)]}")
print(f"Topocentric:          {result_topo[0][0]:.6f}° = {int(result_topo[0][0] % 30)}°{int((result_topo[0][0] % 30 % 1) * 60):02d}' {['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'][int(result_topo[0][0] // 30)]}")
print()
print(f"Expected from Astro.com: 0°04' Taurus = ~30.0667°")
print()

# Also check with slightly different times to see sensitivity
print("Time sensitivity check:")
print("-" * 60)
for minute_offset in [-1, 0, 1]:
    test_dt = datetime(1987, 12, 4, 8, 21 + minute_offset, 0, tzinfo=pytz.UTC)
    test_hours = test_dt.hour + test_dt.minute / 60.0
    test_jd = swe.julday(test_dt.year, test_dt.month, test_dt.day, test_hours, swe.GREG_CAL)
    result = swe.calc_ut(test_jd, swe.MOON, swe.FLG_TOPOCTR)
    print(f"UTC 08:{21+minute_offset:02d}: Moon = {result[0][0]:.6f}° ({int(result[0][0] % 30)}°{int((result[0][0] % 30 % 1) * 60):02d}' {['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'][int(result[0][0] // 30)]})")
