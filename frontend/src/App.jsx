import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import axios from 'axios';
import { GoogleMap, useJsApiLoader, Marker, Polygon } from '@react-google-maps/api';
import { ShieldAlert, Flame, X } from 'lucide-react';

import { API_BASE, fetchLiveWeather, parseWktPolygon, createMarkerIcon } from './utils/helpers';
import TopNav from './components/TopNav';
import RiskPanel from './components/RiskPanel';
import TargetDetailsCard from './components/TargetDetailsCard';
import MapLegend from './components/MapLegend';
import DetectionPanel from './components/DetectionPanel';
import SpreadPanel from './components/SpreadPanel';
import DispatchPanel from './components/DispatchPanel';

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
  
  const mapRef = useRef(null);

  const { isLoaded } = useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey: 'AIzaSyDZKKHPfUl62NLPtJzHhuTrAvUyVGmfZ20'
  });

  const onLoad = useCallback(function callback(map) { mapRef.current = map; }, []);
  const onUnmount = useCallback(function callback(map) { mapRef.current = null; }, []);

  const fetchDatabaseState = useCallback(async () => {
    setIsSyncing(true);
    setErrorMsg(null);

    try {
      let rawPoints = [];
      try {
        const gridRes = await axios.get(`${API_BASE}/risk/turkey-grid`, { params: { hours_ago: 0 } });
        rawPoints = Array.isArray(gridRes.data) ? gridRes.data : (gridRes.data?.data || gridRes.data?.grid || gridRes.data?.sectors || gridRes.data?.points || []);
      } catch (gridErr) {
        try {
          const fallbackRes = await axios.get(`${API_BASE}/risk/grid?hours_ago=0`);
          rawPoints = Array.isArray(fallbackRes.data) ? fallbackRes.data : (fallbackRes.data?.data || []);
        } catch (fbErr) {
          console.error('All risk grid endpoints failed:', fbErr);
        }
      }
      
      let basePoints = rawPoints
        .map((p, idx) => {
          const rawScore = Number(p.risk_score ?? p.score ?? p.risk ?? p.fire_risk ?? 0);
          const normalizedScore = (rawScore > 0 && rawScore <= 1.0) ? Math.round(rawScore * 100) : Math.round(rawScore);

          return {
            ...p,
            latitude: Number(p.latitude ?? p.lat ?? p.koordinat_enlem ?? 0),
            longitude: Number(p.longitude ?? p.lon ?? p.lng ?? p.koordinat_boylam ?? 0),
            risk_score: normalizedScore,
            location: p.location_name || p.name || p.location || p.istasyon_adi || (p.is_fixed ? `Tower #${idx + 1}` : `Grid P-${idx}`),
            is_fixed: Boolean(p.is_fixed ?? p.fixed ?? p.is_station),
            is_wildfire: Boolean(p.is_wildfire || p.wildfire || normalizedScore >= 95),
            slope: Number(p.slope ?? 5.0),
            vegetation_density: Number(p.vegetation_density ?? 0.7)
          };
        })
        .filter(pt => pt.is_fixed === true || pt.is_wildfire === true || pt.risk_score > 60);

      let droneDetections = [];
      try {
        const detRes = await axios.get(`${API_BASE}/detection/history?limit=50`);
        droneDetections = Array.isArray(detRes.data) ? detRes.data : (detRes.data?.data || []);
      } catch (detErr) {
        console.warn('Detection history fetch failed:', detErr);
      }

      let activeSpreads = [];
      try {
        const spreadHistoryRes = await axios.get(`${API_BASE}/spread/history?limit=50`);
        activeSpreads = Array.isArray(spreadHistoryRes.data) ? spreadHistoryRes.data : (spreadHistoryRes.data?.data || []);
      } catch (spreadErr) {
        console.warn('Spread history fetch failed:', spreadErr);
      }

      let dispatchPlans = [];
      try {
        const dispatchRes = await axios.get(`${API_BASE}/dispatch/history?limit=20`);
        dispatchPlans = Array.isArray(dispatchRes.data) ? dispatchRes.data : (dispatchRes.data?.data || []);
      } catch (dispErr) {
        console.warn('Dispatch history fetch failed:', dispErr);
      }

      const confirmedFires = [];

      for (const det of droneDetections) {
        const detId = det.id ?? det.detection_id ?? det.fire_detection_id;
        const detLat = Number(det.latitude ?? det.parsed_latitude ?? det.lat ?? 0);
        const detLng = Number(det.longitude ?? det.parsed_longitude ?? det.lon ?? det.lng ?? 0);
        
        const matchingSpread = activeSpreads.find(s => s.fire_detection_id === detId);
        const matchingDispatch = dispatchPlans.find(p => p.fire_detection_id === detId);

        const liveWeather = await fetchLiveWeather(detLat, detLng);

        let spreadObj = null;
        if (matchingSpread) {
          spreadObj = {
            detection_id: detId,
            prediction_hours: matchingSpread.prediction_hours || 6,
            spread_probability: matchingSpread.spread_probability ?? 0.88,
            affected_area_hectares: matchingSpread.affected_area_hectares ?? 10.0,
            wind_speed: matchingSpread.wind_speed ?? liveWeather.wind_speed,
            wind_direction: matchingSpread.wind_direction ?? liveWeather.wind_direction,
            temperature: liveWeather.temperature,
            humidity: liveWeather.humidity,
            raw_wkt: matchingSpread.spread_area,
            spread_area_geojson: matchingSpread.spread_area_geojson
          };
        } else {
          spreadObj = {
            detection_id: detId,
            prediction_hours: 6,
            spread_probability: 0.88,
            affected_area_hectares: 12.5,
            ...liveWeather
          };
        }

        confirmedFires.push({
          detection_id: detId,
          latitude: detLat,
          longitude: detLng,
          class_name: det.class_name || det.label || 'WILDFIRE & SMOKE',
          confidence: det.confidence || det.peak_confidence || 0.88,
          total_frames: det.total_frames || det.total_frames_processed || 0,
          detected_at: det.created_at || det.detected_at || new Date().toISOString(),
          spreadPrediction: spreadObj,
          dispatchPlan: matchingDispatch || null
        });
      }

      for (const spread of activeSpreads) {
        const detId = spread.fire_detection_id;
        if (!confirmedFires.some(f => f.detection_id === detId)) {
          const parsedCoords = parseWktPolygon(spread.spread_area);
          const originLat = parsedCoords?.[0]?.lat || 36.8550;
          const originLng = parsedCoords?.[0]?.lng || 28.2742;
          const matchingDispatch = dispatchPlans.find(p => p.fire_detection_id === detId);
          const liveWeather = await fetchLiveWeather(originLat, originLng);

          confirmedFires.push({
            detection_id: detId,
            latitude: originLat,
            longitude: originLng,
            class_name: 'WILDFIRE & SMOKE',
            confidence: spread.spread_probability ?? 0.88,
            detected_at: spread.created_at || new Date().toISOString(),
            spreadPrediction: {
              detection_id: detId,
              prediction_hours: spread.prediction_hours || 6,
              spread_probability: spread.spread_probability ?? 0.88,
              affected_area_hectares: spread.affected_area_hectares ?? 10.0,
              wind_speed: spread.wind_speed ?? liveWeather.wind_speed,
              wind_direction: spread.wind_direction ?? liveWeather.wind_direction,
              temperature: liveWeather.temperature,
              humidity: liveWeather.humidity,
              raw_wkt: spread.spread_area,
              spread_area_geojson: spread.spread_area_geojson
            },
            dispatchPlan: matchingDispatch || null
          });
        }
      }

      confirmedFires.forEach(fire => {
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
            location: `Wildfire Sector #${fire.detection_id}`,
            threat_name: 'CONFIRMED WILDFIRE',
            detection: fire,
            spreadPrediction: fire.spreadPrediction,
            dispatchPlan: fire.dispatchPlan
          });
        }
      });

      const firstActiveFire = basePoints.find(p => p.is_wildfire);
      if (firstActiveFire) {
        setFireWarning(true);
        setSelectedPoint(firstActiveFire);
        setActiveDetection(firstActiveFire.detection);
        setSpreadPrediction(firstActiveFire.spreadPrediction || null);
        setDispatchPlan(firstActiveFire.dispatchPlan || null);
        setDroneStatus('DISPATCHED');
      }

      setRiskPoints(basePoints);
    } catch (err) {
      console.error('Database Sync Error:', err);
      setErrorMsg('Failed to sync risk grid & active fires from database.');
    } finally {
      setIsSyncing(false);
    }
  }, []);

  useEffect(() => { fetchDatabaseState(); }, [fetchDatabaseState]);

  const handleSelectPoint = (point) => {
    setSelectedPoint(point);
    setErrorMsg(null);
    setDispatchExecuted(false);

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
    return new Blob(["mock-video-binary-stream"], { type: 'video/mp4' });
  };

  const handleGenerateDispatch = async (targetPoint, detectionData, windData) => {
    if (!targetPoint && !detectionData) return;
    const targetLat = targetPoint?.latitude ?? detectionData?.latitude ?? selectedPoint?.latitude;
    const targetLng = targetPoint?.longitude ?? detectionData?.longitude ?? selectedPoint?.longitude;
    
    const rawDetId = detectionData?.detection_id ?? 
                    targetPoint?.detection?.detection_id ?? 
                    targetPoint?.detection_id ?? 
                    null;

    const parsedDetId = rawDetId ? parseInt(rawDetId, 10) : null;
    const validDetId = (parsedDetId && !isNaN(parsedDetId)) ? parsedDetId : null;
    const className = detectionData?.class_name || targetPoint?.detection?.class_name || selectedPoint?.detection?.class_name || 'WILDFIRE';

    setDispatchLoading(true);
    setErrorMsg(null);
    setDispatchExecuted(false);

    let weather = windData;
    if (!weather || !weather.wind_speed) {
      weather = await fetchLiveWeather(targetLat, targetLng);
    }

    const windSpeed = parseFloat(Number(weather.wind_speed).toFixed(1));
    const windDir = parseFloat(Number(weather.wind_direction).toFixed(1));
    const predHours = spreadPrediction?.prediction_hours ?? 6;

    try {
      const res = await axios.post(`${API_BASE}/dispatch/generate-plan`, {
        detection_id: validDetId,
        latitude: parseFloat(Number(targetLat).toFixed(6)),
        longitude: parseFloat(Number(targetLng).toFixed(6)),
        prediction_hours: predHours,
        wind_speed: windSpeed,
        wind_direction: windDir,
        incident_caption: `Aktif ${className} yangını tespit edildi. Koordinat: [${Number(targetLat).toFixed(4)}°N, ${Number(targetLng).toFixed(4)}°E]`,
        available_forces: "2 Amfibik Uçak, 4 Helikopter, 12 Arazöz, 2 Dozer, 50 Personel"
      });

      setDispatchPlan(res.data);

      setRiskPoints(prev => prev.map(p => {
        if (p.latitude === targetLat && p.longitude === targetLng) {
          return { ...p, dispatchPlan: res.data };
        }
        return p;
      }));

      setSelectedPoint(prev => ({ ...prev, dispatchPlan: res.data }));
    } catch (err) {
      console.error('Dispatch model generation failed:', err);
      setErrorMsg('Failed to run AI dispatch model for these coordinates.');
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

      const detectionRes = await axios.post(`${API_BASE}/detection/detect-frame`, fd, { headers: { 'Content-Type': 'multipart/form-data' } });
      const data = detectionRes.data || {};
      
      const rawDetId = data.detection_id ?? data.id ?? data.fire_detection_id ?? data.data?.detection_id ?? data.data?.id ?? null;
      const parsedDetId = rawDetId ? parseInt(rawDetId, 10) : null;
      const detId = (parsedDetId && !isNaN(parsedDetId)) ? parsedDetId : null;
      
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

        const weatherPayload = await fetchLiveWeather(point.latitude, point.longitude);
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
        } catch (spreadErr) { console.warn('Spread ML model failed:', spreadErr); }

        setRiskPoints(prev => prev.map(p => {
          if (p.latitude === point.latitude && p.longitude === point.longitude) {
            return { ...p, risk_score: 99, is_wildfire: true, threat_name: 'CONFIRMED WILDFIRE', detection: detectionData, spreadPrediction: spreadData, detected_at: new Date().toLocaleTimeString() };
          }
          return p;
        }));

        setSelectedPoint(prev => ({ ...prev, risk_score: 99, is_wildfire: true, threat_name: 'CONFIRMED WILDFIRE', detection: detectionData, spreadPrediction: spreadData }));
        handleGenerateDispatch(point, detectionData, weatherPayload);
      } else {
        const clearData = { latitude: point.latitude, longitude: point.longitude, class_name: 'CLEAR', confidence: 0.99 };
        setActiveDetection(clearData);
        setFireWarning(false);
        setRiskPoints(prev => prev.map(p => {
          if (p.latitude === point.latitude && p.longitude === point.longitude) return { ...p, detection: clearData, is_wildfire: false };
          return p;
        }));
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
    if (spreadPrediction?.spread_area_geojson?.coordinates?.[0]) return spreadPrediction.spread_area_geojson.coordinates[0].map(c => ({ lat: Number(c), lng: Number(c[0]) }));
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
      
      <TopNav fetchDatabaseState={fetchDatabaseState} isSyncing={isSyncing} />

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
          {isLoaded ? (
            <GoogleMap
              mapContainerStyle={{ width: '100%', height: '100%' }}
              center={{ lat: 39.0, lng: 35.0 }}
              zoom={6}
              options={{ mapTypeId: 'hybrid', disableDefaultUI: true }}
              onLoad={onLoad}
              onUnmount={onUnmount}
            >
              {filteredPoints.map((pt, i) => (
                <Marker 
                  key={`point-${i}`}
                  position={{ lat: pt.latitude, lng: pt.longitude }}
                  title={pt.is_wildfire ? 'ACTIVE WILDFIRE DETECTED' : pt.location || (pt.is_fixed ? 'Fixed Station' : `Risk Sector (${pt.risk_score})`)}
                  icon={createMarkerIcon(pt)}
                  onClick={() => handleSelectPoint(pt)}
                />
              ))}

              {polyCoords && (
                <Polygon
                  paths={polyCoords}
                  options={{ fillColor: '#ef4444', fillOpacity: 0.45, strokeColor: '#dc2626', strokeOpacity: 0.95, strokeWeight: 2.5, zIndex: 10 }}
                />
              )}
            </GoogleMap>
          ) : (
            <div className="w-full h-full flex items-center justify-center text-text-muted font-mono">Loading Satellite Map...</div>
          )}

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