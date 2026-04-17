#!/bin/bash

# Test Script for Swiss Ephemeris API Backend
# This script tests all the endpoints to ensure the backend is working correctly

echo "🧪 Swiss Ephemeris API Test Script"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Ask for the Railway URL
echo "Enter your Railway backend URL (e.g., https://swiss-ephemeris-api-production.up.railway.app):"
read -r RAILWAY_URL

# Remove trailing slash if present
RAILWAY_URL=${RAILWAY_URL%/}

echo ""
echo "Testing backend at: $RAILWAY_URL"
echo ""

# Test 1: Root endpoint
echo "Test 1: API Root Endpoint"
echo "-------------------------"
response=$(curl -s -w "\n%{http_code}" "$RAILWAY_URL/")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Root endpoint is working"
    echo "  Response: $(echo "$body" | jq -r '.status' 2>/dev/null || echo "OK")"
else
    echo -e "${RED}✗ FAIL${NC} - Root endpoint returned HTTP $http_code"
    exit 1
fi
echo ""

# Test 2: Natal Chart endpoint
echo "Test 2: Natal Chart Endpoint"
echo "----------------------------"
response=$(curl -s -w "\n%{http_code}" "$RAILWAY_URL/api/natal-chart?date=1990-01-01&time=12:00:00&latitude=31.5497&longitude=74.3436")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Natal chart endpoint is working"
    # Check if response contains expected data
    if echo "$body" | jq -e '.planets.Sun' > /dev/null 2>&1; then
        echo "  Sun position: $(echo "$body" | jq -r '.planets.Sun.longitude' 2>/dev/null)°"
        echo "  Moon position: $(echo "$body" | jq -r '.planets.Moon.longitude' 2>/dev/null)°"
        echo "  Ascendant: $(echo "$body" | jq -r '.ascendant' 2>/dev/null)°"
    else
        echo -e "  ${YELLOW}⚠ WARNING${NC} - Response doesn't contain expected planet data"
    fi
else
    echo -e "${RED}✗ FAIL${NC} - Natal chart endpoint returned HTTP $http_code"
    echo "  Error: $body"
    exit 1
fi
echo ""

# Test 3: Astrocartography endpoint
echo "Test 3: Astrocartography Endpoint"
echo "---------------------------------"
response=$(curl -s -w "\n%{http_code}" "$RAILWAY_URL/api/astrocartography?date=1990-01-01&time=12:00:00&latitude=31.5497&longitude=74.3436")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Astrocartography endpoint is working"
    # Check if response contains lines
    line_count=$(echo "$body" | jq -r '.lines | length' 2>/dev/null || echo "0")
    echo "  Total ley lines: $line_count"
    if [ "$line_count" -gt 0 ]; then
        echo "  Sample line: $(echo "$body" | jq -r '.lines[0].planet' 2>/dev/null) $(echo "$body" | jq -r '.lines[0].line_type' 2>/dev/null)"
    else
        echo -e "  ${YELLOW}⚠ WARNING${NC} - No ley lines returned (might be normal for some calculations)"
    fi
else
    echo -e "${RED}✗ FAIL${NC} - Astrocartography endpoint returned HTTP $http_code"
    echo "  Error: $body"
    exit 1
fi
echo ""

# Test 4: Mapbox token endpoint
echo "Test 4: Mapbox Token Endpoint"
echo "-----------------------------"
response=$(curl -s -w "\n%{http_code}" "$RAILWAY_URL/api/mapbox-token")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Mapbox token endpoint is working"
    token=$(echo "$body" | jq -r '.token' 2>/dev/null)
    if [ -n "$token" ] && [ "$token" != "null" ]; then
        echo "  Token (first 20 chars): ${token:0:20}..."
    else
        echo -e "  ${RED}✗ FAIL${NC} - Token is empty or invalid"
        exit 1
    fi
else
    echo -e "${RED}✗ FAIL${NC} - Mapbox token endpoint returned HTTP $http_code"
    echo "  Error: $body"
    echo -e "  ${YELLOW}→ Make sure MAPBOX_TOKEN is set in Railway environment variables${NC}"
    exit 1
fi
echo ""

# Test 5: CORS headers
echo "Test 5: CORS Configuration"
echo "-------------------------"
cors_headers=$(curl -s -I "$RAILWAY_URL/" | grep -i "access-control")
if [ -n "$cors_headers" ]; then
    echo -e "${GREEN}✓ PASS${NC} - CORS headers are present"
    echo "$cors_headers" | sed 's/^/  /'
else
    echo -e "${YELLOW}⚠ WARNING${NC} - CORS headers not detected (might be OK if OPTIONS not checked)"
fi
echo ""

# Summary
echo "=================================="
echo -e "${GREEN}🎉 All tests passed!${NC}"
echo ""
echo "Your backend is ready to use. Next steps:"
echo "1. Copy this URL: $RAILWAY_URL"
echo "2. Add it to Lovable as VITE_API_BASE_URL (or NEXT_PUBLIC_API_BASE_URL)"
echo "3. Deploy your Lovable frontend"
echo ""
echo "Test URLs you can try in browser:"
echo "  • API Docs: $RAILWAY_URL/"
echo "  • Natal Chart: $RAILWAY_URL/api/natal-chart?date=1990-01-01&time=12:00:00&latitude=31.5497&longitude=74.3436"
echo "  • Astrocartography: $RAILWAY_URL/api/astrocartography?date=1990-01-01&time=12:00:00&latitude=31.5497&longitude=74.3436"
echo ""
