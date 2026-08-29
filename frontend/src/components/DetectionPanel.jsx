/**
 * DetectionPanel Component
 * 
 * Telemetry and classification panel for drone-based computer vision surveillance.
 * Presents real-time YOLO model inference results, including detected fire/smoke classes,
 * model confidence scores, precise target coordinates, and frame processing counts.
 */

import { Target } from 'lucide-react';

export default function DetectionPanel({ currentPointDetection }) {
  return (
    <div className="space-y-2">
      <h3 className="text-xs font-bold text-text-muted uppercase tracking-wider flex items-center gap-2">
        <Target size={14} /> 1. YOLO Video Detection
      </h3>
      <div className="border border-border bg-bg-app p-3 font-mono text-sm space-y-1">
        <div className="flex justify-between">
          <span className="text-text-muted">Classification:</span>
          <span className="text-danger font-bold uppercase">
            {currentPointDetection.class_name}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-text-muted">Peak Confidence:</span>
          <span>{((currentPointDetection.confidence || 0) * 100).toFixed(1)}%</span>
        </div>
        <div className="flex justify-between">
          <span className="text-text-muted">Target Coordinates:</span>
          <span>{currentPointDetection.latitude.toFixed(4)}, {currentPointDetection.longitude.toFixed(4)}</span>
        </div>
        {currentPointDetection.total_frames > 0 && (
          <div className="flex justify-between text-xs text-text-muted pt-1 border-t border-border/40">
            <span>Video Frames Analyzed:</span>
            <span>{currentPointDetection.total_frames}</span>
          </div>
        )}
      </div>
    </div>
  );
}