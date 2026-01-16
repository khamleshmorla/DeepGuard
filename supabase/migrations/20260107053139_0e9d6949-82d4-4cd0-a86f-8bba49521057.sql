-- Create table for analysis history
CREATE TABLE public.analysis_history (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID,
  file_name TEXT NOT NULL,
  file_type TEXT NOT NULL CHECK (file_type IN ('image', 'video')),
  verdict TEXT NOT NULL CHECK (verdict IN ('REAL', 'FAKE')),
  confidence INTEGER NOT NULL CHECK (confidence >= 0 AND confidence <= 100),
  facial_analysis INTEGER CHECK (facial_analysis >= 0 AND facial_analysis <= 100),
  temporal_consistency INTEGER CHECK (temporal_consistency >= 0 AND temporal_consistency <= 100),
  artifact_detection INTEGER CHECK (artifact_detection >= 0 AND artifact_detection <= 100),
  metadata_analysis INTEGER CHECK (metadata_analysis >= 0 AND metadata_analysis <= 100),
  ai_explanation TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.analysis_history ENABLE ROW LEVEL SECURITY;

-- Allow public read/write for now (no auth required)
CREATE POLICY "Allow public insert" ON public.analysis_history FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public select" ON public.analysis_history FOR SELECT USING (true);

-- Create index for faster queries
CREATE INDEX idx_analysis_history_created_at ON public.analysis_history(created_at DESC);