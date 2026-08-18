import { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import { GoogleMap, useJsApiLoader, Marker, Polygon } from '@react-google-maps/api';
import { Target, Activity, ShieldAlert, Truck, Wind, Flame, Crosshair } from 'lucide-react';

const API_BASE = 'http://localhost:5000/api/v1'; // Adjusted to a typical backend URL if needed, but relative works if proxy is set.

export default function App() {
  const [riskPoints, setRiskPoints] = useState([]);
  const [activeDetection, setActiveDetection] = useState(null);
  const [spreadPrediction, setSpreadPrediction] = useState(null);
  const [dispatchPlan, setDispatchPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  
  const mapRef = useRef(null);

  const { isLoaded } = useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey: 'AIzaSyDZKKHPfUl62NLPtJzHhuTrAvUyVGmfZ20'
  });

  const onLoad = useCallback(function callback(map) {
    mapRef.current = map;
  }, []);

  const onUnmount = useCallback(function callback(map) {
    mapRef.current = null;
  }, []);

  useEffect(() => {
    const fetchRiskPoints = async () => {
      try {
        setErrorMsg(null);
        const res = await axios.get(`${API_BASE}/risk/turkey-grid?hours_ago=0`);
        const highRisk = res.data.filter(pt => pt.risk_score >= 0.60);
        setRiskPoints(highRisk);
      } catch (err) {
        console.error('API /risk/turkey-grid failed', err);
        setErrorMsg('Failed to load risk grid from API.');
      }
    };
    fetchRiskPoints();
  }, []);

  const handleScanLocation = async (point) => {
    if (mapRef.current) {
      mapRef.current.panTo({ lat: point.latitude, lng: point.longitude });
      mapRef.current.setZoom(15);
    }
    
    setLoading(true);
    setSpreadPrediction(null);
    setDispatchPlan(null);
    setActiveDetection(null);
    setErrorMsg(null);

    try {
       const fd = new FormData();
       // Note: In production, 'file' should be the actual image blob.
       fd.append('file', new Blob(["mock"], { type: 'image/jpeg' }));
       fd.append('latitude', point.latitude);
       fd.append('longitude', point.longitude);
       
       const detectionRes = await axios.post(`${API_BASE}/detection/detect-frame`, fd);
      
      const detId = detectionRes.data.detection_id;
      const detectedFire = detectionRes.data.detections[0];
      
      if (!detectedFire) {
         setLoading(false);
         return;
      }

      setActiveDetection({ ...point, detection_id: detId, ...detectedFire });

      if (detectedFire.class_name === 'fire') {
          const spreadRes = await axios.post(`${API_BASE}/spread/predict-spread`, {
            detection_id: detId, prediction_hours: 24, wind_speed: 25.0, wind_direction: 180.0, slope: 5.0, vegetation_density: 0.7
          });
          setSpreadPrediction(spreadRes.data);

          const dispatchRes = await axios.post(`${API_BASE}/dispatch/generate-plan`, { detection_id: detId });
          setDispatchPlan(dispatchRes.data);
      }
    } catch (err) {
      console.error(err);
      setErrorMsg('Failed to execute AI models. Ensure API backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const polyCoords = spreadPrediction?.spread_area_geojson?.coordinates[0]?.map(c => ({ lat: c[1], lng: c[0] }));

  return (
    <div className="h-screen w-full flex flex-col bg-bg-app">
      
      {/* TOP NAVIGATION BAR */}
      <header className="h-14 bg-bg-panel border-b border-border flex items-center justify-between px-4 shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-primary text-white flex items-center justify-center font-bold">FF</div>
          <h1 className="text-lg font-bold tracking-wide text-text-main">FIREFLAI <span className="text-text-muted font-normal text-sm ml-2">v1.0.0</span></h1>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-sm font-mono text-text-muted bg-bg-app px-3 py-1 border border-border">
            <Activity size={16} className="text-secondary" />
            <span>SYS: ONLINE</span>
          </div>
          <button className="btn-outline text-sm">Operator Login</button>
        </div>
      </header>

      {/* MAIN WORKSPACE */}
      <div className="flex flex-1 overflow-hidden">
        
        {/* LEFT SIDEBAR - RISK GRID */}
        <aside className="w-80 bg-bg-panel border-r border-border flex flex-col shrink-0">
          <div className="p-4 border-b border-border">
            <h2 className="text-xs font-bold text-text-muted uppercase tracking-wider mb-2">High Risk Zones (Score &gt; 60)</h2>
            <p className="text-sm text-text-muted">Select a sector to run YOLO detection & spread analysis.</p>
          </div>
          
          {errorMsg && (
             <div className="m-4 p-3 bg-danger/20 text-danger border border-danger text-sm font-mono">
               {errorMsg}
             </div>
          )}

          <div className="flex-1 overflow-y-auto p-2 space-y-2">
            {riskPoints.map((pt, i) => (
              <div 
                key={i} 
                className="p-3 border border-border bg-bg-app hover:border-primary cursor-pointer flex flex-col gap-2"
                onClick={() => handleScanLocation(pt)}
              >
                <div className="flex justify-between items-center">
                  <span className="font-bold text-sm">{pt.location || `Grid P-${i}`}</span>
                  <span className="bg-danger/20 text-danger text-xs font-mono px-2 py-0.5 font-bold">RISK: {pt.risk_score}</span>
                </div>
                <div className="text-xs font-mono text-text-muted">
                  {pt.latitude.toFixed(4)}, {pt.longitude.toFixed(4)}
                </div>
              </div>
            ))}
          </div>
        </aside>

        {/* CENTER - MAP VIEW */}
        <main className="flex-1 relative bg-[#020617]">
          {isLoaded ? (
            <GoogleMap
              mapContainerStyle={{ width: '100%', height: '100%' }}
              center={{ lat: 39.0, lng: 35.0 }}
              zoom={6}
              options={{
                mapTypeId: 'terrain',
                disableDefaultUI: true,
                backgroundColor: '#020617',
                styles: [
                  { elementType: "geometry", stylers: [{ color: "#0f172a" }] },
                  { elementType: "labels.text.fill", stylers: [{ color: "#94a3b8" }] },
                  { featureType: "water", elementType: "geometry", stylers: [{ color: "#020617" }] }
                ]
              }}
              onLoad={onLoad}
              onUnmount={onUnmount}
            >
              {/* Highlight Risk Zones */}
              {riskPoints.map((pt, i) => (
                <Marker 
                  key={`risk-${i}`}
                  position={{ lat: pt.latitude, lng: pt.longitude }}
                  icon={{
                    path: window.google.maps.SymbolPath.CIRCLE,
                    fillColor: '#f97316',
                    fillOpacity: 0.5,
                    strokeWeight: 1,
                    strokeColor: '#f97316',
                    scale: 6
                  }}
                  onClick={() => handleScanLocation(pt)}
                />
              ))}

              {/* Active Fire Detection */}
              {activeDetection && (
                <Marker
                  position={{ lat: activeDetection.latitude, lng: activeDetection.longitude }}
                  icon={{
                    path: window.google.maps.SymbolPath.CIRCLE,
                    fillColor: '#ef4444',
                    fillOpacity: 1,
                    strokeWeight: 2,
                    strokeColor: '#ffffff',
                    scale: 10
                  }}
                />
              )}

              {/* Fire Spread Polygon */}
              {spreadPrediction && polyCoords && (
                <Polygon
                  paths={polyCoords}
                  options={{
                    fillColor: '#ef4444',
                    fillOpacity: 0.3,
                    strokeColor: '#ef4444',
                    strokeOpacity: 0.8,
                    strokeWeight: 2,
                  }}
                />
              )}
            </GoogleMap>
          ) : (
            <div className="w-full h-full flex items-center justify-center text-text-muted font-mono">
              Loading Tactical Map...
            </div>
          )}

          {/* LOADING OVERLAY */}
          {loading && (
            <div className="absolute top-4 left-4 bg-bg-panel border border-primary px-4 py-3 flex items-center gap-3 text-sm font-mono shadow-lg">
              <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
              <span>EXECUTING MODELS...</span>
            </div>
          )}
        </main>

        {/* RIGHT SIDEBAR - ANALYSIS & DISPATCH */}
        {activeDetection && (
          <aside className="w-[400px] bg-bg-panel border-l border-border flex flex-col shrink-0 overflow-y-auto">
            <div className="p-4 bg-primary text-white font-bold flex items-center gap-2">
              <ShieldAlert size={20} />
              TACTICAL INCIDENT REPORT
            </div>
            
            <div className="p-4 space-y-6">
              
              {/* DETECTION BLOCK */}
              <div className="space-y-2">
                <h3 className="text-xs font-bold text-text-muted uppercase tracking-wider flex items-center gap-2">
                  <Target size={14} /> 1. YOLO Detection
                </h3>
                <div className="border border-border bg-bg-app p-3 font-mono text-sm space-y-1">
                  <div className="flex justify-between">
                    <span className="text-text-muted">Class:</span>
                    <span className="text-danger font-bold uppercase">{activeDetection.class_name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-text-muted">Confidence:</span>
                    <span>{(activeDetection.confidence * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-text-muted">Coords:</span>
                    <span>{activeDetection.latitude.toFixed(4)}, {activeDetection.longitude.toFixed(4)}</span>
                  </div>
                </div>
              </div>

              {/* SPREAD BLOCK */}
              {spreadPrediction && (
                <div className="space-y-2">
                  <h3 className="text-xs font-bold text-text-muted uppercase tracking-wider flex items-center gap-2">
                    <Wind size={14} /> 2. Spread Projection ({spreadPrediction.prediction_hours}H)
                  </h3>
                  <div className="border border-border bg-bg-app p-3 font-mono text-sm space-y-1">
                    <div className="flex justify-between">
                      <span className="text-text-muted">Area Hectares:</span>
                      <span className="text-warning font-bold">{spreadPrediction.affected_area_hectares} HA</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-text-muted">Spread Prob:</span>
                      <span>{(spreadPrediction.spread_probability * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                </div>
              )}

              {/* DISPATCH BLOCK */}
              {dispatchPlan && (
                <div className="space-y-2">
                  <h3 className="text-xs font-bold text-text-muted uppercase tracking-wider flex items-center gap-2">
                    <Truck size={14} /> 3. Automated Dispatch
                  </h3>
                  <div className="border border-secondary bg-bg-app p-4 space-y-4">
                    <p className="text-sm text-text-main leading-relaxed">
                      {dispatchPlan.action_summary}
                    </p>
                    
                    <div className="grid grid-cols-2 gap-2 font-mono text-xs">
                      <div className="bg-bg-panel border border-border p-2">
                        <div className="text-text-muted mb-1">AERIAL</div>
                        <div className="font-bold text-secondary">
                          {dispatchPlan.assigned_resources.helicopters} Heli <br/>
                          {dispatchPlan.assigned_resources.water_bombers} Bomber
                        </div>
                      </div>
                      <div className="bg-bg-panel border border-border p-2">
                        <div className="text-text-muted mb-1">GROUND</div>
                        <div className="font-bold text-secondary">
                          {dispatchPlan.assigned_resources.fire_trucks} Trucks <br/>
                          {dispatchPlan.assigned_resources.ground_personnel} Pers
                        </div>
                      </div>
                    </div>
                    
                    <button className="btn-primary w-full flex items-center justify-center gap-2 mt-2">
                      <Crosshair size={16} /> EXECUTE TACTICAL ORDER
                    </button>
                  </div>
                </div>
              )}

            </div>
          </aside>
        )}
      </div>
    </div>
  );
}
