import { Shield, Scan, AlertTriangle, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";

interface HeroSectionProps {
  onStartAnalysis: () => void;
  onScrollToHowItWorks?: () => void;
}

export function HeroSection({ onStartAnalysis, onScrollToHowItWorks }: HeroSectionProps) {
  const handleLearnMore = () => {
    if (onScrollToHowItWorks) {
      onScrollToHowItWorks();
    } else {
      // Scroll to how it works section
      const howItWorksSection = document.getElementById('how-it-works');
      if (howItWorksSection) {
        howItWorksSection.scrollIntoView({ behavior: 'smooth' });
      }
    }
  };

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
      {/* Background Effects */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-primary/5 rounded-full blur-3xl" />
        
        {/* Grid Pattern */}
        <div 
          className="absolute inset-0 opacity-[0.02]"
          style={{
            backgroundImage: `linear-gradient(hsl(var(--primary)) 1px, transparent 1px),
                              linear-gradient(90deg, hsl(var(--primary)) 1px, transparent 1px)`,
            backgroundSize: '60px 60px'
          }}
        />
      </div>

      <div className="container mx-auto px-4 relative z-10">
        <div className="max-w-4xl mx-auto text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 mb-8 animate-fade-in">
            <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
            <span className="text-sm font-medium text-primary">AI-Powered Detection</span>
          </div>

          {/* Main Heading */}
          <h1 className="font-display text-5xl md:text-7xl font-bold mb-6 animate-fade-in tracking-tight">
            Detect Deepfakes
            <br />
            <span className="text-gradient">Protect Truth</span>
          </h1>

          {/* Subtitle */}
          <p className="text-lg md:text-xl text-muted-foreground mb-10 max-w-2xl mx-auto animate-fade-in">
            Advanced AI technology to identify manipulated media in seconds. 
            Safeguard yourself from misinformation with confidence scores you can trust.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16 animate-fade-in">
            <Button variant="glow" size="xl" onClick={onStartAnalysis}>
              <Scan className="w-5 h-5" />
              Analyze Media
            </Button>
            <Button variant="outline" size="xl" onClick={handleLearnMore}>
              Learn How It Works
            </Button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-8 animate-fade-in">
            {[
              { value: "99.2%", label: "Detection Accuracy" },
              { value: "<3s", label: "Analysis Time" },
              { value: "4", label: "Ensemble AI Engines" },
              { value: "100%", label: "Privacy Secured" },
            ].map((stat, index) => (
              <div key={index} className="stat-card text-center">
                <div className="font-display text-2xl md:text-3xl font-bold text-gradient mb-1">
                  {stat.value}
                </div>
                <div className="text-sm text-muted-foreground">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Floating Elements */}
        <div className="absolute top-1/4 left-10 hidden lg:block animate-float">
          <div className="glass-card p-4 rounded-xl">
            <CheckCircle2 className="w-8 h-8 text-success" />
          </div>
        </div>
        
        <div className="absolute top-1/3 right-10 hidden lg:block animate-float" style={{ animationDelay: '1s' }}>
          <div className="glass-card p-4 rounded-xl">
            <AlertTriangle className="w-8 h-8 text-warning" />
          </div>
        </div>
        
        <div className="absolute bottom-1/4 left-20 hidden lg:block animate-float" style={{ animationDelay: '0.5s' }}>
          <div className="glass-card p-4 rounded-xl">
            <Shield className="w-8 h-8 text-primary" />
          </div>
        </div>
      </div>
    </section>
  );
}
