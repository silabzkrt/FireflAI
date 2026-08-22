import { Truck, Loader2, RefreshCw, FileText, Droplets, Home, CheckCircle2, Crosshair, ShieldAlert } from 'lucide-react';

export default function DispatchPanel({
  dispatchPlan,
  dispatchLoading,
  dispatchExecuted,
  selectedPoint,
  currentPointDetection,
  handleGenerateDispatch,
  setDispatchExecuted
}) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-bold text-text-muted uppercase tracking-wider flex items-center gap-2">
          <Truck size={14} /> 3. AI Tactical Dispatch
        </h3>
        {!dispatchPlan && (
          <button
            onClick={() => handleGenerateDispatch(selectedPoint, currentPointDetection)}
            disabled={dispatchLoading}
            className="text-[11px] font-mono text-primary hover:underline flex items-center gap-1 cursor-pointer"
          >
            {dispatchLoading ? <Loader2 size={12} className="animate-spin" /> : <RefreshCw size={12} />}
            <span>Generate Order</span>
          </button>
        )}
      </div>

      {dispatchLoading ? (
        <div className="border border-border bg-bg-app p-4 flex flex-col items-center justify-center gap-2 text-xs font-mono text-text-muted">
          <Loader2 size={20} className="animate-spin text-primary" />
          <span>Fetching live weather & generating Qwen-3B TAMP Directive...</span>
        </div>
      ) : dispatchPlan ? (
        <div className="space-y-3">
          {dispatchPlan.tactical_order && (
            <div className="bg-bg-app border border-border p-3 space-y-2 font-mono text-xs">
              <div className="text-secondary font-bold flex items-center gap-1.5 text-[11px]">
                <FileText size={14} /> TAMP COMMAND DIRECTIVE (AI GENERATED)
              </div>
              <div className="whitespace-pre-line text-text-main leading-relaxed bg-bg-panel/75 p-2.5 border border-border/60 rounded text-[11px] max-h-52 overflow-y-auto select-text font-mono">
                {dispatchPlan.tactical_order}
              </div>
            </div>
          )}

          {dispatchPlan.nearest_water_sources && dispatchPlan.nearest_water_sources.length > 0 && (
            <div className="space-y-1 text-xs font-mono">
              <div className="text-text-muted font-bold flex items-center gap-1 text-[11px]">
                <Droplets size={12} className="text-cyan-400" /> Nearest Water Sources:
              </div>
              <div className="space-y-1">
                {dispatchPlan.nearest_water_sources.slice(0, 3).map((w, idx) => (
                  <div key={idx} className="bg-bg-app p-2 border border-border flex justify-between items-center text-[11px]">
                    <span className="text-cyan-400 font-bold">{w.isim}</span>
                    <span className="text-text-muted text-[10px]">{w.gps_format || `${w.koordinat_enlem}, ${w.koordinat_boylam}`}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {dispatchPlan.threatened_facilities && dispatchPlan.threatened_facilities.length > 0 && (
            <div className="space-y-1 text-xs font-mono">
              <div className="text-text-muted font-bold flex items-center gap-1 text-[11px]">
                <Home size={12} className="text-amber-400" /> Threatened Settlements & Facilities:
              </div>
              <div className="space-y-1">
                {dispatchPlan.threatened_facilities.slice(0, 3).map((s, idx) => (
                  <div key={idx} className="bg-bg-app p-2 border border-border flex justify-between items-center text-[11px]">
                    <span className="text-amber-400 font-bold">{s.isim}</span>
                    <span className="text-text-muted text-[10px]">{s.nufus_yatak_kapasitesi || s.gps_format}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <button
            onClick={() => setDispatchExecuted(true)}
            disabled={dispatchExecuted}
            className={`w-full py-2.5 px-4 font-bold text-xs tracking-wider flex items-center justify-center gap-2 transition-all shadow-md ${
              dispatchExecuted
                ? 'bg-emerald-600 text-white cursor-default'
                : 'bg-primary hover:bg-primary/90 text-white active:scale-98 cursor-pointer'
            }`}
          >
            {dispatchExecuted ? (
              <>
                <CheckCircle2 size={16} /> ORDER TRANSMITTED TO OGM / AFAD
              </>
            ) : (
              <>
                <Crosshair size={16} /> CONFIRM & TRANSMIT DISPATCH ORDER
              </>
            )}
          </button>
        </div>
      ) : (
        <button
          onClick={() => handleGenerateDispatch(selectedPoint, currentPointDetection)}
          className="w-full py-2.5 px-4 bg-primary hover:bg-primary/90 text-white font-bold text-xs tracking-wider flex items-center justify-center gap-2 transition-all shadow-md cursor-pointer"
        >
          <ShieldAlert size={16} />
          <span>GENERATE AI DISPATCH PLAN</span>
        </button>
      )}
    </div>
  );
}