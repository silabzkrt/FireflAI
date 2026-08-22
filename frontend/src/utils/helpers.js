import axios from 'axios';

export const API_BASE = 'http://localhost:8000/api/v1';

export const fetchLiveWeather = async (lat, lng) => {
  if (lat === undefined || lng === undefined || isNaN(Number(lat)) || isNaN(Number(lng))) {
    return { wind_speed: 16.5, wind_direction: 160.0, temperature: 28.5, humidity: 40.0 };
  }
  
  const latitude = parseFloat(Number(lat).toFixed(4));
  const longitude = parseFloat(Number(lng).toFixed(4));

  try {
    const res = await axios.get(
      `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m&current_weather=true`
    );

    if (res.data?.current) {
      const cur = res.data.current;
      return {
        wind_speed: Number(cur.wind_speed_10m ?? res.data.current_weather?.windspeed ?? 18.0),
        wind_direction: Number(cur.wind_direction_10m ?? res.data.current_weather?.winddirection ?? 160.0),
        temperature: Number(cur.temperature_2m ?? res.data.current_weather?.temperature ?? 28.0),
        humidity: Number(cur.relative_humidity_2m ?? 42.0)
      };
    }
    if (res.data?.current_weather) {
      const cur = res.data.current_weather;
      return {
        wind_speed: Number(cur.windspeed ?? 18.0),
        wind_direction: Number(cur.winddirection ?? 160.0),
        temperature: Number(cur.temperature ?? 28.0),
        humidity: 42.0
      };
    }
  } catch (err) {
    console.warn(`Open-Meteo weather request for [${latitude}, ${longitude}] failed:`, err);
  }

  return {
    wind_speed: parseFloat((14.0 + (Math.abs(Math.sin(latitude * 12.0)) * 14.0)).toFixed(1)),
    wind_direction: parseFloat((((longitude * 45.0) % 360 + 360) % 360).toFixed(0)),
    temperature: parseFloat((25.0 + (Math.abs(Math.cos(latitude * 8.0)) * 10.0)).toFixed(1)),
    humidity: parseFloat((30.0 + (Math.abs(Math.sin(longitude * 6.0)) * 25.0)).toFixed(0))
  };
};

export const getRiskColor = (score, isWildfire = false) => {
  if (isWildfire || score >= 85) return '#ef4444'; 
  if (score >= 70) return '#f97316'; 
  return '#f59e0b'; 
};

export const getRiskTier = (score, isWildfire = false) => {
  if (isWildfire) return { label: 'WILDFIRE', bg: 'bg-red-600/30', text: 'text-red-300', border: 'border-red-500 font-extrabold animate-pulse' };
  if (score >= 85) return { label: 'CRITICAL', bg: 'bg-red-500/20', text: 'text-red-400', border: 'border-red-500/40' };
  if (score >= 70) return { label: 'HIGH', bg: 'bg-orange-500/20', text: 'text-orange-400', border: 'border-orange-500/40' };
  return { label: 'ELEVATED', bg: 'bg-amber-500/20', text: 'text-amber-400', border: 'border-amber-500/40' };
};

export const parseWktPolygon = (wkt) => {
  if (!wkt || typeof wkt !== 'string') return null;
  try {
    const cleanWkt = wkt.includes('((') 
      ? wkt.split('((').pop().split('))')[0] 
      : wkt.replace(/[A-Z\(\);=]/gi, '').trim();
    if (!cleanWkt) return null;
    
    const pairs = cleanWkt.split(',');
    const parsed = pairs.map(pair => {
      const parts = pair.trim().split(/[\s,]+/);
      if (parts.length >= 2) {
        const lng = parseFloat(parts[0]);
        const lat = parseFloat(parts[1]);
        if (!isNaN(lat) && !isNaN(lng)) {
          return { lat, lng };
        }
      }
      return null;
    }).filter(Boolean);

    return parsed.length > 0 ? parsed : null;
  } catch (e) {
    console.warn('WKT parsing fallback:', e);
    return null;
  }
};

export const createMarkerIcon = (pt) => {
  if (!window.google?.maps) return undefined;

  if (pt.is_wildfire) {
    const svg = `
      <svg xmlns="http://www.w3.org/2000/svg" width="56" height="56" viewBox="0 0 56 56">
        <defs>
          <radialGradient id="fire-glow-${pt.latitude}" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#ff0000" stop-opacity="1"/>
            <stop offset="35%" stop-color="#ef4444" stop-opacity="0.8"/>
            <stop offset="70%" stop-color="#f97316" stop-opacity="0.4"/>
            <stop offset="100%" stop-color="#dc2626" stop-opacity="0"/>
          </radialGradient>
        </defs>
        <circle cx="28" cy="28" r="26" fill="url(#fire-glow-${pt.latitude})" />
        <circle cx="28" cy="28" r="20" fill="#7f1d1d" fill-opacity="0.75" stroke="#ef4444" stroke-width="2.5" stroke-dasharray="4 2"/>
        <circle cx="28" cy="28" r="13" fill="#dc2626" stroke="#ffffff" stroke-width="2.5"/>
        <path d="M28 17 C26 21, 22 23, 22 28 C22 31.3, 24.7 34, 28 34 C31.3 34, 34 31.3, 34 28 C34 24, 30 20, 28 17 Z M28 31 C26.3 31, 25 29.7, 25 28 C25 26.5, 27 24.5, 28 23.5 C29 24.5, 31 26.5, 31 28 C31 29.7, 29.7 31, 28 31 Z" fill="#fef08a"/>
      </svg>
    `;
    return {
      url: `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`,
      scaledSize: new window.google.maps.Size(56, 56),
      anchor: new window.google.maps.Point(28, 28),
    };
  }

  if (pt.is_fixed) {
    const svg = `
      <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 36 36">
        <circle cx="18" cy="18" r="16" fill="#0284c7" fill-opacity="0.25" stroke="#38bdf8" stroke-width="1.5" stroke-dasharray="3 2"/>
        <polygon points="18,7 28,18 18,29 8,18" fill="#0284c7" stroke="#38bdf8" stroke-width="1.5"/>
        <circle cx="18" cy="18" r="5" fill="#38bdf8" stroke="#ffffff" stroke-width="1.5"/>
        <circle cx="18" cy="18" r="1.8" fill="#ffffff"/>
      </svg>
    `;
    return {
      url: `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`,
      scaledSize: new window.google.maps.Size(36, 36),
      anchor: new window.google.maps.Point(18, 18),
    };
  }

  const color = getRiskColor(pt.risk_score);
  const isCritical = pt.risk_score >= 85;
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40">
      <defs>
        <radialGradient id="aura-${pt.risk_score}" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="${color}" stop-opacity="0.9"/>
          <stop offset="50%" stop-color="${color}" stop-opacity="0.35"/>
          <stop offset="100%" stop-color="${color}" stop-opacity="0"/>
        </radialGradient>
      </defs>
      <circle cx="20" cy="20" r="19" fill="url(#aura-${pt.risk_score})" />
      <circle cx="20" cy="20" r="${isCritical ? 8 : 6.5}" fill="${color}" />
    </svg>
  `;
  return {
    url: `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`,
    scaledSize: new window.google.maps.Size(40, 40),
    anchor: new window.google.maps.Point(20, 20),
  };
};