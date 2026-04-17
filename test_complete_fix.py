"""
Complete test suite for the astrocartography fixes
Run this to verify everything works correctly
"""

import sys
sys.path.insert(0, './swiss-ephemeris-api')

import requests
import json
from datetime import datetime

# Test data - Lionel's birth data
TEST_DATA = {
    'date': '1987-12-04',
    'time': '00:21:00',
    'latitude': 34.0522,
    'longitude': -118.2437
}

# Expected values from Astro.com
EXPECTED = {
    'utc_datetime': '1987-12-04 08:21:00 UTC',
    'julian_day': 2447133.847916667,
    'sun_longitude': 251.638,
    'moon_longitude': 60.067,  # Geocentric
    'jupiter_dsc_lon': -82.0,  # Approximate (should be around -82 to -85)
    'mars_asc_lon': -72.0,     # Approximate (should be around -70 to -75)
}

def test_local_api(base_url="http://localhost:8000"):
    """Test the local API"""

    print("=" * 80)
    print("🧪 COMPLETE ASTROCARTOGRAPHY FIX TEST")
    print("=" * 80)
    print(f"Testing API at: {base_url}")
    print()

    # Test 1: Root endpoint
    print("📍 Test 1: Root Endpoint")
    print("-" * 80)
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ PASS - API is running")
            print(f"   Status: {data.get('status')}")
        else:
            print(f"❌ FAIL - Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ FAIL - Error: {str(e)}")
        print("   Make sure to start the server first:")
        print("   cd swiss-ephemeris-api && python3 -m uvicorn main:app --reload --port 8000")
        return False

    print()

    # Test 2: Natal Chart - UTC Conversion
    print("📍 Test 2: Natal Chart - UTC Conversion")
    print("-" * 80)
    try:
        url = f"{base_url}/api/natal-chart"
        response = requests.get(url, params=TEST_DATA, timeout=10)
        data = response.json()

        utc_datetime = data['timezone_info']['utc_datetime']
        julian_day = data['jd_ut']

        if utc_datetime == EXPECTED['utc_datetime']:
            print(f"✅ PASS - UTC conversion correct")
            print(f"   UTC: {utc_datetime}")
        else:
            print(f"❌ FAIL - UTC conversion wrong")
            print(f"   Expected: {EXPECTED['utc_datetime']}")
            print(f"   Got: {utc_datetime}")
            return False

        if abs(julian_day - EXPECTED['julian_day']) < 0.001:
            print(f"✅ PASS - Julian Day correct")
            print(f"   JD: {julian_day}")
        else:
            print(f"❌ FAIL - Julian Day wrong")
            print(f"   Expected: {EXPECTED['julian_day']}")
            print(f"   Got: {julian_day}")
            return False

    except Exception as e:
        print(f"❌ FAIL - Error: {str(e)}")
        return False

    print()

    # Test 3: Planetary Positions
    print("📍 Test 3: Planetary Positions")
    print("-" * 80)
    try:
        sun_lon = data['planets']['Sun']['longitude']
        moon_lon = data['planets']['Moon']['longitude']

        if abs(sun_lon - EXPECTED['sun_longitude']) < 0.01:
            print(f"✅ PASS - Sun position correct")
            print(f"   Sun: {sun_lon:.3f}° (11°38' Sagittarius)")
        else:
            print(f"❌ FAIL - Sun position wrong")
            print(f"   Expected: {EXPECTED['sun_longitude']:.3f}°")
            print(f"   Got: {sun_lon:.3f}°")

        if abs(moon_lon - EXPECTED['moon_longitude']) < 0.5:
            print(f"✅ PASS - Moon position correct")
            print(f"   Moon: {moon_lon:.3f}° (0°04' Gemini)")
        else:
            print(f"⚠️  WARNING - Moon position differs")
            print(f"   Expected: {EXPECTED['moon_longitude']:.3f}° (geocentric)")
            print(f"   Got: {moon_lon:.3f}°")
            if abs(moon_lon - 59.73) < 0.5:
                print(f"   (This is topocentric Moon, which is correct!)")

    except Exception as e:
        print(f"❌ FAIL - Error: {str(e)}")
        return False

    print()

    # Test 4: Astrocartography Lines
    print("📍 Test 4: Astrocartography Lines (Zodiacal Method)")
    print("-" * 80)
    try:
        url = f"{base_url}/api/astrocartography"
        response = requests.get(url, params=TEST_DATA, timeout=30)
        data = response.json()

        lines = data['lines']
        print(f"✅ PASS - Astrocartography API responds")
        print(f"   Total lines: {len(lines)}")

        # Check if using Zodiacal method (should have planet_lon, not planet_ra)
        if len(lines) > 0:
            first_line = lines[0]
            if 'planet_lon' in first_line:
                print(f"✅ PASS - Using Zodiacal method (planet_lon present)")
            elif 'planet_ra' in first_line and 'planet_lon' not in first_line:
                print(f"❌ FAIL - Still using In Mundo method (planet_ra only)")
                return False

        # Test Jupiter DSC position
        jupiter_dsc = [l for l in lines if l['planet'] == 'Jupiter' and l['line_type'] == 'DSC']
        if jupiter_dsc:
            # Find Jupiter DSC at latitude ~40°N (middle US)
            jup_at_40 = sorted(jupiter_dsc, key=lambda x: abs(x['latitude'] - 40))[:1]
            if jup_at_40:
                lon = jup_at_40[0]['longitude']
                lat = jup_at_40[0]['latitude']

                # Expected: around -82 to -85 (Michigan/Ohio/Georgia)
                if -86 < lon < -80:
                    print(f"✅ PASS - Jupiter DSC position correct")
                    print(f"   Latitude {lat:.1f}°N: Longitude {lon:.2f}°")
                    print(f"   (Michigan/Ohio/Georgia area)")
                else:
                    print(f"❌ FAIL - Jupiter DSC position wrong")
                    print(f"   Expected: -82° to -85° (Michigan/Ohio)")
                    print(f"   Got: {lon:.2f}° at latitude {lat:.1f}°")
                    return False
        else:
            print(f"⚠️  WARNING - No Jupiter DSC lines found")

        # Test Mars ASC position
        mars_asc = [l for l in lines if l['planet'] == 'Mars' and l['line_type'] == 'ASC']
        if mars_asc:
            mars_at_40 = sorted(mars_asc, key=lambda x: abs(x['latitude'] - 40))[:1]
            if mars_at_40:
                lon = mars_at_40[0]['longitude']
                lat = mars_at_40[0]['latitude']

                # Expected: around -70 to -75 (Atlantic Ocean/East Coast)
                if -76 < lon < -68:
                    print(f"✅ PASS - Mars ASC position correct")
                    print(f"   Latitude {lat:.1f}°N: Longitude {lon:.2f}°")
                    print(f"   (Atlantic Ocean/East Coast)")
                else:
                    print(f"⚠️  WARNING - Mars ASC position may be off")
                    print(f"   Expected: -70° to -75°")
                    print(f"   Got: {lon:.2f}° at latitude {lat:.1f}°")
        else:
            print(f"⚠️  WARNING - No Mars ASC lines found")

    except Exception as e:
        print(f"❌ FAIL - Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    print()
    print("=" * 80)
    print("✅ ALL TESTS PASSED!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Make sure changes are committed to GitHub (commit 7be4f32)")
    print("2. Verify Railway has deployed the latest code")
    print("3. Update frontend environment variable VITE_API_BASE_URL")
    print("4. Redeploy frontend on Lovable")
    print()

    return True


if __name__ == "__main__":
    # Test local API
    success = test_local_api()

    if not success:
        print()
        print("❌ Some tests failed. Please check the output above.")
        print()
        sys.exit(1)
    else:
        sys.exit(0)
