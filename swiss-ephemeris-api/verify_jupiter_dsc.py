#!/usr/bin/env python3
"""
Manually verify Jupiter DSC calculation for December 4, 1987, 00:21 Los Angeles
"""
import swisseph as swe
import math
from datetime import datetime
import pytz

# Birth data
local_time = datetime(1987, 12, 4, 0, 21, 0)
timezone_str = 'America/Los_Angeles'
birth_lat = 34.0522
birth_lon = -118.2437

# Convert to UTC
timezone = pytz.timezone(timezone_str)
local_dt = timezone.localize(local_time)
utc_dt = local_dt.astimezone(pytz.UTC)

print("=" * 60)
print("JUPITER DSC VERIFICATION")
print("=" * 60)
print(f"Local time: {local_time} {timezone_str}")
print(f"UTC time: {utc_dt}")
print(f"Birth location: {birth_lat}°N, {birth_lon}°E")
print()

# Calculate Julian Day
jd_ut = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day,
                    utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0)

print(f"Julian Day (UTC): {jd_ut:.6f}")
print()

# Get Jupiter position in ecliptic coordinates
jupiter_ecl = swe.calc_ut(jd_ut, swe.JUPITER, swe.FLG_SPEED)
jupiter_lon = jupiter_ecl[0][0]
jupiter_lat = jupiter_ecl[0][1]

print("JUPITER ECLIPTIC COORDINATES:")
print(f"  Longitude: {jupiter_lon:.4f}° ({int(jupiter_lon//30)} {['Ari','Tau','Gem','Can','Leo','Vir','Lib','Sco','Sag','Cap','Aqu','Pis'][int(jupiter_lon//30)]} {jupiter_lon%30:.2f}°)")
print(f"  Latitude: {jupiter_lat:.4f}°")
print()

# Get Jupiter position in equatorial coordinates
jupiter_equ = swe.calc_ut(jd_ut, swe.JUPITER, swe.FLG_SPEED | swe.FLG_EQUATORIAL)
jupiter_ra = jupiter_equ[0][0]
jupiter_dec = jupiter_equ[0][1]

print("JUPITER EQUATORIAL COORDINATES:")
print(f"  Right Ascension: {jupiter_ra:.4f}° ({jupiter_ra/15:.2f}h)")
print(f"  Declination: {jupiter_dec:.4f}°")
print()

# Now calculate where Jupiter sets (DSC) at latitude 40°N
test_lat = 40.0

print(f"CALCULATING JUPITER DSC AT {test_lat}°N:")
print()

# Step 1: Calculate hour angle when Jupiter crosses horizon
lat_rad = math.radians(test_lat)
dec_rad = math.radians(jupiter_dec)

cos_ha0 = -math.tan(lat_rad) * math.tan(dec_rad)
print(f"cos(ha₀) = -tan({test_lat}°) × tan({jupiter_dec:.4f}°) = {cos_ha0:.6f}")

if cos_ha0 < -1 or cos_ha0 > 1:
    print(f"ERROR: cos(ha₀) = {cos_ha0} is out of range [-1, 1]")
    print("Jupiter never rises/sets at this latitude!")
    exit(1)

ha0 = math.degrees(math.acos(cos_ha0))
print(f"ha₀ = arccos({cos_ha0:.6f}) = {ha0:.4f}°")
print()

# For setting (DSC): hour angle is positive
hour_angle_dsc = ha0
print(f"Hour angle for DSC (setting): {hour_angle_dsc:.4f}° (positive = West)")
print()

# Step 2: Calculate required sidereal time (ARMC)
required_armc = jupiter_ra + hour_angle_dsc
while required_armc < 0:
    required_armc += 360
while required_armc >= 360:
    required_armc -= 360

print(f"Required ARMC = RA + hour_angle")
print(f"              = {jupiter_ra:.4f}° + {hour_angle_dsc:.4f}°")
print(f"              = {required_armc:.4f}°")
print()

# Step 3: Binary search to find longitude
print("Binary search for longitude that gives this ARMC...")
left = -180.0
right = 180.0
tolerance = 0.01

for iteration in range(100):
    mid = (left + right) / 2.0

    try:
        houses, ascmc = swe.houses(jd_ut, test_lat, mid, b'P')
        current_armc = ascmc[2]

        diff = current_armc - required_armc
        if diff > 180:
            diff -= 360
        elif diff < -180:
            diff += 360

        if iteration < 10 or abs(diff) < 0.1:
            print(f"  Iteration {iteration:2d}: lon={mid:7.2f}°, ARMC={current_armc:7.2f}°, diff={diff:6.2f}°")

        if abs(diff) < tolerance:
            print()
            print("=" * 60)
            print(f"✅ FOUND: Jupiter DSC at {test_lat}°N is at longitude {mid:.2f}°")
            print("=" * 60)
            break

        if diff > 0:
            right = mid
        else:
            left = mid

        if abs(right - left) < tolerance:
            print()
            print("=" * 60)
            print(f"✅ CONVERGED: Jupiter DSC at {test_lat}°N is at longitude {mid:.2f}°")
            print("=" * 60)
            break
    except Exception as e:
        print(f"  Error at longitude {mid:.2f}°: {e}")
        break
