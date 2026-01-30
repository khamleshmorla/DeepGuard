import { useState, useRef, useCallback, useEffect } from "react";
import { Upload, FileVideo, FileImage, X, Play } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

interface UploadZoneProps {
  onFileSelect: (file: File) => void;
  isAnalyzing: boolean;
}

export function UploadZone({ onFileSelect, isAnalyzing }: UploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [videoThumbnail, setVideoThumbnail] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const file = e.dataTransfer.files[0];
    if (file) {
      if (isValidFileType(file)) {
        handleFileSelected(file);
      } else {
        toast.error('Unsupported file format', {
          description: 'Please upload JPG, PNG, WebP, MP4, WebM, or MOV files.'
        });
      }
    }
  }, []);

  const isValidFileType = (file: File): boolean => {
    const validTypes = [
      'image/jpeg',
      'image/png',
      'image/webp',
      'video/mp4',
      'video/webm',
      'video/quicktime' // MOV files
    ];
    // Also check file extension for MOV files that may not have correct MIME type
    const fileName = file.name.toLowerCase();
    if (fileName.endsWith('.mov')) return true;
    return validTypes.includes(file.type);
  };

  const generateVideoThumbnail = async (file: File): Promise<string | null> => {
    return new Promise((resolve) => {
      const video = document.createElement('video');
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');

      video.preload = 'metadata';
      video.muted = true;
      video.playsInline = true;

      const cleanup = () => {
        URL.revokeObjectURL(video.src);
      };

      video.onloadeddata = () => {
        video.currentTime = Math.min(0.5, video.duration * 0.1);
      };

      video.onseeked = () => {
        if (!ctx) {
          cleanup();
          resolve(null);
          return;
        }
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0);
        const thumbnail = canvas.toDataURL('image/jpeg', 0.7);
        cleanup();
        resolve(thumbnail);
      };

      video.onerror = () => {
        cleanup();
        resolve(null);
      };

      // Timeout fallback
      const timeout = setTimeout(() => {
        cleanup();
        resolve(null);
      }, 5000);

      video.onloadedmetadata = () => {
        clearTimeout(timeout);
      };

      video.src = URL.createObjectURL(file);
      video.load();
    });
  };

  const handleFileSelected = async (file: File) => {
    setSelectedFile(file);
    setVideoThumbnail(null);

    // Create preview
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    } else if (file.type.startsWith('video/') || file.name.toLowerCase().endsWith('.mov')) {
      setPreview(null);
      // Generate video thumbnail
      const thumbnail = await generateVideoThumbnail(file);
      setVideoThumbnail(thumbnail);
    } else {
      setPreview(null);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (isValidFileType(file)) {
        handleFileSelected(file);
      } else {
        toast.error('Unsupported file format', {
          description: 'Please upload JPG, PNG, WebP, MP4, WebM, or MOV files.'
        });
      }
    }
    // Reset input value to allow selecting the same file again if needed
    if (e.target) {
      e.target.value = '';
    }
  };

  const handleStartAnalysis = () => {
    if (selectedFile) {
      onFileSelect(selectedFile);
    }
  };

  const handleClear = () => {
    setSelectedFile(null);
    setPreview(null);
    setVideoThumbnail(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(1)} KB`;
    }
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  // Enable "Enter" key to start analysis
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Enter" && selectedFile && !isAnalyzing) {
        handleStartAnalysis();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [selectedFile, isAnalyzing, onFileSelect]);

  const isVideo = selectedFile && (
    selectedFile.type.startsWith('video/') ||
    selectedFile.name.toLowerCase().endsWith('.mov')
  );

  return (
    <div className="w-full max-w-2xl mx-auto">
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp,video/mp4,video/webm,video/quicktime,.mov"
        onChange={handleInputChange}
        className="hidden"
      />

      {!selectedFile ? (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={cn(
            "upload-zone cursor-pointer min-h-[300px] flex flex-col items-center justify-center gap-4",
            isDragging && "dragging"
          )}
        >
          <div className="w-20 h-20 rounded-2xl bg-primary/10 flex items-center justify-center">
            <Upload className="w-10 h-10 text-primary" />
          </div>

          <div className="text-center">
            <p className="font-display font-semibold text-lg mb-2">
              Drop your file here
            </p>
            <p className="text-muted-foreground text-sm mb-4">
              or click to browse
            </p>
            <div className="flex items-center justify-center gap-4 text-xs text-muted-foreground">
              <span className="flex items-center gap-1">
                <FileImage className="w-4 h-4" />
                JPG, PNG, WebP
              </span>
              <span className="flex items-center gap-1">
                <FileVideo className="w-4 h-4" />
                MP4, WebM, MOV
              </span>
            </div>
          </div>
        </div>
      ) : (
        <div className="glass-card glow-border p-6">
          {/* Preview */}
          <div className="relative mb-6">
            {preview ? (
              <div className="relative rounded-lg overflow-hidden">
                <img
                  src={preview}
                  alt="Preview"
                  className="w-full h-64 object-contain bg-background/50"
                />
                {isAnalyzing && (
                  <div className="absolute inset-0 bg-background/80 flex items-center justify-center">
                    <div className="scan-line" />
                  </div>
                )}
              </div>
            ) : videoThumbnail ? (
              <div className="relative rounded-lg overflow-hidden">
                <img
                  src={videoThumbnail}
                  alt="Video thumbnail"
                  className="w-full h-64 object-contain bg-background/50"
                />
                {!isAnalyzing && (
                  <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <div className="w-16 h-16 rounded-full bg-primary/80 flex items-center justify-center">
                      <Play className="w-8 h-8 text-primary-foreground ml-1" />
                    </div>
                  </div>
                )}
                {isAnalyzing && (
                  <div className="absolute inset-0 bg-background/80 flex items-center justify-center">
                    <div className="text-center">
                      <div className="scan-line mb-4" />
                      <p className="text-sm text-muted-foreground">Extracting frames...</p>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="h-64 rounded-lg bg-muted flex flex-col items-center justify-center gap-2">
                <FileVideo className="w-16 h-16 text-muted-foreground" />
                {isVideo && (
                  <p className="text-xs text-muted-foreground">Video ready for analysis</p>
                )}
                {isAnalyzing && (
                  <div className="absolute inset-0 bg-background/80 flex items-center justify-center rounded-lg">
                    <div className="text-center">
                      <div className="w-8 h-8 border-2 border-primary/30 border-t-primary rounded-full animate-spin mx-auto mb-2" />
                      <p className="text-sm text-muted-foreground">Extracting frames...</p>
                    </div>
                  </div>
                )}
              </div>
            )}

            {!isAnalyzing && (
              <button
                onClick={handleClear}
                className="absolute top-2 right-2 p-2 rounded-lg bg-background/80 hover:bg-background transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* File Info */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <p className="font-medium truncate max-w-[300px]">{selectedFile.name}</p>
              <p className="text-sm text-muted-foreground">
                {formatFileSize(selectedFile.size)}
                {isVideo && <span className="ml-2">• Video file</span>}
              </p>
            </div>
            <div className="flex items-center gap-2">
              {isVideo ? (
                <FileVideo className="w-5 h-5 text-primary" />
              ) : (
                <FileImage className="w-5 h-5 text-primary" />
              )}
            </div>
          </div>

          {/* Action Button */}
          <Button
            variant="glow"
            size="lg"
            className="w-full"
            onClick={handleStartAnalysis}
            disabled={isAnalyzing}
          >
            {isAnalyzing ? (
              <>
                <div className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
                {isVideo ? 'Analyzing Video...' : 'Analyzing...'}
              </>
            ) : (
              <>
                <Upload className="w-4 h-4" />
                Start Analysis
              </>
            )}
          </Button>

          {/* Video analysis note */}
          {isVideo && !isAnalyzing && (
            <p className="text-xs text-muted-foreground text-center mt-3">
              Video analysis extracts multiple frames for comprehensive detection
            </p>
          )}
        </div>
      )}
    </div>
  );
}
