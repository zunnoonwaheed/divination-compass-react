#!/usr/bin/env python3
"""
Manually verify Mars ASC calculation for December 4, 1987, 00:21 Los Angeles
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
print("MARS ASC VERIFICATION")
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

# Get Mars position in ecliptic coordinates
mars_ecl = swe.calc_ut(jd_ut, swe.MARS, swe.FLG_SPEED)
mars_lon = mars_ecl[0][0]
mars_lat = mars_ecl[0][1]

print("MARS ECLIPTIC COORDINATES:")
print(f"  Longitude: {mars_lon:.4f}° ({int(mars_lon//30)} {['Ari','Tau','Gem','Can','Leo','Vir','Lib','Sco','Sag','Cap','Aqu','Pis'][int(mars_lon//30)]} {mars_lon%30:.2f}°)")
print(f"  Latitude: {mars_lat:.4f}°")
print()

# Get Mars position in equatorial coordinates
mars_equ = swe.calc_ut(jd_ut, swe.MARS, swe.FLG_SPEED | swe.FLG_EQUATORIAL)
mars_ra = mars_equ[0][0]
mars_dec = mars_equ[0][1]

print("MARS EQUATORIAL COORDINATES:")
print(f"  Right Ascension: {mars_ra:.4f}° ({mars_ra/15:.2f}h)")
print(f"  Declination: {mars_dec:.4f}°")
print()

# Now calculate where Mars rises (ASC) at latitude 40°N
test_lat = 40.0

print(f"CALCULATING MARS ASC AT {test_lat}°N:")
print()

# Step 1: Calculate hour angle when Mars crosses horizon
lat_rad = math.radians(test_lat)
dec_rad = math.radians(mars_dec)

cos_ha0 = -math.tan(lat_rad) * math.tan(dec_rad)
print(f"cos(ha₀) = -tan({test_lat}°) × tan({mars_dec:.4f}°) = {cos_ha0:.6f}")

if cos_ha0 < -1 or cos_ha0 > 1:
    print(f"ERROR: cos(ha₀) = {cos_ha0} is out of range [-1, 1]")
    print("Mars never rises/sets at this latitude!")
    exit(1)

ha0 = math.degrees(math.acos(cos_ha0))
print(f"ha₀ = arccos({cos_ha0:.6f}) = {ha0:.4f}°")
print()

# For rising (ASC): hour angle is negative
hour_angle_asc = -ha0
print(f"Hour angle for ASC (rising): {hour_angle_asc:.4f}° (negative = East)")
print()

# Step 2: Calculate required sidereal time (ARMC)
required_armc = mars_ra + hour_angle_asc
while required_armc < 0:
    required_armc += 360
while required_armc >= 360:
    required_armc -= 360

print(f"Required ARMC = RA + hour_angle")
print(f"              = {mars_ra:.4f}° + {hour_angle_asc:.4f}°")
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
            print(f"✅ FOUND: Mars ASC at {test_lat}°N is at longitude {mid:.2f}°")
            print("=" * 60)
            break

        if diff > 0:
            right = mid
        else:
            left = mid

        if abs(right - left) < tolerance:
            print()
            print("=" * 60)
            print(f"✅ CONVERGED: Mars ASC at {test_lat}°N is at longitude {mid:.2f}°")
            print("=" * 60)
            break
    except Exception as e:
        print(f"  Error at longitude {mid:.2f}°: {e}")
        break
