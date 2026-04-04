import { forwardRef } from "react";
import { Shield, Github, Twitter, Mail } from "lucide-react";

interface FooterProps {
  onNavigate?: (page: string) => void;
}

export const Footer = forwardRef<HTMLElement, FooterProps>(({ onNavigate }, ref) => {
  const handleNavClick = (page: string) => (e: React.MouseEvent) => {
    e.preventDefault();
    onNavigate?.(page);
  };

  return (
    <footer ref={ref} className="border-t border-border/30 py-12 mt-auto">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 mb-8">
          {/* Brand */}
          <div className="lg:col-span-2">
            <div className="flex items-center gap-3 mb-4">
              <Shield className="w-6 h-6 text-primary" />
              <span className="font-display font-bold text-lg">
                Deep<span className="text-gradient">Guard</span>
              </span>
            </div>
            <p className="text-muted-foreground text-sm max-w-md">
              AI-powered deepfake detection to help you verify the authenticity 
              of digital media. Protect yourself from misinformation.
            </p>
          </div>

          {/* Links */}
          <div>
            <h4 className="font-display font-semibold mb-4">Product</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <button 
                  onClick={handleNavClick("home")} 
                  className="hover:text-foreground transition-colors text-left"
                >
                  Features
                </button>
              </li>
              <li>
                <button 
                  onClick={handleNavClick("analyze")} 
                  className="hover:text-foreground transition-colors text-left"
                >
                  Analyze Media
                </button>
              </li>
              <li>
                <button 
                  onClick={handleNavClick("history")} 
                  className="hover:text-foreground transition-colors text-left"
                >
                  History
                </button>
              </li>
              <li>
                <button 
                  onClick={handleNavClick("about")} 
                  className="hover:text-foreground transition-colors text-left"
                >
                  Documentation
                </button>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="font-display font-semibold mb-4">Company</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <button 
                  onClick={handleNavClick("about")} 
                  className="hover:text-foreground transition-colors text-left"
                >
                  About
                </button>
              </li>
              <li>
                <button 
                  onClick={handleNavClick("about")} 
                  className="hover:text-foreground transition-colors text-left"
                >
                  Blog
                </button>
              </li>
              <li>
                <button 
                  onClick={handleNavClick("about")} 
                  className="hover:text-foreground transition-colors text-left"
                >
                  Privacy Policy
                </button>
              </li>
              <li>
                <button 
                  onClick={handleNavClick("about")} 
                  className="hover:text-foreground transition-colors text-left"
                >
                  Terms of Service
                </button>
              </li>
            </ul>
          </div>
          
          {/* Contact */}
          <div>
            <h4 className="font-display font-semibold mb-4">Contact Details</h4>
            <ul className="space-y-3 text-sm text-muted-foreground">
              <li className="flex flex-col gap-1">
                <span className="text-foreground font-medium">Email</span>
                <a href="mailto:morlakhamlesh@gmail.com" className="hover:text-primary transition-colors">
                  morlakhamlesh@gmail.com
                </a>
              </li>
              <li className="flex flex-col gap-1">
                <span className="text-foreground font-medium">Phone</span>
                <a href="tel:+919182056492" className="hover:text-primary transition-colors">
                  +91-9182056492
                </a>
              </li>
              <li className="flex flex-col gap-1">
                <span className="text-foreground font-medium">Location</span>
                <span>Hyper-Secure Server Facility, Global</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom */}
        <div className="flex flex-col md:flex-row items-center justify-between pt-8 border-t border-border/30">
          <p className="text-sm text-muted-foreground mb-4 md:mb-0">
            © 2026 DeepGuard. All rights reserved.
          </p>
          <div className="flex items-center gap-4">
            <a 
              href="https://github.com/khamleshmorla" 
              target="_blank" 
              rel="noopener noreferrer" 
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              <Github className="w-5 h-5" />
            </a>
            <a 
              href="https://twitter.com" 
              target="_blank" 
              rel="noopener noreferrer" 
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              <Twitter className="w-5 h-5" />
            </a>
            <a 
              href="mailto:morlakhamlesh@gmail.com" 
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              <Mail className="w-5 h-5" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
});

Footer.displayName = "Footer";
