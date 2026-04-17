#!/usr/bin/env python3
"""
Debug the 30° Moon offset issue.
"""

import swisseph as swe
import os

# Set ephemeris path
ephe_path = './swiss-ephemeris-api/ephe'
swe.set_ephe_path(ephe_path)

print("=" * 80)
print("DEBUG: 30° MOON OFFSET ISSUE")
print("=" * 80)
print()

# Check ephemeris files
print("EPHEMERIS FILES:")
print(f"Path: {ephe_path}")
if os.path.exists(ephe_path):
    files = os.listdir(ephe_path)
    moon_files = [f for f in files if 'semo' in f.lower() or 'moon' in f.lower()]
    print(f"Moon-related files: {moon_files}")
else:
    print("ERROR: Ephemeris path does not exist!")
print()

# Check Swiss Ephemeris version
print("SWISS EPHEMERIS VERSION:")
print(f"Version: {swe.version}")
print()

# Check planet ID constants
print("PLANET ID CONSTANTS:")
print(f"swe.MOON = {swe.MOON}")
print(f"swe.SUN = {swe.SUN}")
print(f"swe.MERCURY = {swe.MERCURY}")
print(f"swe.MEAN_NODE = {swe.MEAN_NODE}")
print(f"swe.TRUE_NODE = {swe.TRUE_NODE}")
print()

# Test case
jd_ut = 2447133.847916667  # 1987-12-04 08:21:00 UTC
print(f"Julian Day: {jd_ut}")
print()

# Calculate Moon with different methods
print("MOON CALCULATIONS:")
print()

# Method 1: Default geocentric
result = swe.calc_ut(jd_ut, swe.MOON)
lon, lat, dist, speed = result[0][:4]
print(f"Method 1 - Geocentric (default):")
print(f"  Longitude: {lon:.6f}°")
print(f"  Latitude: {lat:.6f}°")
print(f"  Distance: {dist:.6f} AU")
print(f"  Speed: {speed:.6f}°/day")
print()

# Method 2: Using planet ID 1 directly (should be same as swe.MOON)
result = swe.calc_ut(jd_ut, 1)
lon2 = result[0][0]
print(f"Method 2 - Using planet ID=1 directly:")
print(f"  Longitude: {lon2:.6f}°")
print(f"  Same as Method 1? {abs(lon - lon2) < 0.0001}")
print()

# Method 3: Check if Sun is correct (to verify ephemeris files)
result_sun = swe.calc_ut(jd_ut, swe.SUN)
sun_lon = result_sun[0][0]
expected_sun = 251.6333  # from Astro.com
print(f"SUN VERIFICATION:")
print(f"  Calculated: {sun_lon:.6f}°")
print(f"  Expected: {expected_sun:.6f}°")
print(f"  Difference: {abs(sun_lon - expected_sun):.6f}° {'✅ MATCH' if abs(sun_lon - expected_sun) < 0.01 else '❌ MISMATCH'}")
print()

# Method 4: Calculate for a different date to see if offset is consistent
jd_test = 2451545.0  # J2000.0 epoch (2000-01-01 12:00 TT)
result_j2000 = swe.calc_ut(jd_test, swe.MOON)
print(f"MOON AT J2000.0 EPOCH (2000-01-01 12:00 UTC):")
print(f"  Longitude: {result_j2000[0][0]:.6f}°")
print(f"  (Reference value from JPL: should be around 218-220°)")
print()

# Calculate exact expected vs actual
print("=" * 80)
print("LIONEL TEST CASE ANALYSIS")
print("=" * 80)
expected_moon = 30.0667  # 0°04' Taurus (from Astro.com)
calculated_moon = lon
difference = calculated_moon - expected_moon

print(f"Expected Moon (Astro.com): {expected_moon:.4f}° (0°04' Taurus)")
print(f"Calculated Moon (Swiss Eph): {calculated_moon:.4f}° (0°04' Gemini)")
print(f"Difference: {difference:+.4f}°")
print()

if abs(difference - 30.0) < 0.1:
    print("⚠️  EXACTLY 30° OFF = ONE ZODIAC SIGN!")
    print("This suggests a systematic error, not random calculation drift")
    print()
    print("POSSIBLE CAUSES:")
    print("1. Wrong sidereal vs tropical zodiac setting")
    print("2. Corrupted or wrong ephemeris files")
    print("3. Ayanamsa accidentally applied")
    print("4. Different epoch or reference frame")
    print()

    # Check ayanamsa
    print("CHECKING SIDEREAL/TROPICAL SETTING:")
    ayanamsa = swe.get_ayanamsa_ut(jd_ut)
    print(f"Current ayanamsa: {ayanamsa:.6f}°")
    print(f"(Should be ~23.8° for 1987 if sidereal mode is on)")
    print()

    # Try setting to tropical explicitly
    swe.set_sid_mode(swe.SIDM_FAGAN_BRADLEY, 0, 0)
    result_sidereal = swe.calc_ut(jd_ut, swe.MOON, swe.FLG_SIDEREAL)
    print(f"Moon with sidereal flag: {result_sidereal[0][0]:.6f}°")

    # Calculate without any flags to get tropical
    result_tropical = swe.calc_ut(jd_ut, swe.MOON)
    print(f"Moon without sidereal (tropical): {result_tropical[0][0]:.6f}°")
    print()

print("=" * 80)
