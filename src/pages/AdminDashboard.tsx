import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import {
  Shield,
  Database,
  AlertTriangle,
  Lock,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const AdminDashboard = () => {
  return (
    <div className="min-h-screen flex flex-col">
      <Header currentPage="admin" onNavigate={() => {}} />

      <main className="flex-1 pt-24 pb-12">
        <div className="container mx-auto px-4">
          {/* Header */}
          <div className="mb-8">
            <h1 className="font-display text-3xl font-bold mb-2">
              Admin <span className="text-gradient">Dashboard</span>
            </h1>
            <p className="text-muted-foreground">
              Model management and human-in-the-loop controls
            </p>
          </div>

          {/* Disabled Notice */}
          <div className="glass-card glow-border p-8 mb-10 border border-destructive/30">
            <div className="flex items-start gap-4">
              <AlertTriangle className="w-6 h-6 text-destructive mt-1" />
              <div>
                <h2 className="font-semibold text-lg mb-2">
                  Admin Features Temporarily Disabled
                </h2>
                <p className="text-sm text-muted-foreground mb-4">
                  This dashboard was originally connected to Lovable AI / Supabase
                  for feedback verification and model retraining.
                  <br /><br />
                  The project has now been fully migrated to a custom FastAPI backend.
                  Admin and training workflows will be re-introduced in a future release.
                </p>

                <div className="flex flex-wrap gap-3">
                  <Button variant="outline" disabled className="gap-2">
                    <Lock className="w-4 h-4" />
                    Feedback Review
                  </Button>
                  <Button variant="outline" disabled className="gap-2">
                    <Database className="w-4 h-4" />
                    Training Control
                  </Button>
                  <Button variant="outline" disabled className="gap-2">
                    <Shield className="w-4 h-4" />
                    Model Versioning
                  </Button>
                </div>
              </div>
            </div>
          </div>

          {/* Documentation / Roadmap */}
          <div className="glass-card p-6 border border-border/50">
            <h3 className="font-display font-semibold mb-4">
              Planned Admin Capabilities
            </h3>

            <div className="grid md:grid-cols-3 gap-4 text-sm">
              <div className="p-4 rounded-lg bg-muted/30">
                <div className="font-medium mb-1">Feedback Review</div>
                <p className="text-muted-foreground">
                  Review user-flagged predictions and verify corrections.
                </p>
              </div>

              <div className="p-4 rounded-lg bg-muted/30">
                <div className="font-medium mb-1">Model Retraining</div>
                <p className="text-muted-foreground">
                  Batch retraining based on verified human feedback.
                </p>
              </div>

              <div className="p-4 rounded-lg bg-muted/30">
                <div className="font-medium mb-1">Version Management</div>
                <p className="text-muted-foreground">
                  Track deployed model versions and performance metrics.
                </p>
              </div>
            </div>

            <p className="text-xs text-muted-foreground mt-6">
              These features will be enabled once a dedicated admin backend
              and authentication layer are implemented.
            </p>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default AdminDashboard;
