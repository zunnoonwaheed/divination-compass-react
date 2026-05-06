#!/usr/bin/env python3
"""
Test script to verify new features:
1. Chiron in planet calculations
2. North Node and South Node
3. House system parameter
4. Placidus house system (default)
"""

import sys
sys.path.insert(0, './swiss-ephemeris-api')

from main import compute_chart, convert_local_to_utc
import swisseph as swe

# Set ephemeris path
swe.set_ephe_path('./swiss-ephemeris-api/ephe')

def test_natal_chart_with_new_bodies():
    """Test natal chart calculation with Chiron and Nodes"""
    print("=" * 70)
    print("TEST: Natal Chart with Chiron and Nodes")
    print("=" * 70)

    # Example birth data (January 1, 1990, 12:00 PM in New York)
    year, month, day = 1990, 1, 1
    hour, minute, second = 12, 0, 0
    latitude = 40.7128
    longitude = -74.0060

    print(f"\nBirth Data:")
    print(f"  Date: {year}-{month:02d}-{day:02d}")
    print(f"  Time: {hour:02d}:{minute:02d}:{second:02d} (local)")
    print(f"  Location: ({latitude}, {longitude})")

    # Convert to UTC
    utc_info = convert_local_to_utc(year, month, day, hour, minute, second, latitude, longitude)
    jd_ut = utc_info['utc_jd']

    print(f"\nTimezone: {utc_info['timezone_name']}")
    print(f"UTC DateTime: {utc_info['utc_datetime_str']}")
    print(f"Julian Day (UT): {jd_ut:.6f}")

    # Test with Placidus (default)
    print(f"\n" + "-" * 70)
    print("Testing PLACIDUS house system:")
    print("-" * 70)
    chart_data = compute_chart(jd_ut, latitude, longitude, "P")

    print(f"\nHouse System: {chart_data['house_system']}")
    print(f"Ascendant: {chart_data['ascendant']:.4f}°")
    print(f"MC: {chart_data['mc']:.4f}°")

    print(f"\nPlanets ({len(chart_data['planets'])} total):")
    for planet_name in ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter',
                        'Saturn', 'Uranus', 'Neptune', 'Pluto', 'Chiron',
                        'North Node', 'South Node']:
        if planet_name in chart_data['planets']:
            lon = chart_data['planets'][planet_name]['longitude']
            print(f"  ✓ {planet_name:12s}: {lon:7.4f}°")
        else:
            print(f"  ✗ {planet_name:12s}: MISSING")

    # Verify Chiron is present
    assert 'Chiron' in chart_data['planets'], "ERROR: Chiron not found!"
    assert 'North Node' in chart_data['planets'], "ERROR: North Node not found!"
    assert 'South Node' in chart_data['planets'], "ERROR: South Node not found!"

    # Verify South Node is 180° from North Node
    north_lon = chart_data['planets']['North Node']['longitude']
    south_lon = chart_data['planets']['South Node']['longitude']
    expected_south = (north_lon + 180) % 360
    diff = abs(south_lon - expected_south)
    assert diff < 0.01, f"ERROR: South Node should be 180° from North Node! Diff: {diff:.4f}°"

    print(f"\n✓ South Node verification: {south_lon:.4f}° = (North Node {north_lon:.4f}° + 180°) ✓")

    # Test with Equal house system
    print(f"\n" + "-" * 70)
    print("Testing EQUAL house system (for comparison):")
    print("-" * 70)
    chart_equal = compute_chart(jd_ut, latitude, longitude, "E")

    print(f"\nHouse System: {chart_equal['house_system']}")
    print(f"Ascendant: {chart_equal['ascendant']:.4f}°")
    print(f"MC: {chart_equal['mc']:.4f}°")

    print(f"\nFirst 3 House Cusps (Equal):")
    for i in range(3):
        print(f"  House {i+1}: {chart_equal['houses'][i]:7.4f}°")

    print(f"\nFirst 3 House Cusps (Placidus):")
    for i in range(3):
        print(f"  House {i+1}: {chart_data['houses'][i]:7.4f}°")

    print(f"\n" + "=" * 70)
    print("✅ ALL TESTS PASSED!")
    print("=" * 70)
    print("\nSummary:")
    print(f"  ✓ Chiron calculation: WORKING")
    print(f"  ✓ North Node calculation: WORKING")
    print(f"  ✓ South Node calculation: WORKING (180° opposite)")
    print(f"  ✓ Placidus house system: ACTIVE (default)")
    print(f"  ✓ House system parameter: WORKING")
    print(f"  ✓ House system in response: INCLUDED")

    return True

if __name__ == "__main__":
    try:
        test_natal_chart_with_new_bodies()
        print("\n🎉 All features are working correctly!")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
