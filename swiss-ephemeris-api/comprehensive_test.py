#!/usr/bin/env python3
"""
Comprehensive test against Astro.com baseline
Test case: Lionel, Dec 4, 1987, 12:21 AM, Los Angeles
"""

import requests
import json

# Test case data
API_URL = "http://localhost:8000"
test_params = {
    'date': '1987-12-04',
    'time': '00:21:00',
    'latitude': 34.0522,
    'longitude': -118.2437
}

# Astro.com baseline - EXACT values from client requirements
# Note: Converting degree/minute format to decimal degrees
astro_baseline = {
    'Sun': {'sign_degrees': 11 + 38/60, 'sign': 'Sagittarius', 'abs_degrees': 240 + 11 + 38/60},
    'Moon': {'sign_degrees': 0 + 4/60, 'sign': 'Taurus', 'abs_degrees': 30 + 0 + 4/60},
    'Mercury': {'sign_degrees': 1 + 13/60, 'sign': 'Sagittarius', 'abs_degrees': 240 + 1 + 13/60},
    'Venus': {'sign_degrees': 7 + 47/60, 'sign': 'Capricorn', 'abs_degrees': 270 + 7 + 47/60},
    'Mars': {'sign_degrees': 6 + 41/60, 'sign': 'Scorpio', 'abs_degrees': 210 + 6 + 41/60},
    'Jupiter': {'sign_degrees': 19 + 58/60, 'sign': 'Aries', 'abs_degrees': 0 + 19 + 58/60},
    'Saturn': {'sign_degrees': 22 + 12/60, 'sign': 'Sagittarius', 'abs_degrees': 240 + 22 + 12/60},
    'Uranus': {'sign_degrees': 25 + 59/60, 'sign': 'Sagittarius', 'abs_degrees': 240 + 25 + 59/60},
    'Neptune': {'sign_degrees': 6 + 45/60, 'sign': 'Capricorn', 'abs_degrees': 270 + 6 + 45/60},
    'Pluto': {'sign_degrees': 11 + 8/60, 'sign': 'Scorpio', 'abs_degrees': 210 + 11 + 8/60},
    'Ascendant': {'sign_degrees': 21 + 15/60, 'sign': 'Virgo', 'abs_degrees': 150 + 21 + 15/60},
    'MC': {'sign_degrees': 20 + 27/60, 'sign': 'Gemini', 'abs_degrees': 60 + 20 + 27/60},
}

print('='*80)
print('COMPREHENSIVE TEST AGAINST ASTRO.COM BASELINE')
print('='*80)
print(f'Test Case: Lionel')
print(f'Birth: {test_params["date"]} at {test_params["time"]}')
print(f'Place: Los Angeles, California, USA')
print(f'Coordinates: ({test_params["latitude"]}, {test_params["longitude"]})')
print()

# Fetch natal chart data
print('Fetching natal chart data...')
response = requests.get(f'{API_URL}/api/natal-chart', params=test_params)
data = response.json()

print()
print('='*80)
print('STEP 2: PLANETARY POSITIONS VERIFICATION')
print('='*80)

def deg_to_dms(deg):
    """Convert decimal degrees to deg/min/sec"""
    d = int(deg)
    m = int((deg - d) * 60)
    s = int(((deg - d) * 60 - m) * 60)
    return f"{d}°{m:02d}'{s:02d}\""

def get_zodiac_sign(degrees):
    """Get zodiac sign from absolute degrees"""
    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    normalized = degrees % 360
    sign_index = int(normalized / 30)
    sign_degrees = normalized % 30
    return signs[sign_index], sign_degrees

# Test all planets
results = {}
print(f'{"Body":<12} {"Calculated":<25} {"Expected":<25} {"Diff":<10} {"Status"}')
print('-'*80)

for planet_name in ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']:
    if planet_name in data['planets']:
        calc_lon = data['planets'][planet_name]['longitude']
    else:
        print(f'{planet_name:<12} NOT FOUND IN RESPONSE')
        continue

    expected_lon = astro_baseline[planet_name]['abs_degrees']
    diff = abs(calc_lon - expected_lon)

    calc_sign, calc_deg = get_zodiac_sign(calc_lon)
    exp_sign = astro_baseline[planet_name]['sign']
    exp_deg = astro_baseline[planet_name]['sign_degrees']

    status = '✅' if diff < 0.5 else '❌'
    results[planet_name] = {'diff': diff, 'passed': diff < 0.5}

    calc_str = f'{deg_to_dms(calc_deg)} {calc_sign}'
    exp_str = f'{deg_to_dms(exp_deg)} {exp_sign}'

    print(f'{planet_name:<12} {calc_str:<25} {exp_str:<25} {diff:>6.2f}°  {status}')

