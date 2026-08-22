import { Flame, Crosshair, X, Loader2, CheckCircle2, Send, ShieldAlert } from 'lucide-react';
import { getRiskColor } from '../utils/helpers';

export default function TargetDetailsCard({
  selectedPoint,
  currentPointDetection,
  setSelectedPoint,
  handleSendDrone,
  loading,
  droneStatus,
  handleGenerateDispatch,
  dispatchLoading
}) {
  if (!selectedPoint) return null;

  return (
    <div className="absolute top-4 left-4 z-20 w-88 bg-bg-panel/95 backdrop-blur-md border border-primary shadow-2xl p-4 space-y-3 font-mono animate-in fade-in slide-in-from-top-2 duration-200">
      <div className="flex items-center justify-between border-b border-border pb-2">
        <div className="flex items-center gap-2">
          <Crosshair size={16} className="text-primary animate-pulse" />
          <span className="font-bold text-xs text-text-main tracking-wider uppercase">
            {selectedPoint.is_wildfire && currentPointDetection?.class_name !== 'CLEAR'
              ? 'ACTIVE WILDFIRE SECTOR' 
              : selectedPoint.location || (selectedPoint.is_fixed ? 'Observation Station' : 'Target Point')}
          </span>
        </div>
        <button 
          onClick={() => setSelectedPoint(null)}
          className="text-text-muted hover:text-text-main transition-colors cursor-pointer"
        >
          <X size={16} />
        </button>
      </div>

      {selectedPoint.is_wildfire && currentPointDetection && currentPointDetection.class_name !== 'CLEAR' && (
        <div className="bg-red-600/25 border-2 border-red-500 text-red-300 p-2.5 flex items-center gap-2.5 font-bold text-xs animate-pulse">
          <Flame size={22} className="text-red-500 shrink-0" />
          <div className="flex flex-col">
            <span className="font-black text-red-400 tracking-wide">LEVEL 1 WILDFIRE INCIDENT</span>
            <span className="text-[10px] text-red-300 font-mono">
              Database Logged • Active ML Spread Tracking
            </span>
          </div>
        </div>
      )}

      <div className="bg-bg-app border border-border p-2.5 space-y-1.5 text-xs">
        <div className="flex justify-between">
          <span className="text-text-muted">Latitude:</span>
          <span className="text-text-main font-bold">{selectedPoint.latitude.toFixed(5)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-text-muted">Longitude:</span>
          <span className="text-text-main font-bold">{selectedPoint.longitude.toFixed(5)}</span>
        </div>
        {!selectedPoint.is_wildfire && (
          <div className="flex justify-between">
            <span className="text-text-muted">Risk Score:</span>
            <span 
              className="font-bold px-1.5 py-0.2 rounded"
              style={{ color: getRiskColor(selectedPoint.risk_score) }}
            >
              {selectedPoint.risk_score} / 100
            </span>
          </div>
        )}
        {currentPointDetection && (
          <div className="flex justify-between border-t border-border/50 pt-1.5 font-bold">
            <span className="text-text-muted">Detection:</span>
            <span className={currentPointDetection.class_name !== 'CLEAR' ? "text-danger uppercase" : "text-emerald-400 uppercase"}>
              {currentPointDetection.class_name} ({((currentPointDetection.confidence || 0) * 100).toFixed(1)}%)
            </span>
          </div>
        )}
      </div>

      <div className="space-y-2">
        <button
          onClick={() => handleSendDrone(selectedPoint)}
          disabled={loading || droneStatus === 'DEPLOYING'}
          className={`w-full py-2.5 px-4 font-bold text-xs tracking-wider flex items-center justify-center gap-2 transition-all shadow-md ${
            droneStatus === 'DISPATCHED'
              ? 'bg-emerald-600 hover:bg-emerald-500 text-white'
              : 'bg-primary hover:bg-primary/90 text-white active:scale-98'
          } ${loading ? 'opacity-80 cursor-wait' : 'cursor-pointer'}`}
        >
          {droneStatus === 'DEPLOYING' ? (
            <>
              <Loader2 size={15} className="animate-spin" />
              <span>FETCHING WIND & RUNNING MODELS...</span>
            </>
          ) : droneStatus === 'DISPATCHED' ? (
            <>
              <CheckCircle2 size={15} />
              <span>DRONE DEPLOYED (RE-EVALUATE)</span>
            </>
          ) : (
            <>
              <Send size={15} />
              <span>SEND DRONE</span>
            </>
          )}
        </button>

        {selectedPoint.is_wildfire && currentPointDetection?.class_name !== 'CLEAR' && (
          <button
            onClick={() => handleGenerateDispatch(selectedPoint, currentPointDetection)}
            disabled={dispatchLoading}
            className="w-full py-2 px-3 bg-red-600 hover:bg-red-700 text-white font-bold text-xs tracking-wider flex items-center justify-center gap-1.5 transition-all shadow-md border border-red-400 cursor-pointer"
          >
            {dispatchLoading ? (
              <>
                <Loader2 size={14} className="animate-spin" />
                <span>FETCHING LIVE WIND & RUNNING QWEN-3B...</span>
              </>
            ) : (
              <>
                <ShieldAlert size={14} />
                <span>DISPATCH EMERGENCY FORCES</span>
              </>
            )}
          </button>
        )}
      </div>
    </div>
  );
}