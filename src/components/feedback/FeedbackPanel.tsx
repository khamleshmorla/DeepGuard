import { useState } from "react";
import {
  ThumbsUp,
  ThumbsDown,
  MessageSquare,
  CheckCircle,
  AlertCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

interface FeedbackPanelProps {
  analysisId?: string;
  fileName: string;
  originalPrediction: "REAL" | "FAKE";
  originalConfidence: number;
  onFeedbackSubmitted?: () => void;
}

type FeedbackState = "initial" | "selecting" | "submitted";

export function FeedbackPanel({
  fileName,
  originalPrediction,
  originalConfidence,
  onFeedbackSubmitted,
}: FeedbackPanelProps) {
  const [state, setState] = useState<FeedbackState>("initial");
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);
  const [userLabel, setUserLabel] = useState<"REAL" | "FAKE" | null>(null);
  const [feedbackText, setFeedbackText] = useState("");
  const [showTextInput, setShowTextInput] = useState(false);

  const handleSubmit = () => {
    toast.info("Feedback storage is disabled", {
      description:
        "Feedback collection will be enabled in a future update once a custom backend is added.",
    });

    setState("submitted");
    onFeedbackSubmitted?.();
  };

  if (state === "submitted") {
    return (
      <div className="glass-card p-6 border border-success/30">
        <div className="flex items-center gap-3 text-success">
          <CheckCircle className="w-5 h-5" />
          <div>
            <p className="font-medium">Feedback Recorded Locally</p>
            <p className="text-sm text-muted-foreground">
              Thank you! Feedback storage will be enabled in a future release.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="glass-card glow-border p-6">
      <div className="flex items-start gap-3 mb-4">
        <AlertCircle className="w-5 h-5 text-primary mt-0.5" />
        <div>
          <h3 className="font-display font-semibold text-lg">
            Help Improve DeepGuard
          </h3>
          <p className="text-sm text-muted-foreground">
            Feedback features are temporarily disabled while we migrate to a
            custom backend.
          </p>
        </div>
      </div>

      {state === "initial" && (
        <div className="space-y-4">
          <p className="text-sm font-medium">Is this prediction correct?</p>
          <div className="flex gap-3">
            <Button
              variant="outline"
              className="flex-1 gap-2 hover:bg-success/10 hover:border-success hover:text-success"
              onClick={() => {
                setIsCorrect(true);
                setUserLabel(originalPrediction);
                setState("selecting");
              }}
            >
              <ThumbsUp className="w-4 h-4" />
              Yes, Correct
            </Button>

            <Button
              variant="outline"
              className="flex-1 gap-2 hover:bg-destructive/10 hover:border-destructive hover:text-destructive"
              onClick={() => {
                setIsCorrect(false);
                setState("selecting");
              }}
            >
              <ThumbsDown className="w-4 h-4" />
              No, Incorrect
            </Button>
          </div>
        </div>
      )}

      {state === "selecting" && (
        <div className="space-y-4">
          {!isCorrect && (
            <div className="space-y-3">
              <p className="text-sm font-medium">
                What should the correct label be?
              </p>
              <div className="flex gap-3">
                <Button
                  variant="outline"
                  className={cn(
                    "flex-1 gap-2",
                    userLabel === "REAL" &&
                      "bg-success/10 border-success text-success"
                  )}
                  onClick={() => setUserLabel("REAL")}
                >
                  REAL
                </Button>
                <Button
                  variant="outline"
                  className={cn(
                    "flex-1 gap-2",
                    userLabel === "FAKE" &&
                      "bg-destructive/10 border-destructive text-destructive"
                  )}
                  onClick={() => setUserLabel("FAKE")}
                >
                  FAKE
                </Button>
              </div>
            </div>
          )}

          <div className="space-y-3">
            <Button
              variant="ghost"
              size="sm"
              className="gap-2 text-muted-foreground"
              onClick={() => setShowTextInput(!showTextInput)}
            >
              <MessageSquare className="w-4 h-4" />
              {showTextInput ? "Hide" : "Add"} comment
            </Button>

            {showTextInput && (
              <Textarea
                placeholder="Optional feedback (stored locally only)"
                value={feedbackText}
                onChange={(e) => setFeedbackText(e.target.value)}
                className="min-h-[80px] resize-none"
              />
            )}
          </div>

          <div className="flex gap-3">
            <Button
              variant="outline"
              className="flex-1"
              onClick={() => {
                setState("initial");
                setIsCorrect(null);
                setUserLabel(null);
                setFeedbackText("");
              }}
            >
              Cancel
            </Button>
            <Button className="flex-1" onClick={handleSubmit}>
              Submit Feedback
            </Button>
          </div>
        </div>
      )}

      <div className="mt-4 pt-4 border-t border-border/50">
        <p className="text-xs text-muted-foreground text-center">
          🔒 Feedback storage and human-in-the-loop training will be enabled in a
          future release.
        </p>
      </div>
    </div>
  );
}
