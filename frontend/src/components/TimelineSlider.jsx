/**
 * TimelineSlider Component
 * 
 * Interactive temporal scrubbing control positioned at the bottom of the map view.
 * Allows operators to scrub back up to 48 hours to examine historical wildfire risk grids,
 * past detections, and weather states with playback automation and quick-jump presets.
 */

import { useState, useEffect, useRef } from 'react';
import { Play, Pause, RotateCcw, Clock, History, Loader2 } from 'lucide-react';

export default function TimelineSlider({ hoursAgo, onHourChange, onPresetClick, isSyncing }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const playIntervalRef = useRef(null);

  const presets = [
    { label: 'LIVE', value: 0 },
    { label: '-3H', value: 3 },
    { label: '-6H', value: 6 },
    { label: '-12H', value: 12 },
    { label: '-24H', value: 24 },
    { label: '-48H', value: 48 },
  ];

  // Auto-play
  useEffect(() => {
    if (isPlaying) {
      playIntervalRef.current = setInterval(() => {
        const next = hoursAgo <= 0 ? 0 : hoursAgo - 1;
        if (next === 0) setIsPlaying(false);
        onPresetClick(next);
      }, 2500);
    } else {
      if (playIntervalRef.current) clearInterval(playIntervalRef.current);
    }
    return () => {
      if (playIntervalRef.current) clearInterval(playIntervalRef.current);
    };
  }, [isPlaying, hoursAgo, onPresetClick]);

  return (
    <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-30 w-[600px] max-w-[92%] bg-bg-panel/95 backdrop-blur-md border border-border p-3.5 shadow-2xl space-y-2.5 font-mono text-xs select-none">
      <div className="flex items-center justify-between border-b border-border/60 pb-2">
        <div className="flex items-center gap-2">
          <History size={15} className={hoursAgo > 0 ? "text-amber-400 animate-pulse" : "text-primary"} />
          <span className="font-bold uppercase tracking-wider text-[11px] text-text-main">
            Temporal Risk & Detection Scrubbing
          </span>
        </div>

        <div className="flex items-center gap-2">
          {isSyncing && <Loader2 size={13} className="animate-spin text-primary" />}
          <span className={`px-2 py-0.5 text-[10px] font-bold border transition-colors ${
            hoursAgo === 0 
              ? 'bg-emerald-950/40 text-emerald-400 border-emerald-500/40' 
              : 'bg-amber-950/40 text-amber-400 border-amber-500/40 animate-pulse'
          }`}>
            {hoursAgo === 0 ? '● LIVE (0H)' : `HISTORICAL: T - ${hoursAgo} HOURS`}
          </span>
        </div>
      </div>

      {/* Slider Controls */}
      <div className="space-y-1.5">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className={`p-1.5 border transition-all cursor-pointer ${
              isPlaying 
                ? 'bg-amber-600 text-white border-amber-500' 
                : 'bg-bg-app hover:bg-border text-text-main border-border'
            }`}
            title={isPlaying ? "Pause" : "Play Timeline"}
          >
            {isPlaying ? <Pause size={14} /> : <Play size={14} />}
          </button>

          <input
            type="range"
            min="0"
            max="48"
            step="1"
            value={hoursAgo}
            onChange={(e) => {
              setIsPlaying(false);
              onHourChange(Number(e.target.value));
            }}
            className="flex-1 accent-primary cursor-pointer h-2 bg-bg-app rounded border border-border"
          />

          <button
            onClick={() => {
              setIsPlaying(false);
              onPresetClick(0);
            }}
            className="px-2 py-1 bg-bg-app hover:bg-border border border-border text-[10px] text-text-muted hover:text-primary transition-colors flex items-center gap-1 cursor-pointer"
            title="Reset to Live"
          >
            <RotateCcw size={11} /> Reset
          </button>
        </div>

        <div className="flex justify-between text-[10px] text-text-muted px-8 font-mono">
          <span>NOW (Live)</span>
          <span>-12H</span>
          <span>-24H (1d)</span>
          <span>-36H</span>
          <span>-48H (2d)</span>
        </div>
      </div>

      {/* Quick Presets */}
      <div className="flex items-center justify-between pt-1 border-t border-border/40">
        <div className="flex gap-1.5">
          {presets.map(p => (
            <button
              key={p.value}
              onClick={() => {
                setIsPlaying(false);
                onPresetClick(p.value);
              }}
              className={`px-2 py-0.5 text-[10px] border transition-all cursor-pointer ${
                hoursAgo === p.value
                  ? 'bg-primary text-white border-primary font-bold shadow-sm'
                  : 'bg-bg-app text-text-muted border-border hover:border-text-muted'
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>

        <div className="text-[10px] text-text-muted flex items-center gap-1">
          <Clock size={11} />
          <span>{isSyncing ? 'Sending request to backend...' : `Offset: T - ${hoursAgo}h`}</span>
        </div>
      </div>
    </div>
  );
}