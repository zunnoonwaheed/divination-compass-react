/**
 * FRONTEND VERIFICATION SCRIPT FOR LIONEL TEST CASE
 *
 * How to use:
 * 1. Open https://thedivinatoryreport.com/full-report in your browser
 * 2. Press F12 to open DevTools
 * 3. Go to Console tab
 * 4. Copy and paste this entire script
 * 5. Press Enter
 *
 * This will verify your frontend against Astro.com baseline values
 */

console.log('🧪 LIONEL TEST CASE VERIFICATION - FRONTEND');
console.log('===========================================\n');

// Expected values from Astro.com
const EXPECTED_VALUES = {
  planets: {
    'Sun': { longitude: 251.6333, zodiac: 'Sagittarius', degree: 11, minute: 38 },
    'Moon': { longitude: 30.0667, zodiac: 'Taurus', degree: 0, minute: 4 },
    'Mercury': { longitude: 241.2167, zodiac: 'Sagittarius', degree: 1, minute: 13 },
    'Venus': { longitude: 277.7833, zodiac: 'Capricorn', degree: 7, minute: 47 },
    'Mars': { longitude: 216.6833, zodiac: 'Scorpio', degree: 6, minute: 41 },
    'Jupiter': { longitude: 19.9667, zodiac: 'Aries', degree: 19, minute: 58 },
    'Saturn': { longitude: 262.2000, zodiac: 'Sagittarius', degree: 22, minute: 12 },
    'Uranus': { longitude: 265.9833, zodiac: 'Sagittarius', degree: 25, minute: 59 },
    'Neptune': { longitude: 276.7500, zodiac: 'Capricorn', degree: 6, minute: 45 },
    'Pluto': { longitude: 221.1333, zodiac: 'Scorpio', degree: 11, minute: 8 }
  },
  angles: {
    'Ascendant': { longitude: 171.2500, zodiac: 'Virgo', degree: 21, minute: 15 },
    'MC': { longitude: 80.4500, zodiac: 'Gemini', degree: 20, minute: 27 }
  },
  birthData: {
    date: '1987-12-04',
    time: '00:21:00',
    latitude: 34.0522,
    longitude: -118.2437,
    utc: '1987-12-04 08:21:00 UTC'
  }
};

// Tolerance settings
const TOLERANCE = {
  planets: 0.1,  // ±0.1° (6 arc minutes)
  angles: 0.5,   // ±0.5° (30 arc minutes) - angles are more sensitive
  strict: 0.05   // ±0.05° (3 arc minutes) for excellent accuracy
};

// Utility functions
function degreesToZodiacSign(degrees) {
  const normalized = ((degrees % 360) + 360) % 360;
  const signs = [
    'Aries', 'Taurus', 'Gemini', 'Cancer',
    'Leo', 'Virgo', 'Libra', 'Scorpio',
    'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
  ];
  const signIndex = Math.floor(normalized / 30);
  const signDegrees = normalized % 30;
  const degree = Math.floor(signDegrees);
  const minute = Math.round((signDegrees - degree) * 60);

  return {
    sign: signs[signIndex],
    degree: degree,
    minute: minute,
    formatted: `${degree}°${minute.toString().padStart(2, '0')}' ${signs[signIndex]}`
  };
}

function checkTolerance(actual, expected, tolerance) {
  const diff = Math.abs(actual - expected);
  return {
    pass: diff <= tolerance,
    difference: diff.toFixed(4),
    percentage: ((diff / expected) * 100).toFixed(2)
  };
}

function formatResult(pass, actual, expected, diff) {
  const icon = pass ? '✅' : '❌';
  const status = pass ? 'PASS' : 'FAIL';
  return `${icon} ${status} - Actual: ${actual}°, Expected: ${expected}°, Diff: ${diff}°`;
}

// Test Results Storage
const results = {
  passed: 0,
  failed: 0,
  tests: []
};

function addResult(category, name, pass, actual, expected, diff) {
  results.tests.push({ category, name, pass, actual, expected, diff });
  if (pass) results.passed++;
  else results.failed++;
}

