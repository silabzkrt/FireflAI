/**
 * RiskPanel Component
 * 
 * Left-hand sidebar panel for sector surveillance and risk assessment.
 * Filters and lists monitored sectors across Turkey by risk level (Critical, High, Fixed Stations),
 * allowing operators to inspect individual sector coordinates, risk score bars, and active fire alerts.
 */

import { Radio, ChevronRight, Flame } from 'lucide-react';
import { getRiskColor, getRiskTier } from '../utils/helpers';

export default function RiskPanel({
  counts,
  filterType,
  setFilterType,
  errorMsg,
  filteredPoints,
  selectedPoint,
  handleSelectPoint
}) {
  return (
    <aside className="w-84 bg-bg-panel border-r border-border flex flex-col shrink-0">
      <div className="p-4 border-b border-border space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-bold text-text-muted uppercase tracking-wider flex items-center gap-1.5">
            <Radio size={14} className="text-primary" /> Monitored Sectors
          </h2>
          <span className="text-[11px] font-mono text-text-muted">
            {counts.all} Total
          </span>
        </div>

        <div className="flex gap-1">
          {[
            { id: 'ALL', label: `All (${counts.all})` },
            { id: 'CRITICAL', label: `Crit (${counts.critical})` },
            { id: 'HIGH', label: `High (${counts.high})` },
            { id: 'FIXED', label: `Fixed (${counts.fixed})` },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setFilterType(tab.id)}
              className={`text-[10px] font-mono px-2 py-1 border transition-all cursor-pointer ${
                filterType === tab.id
                  ? 'bg-primary text-white border-primary font-bold shadow-sm'
                  : 'bg-bg-app text-text-muted border-border hover:border-text-muted'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>
      
      {errorMsg && (
        <div className="m-3 p-3 bg-danger/20 text-danger border border-danger text-xs font-mono">
          {errorMsg}
        </div>
      )}

      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {filteredPoints.map((pt, i) => {
          const isFixed = Boolean(pt.is_fixed);
          const isWildfire = Boolean(pt.is_wildfire);
          const tier = getRiskTier(pt.risk_score, isWildfire);
          const riskColor = getRiskColor(pt.risk_score, isWildfire);
          const isSelected = selectedPoint && selectedPoint.latitude === pt.latitude && selectedPoint.longitude === pt.longitude;
          
          return (
            <div 
              key={i} 
              className={`p-3 border cursor-pointer flex flex-col gap-2 transition-all group ${
                isSelected ? 'ring-2 ring-primary bg-bg-panel' : 'bg-bg-app hover:border-primary'
              } ${
                isWildfire
                  ? 'border-red-600 border-l-4 bg-red-950/20 shadow-[inset_0_0_8px_rgba(239,68,68,0.2)]'
                  : isFixed 
                    ? 'border-secondary/40 border-l-4 border-l-secondary' 
                    : pt.risk_score >= 85 
                      ? 'border-red-500/40 border-l-4 border-l-red-500' 
                      : 'border-border border-l-4 border-l-orange-500/50'
              }`}
              onClick={() => handleSelectPoint(pt)}
            >
              <div className="flex justify-between items-start gap-2">
                <div className="flex items-center gap-1.5 flex-wrap">
                  <span
                    className={`text-[10px] font-mono px-1.5 py-0.5 font-bold uppercase tracking-wider ${
                      isFixed 
                        ? 'bg-secondary/20 text-secondary border border-secondary/40' 
                        : `${tier.bg} ${tier.text} border ${tier.border}`
                    }`}
                  >
                    {isFixed ? 'FIXED' : tier.label}
                  </span>
                  <span className="font-bold text-sm text-text-main group-hover:text-primary transition-colors flex items-center gap-1">
                    {isWildfire && <Flame size={14} className="text-red-500 animate-bounce" />}
                    {pt.location || (isFixed ? `Tower #${i + 1}` : `Grid P-${i}`)}
                  </span>
                </div>

                <div 
                  className="text-xs font-mono px-2 py-0.5 font-bold shrink-0 border"
                  style={{ 
                    backgroundColor: `${isFixed ? '#0284c7' : riskColor}20`, 
                    color: isFixed ? '#38bdf8' : riskColor,
                    borderColor: `${isFixed ? '#0284c7' : riskColor}40`
                  }}
                >
                  {isWildfire ? 'ACTIVE FIRE' : isFixed ? 'STATION' : `RISK: ${pt.risk_score}`}
                </div>
              </div>

              {!isFixed && (
                <div className="w-full bg-bg-panel h-1.5 border border-border/50 overflow-hidden">
                  <div 
                    className="h-full transition-all"
                    style={{ 
                      width: `${Math.min(pt.risk_score, 100)}%`, 
                      backgroundColor: riskColor 
                    }}
                  />
                </div>
              )}

              <div className="flex items-center justify-between text-xs font-mono text-text-muted">
                <span>{pt.latitude.toFixed(4)}, {pt.longitude.toFixed(4)}</span>
                <span className="text-[11px] text-primary flex items-center gap-0.5 group-hover:translate-x-0.5 transition-transform font-bold">
                  SELECT <ChevronRight size={12} />
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </aside>
  );
}