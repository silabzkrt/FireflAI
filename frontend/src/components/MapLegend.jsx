/**
 * MapLegend Component
 * 
 * Tactical map symbology reference key rendered in the lower corner of the viewport.
 * Explains markers and status indicators including active wildfire incidents, nearby water sources,
 * threatened settlement assets, observation stations, and color-coded risk severity tiers.
 */

export default function MapLegend() {
  return (
    <div className="absolute bottom-4 right-4 bg-bg-panel/95 backdrop-blur border border-border p-3 text-xs font-mono space-y-2 shadow-xl pointer-events-auto">
      <div className="text-text-muted font-bold tracking-wider text-[11px] uppercase border-b border-border pb-1">
        Tactical Legend
      </div>
      <div className="flex items-center gap-2">
        <div className="w-4 h-4 rounded-full bg-red-600 border-2 border-white shadow-[0_0_8px_#ef4444] shrink-0"></div>
        <span className="text-red-400 font-bold">Active Wildfire (Confirmed)</span>
      </div>
      <div className="flex items-center gap-2">
        <div className="w-3 h-3 bg-cyan-400 rounded-full shrink-0"></div>
        <span className="text-cyan-400 font-bold">Water Source (Dispatch)</span>
      </div>
      <div className="flex items-center gap-2">
        <div className="w-3 h-3 bg-amber-400 rounded-full shrink-0"></div>
        <span className="text-amber-400 font-bold">Settlement / Asset (Threatened)</span>
      </div>
      <div className="flex items-center gap-2">
        <div className="w-3 h-3 bg-[#38bdf8] rotate-45 shrink-0"></div>
        <span className="text-text-main">Fixed Station</span>
      </div>
      <div className="flex items-center gap-2">
        <div className="w-3 h-3 rounded-full bg-[#ef4444] shrink-0"></div>
        <span className="text-text-main">Critical Risk (≥ 85)</span>
      </div>
      <div className="flex items-center gap-2">
        <div className="w-3 h-3 rounded-full bg-[#f97316] shrink-0"></div>
        <span className="text-text-main">High Risk (70–84)</span>
      </div>
    </div>
  );
}