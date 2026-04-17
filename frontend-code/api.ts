/**
 * API Configuration and Functions for Swiss Ephemeris
 *
 * Copy this file to your Lovable project at: src/lib/api.ts
 */

// API Configuration - reads from environment variables
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  '';

const MAPBOX_TOKEN =
  import.meta.env.VITE_MAPBOX_TOKEN ||
  process.env.NEXT_PUBLIC_MAPBOX_TOKEN ||
  '';

export const apiConfig = {
  baseUrl: API_BASE_URL,
  mapboxToken: MAPBOX_TOKEN,
};

// Type definitions
export interface NatalChartParams {
  date: string;      // Format: YYYY-MM-DD (e.g., "1990-01-01")
  time: string;      // Format: HH:MM:SS (e.g., "12:00:00")
  latitude: number;  // Decimal degrees (e.g., 31.5497 for Lahore)
  longitude: number; // Decimal degrees (e.g., 74.3436 for Lahore)
}

export interface PlanetPosition {
  longitude: number;
  latitude: number;
  distance: number;
  speed: number;
}

export interface NatalChartData {
  jd_ut: number;
  input: NatalChartParams;
  planets: Record<string, PlanetPosition>;
  houses: number[];
  ascendant: number;
  mc: number;
}

export interface AstrocartographyLine {
  planet: string;
  line_type: 'ASC' | 'MC' | 'DSC' | 'IC';
  latitude: number;
  longitude: number;
  planet_longitude: number;
}

export interface AstrocartographyData {
  jd_ut: number;
  input: NatalChartParams;
  lines: AstrocartographyLine[];
  birth_location: {
    latitude: number;
    longitude: number;
  };
}

/**
 * Fetch natal chart data from the backend
 */
export async function fetchNatalChart(params: NatalChartParams): Promise<NatalChartData> {
  if (!API_BASE_URL) {
    throw new Error('API_BASE_URL is not configured. Please set VITE_API_BASE_URL or NEXT_PUBLIC_API_BASE_URL environment variable.');
  }

  const url = new URL(`${API_BASE_URL}/api/natal-chart`);
  url.searchParams.append('date', params.date);
  url.searchParams.append('time', params.time);
  url.searchParams.append('latitude', params.latitude.toString());
  url.searchParams.append('longitude', params.longitude.toString());

  console.log('Fetching natal chart from:', url.toString());

  const response = await fetch(url.toString(), {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error('Natal chart fetch failed:', response.status, errorText);
    throw new Error(`Failed to fetch natal chart: ${response.statusText}`);
  }

  const data = await response.json();
  console.log('Natal chart data received:', data);
  return data;
}

/**
 * Fetch astrocartography data from the backend
 */
export async function fetchAstrocartography(params: NatalChartParams): Promise<AstrocartographyData> {
  if (!API_BASE_URL) {
    throw new Error('API_BASE_URL is not configured. Please set VITE_API_BASE_URL or NEXT_PUBLIC_API_BASE_URL environment variable.');
  }

  const url = new URL(`${API_BASE_URL}/api/astrocartography`);
  url.searchParams.append('date', params.date);
  url.searchParams.append('time', params.time);
  url.searchParams.append('latitude', params.latitude.toString());
  url.searchParams.append('longitude', params.longitude.toString());

  console.log('Fetching astrocartography from:', url.toString());

  const response = await fetch(url.toString(), {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error('Astrocartography fetch failed:', response.status, errorText);
    throw new Error(`Failed to fetch astrocartography: ${response.statusText}`);
  }

  const data = await response.json();
  console.log('Astrocartography data received:', data);
  return data;
}

/**
 * Get Mapbox token from backend (alternative to env var)
 */
export async function getMapboxToken(): Promise<string> {
  // First try environment variable
  if (MAPBOX_TOKEN) {
    console.log('Using Mapbox token from environment variable');
    return MAPBOX_TOKEN;
  }

  // Fallback to fetching from backend
  if (!API_BASE_URL) {
    throw new Error('Neither MAPBOX_TOKEN nor API_BASE_URL is configured');
  }

  console.log('Fetching Mapbox token from backend...');
  const response = await fetch(`${API_BASE_URL}/api/mapbox-token`);

  if (!response.ok) {
    throw new Error(`Failed to fetch Mapbox token: ${response.statusText}`);
  }

  const data = await response.json();
  console.log('Mapbox token received from backend');
  return data.token;
}

/**
 * Test connection to the backend API
 */
export async function testApiConnection(): Promise<boolean> {
  if (!API_BASE_URL) {
    console.error('API_BASE_URL is not configured');
    return false;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/`);
    if (response.ok) {
      const data = await response.json();
      console.log('API connection successful:', data);
      return true;
    }
    return false;
  } catch (error) {
    console.error('API connection failed:', error);
    return false;
  }
}