// ==========================================
// TEST 1: Check if API data is available
// ==========================================
console.log('📋 TEST 1: Checking for API Data in Page');
console.log('------------------------------------------');

let natalChartData = null;
let astroData = null;

// Try to find data in various common locations
const possibleDataLocations = [
  // React state (if exposed)
  () => window.__REACT_DEVTOOLS_GLOBAL_HOOK__?.renderers,
  // Global variables
  () => window.natalChartData,
  () => window.astroData,
  () => window.chartData,
  // Check if data is in local storage
  () => {
    try {
      const stored = localStorage.getItem('natalChartData');
      return stored ? JSON.parse(stored) : null;
    } catch (e) {
      return null;
    }
  }
];

console.log('⚠️  Note: This script cannot directly access React component state.');
console.log('📝 Please manually verify the values displayed on your page.\n');

// ==========================================
// TEST 2: Network Request Verification
// ==========================================
console.log('📋 TEST 2: Network Request Verification');
console.log('------------------------------------------');
console.log('To verify API calls:');
console.log('1. Open the Network tab in DevTools');
console.log('2. Filter by "natal-chart" or "astrocartography"');
console.log('3. Check the Response tab for each request\n');

console.log('Expected API calls:');
console.log(`✓ GET /api/natal-chart?date=1987-12-04&time=00:21:00&latitude=34.0522&longitude=-118.2437`);
console.log(`✓ GET /api/astrocartography?date=1987-12-04&time=00:21:00&latitude=34.0522&longitude=-118.2437\n`);

console.log('Expected natal-chart response should include:');
console.log(`  "timezone_info": { "utc_datetime": "1987-12-04 08:21:00 UTC" }`);
console.log(`  "planets": { "Sun": { "longitude": ~251.63 }, ... }`);
console.log(`  "ascendant": ~171.25`);
console.log(`  "mc": ~80.45\n`);

console.log('Expected astrocartography response should include:');
console.log(`  "lines": [ ... ] // Array with ~1700 items`);
console.log(`  "birth_location": { "latitude": 34.0522, "longitude": -118.2437 }\n`);

// ==========================================
// TEST 3: Manual Verification Guide
// ==========================================
console.log('📋 TEST 3: Manual Verification Checklist');
console.log('------------------------------------------');
console.log('Please verify the following values are displayed on your page:\n');

console.log('🌟 PLANETARY POSITIONS:');
console.table({
  'Sun': '11°38\' Sagittarius (251.63°)',
  'Moon': '0°04\' Taurus (30.07°)',
  'Mercury': '1°13\' Sagittarius (241.22°)',
  'Venus': '7°47\' Capricorn (277.78°)',
  'Mars': '6°41\' Scorpio (216.68°)',
  'Jupiter': '19°58\' Aries (19.97°)',
  'Saturn': '22°12\' Sagittarius (262.20°)',
  'Uranus': '25°59\' Sagittarius (265.98°)',
  'Neptune': '6°45\' Capricorn (276.75°)',
  'Pluto': '11°08\' Scorpio (221.13°)'
});

console.log('\n🎯 CHART ANGLES:');
console.table({
  'Ascendant': '21°15\' Virgo (171.25°)',
  'MC (Midheaven)': '20°27\' Gemini (80.45°)'
});

console.log('\n⏰ BIRTH DATA:');
console.table({
  'Date': 'December 4, 1987',
  'Time': '12:21 AM (00:21:00)',
  'Location': 'Los Angeles, California',
  'Latitude': '34.0522°N',
  'Longitude': '118.2437°W',
  'UTC Result': '1987-12-04 08:21:00 UTC (NOT 00:21)'
});

// ==========================================
// TEST 4: Visual Map Verification
// ==========================================
console.log('\n📋 TEST 4: Visual Map Checklist');
console.log('------------------------------------------');
console.log('Check the following on your astrocartography map:\n');

