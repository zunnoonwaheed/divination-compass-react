"""
Work backwards to find what datetime gives Moon at 0°04' Taurus
"""

import swisseph as swe
from datetime import datetime, timedelta
import pytz

swe.set_ephe_path('./ephe')

target_moon = 30.0667  # 0°04' Taurus
LATITUDE = 34.0522
LONGITUDE = -118.2437

print("=" * 80)
print("FINDING THE CORRECT DATE/TIME FOR MOON AT 0°04' TAURUS")
print("=" * 80)
print()

# Start from Dec 4, 1987, 08:21 UTC and work backwards
base_utc = datetime(1987, 12, 4, 8, 21, 0, tzinfo=pytz.UTC)

print(f"Target Moon position: 0°04' Taurus (30.0667°)")
print(f"Current calculation: Dec 4, 1987, 00:21 PST (08:21 UTC) gives Moon at 60.07° (0°04' Gemini)")
print()
print("Testing different times:")
print("-" * 80)

best_match = None
best_diff = float('inf')

# Test times from 3 days before to 3 days after
for hours_offset in range(-72, 73, 1):  # Test every hour
    test_utc = base_utc + timedelta(hours=hours_offset)
    utc_hours = test_utc.hour + test_utc.minute / 60.0
    jd = swe.julday(test_utc.year, test_utc.month, test_utc.day, utc_hours, swe.GREG_CAL)

    moon_lon = swe.calc_ut(jd, swe.MOON)[0][0]
    diff = abs(moon_lon - target_moon)

    if diff < abs(best_diff):
        best_diff = moon_lon - target_moon
        best_match = test_utc

        # Convert UTC back to LA time
        la_tz = pytz.timezone('America/Los_Angeles')
        la_time = test_utc.astimezone(la_tz)

        signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        sign_idx = int(moon_lon // 30)
        deg = moon_lon % 30
        min = (deg % 1) * 60

        print(f"Offset {hours_offset:+4}h: UTC {test_utc.strftime('%Y-%m-%d %H:%M')}, LA {la_time.strftime('%Y-%m-%d %H:%M %Z')}, Moon {int(deg)}°{int(min):02d}' {signs[sign_idx]} ({moon_lon:.4f}°), diff {moon_lon - target_moon:+.4f}°")

        if diff < 0.1:  # Found a very close match
            print()
            print("=" * 80)
            print("✅ FOUND EXACT MATCH!")
            print("=" * 80)
            print(f"UTC Time:  {test_utc.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"LA Time:   {la_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            print(f"Moon:      {int(deg)}°{int(min):02d}' {signs[sign_idx]} ({moon_lon:.4f}°)")
            print(f"Diff from target: {diff:.4f}°")
            print()
            print("This suggests the correct birth time should be:")
            print(f"  Date: {la_time.strftime('%B %d, %Y')}")
            print(f"  Time: {la_time.strftime('%I:%M %p')}")
            print("=" * 80)
            break

if best_match:
    print()
    print("COMPARISON:")
    print("-" * 80)
    print(f"Original input:  Dec 4, 1987, 12:21 AM (PST)")
    la_tz = pytz.timezone('America/Los_Angeles')
    best_la = best_match.astimezone(la_tz)
    print(f"Correct time:    {best_la.strftime('%b %d, %Y, %I:%M %p (%Z)')}")
    print()
    time_diff = (base_utc - best_match).total_seconds() / 3600
    print(f"Time difference: {time_diff:.1f} hours")
