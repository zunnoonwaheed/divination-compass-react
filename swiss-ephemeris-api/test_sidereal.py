"""
Test sidereal vs tropical zodiac calculations
"""

import swisseph as swe
from datetime import datetime
import pytz

swe.set_ephe_path('./ephe')

# Test case: Dec 4, 1987, 00:21 PST -> Dec 4, 1987, 08:21 UTC
LATITUDE = 34.0522
LONGITUDE = -118.2437
utc_dt = datetime(1987, 12, 4, 8, 21, 0, tzinfo=pytz.UTC)
utc_hours = utc_dt.hour + utc_dt.minute / 60.0
jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_hours, swe.GREG_CAL)

def deg_to_dms(deg, name=""):
    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    sign_idx = int(deg // 30) % 12
    deg_in_sign = deg % 30
    minutes = (deg_in_sign % 1) * 60
    return f"{name:<12} {int(deg_in_sign):2d}°{int(minutes):02d}' {signs[sign_idx]:<12} ({deg:8.3f}°)"

print("=" * 80)
print("TROPICAL VS SIDEREAL ZODIAC TEST")
print("=" * 80)
print(f"UTC: {utc_dt}")
print(f"JD:  {jd}")
print()

# Expected from Astro.com (tropical)
expected = {
    'Sun': (11, 38, 'Sagittarius', 240 + 11 + 38/60),
    'Moon': (0, 4, 'Taurus', 30 + 0 + 4/60),
    'Mercury': (1, 13, 'Sagittarius', 240 + 1 + 13/60),
}

print("EXPECTED FROM ASTRO.COM (TROPICAL):")
print("-" * 80)
for name, (deg, min, sign, lon) in expected.items():
    print(f"{name:<12} {deg:2d}°{min:02d}' {sign:<12} ({lon:8.3f}°)")
print()

# 1. TROPICAL (default - no ayanamsa)
print("CALCULATED - TROPICAL ZODIAC (DEFAULT):")
print("-" * 80)
sun_trop = swe.calc_ut(jd, swe.SUN)[0][0]
moon_trop = swe.calc_ut(jd, swe.MOON)[0][0]
mercury_trop = swe.calc_ut(jd, swe.MERCURY)[0][0]

print(deg_to_dms(sun_trop, "Sun"))
print(deg_to_dms(moon_trop, "Moon"))
print(deg_to_dms(mercury_trop, "Mercury"))
print()
print(f"Sun diff:     {sun_trop - expected['Sun'][3]:+7.3f}°")
print(f"Moon diff:    {moon_trop - expected['Moon'][3]:+7.3f}°")
print(f"Mercury diff: {mercury_trop - expected['Mercury'][3]:+7.3f}°")
print()

# 2. SIDEREAL with various ayanamsas
print("CALCULATED - SIDEREAL ZODIAC (WITH AYANAMSA):")
print("-" * 80)

ayanamsas = {
    'Lahiri': swe.SIDM_LAHIRI,
    'Fagan/Bradley': swe.SIDM_FAGAN_BRADLEY,
    'Raman': swe.SIDM_RAMAN,
    'Krishnamurti': swe.SIDM_KRISHNAMURTI,
}

for name, ayanamsa_id in ayanamsas.items():
    swe.set_sid_mode(ayanamsa_id)
    ayanamsa_value = swe.get_ayanamsa_ut(jd)

    sun_sid = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)[0][0]
    moon_sid = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)[0][0]

    moon_diff = abs(moon_sid - expected['Moon'][3])

    print(f"\n{name} (ayanamsa = {ayanamsa_value:.3f}°):")
    print(f"  {deg_to_dms(sun_sid, 'Sun')}")
    print(f"  {deg_to_dms(moon_sid, 'Moon')}")
    print(f"  Moon diff: {moon_sid - expected['Moon'][3]:+7.3f}° (abs: {moon_diff:.3f}°)")

    if moon_diff < 5.0:  # If we're close
        print(f"  ← POSSIBLE MATCH!")

print()
print("=" * 80)
print("ANALYSIS")
print("=" * 80)

# Check what ayanamsa would make the Moon match
moon_tropical = moon_trop
moon_expected = expected['Moon'][3]
needed_ayanamsa = moon_tropical - moon_expected

print(f"Tropical Moon:    {moon_tropical:.3f}°")
print(f"Expected Moon:    {moon_expected:.3f}°")
print(f"Difference:       {needed_ayanamsa:.3f}°")
print()

if abs(needed_ayanamsa) > 20 and abs(needed_ayanamsa) < 30:
    print("⚠️  The ~30° difference suggests:")
    print("   • NOT a sidereal/tropical issue (ayanamsa is ~24°, not 30°)")
    print("   • Possibly a calculation or interpretation error")
    print("   • May need to verify the expected values from Astro.com are correct")
else:
    print("Analysis inconclusive.")
