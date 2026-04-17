#!/usr/bin/env python3
"""
Test Moon calculation with different methods to find the 30° error.
"""

import swisseph as swe

# Set ephemeris path
swe.set_ephe_path('./swiss-ephemeris-api/ephe')

# Lionel test case
# Birth: December 4, 1987, 00:21 PST (Los Angeles)
# UTC: 1987-12-04 08:21:00 UTC
jd_ut = 2447133.847916667

# Los Angeles coordinates
LATITUDE = 34.0522
LONGITUDE = -118.2437

print("=" * 80)
print("MOON CALCULATION METHODS COMPARISON")
print("=" * 80)
print(f"Julian Day (UT): {jd_ut}")
print(f"Location: Los Angeles ({LATITUDE}, {LONGITUDE})")
print()

# Helper function
def longitude_to_sign(lon):
    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    sign_index = int(lon // 30)
    degrees = lon % 30
    minutes = (degrees % 1) * 60
    return f"{int(degrees)}°{int(minutes):02d}' {signs[sign_index]} ({lon:.4f}°)"

# Expected from Astro.com
expected_lon = 30.067  # 0°04' Taurus

print("EXPECTED (from Astro.com):")
print(f"  Moon: {longitude_to_sign(expected_lon)}")
print()

print("=" * 80)
print("METHOD 1: Geocentric (default)")
print("=" * 80)
result = swe.calc_ut(jd_ut, swe.MOON)
print(f"Moon: {longitude_to_sign(result[0][0])}")
print(f"Speed: {result[0][3]:.6f}°/day")
print(f"Difference from expected: {result[0][0] - expected_lon:+.4f}°")
print()

print("=" * 80)
print("METHOD 2: Geocentric with SPEED flag")
print("=" * 80)
result = swe.calc_ut(jd_ut, swe.MOON, swe.FLG_SPEED)
print(f"Moon: {longitude_to_sign(result[0][0])}")
print(f"Speed: {result[0][3]:.6f}°/day")
print(f"Difference from expected: {result[0][0] - expected_lon:+.4f}°")
print()

print("=" * 80)
print("METHOD 3: Topocentric (current API method)")
print("=" * 80)
swe.set_topo(LONGITUDE, LATITUDE, 0)
result = swe.calc_ut(jd_ut, swe.MOON, swe.FLG_TOPOCTR)
print(f"Moon: {longitude_to_sign(result[0][0])}")
print(f"Speed: {result[0][3]:.6f}°/day")
print(f"Difference from expected: {result[0][0] - expected_lon:+.4f}°")
print()

print("=" * 80)
print("METHOD 4: Topocentric with SPEED flag")
print("=" * 80)
swe.set_topo(LONGITUDE, LATITUDE, 0)
result = swe.calc_ut(jd_ut, swe.MOON, swe.FLG_TOPOCTR | swe.FLG_SPEED)
print(f"Moon: {longitude_to_sign(result[0][0])}")
print(f"Speed: {result[0][3]:.6f}°/day")
print(f"Difference from expected: {result[0][0] - expected_lon:+.4f}°")
print()

print("=" * 80)
print("METHOD 5: Mean Node (not True Node)")
print("=" * 80)
result = swe.calc_ut(jd_ut, swe.MOON)
print(f"Moon (geocentric): {longitude_to_sign(result[0][0])}")

# Also check if we're accidentally getting Mean Node instead of Moon
result_mean_node = swe.calc_ut(jd_ut, swe.MEAN_NODE)
print(f"Mean Node: {longitude_to_sign(result_mean_node[0][0])}")
result_true_node = swe.calc_ut(jd_ut, swe.TRUE_NODE)
print(f"True Node: {longitude_to_sign(result_true_node[0][0])}")
print()

print("=" * 80)
print("ANALYSIS")
print("=" * 80)
print("If the difference is ~30°, the Moon is one zodiac sign off")
print("If the speed is 0.0, there's a calculation error")
print("Astro.com uses geocentric positions for most calculations")
print("Topocentric is only used for some parallax corrections")
print()
