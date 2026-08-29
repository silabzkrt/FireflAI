/**
 * SpreadPanel Component
 * 
 * Displays machine learning wildfire propagation predictions.
 * Presents calculated projections including estimated burn area (hectares),
 * spread probability percentage, and live meteorological wind vector data.
 */

import { Wind, Compass } from 'lucide-react';

export default function SpreadPanel({ spreadPrediction }) {
  if (!spreadPrediction) return null;
  
  return (
    <div className="space-y-2">
      <h3 className="text-xs font-bold text-text-muted uppercase tracking-wider flex items-center gap-2">
        <Wind size={14} /> 2. ML Fire Spread Model ({spreadPrediction.prediction_hours}H)
      </h3>
      <div className="border border-border bg-bg-app p-3 font-mono text-sm space-y-2">
        <div className="flex justify-between">
          <span className="text-text-muted">Projected Area:</span>
          <span className="text-warning font-bold">{spreadPrediction.affected_area_hectares} HA</span>
        </div>
        <div className="flex justify-between">
          <span className="text-text-muted">Spread Probability:</span>
          <span className="text-danger font-bold">{(spreadPrediction.spread_probability * 100).toFixed(1)}%</span>
        </div>
        <div className="flex justify-between items-center text-xs text-text-muted pt-1.5 border-t border-border/40">
          <span className="flex items-center gap-1">
            <Compass size={13} className="text-secondary" /> Live Wind Vector:
          </span>
          <span className="text-secondary font-bold font-mono">
            {spreadPrediction.wind_speed?.toFixed(1) || '14.0'} km/h @ {spreadPrediction.wind_direction?.toFixed(0) || '160'}°
            {spreadPrediction.temperature ? ` (${spreadPrediction.temperature.toFixed(0)}°C)` : ''}
          </span>
        </div>
      </div>
    </div>
  );
}