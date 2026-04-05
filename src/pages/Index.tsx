import { useState } from "react";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { HeroSection } from "@/components/home/HeroSection";
import { FeaturesSection } from "@/components/home/FeaturesSection";
import { HowItWorksSection } from "@/components/home/HowItWorksSection";
import { UploadZone } from "@/components/analyze/UploadZone";
import { AnalysisResult } from "@/components/analyze/AnalysisResult";
import { HistoryList } from "@/components/history/HistoryList";
import { AboutSection } from "@/components/about/AboutSection";
import { useAnalysis } from "@/hooks/useAnalysis";
import { Scan } from "lucide-react";

type Page = "home" | "analyze" | "history" | "about";

const Index = () => {
  const [currentPage, setCurrentPage] = useState<Page>("home");
  const { isAnalyzing, isLoadingHistory, result, history, analyzeMedia, clearResult, clearHistory } = useAnalysis();

  const handleNavigate = (page: string) => {
    setCurrentPage(page as Page);
    // Always clear the previous result when returning to or re-clicking the Analysis page to ensure a fresh start
    if (page === "analyze" || page === "home") {
      clearResult();
    }
    // Scroll to top on page change
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleStartAnalysis = () => {
    setCurrentPage("analyze");
    clearResult();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleScrollToHowItWorks = () => {
    const element = document.getElementById('how-it-works');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const renderPage = () => {
    switch (currentPage) {
      case "home":
        return (
          <>
            <HeroSection 
              onStartAnalysis={handleStartAnalysis} 
              onScrollToHowItWorks={handleScrollToHowItWorks}
            />
            <FeaturesSection />
            <HowItWorksSection />
          </>
        );

      case "analyze":
        return (
          <section className="min-h-screen pt-24 pb-12">
            <div className="container mx-auto px-4">
              {/* Page Header */}
              <div className="text-center mb-12">
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 mb-6">
                  <Scan className="w-4 h-4 text-primary" />
                  <span className="text-sm font-medium text-primary">Media Analysis</span>
                </div>
                <h1 className="font-display text-3xl md:text-4xl font-bold mb-4">
                  Analyze Your <span className="text-gradient">Media</span>
                </h1>
                <p className="text-muted-foreground max-w-md mx-auto">
                  Upload an image or video to check for signs of AI manipulation or deepfake content.
                </p>
              </div>

              {/* Content */}
              {result ? (
                <AnalysisResult result={result} onNewAnalysis={clearResult} />
              ) : (
                <UploadZone onFileSelect={analyzeMedia} isAnalyzing={isAnalyzing} />
              )}
            </div>
          </section>
        );

      case "history":
        return (
          <section className="min-h-screen pt-24 pb-12">
            <div className="container mx-auto px-4 max-w-4xl">
              <HistoryList items={history} onClear={clearHistory} isLoading={isLoadingHistory} />
            </div>
          </section>
        );

      case "about":
        return <AboutSection />;

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Header currentPage={currentPage} onNavigate={handleNavigate} />
      <main className="flex-1">
        {renderPage()}
      </main>
      <Footer onNavigate={handleNavigate} />
    </div>
  );
};

export default Index;
