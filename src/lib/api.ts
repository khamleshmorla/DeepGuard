// Backend API URL - use environment variable or fallback to Render URL
const BACKEND_API_URL =
  import.meta.env.VITE_API_URL || "https://deepguard-backend-p5yq.onrender.com";

// -----------------------------
// Type Definitions
// -----------------------------
export interface FacialAnalysisDetails {
  score: number;
  landmarks?: number;
  skinTexture?: number;
  eyeConsistency?: number;
  hairBoundary?: number;
}

export interface TemporalConsistencyDetails {
  score: number;
  lighting?: number;
  shadows?: number;
  colorTemp?: number;
}

export interface ArtifactDetectionDetails {
  score: number;
  ganFingerprints?: number;
  blendingArtifacts?: number;
  compressionAnomalies?: number;
}

export interface MetadataAnalysisDetails {
  score: number;
  resolutionConsistency?: number;
  noisePatterns?: number;
}

export interface AnalysisDetails {
  facialAnalysis: FacialAnalysisDetails | number;
  temporalConsistency: TemporalConsistencyDetails | number;
  artifactDetection: ArtifactDetectionDetails | number;
  metadataAnalysis: MetadataAnalysisDetails | number;
}

export interface AnalysisResult {
  verdict: "REAL" | "FAKE";
  confidence: number;
  riskLevel: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  fileName: string;
  analyzedAt: string;
  details: AnalysisDetails;
  detectedTechniques?: string[];
  authenticityMarkers?: string[];
  explanation?: string;
  technicalNotes?: string;
}

export interface HistoryItem extends AnalysisResult {
  id: string;
  fileType: "image" | "video";
}

// Backend response type (FastAPI /api/predict)
interface BackendPredictResponse {
  verdict: "REAL" | "FAKE";
  confidence: number;
  fileName: string;
  fileType: string;
  analyzedAt: string;
  details: {
    facialAnalysis: number;
    temporalConsistency: number;
    artifactDetection: number;
    metadataAnalysis: number;
  };
  engine: {
    primary: string;
    secondary: string | null;
  };
}

// -----------------------------
// Core API Call
// -----------------------------
export async function analyzeMedia(file: File): Promise<AnalysisResult> {
  const isVideo = file.type.startsWith("video/");
  const fileType = isVideo ? "video" : "image";

  console.log(
    `[DeepGuard] Analyzing ${file.name} (${fileType}) via ${BACKEND_API_URL}`
  );

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch(`${BACKEND_API_URL}/api/predict`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Backend error ${response.status}: ${errorText}`);
    }

    const data: BackendPredictResponse = await response.json();

    const confidence = data.confidence;
    const verdict = data.verdict;

    const result: AnalysisResult = {
      verdict,
      confidence,
      riskLevel:
        verdict === "FAKE"
          ? confidence >= 80
            ? "CRITICAL"
            : confidence >= 60
            ? "HIGH"
            : "MEDIUM"
          : "LOW",
      fileName: data.fileName,
      analyzedAt: data.analyzedAt,
      details: {
        facialAnalysis: data.details.facialAnalysis,
        temporalConsistency: data.details.temporalConsistency,
        artifactDetection: data.details.artifactDetection,
        metadataAnalysis: data.details.metadataAnalysis,
      },
      detectedTechniques: [],
      authenticityMarkers: [],
      explanation: `Analysis performed by ${data.engine.primary}${
        data.engine.secondary ? ` with ${data.engine.secondary}` : ""
      }`,
      technicalNotes: `Primary engine: ${data.engine.primary}, Secondary: ${
        data.engine.secondary || "N/A"
      }`,
    };

    return result;
  } catch (error) {
    console.error("[DeepGuard] Analysis failed:", error);

    if (
      error instanceof TypeError &&
      error.message.toLowerCase().includes("fetch")
    ) {
      throw new Error(
        "Backend is waking up (free tier cold start). Please retry in a few seconds."
      );
    }

    throw error;
  }
}

// -----------------------------
// History (Lovable removed)
// -----------------------------
export async function fetchHistory(): Promise<HistoryItem[]> {
  console.warn(
    "[DeepGuard] History is disabled (Lovable/Supabase removed)."
  );
  return [];
}

// -----------------------------
// Backend Health Check
// -----------------------------
export async function checkBackendHealth(): Promise<{
  healthy: boolean;
  message: string;
}> {
  try {
    const response = await fetch(`${BACKEND_API_URL}/health`);
    if (response.ok) {
      const data = await response.json();
      return { healthy: true, message: data.status || "Backend healthy" };
    }
    return { healthy: false, message: `Status ${response.status}` };
  } catch {
    return {
      healthy: false,
      message: "Backend offline or cold starting (Render free tier)",
    };
  }
}

// -----------------------------
// Report Generation
// -----------------------------
export function generateReport(result: AnalysisResult): Blob {
  const reportContent = `
DEEPGUARD ANALYSIS REPORT
========================

File: ${result.fileName}
Analyzed: ${new Date(result.analyzedAt).toLocaleString()}

VERDICT: ${result.verdict}
Confidence: ${result.confidence}%
Risk Level: ${result.riskLevel}

${result.explanation ?? ""}

TECHNICAL NOTES:
${result.technicalNotes ?? ""}

FORENSIC BREAKDOWN:
- Facial Analysis: ${
    typeof result.details.facialAnalysis === "object"
      ? result.details.facialAnalysis.score
      : result.details.facialAnalysis
  }%
- Temporal Consistency: ${
    typeof result.details.temporalConsistency === "object"
      ? result.details.temporalConsistency.score
      : result.details.temporalConsistency
  }%
- Artifact Detection: ${
    typeof result.details.artifactDetection === "object"
      ? result.details.artifactDetection.score
      : result.details.artifactDetection
  }%
- Metadata Analysis: ${
    typeof result.details.metadataAnalysis === "object"
      ? result.details.metadataAnalysis.score
      : result.details.metadataAnalysis
  }%

Generated by DeepGuard AI
`.trim();

  return new Blob([reportContent], { type: "text/plain" });
}

// -----------------------------
// Share Result
// -----------------------------
export async function shareResult(result: AnalysisResult): Promise<boolean> {
  const shareData = {
    title: "DeepGuard Analysis Result",
    text: `DeepGuard: ${result.fileName} — ${result.verdict} (${result.confidence}%)`,
    url: window.location.href,
  };

  if (navigator.share && navigator.canShare(shareData)) {
    try {
      await navigator.share(shareData);
      return true;
    } catch {
      return false;
    }
  }

  await navigator.clipboard.writeText(
    `${shareData.text}\n${shareData.url}`
  );
  return true;
}
