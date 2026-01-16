import { Upload, Cpu, FileCheck } from "lucide-react";

const steps = [
  {
    icon: Upload,
    step: "01",
    title: "Upload Media",
    description: "Drag and drop your image or video file. We support all major formats including MP4, JPG, PNG, and WebM.",
  },
  {
    icon: Cpu,
    step: "02",
    title: "AI Analysis",
    description: "Our neural network processes each frame, detecting manipulation artifacts, facial inconsistencies, and synthetic patterns.",
  },
  {
    icon: FileCheck,
    step: "03",
    title: "Get Results",
    description: "Receive a detailed report with confidence scores, highlighted areas of concern, and a final verdict.",
  },
];

export function HowItWorksSection() {
  return (
    <section id="how-it-works" className="py-24 relative scroll-mt-20">
      {/* Background accent */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[400px] bg-primary/5 rounded-full blur-3xl" />
      </div>

      <div className="container mx-auto px-4 relative z-10">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="font-display text-3xl md:text-4xl font-bold mb-4">
            How <span className="text-gradient">DeepGuard</span> Works
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Three simple steps to verify the authenticity of any media file.
          </p>
        </div>

        {/* Steps */}
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {steps.map((step, index) => (
            <div key={index} className="relative">
              {/* Connector Line */}
              {index < steps.length - 1 && (
                <div className="hidden md:block absolute top-12 left-1/2 w-full h-0.5 bg-gradient-to-r from-primary/50 to-transparent" />
              )}
              
              <div className="glass-card glow-border p-8 text-center relative z-10">
                {/* Step Number */}
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-background border border-primary/30 rounded-full">
                  <span className="text-sm font-display font-bold text-primary">{step.step}</span>
                </div>
                
                {/* Icon */}
                <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-6 mt-4">
                  <step.icon className="w-8 h-8 text-primary" />
                </div>
                
                {/* Content */}
                <h3 className="font-display font-semibold text-xl mb-3">
                  {step.title}
                </h3>
                <p className="text-muted-foreground text-sm leading-relaxed">
                  {step.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
