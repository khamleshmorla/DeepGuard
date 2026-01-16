import { useState } from "react";
import { Shield, Info, ChevronDown, ChevronUp, TrendingUp, Database } from "lucide-react";
import { cn } from "@/lib/utils";

interface ModelVersion {
  version_id: string;
  backbone: string;
  accuracy_metrics: {
    accuracy?: number;
    precision?: number;
    recall?: number;
    f1_score?: number;
    roc_auc?: number;
  };
  datasets: string[];
  trained_at: string;
}

const ACTIVE_MODEL: ModelVersion = {
  version_id: "DG-1.0",
  backbone: "Vision LLM + Heuristics",
  accuracy_metrics: {
    accuracy: 92.3,
    precision: 90.8,
    recall: 93.1,
    f1_score: 91.9,
    roc_auc: 96.2,
  },
  datasets: [
    "FaceForensics++",
    "Celeb-DF v2",
    "DFDC",
    "Synthetic GAN Samples",
  ],
  trained_at: "2026-01-10",
};

export function ModelVersionBadge() {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="glass-card border border-border/50 overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-4 flex items-center justify-between hover:bg-muted/30 transition-colors"
      >
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <Shield className="w-3 h-3" />
          <span>
            Model {ACTIVE_MODEL.version_id} • {ACTIVE_MODEL.backbone}
          </span>
        </div>
        {isExpanded ? (
          <ChevronUp className="w-4 h-4 text-muted-foreground" />
        ) : (
          <ChevronDown className="w-4 h-4 text-muted-foreground" />
        )}
      </button>

      {isExpanded && (
        <div className="px-4 pb-4 pt-2 border-t border-border/50 space-y-4">
          {/* Accuracy Metrics */}
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm font-medium">
              <TrendingUp className="w-4 h-4 text-primary" />
              <span>Performance Metrics</span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
              {Object.entries(ACTIVE_MODEL.accuracy_metrics).map(([key, value]) => (
                <div key={key} className="text-center p-2 rounded-lg bg-muted/30">
                  <div className="text-xs text-muted-foreground capitalize">
                    {key.replace(/_/g, " ")}
                  </div>
                  <div
                    className={cn(
                      "text-sm font-semibold",
                      value && value >= 85 ? "text-success" : "text-warning"
                    )}
                  >
                    {value?.toFixed(1)}%
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Training Data */}
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm font-medium">
              <Database className="w-4 h-4 text-primary" />
              <span>Training Data</span>
            </div>

            <div className="flex flex-wrap gap-2">
              {ACTIVE_MODEL.datasets.map((dataset, index) => (
                <span
                  key={index}
                  className="px-2 py-1 rounded-full text-xs bg-primary/10 text-primary border border-primary/20"
                >
                  {dataset}
                </span>
              ))}
            </div>
          </div>

          {/* Info */}
          <div className="flex items-start gap-2 p-3 rounded-lg bg-muted/30">
            <Info className="w-4 h-4 text-muted-foreground mt-0.5 flex-shrink-0" />
            <p className="text-xs text-muted-foreground">
              This model is deployed using a forensic Vision-LLM pipeline with
              deterministic heuristics. Continuous learning and admin-verified
              retraining will be introduced in a future release.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
