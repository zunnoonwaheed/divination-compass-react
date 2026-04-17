#!/usr/bin/env python3
"""
Test In Mundo method for ASC lines vs Zodiacal method
"""

import swisseph as swe
import math

swe.set_ephe_path('./swiss-ephemeris-api/ephe')

jd_ut = 2447133.847916667
test_lat = 40.0

# Get Mars position
mars_result = swe.calc_ut(jd_ut, swe.MARS)
mars_lon = mars_result[0][0]  # Ecliptic longitude
mars_lat = mars_result[0][1]  # Ecliptic latitude

print("=" * 80)
print("IN MUNDO vs ZODIACAL METHOD COMPARISON")
print("=" * 80)
print(f"Julian Day: {jd_ut}")
print(f"Mars ecliptic longitude: {mars_lon:.4f}°")
print(f"Mars ecliptic latitude: {mars_lat:.4f}°")
print()

# Convert Mars ecliptic coordinates to equatorial (RA/Dec)
# This is needed for In Mundo method
mars_eq = swe.cotrans([mars_lon, mars_lat, 1.0], -swe.get_ayanamsa_ut(jd_ut) if False else 0)  # Simplified
# Actually, let's use proper conversion
obliquity = 23.4393  # Approximate obliquity for 1987
mars_ra, mars_dec, _ = swe.cotrans([mars_lon, mars_lat, 1.0], -obliquity)

print(f"Mars right ascension (RA): {mars_ra:.4f}°")
print(f"Mars declination (Dec): {mars_dec:.4f}°")
print()

print("=" * 80)
print("METHOD COMPARISON AT LATITUDE 40°N")
print("=" * 80)
print()

# Method 1: Zodiacal (current implementation)
print("METHOD 1: ZODIACAL")
print("Find longitude where ASC (ecliptic) = Mars ecliptic longitude")
print()

left, right = -80.0, -50.0
for i in range(25):
    mid = (left + right) / 2.0
    houses, ascmc = swe.houses(jd_ut, test_lat, mid, b'P')
    asc_lon = ascmc[0]
    diff = asc_lon - mars_lon
    if diff > 180:
        diff -= 360
    elif diff < -180:
        diff += 360

    if abs(diff) < 0.001:
        print(f"Zodiacal Mars ASC: {mid:.4f}°")
        print(f"  ASC ecliptic longitude at this location: {asc_lon:.4f}°")
        print(f"  Mars ecliptic longitude: {mars_lon:.4f}°")
        print(f"  Difference: {abs(diff):.6f}°")
        break

    if diff > 0:
        right = mid
    else:
        left = mid

print()

# Method 2: In Mundo
print("METHOD 2: IN MUNDO")
print("Find longitude where Mars is on the horizon (altitude = 0, azimuth = 90° for East/ASC)")
print()

# For In Mundo, we need to find where the planet crosses the horizon
# This involves calculating the planet's altitude at different longitudes
# A planet is on the ASC when it's rising (altitude ≈ 0, azimuth ≈ 90°)

def calculate_azalt(jd_ut, lat, lon, planet_ra, planet_dec):
    """Calculate azimuth and altitude for a planet at given location"""
    # Get local sidereal time
    houses, ascmc = swe.houses(jd_ut, lat, lon, b'P')
    armc = ascmc[2]  # ARMC = sidereal time in degrees

    # Hour angle = LST - RA
    hour_angle = armc - planet_ra

    # Convert to radians
    lat_rad = math.radians(lat)
    dec_rad = math.radians(planet_dec)
    ha_rad = math.radians(hour_angle)

    # Calculate altitude
    sin_alt = math.sin(lat_rad) * math.sin(dec_rad) + math.cos(lat_rad) * math.cos(dec_rad) * math.cos(ha_rad)
    altitude = math.degrees(math.asin(max(-1, min(1, sin_alt))))

    # Calculate azimuth
    cos_az = (math.sin(dec_rad) - math.sin(lat_rad) * math.sin(math.radians(altitude))) / (math.cos(lat_rad) * math.cos(math.radians(altitude)))
    azimuth = math.degrees(math.acos(max(-1, min(1, cos_az))))

    if math.sin(ha_rad) > 0:
        azimuth = 360 - azimuth

    return azimuth, altitude

# Binary search for longitude where planet altitude ≈ 0 and rising (azimuth ≈ 90°)
left, right = -90.0, -40.0
for i in range(25):
    mid = (left + right) / 2.0
    az, alt = calculate_azalt(jd_ut, test_lat, mid, mars_ra, mars_dec)

    # For ASC, we want altitude ≈ 0 and azimuth ≈ 90 (eastern horizon)
    # Simplification: just find where altitude crosses zero while moving east

    if abs(alt) < 0.01:
        print(f"In Mundo Mars ASC: {mid:.4f}°")
        print(f"  Mars altitude at this location: {alt:.4f}°")
        print(f"  Mars azimuth: {az:.4f}°")
        break

    if alt > 0:
        left = mid
    else:
        right = mid

print()
print("=" * 80)
print("COMPARISON WITH EXPECTED VALUES")
print("=" * 80)
print("Expected Mars ASC (from test file): -70° to -75°")
print("Zodiacal method gives: ~-61.7°")
print("In Mundo method gives: ~??? (to be calculated)")
print()
print("If Astro.com shows ~-72°, which method matches?")
print("=" * 80)