const mapChecklist = {
  '🎨 Map Theme': 'Dark theme (mapbox dark-v11)',
  '📍 Birth Marker': 'Red marker at Los Angeles (34.05°N, 118.24°W)',
  '🌈 Line Count': '~40 visible lines (10 planets × 4 line types)',
  '📏 Line Patterns': 'MC/IC lines are straight vertical, ASC/DSC are curved',
  '🎨 Sun Lines': 'Gold colored (#FFD700)',
  '🎨 Moon Lines': 'Silver colored (#C0C0C0)',
  '🎨 Mars Lines': 'Orange-red (#FF4500)',
  '🖱️  Click Test': 'Clicking on line shows planet name popup',
  '🖱️  Hover Test': 'Cursor changes to pointer when hovering over lines',
  '📊 Legend': 'Shows all 10 planets with colors at bottom'
};

console.table(mapChecklist);

// ==========================================
// TEST 5: Console Error Check
// ==========================================
console.log('\n📋 TEST 5: Error Detection');
console.log('------------------------------------------');
console.log('Check for common errors:\n');

const errorChecks = [
  { name: 'CORS Errors', check: 'No "blocked by CORS policy" errors' },
  { name: 'API Connection', check: 'No "Failed to fetch" errors' },
  { name: 'Env Variables', check: 'No "API_BASE_URL is not configured" errors' },
  { name: 'Mapbox Token', check: 'No "Mapbox token is not configured" errors' },
  { name: 'Timezone Warning', check: 'UTC shows 08:21 (not 00:21)' }
];

errorChecks.forEach(({ name, check }) => {
  console.log(`☐ ${name}: ${check}`);
});

// ==========================================
// TEST 6: Calculator for Manual Values
// ==========================================
console.log('\n\n📋 TEST 6: Verification Calculator');
console.log('------------------------------------------');
console.log('Use this function to verify values from your page:\n');

window.verifyPlanet = function(planetName, actualLongitude) {
  const expected = EXPECTED_VALUES.planets[planetName];

  if (!expected) {
    console.log(`❌ Planet "${planetName}" not found in baseline values`);
    console.log('Valid planets:', Object.keys(EXPECTED_VALUES.planets).join(', '));
    return;
  }

  const check = checkTolerance(actualLongitude, expected.longitude, TOLERANCE.planets);
  const zodiac = degreesToZodiacSign(actualLongitude);
  const expectedZodiac = degreesToZodiacSign(expected.longitude);

  console.log(`\n🪐 ${planetName} Verification:`);
  console.log(`  Actual:   ${actualLongitude.toFixed(4)}° (${zodiac.formatted})`);
  console.log(`  Expected: ${expected.longitude.toFixed(4)}° (${expectedZodiac.formatted})`);
  console.log(`  Difference: ${check.difference}° (${check.percentage}%)`);
  console.log(`  Tolerance: ±${TOLERANCE.planets}°`);
  console.log(`  Result: ${check.pass ? '✅ PASS' : '❌ FAIL'}`);

  if (check.pass) {
    if (parseFloat(check.difference) <= TOLERANCE.strict) {
      console.log(`  Quality: ⭐ EXCELLENT (within ±${TOLERANCE.strict}°)`);
    } else {
      console.log(`  Quality: ✓ GOOD (within ±${TOLERANCE.planets}°)`);
    }
  } else {
    console.log(`  ⚠️  Difference exceeds tolerance! Check your API response.`);
  }

  return check.pass;
};

