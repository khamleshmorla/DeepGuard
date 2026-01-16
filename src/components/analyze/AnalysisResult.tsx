import { CheckCircle2, AlertTriangle, ArrowLeft, Download, Share2, Info, Shield, AlertOctagon, Eye, Sparkles, Fingerprint, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { AnalysisResult as AnalysisResultData } from "@/lib/api";
import { generateReport, shareResult } from "@/lib/api";
import { FeedbackPanel } from "@/components/feedback/FeedbackPanel";
import { ModelVersionBadge } from "@/components/feedback/ModelVersionBadge";
import { toast } from "sonner";

interface AnalysisResultProps {
  result: AnalysisResultData;
  onNewAnalysis: () => void;
}

// Helper to extract score from detailed or simple format
function getScore(value: number | { score: number } | undefined): number {
  if (typeof value === 'number') return value;
  if (value && typeof value === 'object' && 'score' in value) return value.score;
  return 0;
}

// Helper to get sub-scores
function getSubScores(value: unknown): Record<string, number> {
  if (typeof value === 'object' && value !== null) {
    const obj = value as Record<string, unknown>;
    const result: Record<string, number> = {};
    for (const [key, val] of Object.entries(obj)) {
      if (key !== 'score' && typeof val === 'number') {
        result[key] = val;
      }
    }
    return result;
  }
  return {};
}

export function AnalysisResult({ result, onNewAnalysis }: AnalysisResultProps) {
  const isReal = result.verdict === "REAL";

  const riskColors = {
    LOW: "text-success",
    MEDIUM: "text-warning",
    HIGH: "text-destructive",
    CRITICAL: "text-destructive"
  };

  const riskBgColors = {
    LOW: "bg-success/10 border-success/30",
    MEDIUM: "bg-warning/10 border-warning/30",
    HIGH: "bg-destructive/10 border-destructive/30",
    CRITICAL: "bg-destructive/20 border-destructive/50"
  };

  const detailsConfig = [
    { 
      key: 'facialAnalysis', 
      label: 'Facial Forensics',
      icon: Eye,
      description: 'Landmarks, skin texture, eye consistency'
    },
    { 
      key: 'temporalConsistency', 
      label: 'Lighting & Consistency',
      icon: Sparkles,
      description: 'Shadows, color temperature, spatial coherence'
    },
    { 
      key: 'artifactDetection', 
      label: 'Artifact Detection',
      icon: Fingerprint,
      description: 'GAN fingerprints, blending, compression'
    },
    { 
      key: 'metadataAnalysis', 
      label: 'Quality Analysis',
      icon: Zap,
      description: 'Resolution, noise patterns, sharpness'
    }
  ];

  const handleDownloadReport = () => {
    try {
      const blob = generateReport(result);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `deepguard-report-${result.fileName.replace(/\.[^/.]+$/, '')}.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      toast.success('Report downloaded successfully');
    } catch (error) {
      console.error('Download failed:', error);
      toast.error('Failed to download report');
    }
  };

  const handleShare = async () => {
    try {
      const success = await shareResult(result);
      if (success) {
        toast.success('Shared successfully', {
          description: navigator.share ? 'Opened share dialog' : 'Link copied to clipboard'
        });
      }
    } catch (error) {
      console.error('Share failed:', error);
      toast.error('Failed to share');
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto animate-scale-in space-y-6">
      {/* Main Result Card */}
      <div className={cn(
        "glass-card glow-border p-8 text-center",
        isReal ? "border-success/30" : "border-destructive/30"
      )}>
        {/* Verdict Icon */}
        <div className={cn(
          "w-24 h-24 rounded-full mx-auto mb-6 flex items-center justify-center relative",
          isReal ? "bg-success/10" : "bg-destructive/10"
        )}>
          {isReal ? (
            <CheckCircle2 className="w-12 h-12 text-success" />
          ) : (
            <AlertTriangle className="w-12 h-12 text-destructive" />
          )}
          <div className={cn(
            "absolute inset-0 rounded-full",
            isReal ? "pulse-ring border-success/50" : "pulse-ring border-destructive/50"
          )} />
        </div>

        {/* Verdict Text */}
        <h2 className={cn(
          "font-display text-4xl font-bold mb-2",
          isReal ? "status-real" : "status-fake"
        )}>
          {result.verdict}
        </h2>
        
        <p className="text-muted-foreground mb-4">
          {isReal 
            ? "This media appears to be authentic." 
            : "This media shows signs of manipulation or AI generation."
          }
        </p>

        {/* Risk Level Badge */}
        <div className={cn(
          "inline-flex items-center gap-2 px-4 py-2 rounded-full border mb-6",
          riskBgColors[result.riskLevel || "LOW"]
        )}>
          {result.riskLevel === "CRITICAL" || result.riskLevel === "HIGH" ? (
            <AlertOctagon className={cn("w-4 h-4", riskColors[result.riskLevel])} />
          ) : (
            <Shield className={cn("w-4 h-4", riskColors[result.riskLevel || "LOW"])} />
          )}
          <span className={cn("text-sm font-medium", riskColors[result.riskLevel || "LOW"])}>
            {result.riskLevel || "LOW"} Risk
          </span>
        </div>

        {/* Confidence Score */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-muted-foreground">Confidence Score</span>
            <span className={cn(
              "font-display font-bold text-2xl",
              isReal ? "text-success" : "text-destructive"
            )}>
              {result.confidence}%
            </span>
          </div>
          <div className="confidence-meter">
            <div
              className={cn(
                "confidence-meter-fill",
                isReal ? "bg-success shadow-glow-success" : "bg-destructive shadow-glow-destructive"
              )}
              style={{ width: `${result.confidence}%` }}
            />
          </div>
        </div>

        {/* File Info */}
        <div className="text-sm text-muted-foreground">
          <p className="font-medium">{result.fileName}</p>
          <p>Analyzed {new Date(result.analyzedAt).toLocaleString()}</p>
        </div>
      </div>

      {/* AI Explanation */}
      {result.explanation && (
        <div className="glass-card glow-border p-6">
          <div className="flex items-start gap-3">
            <Info className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
            <div>
              <h3 className="font-display font-semibold text-lg mb-2">AI Forensic Analysis</h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                {result.explanation}
              </p>
              {result.technicalNotes && (
                <p className="text-muted-foreground/70 text-xs mt-3 italic">
                  Technical: {result.technicalNotes}
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Detected Techniques or Authenticity Markers */}
      {((result.detectedTechniques && result.detectedTechniques.length > 0) || 
        (result.authenticityMarkers && result.authenticityMarkers.length > 0)) && (
        <div className="glass-card glow-border p-6">
          <h3 className="font-display font-semibold text-lg mb-4">
            {isReal ? "Authenticity Markers" : "Detected Manipulation Techniques"}
          </h3>
          <div className="flex flex-wrap gap-2">
            {(isReal ? result.authenticityMarkers : result.detectedTechniques)?.map((item, index) => (
              <span 
                key={index}
                className={cn(
                  "px-3 py-1.5 rounded-full text-xs font-medium border",
                  isReal 
                    ? "bg-success/10 text-success border-success/30"
                    : "bg-destructive/10 text-destructive border-destructive/30"
                )}
              >
                {item}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Detailed Breakdown */}
      <div className="glass-card glow-border p-6">
        <h3 className="font-display font-semibold text-lg mb-4">Forensic Analysis Breakdown</h3>
        
        <div className="space-y-5">
          {detailsConfig.map(({ key, label, icon: Icon, description }) => {
            const value = result.details[key as keyof typeof result.details];
            const mainScore = getScore(value);
            const subScores = getSubScores(value);
            
            return (
              <div key={key} className="space-y-2">
                <div className="flex items-center gap-2 mb-1">
                  <Icon className="w-4 h-4 text-primary" />
                  <span className="text-sm font-medium">{label}</span>
                </div>
                <p className="text-xs text-muted-foreground/70 mb-2">{description}</p>
                
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-muted-foreground">Overall Score</span>
                  <span className={cn(
                    "text-sm font-medium",
                    mainScore > 70 ? (isReal ? "text-success" : "text-destructive") : "text-warning"
                  )}>
                    {mainScore}%
                  </span>
                </div>
                <div className="progress-bar">
                  <div
                    className={cn(
                      "progress-bar-fill",
                      mainScore > 70 
                        ? (isReal ? "bg-success" : "bg-destructive")
                        : "bg-warning"
                    )}
                    style={{ width: `${mainScore}%` }}
                  />
                </div>

                {/* Sub-scores if available */}
                {Object.keys(subScores).length > 0 && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-2">
                    {Object.entries(subScores).map(([subKey, subValue]) => (
                      <div key={subKey} className="text-center p-2 rounded-lg bg-muted/30">
                        <div className="text-xs text-muted-foreground capitalize">
                          {subKey.replace(/([A-Z])/g, ' $1').trim()}
                        </div>
                        <div className={cn(
                          "text-sm font-semibold",
                          subValue > 70 ? (isReal ? "text-success" : "text-destructive") : "text-warning"
                        )}>
                          {subValue}%
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Feedback Panel */}
      <FeedbackPanel
        analysisId={result.id}
        fileName={result.fileName}
        originalPrediction={result.verdict as "REAL" | "FAKE"}
        originalConfidence={result.confidence}
      />

      {/* Model Version Badge */}
      <ModelVersionBadge />

      {/* Actions */}
      <div className="flex flex-col sm:flex-row gap-3">
        <Button
          variant="outline"
          className="flex-1"
          onClick={onNewAnalysis}
        >
          <ArrowLeft className="w-4 h-4" />
          New Analysis
        </Button>
        <Button 
          variant="secondary" 
          className="flex-1"
          onClick={handleDownloadReport}
        >
          <Download className="w-4 h-4" />
          Download Report
        </Button>
        <Button 
          variant="secondary" 
          className="flex-1"
          onClick={handleShare}
        >
          <Share2 className="w-4 h-4" />
          Share
        </Button>
      </div>
    </div>
  );
}
