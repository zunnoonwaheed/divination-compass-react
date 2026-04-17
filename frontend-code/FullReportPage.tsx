/**
 * Full Report Page Component
 *
 * Copy this file to your Lovable project at: src/pages/FullReport.tsx
 * or wherever your full-report page is located
 *
 * This is a complete implementation that fetches and displays both
 * natal chart data and astrocartography map.
 */

import { useEffect, useState } from 'react';
import {
  fetchNatalChart,
  fetchAstrocartography,
  getMapboxToken,
  testApiConnection,
  NatalChartData,
  AstrocartographyData,
  NatalChartParams
} from '@/lib/api';
import { AstrocartographyMap } from '@/components/AstrocartographyMap';

// You can replace this with actual user data from form, URL params, or user profile
const DEFAULT_BIRTH_DATA: NatalChartParams = {
  date: '1990-01-01',
  time: '12:00:00',
  latitude: 31.5497,  // Lahore, Pakistan
  longitude: 74.3436
};

export default function FullReportPage() {
  const [natalChartData, setNatalChartData] = useState<NatalChartData | null>(null);
  const [astroData, setAstroData] = useState<AstrocartographyData | null>(null);
  const [mapboxToken, setMapboxToken] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [apiConnected, setApiConnected] = useState<boolean | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        setError(null);

        // Test API connection first
        console.log('Testing API connection...');
        const connected = await testApiConnection();
        setApiConnected(connected);

        if (!connected) {
          throw new Error('Cannot connect to backend API. Please check your VITE_API_BASE_URL or NEXT_PUBLIC_API_BASE_URL environment variable.');
        }

        // Get Mapbox token
        console.log('Getting Mapbox token...');
        const token = await getMapboxToken();
        setMapboxToken(token);

        // You might want to get this from:
        // - URL query parameters: const params = new URLSearchParams(window.location.search)
        // - User profile/local storage
        // - A form submission
        const birthData = DEFAULT_BIRTH_DATA;

        console.log('Fetching chart data for:', birthData);

        // Fetch both natal chart and astrocartography data in parallel
        const [natalData, astroDataResult] = await Promise.all([
          fetchNatalChart(birthData),
          fetchAstrocartography(birthData)
        ]);

        setNatalChartData(natalData);
        setAstroData(astroDataResult);

        console.log('All data loaded successfully');
      } catch (err) {
        console.error('Error loading data:', err);
        setError(err instanceof Error ? err.message : 'Failed to load chart data');
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold mb-2">Loading Your Full Report...</h2>
          <p className="text-gray-400 text-sm">Calculating natal chart and astrocartography data</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center p-4">
        <div className="max-w-2xl w-full bg-red-950 border border-red-800 rounded-lg p-6">
          <h2 className="text-2xl font-bold mb-4 text-red-300">Failed to Load Report</h2>
          <p className="text-red-200 mb-4">{error}</p>

          <div className="bg-red-900 bg-opacity-50 rounded p-4 mb-4">
            <h3 className="font-semibold mb-2">Troubleshooting Steps:</h3>
            <ol className="list-decimal list-inside space-y-1 text-sm text-red-100">
              <li>Check that your Railway backend is deployed and running</li>
              <li>Verify VITE_API_BASE_URL or NEXT_PUBLIC_API_BASE_URL is set in Lovable Secrets</li>
              <li>Verify VITE_MAPBOX_TOKEN or NEXT_PUBLIC_MAPBOX_TOKEN is set</li>
              <li>Check browser console for detailed error messages</li>
              <li>Verify CORS is configured correctly in Railway backend</li>
            </ol>
          </div>

          <div className="text-sm text-gray-400">
            API Connection Status: {apiConnected === null ? 'Testing...' : apiConnected ? '✓ Connected' : '✗ Failed'}
          </div>

          <button
            onClick={() => window.location.reload()}
            className="mt-4 bg-red-700 hover:bg-red-600 text-white px-6 py-2 rounded-lg transition"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            Your Full Astrological Report
          </h1>
          <p className="text-gray-400 mt-2">
            Birth Details: {DEFAULT_BIRTH_DATA.date} at {DEFAULT_BIRTH_DATA.time}
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8 space-y-8">
        {/* Natal Chart Section */}
        <section className="bg-gray-900 rounded-lg p-6 border border-gray-800">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
            <span className="text-purple-400">✨</span>
            Natal Chart
          </h2>

          {natalChartData ? (
            <div className="space-y-6">
              {/* Chart Angles */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gray-800 rounded-lg p-4">
                  <h3 className="font-semibold mb-2 text-purple-300">Ascendant</h3>
                  <p className="text-2xl">{natalChartData.ascendant.toFixed(2)}°</p>
                  <p className="text-sm text-gray-400 mt-1">
                    {getZodiacSign(natalChartData.ascendant)}
                  </p>
                </div>
                <div className="bg-gray-800 rounded-lg p-4">
                  <h3 className="font-semibold mb-2 text-purple-300">Midheaven (MC)</h3>
                  <p className="text-2xl">{natalChartData.mc.toFixed(2)}°</p>
                  <p className="text-sm text-gray-400 mt-1">
                    {getZodiacSign(natalChartData.mc)}
                  </p>
                </div>
              </div>

              {/* Planetary Positions */}
              <div>
                <h3 className="font-semibold mb-3 text-purple-300">Planetary Positions</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {Object.entries(natalChartData.planets).map(([planet, data]) => (
                    <div key={planet} className="bg-gray-800 rounded p-3">
                      <div className="flex justify-between items-start mb-1">
                        <span className="font-semibold">{planet}</span>
                        <span className="text-sm text-gray-400">
                          {data.longitude.toFixed(2)}°
                        </span>
                      </div>
                      <div className="text-sm text-purple-300">
                        {getZodiacSign(data.longitude)}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        Speed: {data.speed.toFixed(4)}°/day
                        {data.speed < 0 && ' (Retrograde)'}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Houses */}
              <div>
                <h3 className="font-semibold mb-3 text-purple-300">House Cusps</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2">
                  {natalChartData.houses.map((house, index) => (
                    <div key={index} className="bg-gray-800 rounded p-2 text-center">
                      <div className="text-xs text-gray-400">House {index + 1}</div>
                      <div className="text-sm font-semibold">{house.toFixed(2)}°</div>
                      <div className="text-xs text-purple-300">
                        {getZodiacSign(house)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <p className="text-gray-400">No natal chart data available</p>
          )}
        </section>

        {/* Astrocartography Map Section */}
        <section className="bg-gray-900 rounded-lg p-6 border border-gray-800">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
            <span className="text-pink-400">🗺️</span>
            Astrocartography Map
            <span className="text-xs bg-purple-500 text-white px-2 py-1 rounded">AI-Powered</span>
          </h2>

          {astroData && mapboxToken ? (
            <>
              <AstrocartographyMap
                lines={astroData.lines}
                birthLocation={astroData.birth_location}
                mapboxToken={mapboxToken}
                className="rounded-lg overflow-hidden"
              />

              <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-green-950 border border-green-800 rounded-lg p-4">
                  <h3 className="font-semibold mb-2 text-green-300">Favorable Locations</h3>
                  <p className="text-sm text-gray-300">
                    Places where your planetary lines intersect positively, enhancing career, love, and spiritual growth.
                  </p>
                </div>
                <div className="bg-orange-950 border border-orange-800 rounded-lg p-4">
                  <h3 className="font-semibold mb-2 text-orange-300">Challenging Locations</h3>
                  <p className="text-sm text-gray-300">
                    Areas where planetary energies may create obstacles or require extra effort to thrive.
                  </p>
                </div>
              </div>

              <div className="mt-4 text-sm text-gray-400">
                <p>
                  <strong>Origin point:</strong> Lahore, Pakistan ({astroData.birth_location.latitude.toFixed(4)}, {astroData.birth_location.longitude.toFixed(4)})
                </p>
                <p className="mt-2">
                  <strong>Total ley lines:</strong> {astroData.lines.length} calculated based on your birth chart
                </p>
              </div>
            </>
          ) : (
            <div className="bg-red-950 border border-red-800 rounded p-4">
              <p className="text-red-200">
                Failed to load map. {!mapboxToken && 'Mapbox token not available.'}
              </p>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

/**
 * Helper function to convert degrees to zodiac sign
 */
function getZodiacSign(degrees: number): string {
  const normalized = ((degrees % 360) + 360) % 360;
  const signs = [
    'Aries', 'Taurus', 'Gemini', 'Cancer',
    'Leo', 'Virgo', 'Libra', 'Scorpio',
    'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
  ];
  const signIndex = Math.floor(normalized / 30);
  const signDegrees = normalized % 30;
  return `${signs[signIndex]} ${signDegrees.toFixed(0)}°`;
}