window.verifyAngle = function(angleName, actualLongitude) {
  const expected = EXPECTED_VALUES.angles[angleName];

  if (!expected) {
    console.log(`❌ Angle "${angleName}" not found in baseline values`);
    console.log('Valid angles:', Object.keys(EXPECTED_VALUES.angles).join(', '));
    return;
  }

  const check = checkTolerance(actualLongitude, expected.longitude, TOLERANCE.angles);
  const zodiac = degreesToZodiacSign(actualLongitude);
  const expectedZodiac = degreesToZodiacSign(expected.longitude);

  console.log(`\n🎯 ${angleName} Verification:`);
  console.log(`  Actual:   ${actualLongitude.toFixed(4)}° (${zodiac.formatted})`);
  console.log(`  Expected: ${expected.longitude.toFixed(4)}° (${expectedZodiac.formatted})`);
  console.log(`  Difference: ${check.difference}° (${check.percentage}%)`);
  console.log(`  Tolerance: ±${TOLERANCE.angles}°`);
  console.log(`  Result: ${check.pass ? '✅ PASS' : '❌ FAIL'}`);

  if (!check.pass) {
    console.log(`  ⚠️  Note: Angles are sensitive to exact time/location.`);
    console.log(`     • Birth time accurate to the minute?`);
    console.log(`     • Coordinates exact (34.0522, -118.2437)?`);
  }

  return check.pass;
};

console.log('🔧 Helper functions available:');
console.log('  verifyPlanet("Sun", 251.63)     - Verify a planet position');
console.log('  verifyAngle("Ascendant", 171.25) - Verify an angle');
console.log('\nExample usage:');
console.log('  verifyPlanet("Sun", 251.63)');
console.log('  verifyPlanet("Moon", 30.07)');
console.log('  verifyAngle("Ascendant", 171.25)');
console.log('  verifyAngle("MC", 80.45)\n');

// ==========================================
// TEST 7: Batch Verification
// ==========================================
window.verifyAll = function(data) {
  console.log('\n🧪 BATCH VERIFICATION');
  console.log('===========================================\n');

  if (!data || !data.planets) {
    console.log('❌ Invalid data format. Expected format:');
    console.log('{');
    console.log('  planets: { "Sun": { longitude: 251.63 }, ... },');
    console.log('  ascendant: 171.25,');
    console.log('  mc: 80.45');
    console.log('}\n');
    return;
  }

  results.passed = 0;
  results.failed = 0;
  results.tests = [];

  // Check planets
  console.log('🌟 VERIFYING PLANETS:');
  console.log('------------------------------------------');
  Object.entries(EXPECTED_VALUES.planets).forEach(([planet, expected]) => {
    const actual = data.planets[planet]?.longitude;
    if (actual === undefined) {
      console.log(`❌ ${planet}: NOT FOUND in data`);
      addResult('Planet', planet, false, null, expected.longitude, null);
      return;
    }

    const check = checkTolerance(actual, expected.longitude, TOLERANCE.planets);
    console.log(formatResult(check.pass, actual.toFixed(4), expected.longitude.toFixed(4), check.difference));
    addResult('Planet', planet, check.pass, actual, expected.longitude, check.difference);
  });

  // Check angles
  console.log('\n🎯 VERIFYING CHART ANGLES:');
  console.log('------------------------------------------');

  if (data.ascendant !== undefined) {
    const check = checkTolerance(data.ascendant, EXPECTED_VALUES.angles.Ascendant.longitude, TOLERANCE.angles);
    console.log('Ascendant: ' + formatResult(check.pass, data.ascendant.toFixed(4), EXPECTED_VALUES.angles.Ascendant.longitude.toFixed(4), check.difference));
    addResult('Angle', 'Ascendant', check.pass, data.ascendant, EXPECTED_VALUES.angles.Ascendant.longitude, check.difference);
  } else {
    console.log('❌ Ascendant: NOT FOUND in data');
    addResult('Angle', 'Ascendant', false, null, EXPECTED_VALUES.angles.Ascendant.longitude, null);
  }

  if (data.mc !== undefined) {
    const check = checkTolerance(data.mc, EXPECTED_VALUES.angles.MC.longitude, TOLERANCE.angles);
    console.log('MC: ' + formatResult(check.pass, data.mc.toFixed(4), EXPECTED_VALUES.angles.MC.longitude.toFixed(4), check.difference));
    addResult('Angle', 'MC', check.pass, data.mc, EXPECTED_VALUES.angles.MC.longitude, check.difference);
  } else {
    console.log('❌ MC: NOT FOUND in data');
    addResult('Angle', 'MC', false, null, EXPECTED_VALUES.angles.MC.longitude, null);
  }

  // Summary
  console.log('\n📊 SUMMARY:');
  console.log('===========================================');
  console.log(`Total Tests: ${results.passed + results.failed}`);
  console.log(`✅ Passed: ${results.passed}`);
  console.log(`❌ Failed: ${results.failed}`);
  console.log(`Success Rate: ${((results.passed / (results.passed + results.failed)) * 100).toFixed(1)}%\n`);

  if (results.failed === 0) {
    console.log('🎉 ALL TESTS PASSED! Your frontend matches Astro.com baseline!');
  } else {
    console.log('⚠️  Some tests failed. Check your API responses and calculations.');
    console.log('\nFailed tests:');
    results.tests.filter(t => !t.pass).forEach(t => {
      console.log(`  • ${t.category}: ${t.name} (Expected: ${t.expected}, Got: ${t.actual})`);
    });
  }

  return results;
};

