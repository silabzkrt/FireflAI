/**
 * FireflAI - Main Dashboard Application Component
 * 
 * Central controller and layout orchestrator for the FireflAI wildfire intelligence system.
 * Manages Google Maps integration, real-time and historical risk grid synchronization,
 * active wildfire target selections, ML drone deployment workflows (YOLO verification,
 * cellular automata spread modeling, and Qwen-3B tactical dispatch generation), as well as
 * temporal timeline scrubbing and tactical asset overlays (water sources, settlements).
 */

import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import axios from 'axios';
import { GoogleMap, useJsApiLoader, Marker, Polygon } from '@react-google-maps/api';
import { ShieldAlert, Flame, X } from 'lucide-react';

import { API_BASE, parseWktPolygon, createMarkerIcon, createWaterMarkerIcon, createSettlementMarkerIcon } from './utils/helpers';
import TopNav from './components/TopNav';
import RiskPanel from './components/RiskPanel';
import TargetDetailsCard from './components/TargetDetailsCard';
import MapLegend from './components/MapLegend';
import DetectionPanel from './components/DetectionPanel';
import SpreadPanel from './components/SpreadPanel';
import DispatchPanel from './components/DispatchPanel';
import TimelineSlider from './components/TimelineSlider';

const MAP_OPTIONS = {
  mapTypeId: 'hybrid',
  disableDefaultUI: true,
};

const MAP_CENTER = { lat: 39.0, lng: 35.0 };
const POLYGON_STYLE = {
  fillColor: '#ef4444',
  fillOpacity: 0.45,
  strokeColor: '#dc2626',
  strokeOpacity: 0.95,
  strokeWeight: 2.5,
  zIndex: 10,
};