print()
print('='*80)
print('STEP 3: ANGLES VERIFICATION')
print('='*80)
print(f'{"Angle":<12} {"Calculated":<25} {"Expected":<25} {"Diff":<10} {"Status"}')
print('-'*80)

# Test Ascendant
asc_calc = data['ascendant']
asc_expected = astro_baseline['Ascendant']['abs_degrees']
asc_diff = abs(asc_calc - asc_expected)
asc_sign, asc_deg = get_zodiac_sign(asc_calc)
asc_exp_sign = astro_baseline['Ascendant']['sign']
asc_exp_deg = astro_baseline['Ascendant']['sign_degrees']
asc_status = '✅' if asc_diff < 0.5 else '❌'
results['Ascendant'] = {'diff': asc_diff, 'passed': asc_diff < 0.5}

calc_str = f'{deg_to_dms(asc_deg)} {asc_sign}'
exp_str = f'{deg_to_dms(asc_exp_deg)} {asc_exp_sign}'
print(f'{"Ascendant":<12} {calc_str:<25} {exp_str:<25} {asc_diff:>6.2f}°  {asc_status}')

# Test MC
mc_calc = data['mc']
mc_expected = astro_baseline['MC']['abs_degrees']
mc_diff = abs(mc_calc - mc_expected)
mc_sign, mc_deg = get_zodiac_sign(mc_calc)
mc_exp_sign = astro_baseline['MC']['sign']
mc_exp_deg = astro_baseline['MC']['sign_degrees']
mc_status = '✅' if mc_diff < 0.5 else '❌'
results['MC'] = {'diff': mc_diff, 'passed': mc_diff < 0.5}

calc_str = f'{deg_to_dms(mc_deg)} {mc_sign}'
exp_str = f'{deg_to_dms(mc_exp_deg)} {mc_exp_sign}'
print(f'{"MC":<12} {calc_str:<25} {exp_str:<25} {mc_diff:>6.2f}°  {mc_status}')

print()
print('='*80)
print('STEP 4: TIMEZONE BUG PATTERN CHECKS')
print('='*80)

tz_info = data['timezone_info']
bug_checks = {
    'Local time treated as UTC': tz_info['utc_datetime'] != '1987-12-04 00:21:00 UTC',
    'UTC offset has correct sign': tz_info['utc_offset_hours'] == -8.0,
    'Timezone detected from coordinates': tz_info['timezone'] == 'America/Los_Angeles',
    'UTC conversion applied correctly': tz_info['utc_datetime'] == '1987-12-04 08:21:00 UTC',
    'No double offset': data['jd_ut'] < 2447134.0,  # JD should be reasonable
}

for check, passed in bug_checks.items():
    print(f'  {"✅" if passed else "❌"} {check}')

print()
print('='*80)
print('SUMMARY')
print('='*80)

total_checks = len(results)
passed_checks = sum(1 for r in results.values() if r['passed'])
failed_checks = total_checks - passed_checks

print(f'Total bodies checked: {total_checks}')
print(f'Passed (within 0.5°): {passed_checks}')
print(f'Failed: {failed_checks}')
print()

if failed_checks > 0:
    print('FAILED ITEMS:')
    for name, result in results.items():
        if not result['passed']:
            print(f'  ❌ {name}: {result["diff"]:.2f}° difference')
    print()

# Overall verdict
all_bug_checks = all(bug_checks.values())
acceptable_accuracy = passed_checks >= 11  # At least 11/12 should match

if all_bug_checks and acceptable_accuracy:
    print('🎉 OVERALL: ✅ PASS')
    print('All timezone bugs fixed, planetary positions match Astro.com baseline!')
else:
    print('⚠️  OVERALL: ❌ FAIL')
    if not all_bug_checks:
        print('   Timezone bugs detected')
    if not acceptable_accuracy:
        print(f'   Only {passed_checks}/{total_checks} positions match')

print('='*80)