console.log('\n🔧 Batch verification function available:');
console.log('  verifyAll(data) - Verify all planets and angles at once');
console.log('\nExample usage:');
console.log('  // After fetching your API data:');
console.log('  const data = { planets: {...}, ascendant: 171.25, mc: 80.45 };');
console.log('  verifyAll(data);\n');

// ==========================================
// TEST 8: Fetch and Verify from API
// ==========================================
console.log('\n📋 TEST 8: Automatic API Test');
console.log('------------------------------------------');

window.testAPIDirectly = async function(apiBaseUrl) {
  console.log(`🔄 Fetching data from: ${apiBaseUrl}\n`);

  try {
    const url = `${apiBaseUrl}/api/natal-chart?date=1987-12-04&time=00:21:00&latitude=34.0522&longitude=-118.2437`;
    console.log(`GET ${url}`);

    const response = await fetch(url);

    if (!response.ok) {
      console.log(`❌ API request failed: ${response.status} ${response.statusText}`);
      return;
    }

    const data = await response.json();
    console.log('✅ API response received\n');

    // Verify UTC conversion
    console.log('⏰ TIMEZONE VERIFICATION:');
    console.log('------------------------------------------');
    if (data.timezone_info?.utc_datetime) {
      const isCorrect = data.timezone_info.utc_datetime === '1987-12-04 08:21:00 UTC';
      console.log(`UTC DateTime: ${data.timezone_info.utc_datetime}`);
      console.log(`Expected: 1987-12-04 08:21:00 UTC`);
      console.log(`Result: ${isCorrect ? '✅ PASS' : '❌ FAIL'}\n`);
    } else {
      console.log('❌ timezone_info not found in response\n');
    }

    // Run batch verification
    const results = verifyAll(data);

    return { data, results };

  } catch (error) {
    console.log(`❌ Error fetching API: ${error.message}`);
    console.log('\nPossible issues:');
    console.log('  • CORS not configured for this domain');
    console.log('  • API URL is incorrect');
    console.log('  • Backend is not running');
  }
};

console.log('🔧 API test function available:');
console.log('  testAPIDirectly("http://localhost:8000")');
console.log('  testAPIDirectly("https://your-railway-url.up.railway.app")');
console.log('\nThis will:');
console.log('  1. Fetch natal chart data from your API');
console.log('  2. Verify UTC timezone conversion');
console.log('  3. Run batch verification on all planets and angles');
console.log('  4. Display detailed results\n');

// ==========================================
// FINAL INSTRUCTIONS
// ==========================================
console.log('\n\n🎯 NEXT STEPS:');
console.log('===========================================');
console.log('1. Check the Network tab for API calls');
console.log('2. Verify the displayed values match the table above');
console.log('3. Use verifyPlanet() to check individual planets');
console.log('4. Use testAPIDirectly() to test your API endpoint');
console.log('5. Complete the visual map checklist\n');

console.log('📝 Quick Test Commands:');
console.log('  testAPIDirectly("http://localhost:8000")');
console.log('  verifyPlanet("Sun", 251.63)');
console.log('  verifyAngle("Ascendant", 171.25)\n');

console.log('✨ Script loaded successfully! Ready for testing.\n');
