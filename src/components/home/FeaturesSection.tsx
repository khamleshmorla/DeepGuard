import { Brain, Zap, Shield, Eye, BarChart3, Lock } from "lucide-react";

const features = [
  {
    icon: Brain,
    title: "Neural Network Analysis",
    description: "Advanced CNN architecture trained on millions of samples to detect subtle manipulation artifacts.",
  },
  {
    icon: Zap,
    title: "Real-time Processing",
    description: "Get results in seconds with our optimized inference pipeline. No waiting, instant insights.",
  },
  {
    icon: Eye,
    title: "Multi-Modal Detection",
    description: "Analyze images and videos with frame-by-frame examination for comprehensive results.",
  },
  {
    icon: BarChart3,
    title: "Confidence Scoring",
    description: "Detailed probability scores with visual breakdowns of detection confidence levels.",
  },
  {
    icon: Shield,
    title: "Privacy First",
    description: "Your media is processed securely and never stored without your explicit consent.",
  },
  {
    icon: Lock,
    title: "Enterprise Ready",
    description: "API access, bulk processing, and integration options for organizations.",
  },
];

export function FeaturesSection() {
  return (
    <section className="py-24 relative">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="font-display text-3xl md:text-4xl font-bold mb-4">
            Cutting-Edge <span className="text-gradient">Detection Technology</span>
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Built on state-of-the-art machine learning models, our platform provides 
            unparalleled accuracy in identifying AI-generated and manipulated content.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <div
              key={index}
              className="glass-card glow-border p-6 hover:bg-card/80 transition-all duration-300 group"
            >
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
                <feature.icon className="w-6 h-6 text-primary" />
              </div>
              <h3 className="font-display font-semibold text-lg mb-2">
                {feature.title}
              </h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
