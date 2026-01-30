import { useState, useCallback, useEffect } from "react";
import { analyzeMedia as analyzeMediaAPI, fetchHistory, clearHistoryStorage, type AnalysisResult, type HistoryItem } from "@/lib/api";
import { toast } from "sonner";

export function useAnalysis() {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);

  // Load history on mount
  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setIsLoadingHistory(true);
    try {
      const items = await fetchHistory();
      setHistory(items);
    } catch (error) {
      console.error("Failed to load history:", error);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const analyzeMedia = useCallback(async (file: File) => {
    setIsAnalyzing(true);
    setResult(null);

    try {
      const analysisResult = await analyzeMediaAPI(file);

      setResult(analysisResult);

      // Refresh history to include the new item
      await loadHistory();

      if (analysisResult.verdict === "FAKE") {
        toast.warning("⚠️ Potential deepfake detected!", {
          description: `Confidence: ${analysisResult.confidence}%`,
        });
      } else {
        toast.success("✓ Media appears authentic", {
          description: `Confidence: ${analysisResult.confidence}%`,
        });
      }

      return analysisResult;
    } catch (error) {
      console.error("Analysis failed:", error);
      toast.error("Analysis failed", {
        description: error instanceof Error ? error.message : "Please try again",
      });
      throw error;
    } finally {
      setIsAnalyzing(false);
    }
  }, []);

  const clearResult = useCallback(() => {
    setResult(null);
  }, []);

  const clearHistory = useCallback(() => {
    setHistory([]);
    clearHistoryStorage();
  }, []);

  return {
    isAnalyzing,
    isLoadingHistory,
    result,
    history,
    analyzeMedia,
    clearResult,
    clearHistory,
    refreshHistory: loadHistory,
  };
}
