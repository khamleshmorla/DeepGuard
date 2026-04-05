import { Shield, Brain, Users, Globe } from "lucide-react";

export function AboutSection() {
  return (
    <section className="py-24">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="max-w-3xl mx-auto text-center mb-16">
          <h1 className="font-display text-4xl md:text-5xl font-bold mb-6">
            Fighting <span className="text-gradient">Misinformation</span>
            <br />With AI Technology
          </h1>
          <p className="text-lg text-muted-foreground">
            DeepGuard is at the forefront of the battle against synthetic media manipulation. 
            Our mission is to provide accessible, accurate tools that help individuals and 
            organizations verify the authenticity of digital content.
          </p>
        </div>

        {/* Stats */}
        <div className="grid md:grid-cols-4 gap-6 mb-16">
          {[
            { icon: Shield, value: "99.2%", label: "Accuracy Rate" },
            { icon: Brain, value: "4", label: "Ensemble Models" },
            { icon: Users, value: "100%", label: "User Privacy" },
            { icon: Globe, value: "Universal", label: "Format Support" },
          ].map((stat, index) => (
            <div key={index} className="glass-card glow-border p-6 text-center">
              <stat.icon className="w-8 h-8 text-primary mx-auto mb-3" />
              <p className="font-display text-3xl font-bold text-gradient mb-1">
                {stat.value}
              </p>
              <p className="text-sm text-muted-foreground">{stat.label}</p>
            </div>
          ))}
        </div>

        {/* Content Sections */}
        <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          <div className="glass-card glow-border p-8">
            <h2 className="font-display font-bold text-2xl mb-4">Our Technology</h2>
            <p className="text-muted-foreground leading-relaxed mb-4">
              DeepGuard utilizes state-of-the-art convolutional neural networks (CNNs) 
              trained on millions of authentic and manipulated media samples. Our models 
              are continuously updated to detect the latest deepfake generation techniques.
            </p>
            <ul className="space-y-2 text-muted-foreground">
              <li className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                Multi-layer facial analysis
              </li>
              <li className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                Temporal consistency verification
              </li>
              <li className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                Compression artifact detection
              </li>
              <li className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                Metadata forensic analysis
              </li>
            </ul>
          </div>

          <div className="glass-card glow-border p-8">
            <h2 className="font-display font-bold text-2xl mb-4">Why It Matters</h2>
            <p className="text-muted-foreground leading-relaxed mb-4">
              Deepfakes and AI-generated content pose significant risks to society:
            </p>
            <ul className="space-y-3 text-muted-foreground">
              <li className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-destructive/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-xs text-destructive font-bold">!</span>
                </div>
                <span>Political misinformation and election interference</span>
              </li>
              <li className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-destructive/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-xs text-destructive font-bold">!</span>
                </div>
                <span>Financial fraud and impersonation scams</span>
              </li>
              <li className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-destructive/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-xs text-destructive font-bold">!</span>
                </div>
                <span>Erosion of trust in authentic media</span>
              </li>
              <li className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-destructive/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-xs text-destructive font-bold">!</span>
                </div>
                <span>Personal harassment and reputation damage</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="max-w-3xl mx-auto mt-12">
          <div className="glass-card p-6 border-warning/20">
            <p className="text-sm text-muted-foreground text-center">
              <strong className="text-warning">Note:</strong> While our detection system achieves high accuracy, 
              no AI-based detection system is 100% foolproof. Results should be used as one of several 
              verification methods when assessing media authenticity.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
