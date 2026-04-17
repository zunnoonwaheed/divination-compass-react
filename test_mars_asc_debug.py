#!/usr/bin/env python3
"""
Debug Mars ASC line calculation
"""

import swisseph as swe

swe.set_ephe_path('./swiss-ephemeris-api/ephe')

jd_ut = 2447133.847916667  # Lionel test case
mars_result = swe.calc_ut(jd_ut, swe.MARS)
mars_lon = mars_result[0][0]

print("=" * 80)
print("MARS ASC LINE DEBUG")
print("=" * 80)
print(f"Julian Day: {jd_ut}")
print(f"Mars longitude: {mars_lon:.4f}° (216.68° expected)")
print()

# Test at latitude 40°N
test_lat = 40.0

# Expected Mars ASC longitude according to test: around -70 to -75°
# Current API returns: around -62°

print(f"Testing at latitude {test_lat}°N")
print()

# Test different longitudes to find where Mars = ASC
test_longitudes = [-80, -75, -70, -65, -62, -60, -55]

print(f"{'Longitude':<12} {'ASC':<12} {'Diff from Mars':<15}")
print("-" * 45)

for lon in test_longitudes:
    try:
        houses, ascmc = swe.houses(jd_ut, test_lat, lon, b'P')
        asc = ascmc[0]
        diff = (asc - mars_lon) % 360
        if diff > 180:
            diff -= 360

        marker = " ← MATCH!" if abs(diff) < 1.0 else ""
        print(f"{lon:>10}°  {asc:>10.4f}°  {diff:>+12.4f}°{marker}")
    except Exception as e:
        print(f"{lon:>10}°  ERROR: {e}")

print()
print("=" * 80)
print("ANALYSIS")
print("=" * 80)
print("If Mars ASC line is at -62°, ASC should be ~216.68° at that longitude")
print("If Mars ASC line should be at -72°, ASC should be ~216.68° at that longitude")
print("Let's check which is correct:")
print()

# Check ASC at -62 (where API currently puts it)
houses_62, ascmc_62 = swe.houses(jd_ut, test_lat, -62, b'P')
asc_62 = ascmc_62[0]
print(f"At longitude -62°, ASC = {asc_62:.4f}°")
print(f"Mars = {mars_lon:.4f}°")
print(f"Difference: {(asc_62 - mars_lon) % 360:.4f}° (should be ~0° for Mars ASC line)")
print()

# Check ASC at -72 (where it should be according to Astro.com)
houses_72, ascmc_72 = swe.houses(jd_ut, test_lat, -72, b'P')
asc_72 = ascmc_72[0]
print(f"At longitude -72°, ASC = {asc_72:.4f}°")
print(f"Mars = {mars_lon:.4f}°")
print(f"Difference: {(asc_72 - mars_lon) % 360:.4f}° (should be ~0° for Mars ASC line)")
print()

# Try to find exact longitude where ASC = Mars
print("Binary search for exact Mars ASC longitude:")
left, right = -80.0, -60.0
for i in range(20):
    mid = (left + right) / 2.0
    houses, ascmc = swe.houses(jd_ut, test_lat, mid, b'P')
    asc = ascmc[0]
    diff = asc - mars_lon
    if diff > 180:
        diff -= 360
    elif diff < -180:
        diff += 360

    if abs(diff) < 0.01:
        print(f"Found! Mars ASC at longitude {mid:.4f}°")
        break

    if diff > 0:
        right = mid
    else:
        left = mid

print("=" * 80)