export default function App() {
  const [riskPoints, setRiskPoints] = useState([]);
  const [selectedPoint, setSelectedPoint] = useState(null);
  const [activeDetection, setActiveDetection] = useState(null);
  const [droneStatus, setDroneStatus] = useState('IDLE');
  const [fireWarning, setFireWarning] = useState(false);
  const [spreadPrediction, setSpreadPrediction] = useState(null);
  const [dispatchPlan, setDispatchPlan] = useState(null);
  const [dispatchLoading, setDispatchLoading] = useState(false);
  const [dispatchExecuted, setDispatchExecuted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [filterType, setFilterType] = useState('ALL');
  const [hoursAgo, setHoursAgo] = useState(0);

  const mapRef = useRef(null);
  const debounceTimerRef = useRef(null);
  const hourCacheRef = useRef({});
  const abortControllerRef = useRef(null);

  const { isLoaded } = useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY || ''
  });

  const onLoad = useCallback((map) => { mapRef.current = map; }, []);
  const onUnmount = useCallback(() => { mapRef.current = null; }, []);

  const fetchDatabaseState = useCallback(async (targetHours = 0, forceRefresh = false) => {
    setHoursAgo(targetHours);

    if (!forceRefresh && hourCacheRef.current[targetHours]) {
      const cached = hourCacheRef.current[targetHours];
      setRiskPoints(cached.points);
      setFireWarning(cached.hasFire);
      if (cached.activeFire) {
        setSelectedPoint(cached.activeFire);
        setActiveDetection(cached.activeFire.detection || null);
        setSpreadPrediction(cached.activeFire.spreadPrediction || null);
        setDispatchPlan(cached.activeFire.dispatchPlan || null);
        setDroneStatus('DISPATCHED');
      } else {
        setSelectedPoint(null);
        setActiveDetection(null);
        setSpreadPrediction(null);
        setDispatchPlan(null);
        setDroneStatus('IDLE');
      }
      setIsSyncing(false);
      return;
    }

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    setIsSyncing(true);
    setErrorMsg(null);

    try {
      const signal = abortControllerRef.current.signal;
      let rawPoints = [];

      try {
        const gridRes = await axios.get(`${API_BASE}/risk/turkey-grid`, {
          params: { hours_ago: targetHours },
          signal
        });
        rawPoints = Array.isArray(gridRes.data)
          ? gridRes.data
          : (gridRes.data?.data || gridRes.data?.grid || gridRes.data?.sectors || gridRes.data?.points || []);
      } catch (gridErr) {
        if (axios.isCancel(gridErr)) return;
        const fallbackRes = await axios.get(`${API_BASE}/risk/grid`, {
          params: { hours_ago: targetHours },
          signal
        });
        rawPoints = Array.isArray(fallbackRes.data) ? fallbackRes.data : (fallbackRes.data?.data || []);
      }

      let basePoints = rawPoints
        .map((p, idx) => {
          const rawScore = Number(p.risk_score ?? p.risk_level ?? p.score ?? 0);
          const normalizedScore = rawScore > 0 && rawScore <= 1.0 ? Math.round(rawScore * 100) : Math.round(rawScore);

          return {
            ...p,
            latitude: Number(p.latitude ?? p.lat ?? 0),
            longitude: Number(p.longitude ?? p.lon ?? p.lng ?? 0),
            risk_score: normalizedScore,
            temperature: p.temperature != null ? Number(p.temperature) : null,
            humidity: p.humidity != null ? Number(p.humidity) : null,
            wind_speed: p.wind_speed != null ? Number(p.wind_speed) : null,
            wind_direction: p.wind_direction != null ? Number(p.wind_direction) : null,
            location: p.location_name || p.risk_point || p.location || p.istasyon_adi || (p.is_fixed ? `Tower #${idx + 1}` : `Grid P-${idx}`),
            is_fixed: Boolean(p.is_fixed ?? p.fixed ?? p.is_station),
            is_wildfire: Boolean(p.is_wildfire || p.wildfire || normalizedScore >= 95),
            slope: Number(p.slope ?? 5.0),
            vegetation_density: Number(p.vegetation_density ?? 0.7),
            captured_at: p.captured_at
          };
        })
        .filter(pt => pt.is_fixed || pt.is_wildfire || pt.risk_score > 60);

      const [detRes, spreadRes, dispRes] = await Promise.allSettled([
        axios.get(`${API_BASE}/detection/history?limit=50`, { signal }),
        axios.get(`${API_BASE}/spread/history?limit=50`, { signal }),
        axios.get(`${API_BASE}/dispatch/history?limit=20`, { signal })
      ]);

      const droneDetections = detRes.status === 'fulfilled' ? (Array.isArray(detRes.value.data) ? detRes.value.data : detRes.value.data?.data || []) : [];
      const activeSpreads = spreadRes.status === 'fulfilled' ? (Array.isArray(spreadRes.value.data) ? spreadRes.value.data : spreadRes.value.data?.data || []) : [];
      const dispatchPlans = dispRes.status === 'fulfilled' ? (Array.isArray(dispRes.value.data) ? dispRes.value.data : dispRes.value.data?.data || []) : [];

      const confirmedFires = droneDetections.map((det, dIdx) => {
        const detId = det.id ?? det.detection_id ?? det.fire_detection_id ?? `D-${dIdx + 1}`;
        const detLat = Number(det.latitude ?? det.lat ?? 0);
        const detLng = Number(det.longitude ?? det.lon ?? 0);

        const matchingSpread = activeSpreads.find(s => s.fire_detection_id === detId);
        const matchingDispatch = dispatchPlans.find(
          p => p.fire_detection_id === detId || (Math.abs(p.latitude - detLat) < 0.1 && Math.abs(p.longitude - detLng) < 0.1)
        );
        const fallbackPoint = basePoints.find(p => Math.abs(p.latitude - detLat) < 0.25 && Math.abs(p.longitude - detLng) < 0.25);

        return {
          detection_id: detId,
          latitude: detLat,
          longitude: detLng,
          class_name: det.class_name || det.label || 'WILDFIRE & SMOKE',
          confidence: det.confidence || 0.88,
          total_frames: det.total_frames || 0,
          detected_at: det.created_at || new Date().toISOString(),
          spreadPrediction: {
            detection_id: detId,
            prediction_hours: matchingSpread?.prediction_hours || 6,
            spread_probability: matchingSpread?.spread_probability ?? 0.88,
            affected_area_hectares: matchingSpread?.affected_area_hectares ?? 10.0,
            wind_speed: matchingSpread?.wind_speed ?? fallbackPoint?.wind_speed ?? 14.0,
            wind_direction: matchingSpread?.wind_direction ?? fallbackPoint?.wind_direction ?? 160.0,
            temperature: matchingSpread?.temperature ?? fallbackPoint?.temperature,
            humidity: matchingSpread?.humidity ?? fallbackPoint?.humidity,
            raw_wkt: matchingSpread?.spread_area,
            spread_area_geojson: matchingSpread?.spread_area_geojson
          },
          dispatchPlan: matchingDispatch || null
        };
      });

      confirmedFires.forEach((fire, idx) => {
        let matched = false;
        basePoints = basePoints.map(p => {
          if (Math.abs(p.latitude - fire.latitude) < 0.15 && Math.abs(p.longitude - fire.longitude) < 0.15) {
            matched = true;
            return {
              ...p,
              risk_score: 99,
              is_wildfire: true,
              threat_name: 'CONFIRMED WILDFIRE',
              detection: fire,
              spreadPrediction: fire.spreadPrediction,
              dispatchPlan: fire.dispatchPlan
            };
          }
          return p;
        });

        if (!matched && fire.latitude !== 0 && fire.longitude !== 0) {
          basePoints.unshift({
            latitude: fire.latitude,
            longitude: fire.longitude,
            risk_score: 99,
            is_wildfire: true,
            location: fire.detection_id ? `Wildfire Sector #${fire.detection_id}` : `Wildfire Incident #${idx + 1}`,
            threat_name: 'CONFIRMED WILDFIRE',
            detection: fire,
            spreadPrediction: fire.spreadPrediction,
            dispatchPlan: fire.dispatchPlan
          });
        }
      });

      const firstActiveFire = basePoints.find(p => p.is_wildfire);
      const hasFire = Boolean(firstActiveFire);

      hourCacheRef.current[targetHours] = {
        points: basePoints,
        hasFire,
        activeFire: firstActiveFire || null
      };

      setRiskPoints(basePoints);
      setFireWarning(hasFire);
      if (firstActiveFire) {
        setSelectedPoint(firstActiveFire);
        setActiveDetection(firstActiveFire.detection);
        setSpreadPrediction(firstActiveFire.spreadPrediction || null);
        setDispatchPlan(firstActiveFire.dispatchPlan || null);
        setDroneStatus('DISPATCHED');
      }
    } catch (err) {
      if (axios.isCancel(err)) return;
      console.error('Database Sync Error:', err);
      setErrorMsg(`Failed to sync risk grid for T - ${targetHours}H.`);
    } finally {
      setIsSyncing(false);
    }
  }, []);

  useEffect(() => {
    let isMounted = true;
    let timeoutId;
    let intervalId;

    // Fetch ONLY hours=0 at start
    fetchDatabaseState(0, true);

    const now = new Date();
    const nextHour = new Date();
    nextHour.setHours(now.getHours() + 1, 0, 0, 0);
    const msUntilNextHour = nextHour.getTime() - now.getTime();

    timeoutId = setTimeout(() => {
      if (!isMounted) return;
      fetchDatabaseState(0, true);
      intervalId = setInterval(() => {
        if (isMounted) fetchDatabaseState(0, true);
      }, 60 * 60 * 1000);
    }, msUntilNextHour);

    return () => {
      isMounted = false;
      clearTimeout(timeoutId);
      if (intervalId) clearInterval(intervalId);
    };
  }, [fetchDatabaseState]);

  const handleHourSliderChange = (newHours) => {
    setHoursAgo(newHours);

    if (hourCacheRef.current[newHours]) {
      const cached = hourCacheRef.current[newHours];
      setRiskPoints(cached.points);
      setFireWarning(cached.hasFire);
    }

    if (debounceTimerRef.current) clearTimeout(debounceTimerRef.current);

    debounceTimerRef.current = setTimeout(() => {
      fetchDatabaseState(newHours);
    }, 600); 
  };

  const handlePresetClick = (newHours) => {
    setHoursAgo(newHours);
    if (debounceTimerRef.current) clearTimeout(debounceTimerRef.current);
    fetchDatabaseState(newHours);
  };

  const handleSelectPoint = (point) => {
    setSelectedPoint(point);
    setErrorMsg(null);
    setDispatchExecuted(false);

    if (mapRef.current) {
      mapRef.current.panTo({ lat: point.latitude, lng: point.longitude });
      mapRef.current.setZoom(8);
    }

    if (point.detection) {
      setActiveDetection(point.detection);
      setSpreadPrediction(point.spreadPrediction || null);
      setDispatchPlan(point.dispatchPlan || null);
      setDroneStatus('DISPATCHED');
    } else {
      setActiveDetection(null);
      setSpreadPrediction(null);
      setDispatchPlan(null);
      setDroneStatus('IDLE');
    }
  };

  const getTestVideoFile = async () => {
    try {
      const response = await fetch('/Test_Video.mp4');
      if (response.ok) {
        const blob = await response.blob();
        return new File([blob], 'Test_Video.mp4', { type: 'video/mp4' });
      }
    } catch (e) {
      console.warn('Fallback test video load', e);
    }
    return new Blob(['mock-video-binary-stream'], { type: 'video/mp4' });
  };

  const handleGenerateDispatch = async (targetPoint) => {
    const targetLat = targetPoint?.latitude ?? selectedPoint?.latitude;
    const targetLng = targetPoint?.longitude ?? selectedPoint?.longitude;

    if (!targetLat || !targetLng) return;

    if (targetPoint?.dispatchPlan) {
      setDispatchPlan(targetPoint.dispatchPlan);
      setSelectedPoint(prev => ({ ...prev, dispatchPlan: targetPoint.dispatchPlan }));
      return;
    }

    setDispatchLoading(true);
    setErrorMsg(null);
    setDispatchExecuted(false);

    try {
      const histRes = await axios.get(`${API_BASE}/dispatch/history?limit=50`);
      const allPlans = Array.isArray(histRes.data) ? histRes.data : (histRes.data?.data || []);

      const existingPlan = allPlans.find(
        p => p.latitude != null && p.longitude != null &&
             Math.abs(Number(p.latitude) - Number(targetLat)) < 0.01 &&
             Math.abs(Number(p.longitude) - Number(targetLng)) < 0.01
      );

      if (existingPlan) {
        setDispatchPlan(existingPlan);
        setRiskPoints(prev =>
          prev.map(p => (p.latitude === targetLat && p.longitude === targetLng ? { ...p, dispatchPlan: existingPlan } : p))
        );
        setSelectedPoint(prev => ({ ...prev, dispatchPlan: existingPlan }));
      } else {
        const res = await axios.post(`${API_BASE}/dispatch/generate-plan`, {
          latitude: targetLat,
          longitude: targetLng,
          detection_id: targetPoint?.detection?.detection_id || selectedPoint?.detection?.detection_id || null,
          wind_speed: targetPoint?.wind_speed ?? 15.0,
          wind_direction: targetPoint?.wind_direction ?? 180.0
        });

        const newPlan = res.data;
        setDispatchPlan(newPlan);
        setRiskPoints(prev =>
          prev.map(p => (p.latitude === targetLat && p.longitude === targetLng ? { ...p, dispatchPlan: newPlan } : p))
        );
        setSelectedPoint(prev => ({ ...prev, dispatchPlan: newPlan }));
      }
    } catch (err) {
      console.error('Dispatch fetch/generation error:', err);
      setErrorMsg('Failed to load dispatch plan from database.');
    } finally {
      setDispatchLoading(false);
    }
  };

  const handleSendDrone = async (point) => {
    if (!point) return;
    setDroneStatus('DEPLOYING');
    setLoading(true);
    setFireWarning(false);
    setSpreadPrediction(null);
    setDispatchPlan(null);
    setDispatchExecuted(false);
    setErrorMsg(null);

    try {
      const videoFile = await getTestVideoFile();
      const fd = new FormData();
      fd.append('file', videoFile, 'Test_Video.mp4');
      fd.append('latitude', point.latitude);
      fd.append('longitude', point.longitude);

      const detectionRes = await axios.post(`${API_BASE}/detection/detect-frame`, fd, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      const data = detectionRes.data || {};

      const rawDetId = data.detection_id ?? data.id ?? data.fire_detection_id ?? data.data?.detection_id ?? data.data?.id ?? null;
      const parsedDetId = rawDetId ? parseInt(rawDetId, 10) : null;
      const detId = parsedDetId && !isNaN(parsedDetId) ? parsedDetId : null;

      let allDetections = [];
      if (Array.isArray(data.detections_by_frame)) allDetections = data.detections_by_frame.flatMap(frame => frame.detections || []);
      else if (Array.isArray(data.detections)) allDetections = data.detections;
      else if (Array.isArray(data.frames)) allDetections = data.frames.flatMap(f => f.detections || []);

      const wildfireDetections = allDetections.filter(d => {
        const name = (d.class_name || d.name || '').toLowerCase();
        return name.includes('wildfire') || name.includes('fire') || name.includes('flame');
      });

      const smokeDetections = allDetections.filter(d => {
        const name = (d.class_name || d.name || '').toLowerCase();
        return name.includes('smoke');
      });

      const isFireDetected = data.detected === true || wildfireDetections.length > 0 || smokeDetections.length > 0;

      if (isFireDetected) {
        const highestWildfire = wildfireDetections.reduce((max, d) => (d.confidence > (max?.confidence || 0) ? d : max), null);
        const highestSmoke = smokeDetections.reduce((max, d) => (d.confidence > (max?.confidence || 0) ? d : max), null);

        let displayClass = 'WILDFIRE';
        if (highestWildfire && highestSmoke) displayClass = 'WILDFIRE & SMOKE';
        else if (highestSmoke && !highestWildfire) displayClass = 'SMOKE';

        const peakConfidence = highestWildfire?.confidence || highestSmoke?.confidence || 0.88;

        const detectionData = {
          latitude: point.latitude,
          longitude: point.longitude,
          detection_id: detId,
          class_name: displayClass,
          confidence: peakConfidence,
          total_frames: data.total_frames_processed || 0,
          threat_count: allDetections.length
        };

        setActiveDetection(detectionData);
        setFireWarning(true);

        const weatherPayload = {
          wind_speed: point.wind_speed ?? 14.0,
          wind_direction: point.wind_direction ?? 160.0,
          temperature: point.temperature ?? 28.0,
          humidity: point.humidity ?? 45.0
        };

        let spreadData = null;

        try {
          const spreadRes = await axios.post(`${API_BASE}/spread/predict-spread`, {
            detection_id: detId,
            latitude: parseFloat(Number(point.latitude).toFixed(6)),
            longitude: parseFloat(Number(point.longitude).toFixed(6)),
            prediction_hours: 6,
            wind_speed: parseFloat(Number(weatherPayload.wind_speed).toFixed(1)),
            wind_direction: parseFloat(Number(weatherPayload.wind_direction).toFixed(1)),
            slope: point.slope ?? 5.0,
            vegetation_density: point.vegetation_density ?? 0.7
          });

          spreadData = { ...spreadRes.data, detection_id: detId, prediction_hours: spreadRes.data?.prediction_hours ?? 6, ...weatherPayload };
          setSpreadPrediction(spreadData);
        } catch (spreadErr) {
          console.warn('Spread ML model failed:', spreadErr);
        }

        setRiskPoints(prev =>
          prev.map(p =>
            p.latitude === point.latitude && p.longitude === point.longitude
              ? {
                  ...p,
                  risk_score: 99,
                  is_wildfire: true,
                  threat_name: 'CONFIRMED WILDFIRE',
                  detection: detectionData,
                  spreadPrediction: spreadData,
                  detected_at: new Date().toLocaleTimeString()
                }
              : p
          )
        );

        setSelectedPoint(prev => ({ ...prev, risk_score: 99, is_wildfire: true, threat_name: 'CONFIRMED WILDFIRE', detection: detectionData, spreadPrediction: spreadData }));
        handleGenerateDispatch(point);
      } else {
        const clearData = { latitude: point.latitude, longitude: point.longitude, class_name: 'CLEAR', confidence: 0.99 };
        setActiveDetection(clearData);
        setFireWarning(false);
        setRiskPoints(prev => prev.map(p => (p.latitude === point.latitude && p.longitude === point.longitude ? { ...p, detection: clearData, is_wildfire: false } : p)));
        setSelectedPoint(prev => ({ ...prev, detection: clearData, is_wildfire: false }));
      }
      setDroneStatus('DISPATCHED');
    } catch (err) {
      console.error('Drone scan error:', err);
      setErrorMsg('Failed to process video with AI backend.');
      setDroneStatus('DISPATCHED');
    } finally {
      setLoading(false);
    }
  };

  const currentPointDetection = useMemo(() => {
    if (!selectedPoint) return null;
    if (selectedPoint.detection) return selectedPoint.detection;
    if (activeDetection && Math.abs(activeDetection.latitude - selectedPoint.latitude) < 0.0001 && Math.abs(activeDetection.longitude - selectedPoint.longitude) < 0.0001) {
      return activeDetection;
    }
    return null;
  }, [selectedPoint, activeDetection]);

  const polyCoords = useMemo(() => {
    if (spreadPrediction?.spread_area_geojson?.coordinates?.[0]) {
      return spreadPrediction.spread_area_geojson.coordinates[0].map(c => ({ lat: Number(c[1]), lng: Number(c[0]) }));
    }
    if (spreadPrediction?.raw_wkt) return parseWktPolygon(spreadPrediction.raw_wkt);
    if (spreadPrediction?.spread_area) return parseWktPolygon(spreadPrediction.spread_area);
    return null;
  }, [spreadPrediction]);

  const filteredPoints = useMemo(() => {
    if (filterType === 'FIXED') return riskPoints.filter(p => p.is_fixed);
    if (filterType === 'CRITICAL') return riskPoints.filter(p => !p.is_fixed && (p.is_wildfire || p.risk_score >= 85));
    if (filterType === 'HIGH') return riskPoints.filter(p => !p.is_fixed && !p.is_wildfire && p.risk_score >= 70 && p.risk_score < 85);
    return riskPoints;
  }, [riskPoints, filterType]);

  const counts = useMemo(() => ({
    all: riskPoints.length,
    fixed: riskPoints.filter(p => p.is_fixed).length,
    critical: riskPoints.filter(p => !p.is_fixed && (p.is_wildfire || p.risk_score >= 85)).length,
    high: riskPoints.filter(p => !p.is_fixed && !p.is_wildfire && p.risk_score >= 70 && p.risk_score < 85).length,
  }), [riskPoints]);

  return (
    <div className="h-screen w-full flex flex-col bg-bg-app font-sans">
      <TopNav 
        fetchDatabaseState={() => handlePresetClick(hoursAgo)} 
        isSyncing={isSyncing} 
        hoursAgo={hoursAgo}
      />

      <div className="flex flex-1 overflow-hidden relative">
        <RiskPanel 
          counts={counts}
          filterType={filterType}
          setFilterType={setFilterType}
          errorMsg={errorMsg}
          filteredPoints={filteredPoints}
          selectedPoint={selectedPoint}
          handleSelectPoint={handleSelectPoint}
        />

        <main className="flex-1 relative bg-bg-app">
          {/* Loading overlay for fetching historical data */}
          {isSyncing && (
            <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-[2px] pointer-events-none transition-opacity duration-300">
              <div className="bg-slate-900/90 text-white px-6 py-4 rounded-lg shadow-2xl font-mono text-sm border border-slate-700 flex items-center gap-4">
                <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                <span>Loading Map Data, please wait...</span>
              </div>
            </div>
          )}

          {isLoaded ? (
          <GoogleMap
            mapContainerStyle={{ width: '100%', height: '100%' }}
            center={MAP_CENTER}
            zoom={6}
            options={MAP_OPTIONS}
            onLoad={onLoad}
            onUnmount={onUnmount}
          >
            {filteredPoints.map((pt, i) => (
              <Marker 
                key={`marker-${pt.latitude}-${pt.longitude}-${hoursAgo}-${i}`}
                position={{ lat: pt.latitude, lng: pt.longitude }}
                title={pt.is_wildfire ? 'ACTIVE WILDFIRE DETECTED' : pt.location || (pt.is_fixed ? 'Fixed Station' : `Risk Sector (${pt.risk_score})`)}
                icon={createMarkerIcon(pt)}
                onClick={() => handleSelectPoint(pt)}
              />
            ))}

            {dispatchPlan?.nearest_water_sources?.map((w, idx) => {
              const lat = Number(w.koordinat_enlem);
              const lng = Number(w.koordinat_boylam);
              if (!lat || !lng) return null;

              return (
                <Marker
                  key={`water-source-${idx}-${lat}-${lng}`}
                  position={{ lat, lng }}
                  title={`[Water Source] ${w.isim || 'Water Supply'} (${w.tip || 'Supply Point'})`}
                  icon={createWaterMarkerIcon()}
                />
              );
            })}

            {dispatchPlan?.threatened_facilities?.map((s, idx) => {
              const lat = Number(s.koordinat_enlem);
              const lng = Number(s.koordinat_boylam);
              if (!lat || !lng) return null;

              return (
                <Marker
                  key={`threatened-facility-${idx}-${lat}-${lng}`}
                  position={{ lat, lng }}
                  title={`[Settlement/Facility] ${s.isim || 'Settlement'} - ${s.nufus_yatak_kapasitesi || 'Threatened Area'}`}
                  icon={createSettlementMarkerIcon()}
                />
              );
            })}

            {polyCoords && (
              <Polygon
                paths={polyCoords}
                options={POLYGON_STYLE}
              />
            )}
          </GoogleMap>
          ) : (
            <div className="w-full h-full flex items-center justify-center text-text-muted font-mono">Loading Satellite Map...</div>
          )}

          <TimelineSlider 
            hoursAgo={hoursAgo} 
            onHourChange={handleHourSliderChange}
            onPresetClick={handlePresetClick}
            isSyncing={isSyncing} 
          />

          {fireWarning && (
            <div className="absolute top-4 left-1/2 -translate-x-1/2 z-40 bg-red-600 text-white border-2 border-red-300 px-6 py-3 flex items-center gap-3 shadow-2xl animate-pulse font-mono font-black text-sm tracking-widest rounded">
              <Flame size={24} className="animate-bounce text-yellow-300" />
              <span>CRITICAL ALERT: ACTIVE WILDFIRE DETECTED IN MONITORED SECTOR!</span>
              <button onClick={() => setFireWarning(false)} className="ml-3 p-1 hover:bg-red-700 rounded transition-colors cursor-pointer">
                <X size={16} />
              </button>
            </div>
          )}

          <TargetDetailsCard 
            selectedPoint={selectedPoint}
            currentPointDetection={currentPointDetection}
            setSelectedPoint={setSelectedPoint}
            handleSendDrone={handleSendDrone}
            loading={loading}
            droneStatus={droneStatus}
            handleGenerateDispatch={handleGenerateDispatch}
            dispatchLoading={dispatchLoading}
          />

          <MapLegend />
        </main>

        {currentPointDetection && currentPointDetection.class_name !== 'CLEAR' && (
          <aside className="w-[440px] bg-bg-panel border-l border-border flex flex-col shrink-0 overflow-y-auto">
            <div className="p-4 bg-primary text-white font-bold flex items-center justify-between">
              <div className="flex items-center gap-2">
                <ShieldAlert size={20} />
                <span>TACTICAL INCIDENT REPORT</span>
              </div>
              <span className="text-[10px] font-mono bg-red-700/80 px-2 py-0.5 border border-white/20">ACTIVE THREAT</span>
            </div>

            <div className="p-4 space-y-5">
              <DetectionPanel currentPointDetection={currentPointDetection} />
              <SpreadPanel spreadPrediction={spreadPrediction} />
              <DispatchPanel 
                dispatchPlan={dispatchPlan}
                dispatchLoading={dispatchLoading}
                dispatchExecuted={dispatchExecuted}
                selectedPoint={selectedPoint}
                currentPointDetection={currentPointDetection}
                handleGenerateDispatch={handleGenerateDispatch}
                setDispatchExecuted={setDispatchExecuted}
              />
            </div>
          </aside>
        )}
      </div>
    </div>
  );
}