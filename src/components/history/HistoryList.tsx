import { CheckCircle2, AlertTriangle, FileImage, FileVideo, Clock, Trash2, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { HistoryItem } from "@/lib/api";

interface HistoryListProps {
  items: HistoryItem[];
  onClear: () => void;
  isLoading?: boolean;
}

export function HistoryList({ items, onClear, isLoading }: HistoryListProps) {
  if (isLoading) {
    return (
      <div className="glass-card glow-border p-12 text-center">
        <Loader2 className="w-12 h-12 text-primary mx-auto mb-4 animate-spin" />
        <h3 className="font-display font-semibold text-lg mb-2">Loading History</h3>
        <p className="text-muted-foreground text-sm">
          Fetching your analysis history...
        </p>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="glass-card glow-border p-12 text-center">
        <Clock className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
        <h3 className="font-display font-semibold text-lg mb-2">No Analysis History</h3>
        <p className="text-muted-foreground text-sm">
          Your analysis results will appear here after you've analyzed some media.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="font-display font-bold text-2xl">Analysis History</h2>
          <p className="text-muted-foreground text-sm">{items.length} items</p>
        </div>
        <Button variant="ghost" size="sm" onClick={onClear}>
          <Trash2 className="w-4 h-4" />
          Clear All
        </Button>
      </div>

      {/* List */}
      <div className="space-y-3">
        {items.map((item) => {
          const isReal = item.verdict === "REAL";
          return (
            <div
              key={item.id}
              className={cn(
                "glass-card glow-border p-4 flex items-center gap-4",
                isReal ? "border-success/20" : "border-destructive/20"
              )}
            >
              {/* Icon */}
              <div className={cn(
                "w-12 h-12 rounded-xl flex items-center justify-center",
                isReal ? "bg-success/10" : "bg-destructive/10"
              )}>
                {isReal ? (
                  <CheckCircle2 className="w-6 h-6 text-success" />
                ) : (
                  <AlertTriangle className="w-6 h-6 text-destructive" />
                )}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <p className="font-medium truncate">{item.fileName}</p>
                  {item.fileType === "image" ? (
                    <FileImage className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                  ) : (
                    <FileVideo className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                  )}
                </div>
                <p className="text-sm text-muted-foreground">
                  {new Date(item.analyzedAt).toLocaleString()}
                </p>
              </div>

              {/* Verdict */}
              <div className="text-right">
                <p className={cn(
                  "font-display font-bold",
                  isReal ? "text-success" : "text-destructive"
                )}>
                  {item.verdict}
                </p>
                <p className="text-sm text-muted-foreground">
                  {item.confidence}% confidence
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
