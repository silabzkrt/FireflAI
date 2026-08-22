import { Activity, RefreshCw } from 'lucide-react';

export default function TopNav({ fetchDatabaseState, isSyncing }) {
  return (
    <header className="h-14 bg-bg-panel border-b border-border flex items-center justify-between px-4 shrink-0">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 bg-primary text-white flex items-center justify-center font-bold">FF</div>
        <h1 className="text-lg font-bold tracking-wide text-text-main">
          FIREFLAI <span className="text-text-muted font-normal text-sm ml-2">v1.0.0</span>
        </h1>
      </div>
      <div className="flex items-center gap-4">
        <button
          onClick={fetchDatabaseState}
          disabled={isSyncing}
          className="flex items-center gap-1.5 text-xs font-mono text-text-muted hover:text-primary bg-bg-app px-2.5 py-1 border border-border transition-colors cursor-pointer"
        >
          <RefreshCw size={13} className={isSyncing ? "animate-spin text-primary" : ""} />
          <span>DB SYNC (0H)</span>
        </button>

        <div className="flex items-center gap-2 text-sm font-mono text-text-muted bg-bg-app px-3 py-1 border border-border">
          <Activity size={16} className="text-secondary" />
          <span>SYS: ONLINE</span>
        </div>
        <button className="btn-outline text-sm">Operator Login</button>
      </div>
    </header>
  );
}