/**
 * Astrocartography Map Component
 *
 * Copy this file to your Lovable project at: src/components/AstrocartographyMap.tsx
 *
 * This component renders an interactive map with astrocartography ley lines
 * using Mapbox GL.
 */

import { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { AstrocartographyLine } from '@/lib/api';

interface AstrocartographyMapProps {
  lines: AstrocartographyLine[];
  birthLocation: { latitude: number; longitude: number };
  mapboxToken: string;
  className?: string;
}

/**
 * Get color for each planet
 */
function getPlanetColor(planet: string): string {
  const colors: Record<string, string> = {
    Sun: '#FFD700',      // Gold
    Moon: '#C0C0C0',     // Silver
    Mercury: '#87CEEB',  // Sky Blue
    Venus: '#FF69B4',    // Hot Pink
    Mars: '#FF4500',     // Orange Red
    Jupiter: '#FF8C00',  // Dark Orange
    Saturn: '#4B0082',   // Indigo
    Uranus: '#00CED1',   // Dark Turquoise
    Neptune: '#4169E1',  // Royal Blue
    Pluto: '#8B0000',    // Dark Red
    Chiron: '#7CFC00',   // Lawn Green
    'North Node': '#DA70D6' // Orchid
  };
  return colors[planet] || '#FFFFFF';
}

/**
 * Get line style based on line type (ASC, MC, DSC, IC)
 */
function getLineStyle(lineType: string): { width: number; dashArray?: number[] } {
  switch (lineType) {
    case 'ASC':
      return { width: 3 }; // Solid, thicker
    case 'MC':
      return { width: 2 }; // Solid, medium
    case 'DSC':
      return { width: 2, dashArray: [4, 2] }; // Dashed
    case 'IC':
      return { width: 2, dashArray: [2, 2] }; // Dotted
    default:
      return { width: 2 };
  }
}

export function AstrocartographyMap({
  lines,
  birthLocation,
  mapboxToken,
  className = ''
}: AstrocartographyMapProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const [mapError, setMapError] = useState<string | null>(null);

  useEffect(() => {
    if (!mapContainer.current) return;

    if (!mapboxToken) {
      setMapError('Mapbox token is not configured');
      return;
    }

    try {
      // Set Mapbox access token
      mapboxgl.accessToken = mapboxToken;

      // Initialize map
      map.current = new mapboxgl.Map({
        container: mapContainer.current,
        style: 'mapbox://styles/mapbox/dark-v11',
        center: [birthLocation.longitude, birthLocation.latitude],
        zoom: 2,
        projection: 'mercator'
      });

      // Add navigation controls
      map.current.addControl(new mapboxgl.NavigationControl(), 'top-right');

      // Add birth location marker
      const birthMarker = new mapboxgl.Marker({
        color: '#FF0000',
        scale: 1.2
      })
        .setLngLat([birthLocation.longitude, birthLocation.latitude])
        .setPopup(
          new mapboxgl.Popup({ offset: 25 }).setHTML(
            `<div style="padding: 8px;">
              <h3 style="margin: 0 0 4px 0; font-size: 14px; font-weight: bold;">Birth Location</h3>
              <p style="margin: 0; font-size: 12px;">
                Lat: ${birthLocation.latitude.toFixed(4)}<br/>
                Lon: ${birthLocation.longitude.toFixed(4)}
              </p>
            </div>`
          )
        )
        .addTo(map.current);

      // Wait for map to load before adding lines
      map.current.on('load', () => {
        if (!map.current) return;

        // Group lines by planet and line type
        const linesByKey = lines.reduce((acc, line) => {
          const key = `${line.planet}-${line.line_type}`;
          if (!acc[key]) {
            acc[key] = {
              planet: line.planet,
              lineType: line.line_type,
              coordinates: []
            };
          }
          acc[key].coordinates.push([line.longitude, line.latitude]);
          return acc;
        }, {} as Record<string, { planet: string; lineType: string; coordinates: number[][] }>);

        // Add each line to the map
        Object.entries(linesByKey).forEach(([key, data]) => {
          if (!map.current || data.coordinates.length === 0) return;

          // Sort coordinates by latitude for proper line drawing
          const sortedCoords = data.coordinates.sort((a, b) => b[1] - a[1]);

          // Add source
          map.current.addSource(key, {
            type: 'geojson',
            data: {
              type: 'Feature',
              properties: {
                planet: data.planet,
                lineType: data.lineType
              },
              geometry: {
                type: 'LineString',
                coordinates: sortedCoords
              }
            }
          });

          const lineStyle = getLineStyle(data.lineType);
          const color = getPlanetColor(data.planet);

          // Add layer
          map.current.addLayer({
            id: key,
            type: 'line',
            source: key,
            layout: {
              'line-join': 'round',
              'line-cap': 'round'
            },
            paint: {
              'line-color': color,
              'line-width': lineStyle.width,
              'line-opacity': 0.8,
              ...(lineStyle.dashArray && { 'line-dasharray': lineStyle.dashArray })
            }
          });

          // Add click handler for line info
          map.current.on('click', key, (e) => {
            if (!e.features || e.features.length === 0) return;

            const feature = e.features[0];
            const props = feature.properties;

            new mapboxgl.Popup()
              .setLngLat(e.lngLat)
              .setHTML(
                `<div style="padding: 8px;">
                  <h3 style="margin: 0 0 4px 0; font-size: 14px; font-weight: bold; color: ${color};">
                    ${props?.planet} ${props?.lineType}
                  </h3>
                  <p style="margin: 0; font-size: 12px;">
                    ${props?.lineType === 'ASC' ? 'Rising' :
                      props?.lineType === 'MC' ? 'Midheaven' :
                      props?.lineType === 'DSC' ? 'Setting' :
                      'Lower Heaven'}
                  </p>
                </div>`
              )
              .addTo(map.current!);
          });

          // Change cursor on hover
          map.current.on('mouseenter', key, () => {
            if (map.current) {
              map.current.getCanvas().style.cursor = 'pointer';
            }
          });

          map.current.on('mouseleave', key, () => {
            if (map.current) {
              map.current.getCanvas().style.cursor = '';
            }
          });
        });
      });

      map.current.on('error', (e) => {
        console.error('Mapbox error:', e);
        setMapError(`Map error: ${e.error?.message || 'Unknown error'}`);
      });

    } catch (error) {
      console.error('Failed to initialize map:', error);
      setMapError(error instanceof Error ? error.message : 'Failed to initialize map');
    }

    // Cleanup
    return () => {
      map.current?.remove();
      map.current = null;
    };
  }, [lines, birthLocation, mapboxToken]);

  if (mapError) {
    return (
      <div className={`${className} flex items-center justify-center bg-gray-900 text-white p-8`}>
        <div className="text-center">
          <h3 className="text-lg font-bold mb-2">Failed to load map</h3>
          <p className="text-sm text-gray-400">{mapError}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={className}>
      <div ref={mapContainer} className="w-full h-full min-h-[500px]" />

      {/* Legend */}
      <div className="mt-4 p-4 bg-gray-900 rounded-lg">
        <h4 className="text-sm font-bold mb-2 text-white">Planetary Lines</h4>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
          {Object.entries({
            Sun: '#FFD700',
            Moon: '#C0C0C0',
            Mercury: '#87CEEB',
            Venus: '#FF69B4',
            Mars: '#FF4500',
            Jupiter: '#FF8C00',
            Saturn: '#4B0082',
            Uranus: '#00CED1',
            Neptune: '#4169E1',
            Pluto: '#8B0000',
            Chiron: '#7CFC00',
            'North Node': '#DA70D6'
          }).map(([planet, color]) => (
            <div key={planet} className="flex items-center gap-2">
              <div
                className="w-4 h-4 rounded"
                style={{ backgroundColor: color }}
              />
              <span className="text-xs text-white">{planet}</span>
            </div>
          ))}
        </div>
        <div className="mt-3 pt-3 border-t border-gray-700">
          <div className="grid grid-cols-2 gap-2 text-xs text-gray-400">
            <div>ASC: Rising (solid, thick)</div>
            <div>MC: Midheaven (solid)</div>
            <div>DSC: Setting (dashed)</div>
            <div>IC: Lower Heaven (dotted)</div>
          </div>
        </div>
      </div>
    </div>
  );
}
