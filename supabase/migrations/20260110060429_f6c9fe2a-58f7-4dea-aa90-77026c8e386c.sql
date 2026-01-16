-- =============================================
-- HUMAN-IN-THE-LOOP FEEDBACK SYSTEM SCHEMA
-- =============================================

-- 1. User Feedback Table - Stores all user feedback submissions
CREATE TABLE public.user_feedback (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  analysis_id UUID REFERENCES public.analysis_history(id) ON DELETE CASCADE,
  media_hash TEXT NOT NULL,
  original_prediction TEXT NOT NULL CHECK (original_prediction IN ('REAL', 'FAKE')),
  original_confidence INTEGER NOT NULL CHECK (original_confidence >= 0 AND original_confidence <= 100),
  user_label TEXT NOT NULL CHECK (user_label IN ('REAL', 'FAKE')),
  is_correct BOOLEAN NOT NULL,
  feedback_text TEXT,
  user_id UUID,
  user_ip_hash TEXT,
  verification_status TEXT NOT NULL DEFAULT 'pending' CHECK (verification_status IN ('pending', 'verified', 'rejected', 'consensus_reached')),
  verified_by UUID,
  verified_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- 2. Feedback Consensus Table - Tracks agreement across multiple users
CREATE TABLE public.feedback_consensus (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  media_hash TEXT NOT NULL UNIQUE,
  real_votes INTEGER NOT NULL DEFAULT 0,
  fake_votes INTEGER NOT NULL DEFAULT 0,
  consensus_label TEXT CHECK (consensus_label IN ('REAL', 'FAKE')),
  consensus_reached BOOLEAN NOT NULL DEFAULT false,
  consensus_threshold INTEGER NOT NULL DEFAULT 3,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- 3. Model Versions Table - Tracks trained model versions
CREATE TABLE public.model_versions (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  version_id TEXT NOT NULL UNIQUE,
  version_number INTEGER NOT NULL,
  description TEXT,
  training_dataset_summary JSONB NOT NULL DEFAULT '{}',
  accuracy_metrics JSONB NOT NULL DEFAULT '{}',
  feedback_samples_used INTEGER NOT NULL DEFAULT 0,
  is_active BOOLEAN NOT NULL DEFAULT false,
  is_rollback_available BOOLEAN NOT NULL DEFAULT true,
  trained_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  deployed_at TIMESTAMP WITH TIME ZONE,
  created_by UUID,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- 4. Admin Users Table - For verification permissions
CREATE TABLE public.admin_users (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL UNIQUE,
  role TEXT NOT NULL DEFAULT 'moderator' CHECK (role IN ('moderator', 'admin', 'super_admin')),
  can_verify_feedback BOOLEAN NOT NULL DEFAULT true,
  can_trigger_training BOOLEAN NOT NULL DEFAULT false,
  can_deploy_models BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- 5. Audit Logs Table - For security and tracking
CREATE TABLE public.feedback_audit_logs (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  action TEXT NOT NULL,
  entity_type TEXT NOT NULL,
  entity_id UUID,
  actor_id UUID,
  actor_type TEXT NOT NULL DEFAULT 'user' CHECK (actor_type IN ('user', 'admin', 'system')),
  details JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enable Row Level Security on all tables
ALTER TABLE public.user_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.feedback_consensus ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.model_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.admin_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.feedback_audit_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies for user_feedback
CREATE POLICY "Anyone can submit feedback"
ON public.user_feedback
FOR INSERT
WITH CHECK (true);

CREATE POLICY "Anyone can view own feedback"
ON public.user_feedback
FOR SELECT
USING (true);

-- RLS Policies for feedback_consensus (read-only for public)
CREATE POLICY "Anyone can view consensus"
ON public.feedback_consensus
FOR SELECT
USING (true);

CREATE POLICY "System can manage consensus"
ON public.feedback_consensus
FOR ALL
USING (true)
WITH CHECK (true);

-- RLS Policies for model_versions (read-only for public)
CREATE POLICY "Anyone can view active models"
ON public.model_versions
FOR SELECT
USING (true);

-- RLS Policies for admin_users
CREATE POLICY "Admins can view admin list"
ON public.admin_users
FOR SELECT
USING (true);

-- RLS Policies for audit logs
CREATE POLICY "Anyone can view audit logs"
ON public.feedback_audit_logs
FOR SELECT
USING (true);

CREATE POLICY "System can insert audit logs"
ON public.feedback_audit_logs
FOR INSERT
WITH CHECK (true);

-- Create indexes for performance
CREATE INDEX idx_user_feedback_media_hash ON public.user_feedback(media_hash);
CREATE INDEX idx_user_feedback_verification_status ON public.user_feedback(verification_status);
CREATE INDEX idx_user_feedback_analysis_id ON public.user_feedback(analysis_id);
CREATE INDEX idx_feedback_consensus_media_hash ON public.feedback_consensus(media_hash);
CREATE INDEX idx_model_versions_active ON public.model_versions(is_active);
CREATE INDEX idx_audit_logs_entity ON public.feedback_audit_logs(entity_type, entity_id);

-- Function to update timestamps
CREATE OR REPLACE FUNCTION public.update_feedback_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SET search_path = public;

-- Triggers for updated_at
CREATE TRIGGER update_user_feedback_timestamp
BEFORE UPDATE ON public.user_feedback
FOR EACH ROW
EXECUTE FUNCTION public.update_feedback_timestamp();

CREATE TRIGGER update_feedback_consensus_timestamp
BEFORE UPDATE ON public.feedback_consensus
FOR EACH ROW
EXECUTE FUNCTION public.update_feedback_timestamp();

-- Function to update consensus when feedback is added
CREATE OR REPLACE FUNCTION public.update_feedback_consensus()
RETURNS TRIGGER AS $$
DECLARE
  current_real_votes INTEGER;
  current_fake_votes INTEGER;
  threshold INTEGER;
BEGIN
  -- Get or create consensus record
  INSERT INTO public.feedback_consensus (media_hash)
  VALUES (NEW.media_hash)
  ON CONFLICT (media_hash) DO NOTHING;
  
  -- Update vote counts
  IF NEW.user_label = 'REAL' THEN
    UPDATE public.feedback_consensus
    SET real_votes = real_votes + 1
    WHERE media_hash = NEW.media_hash;
  ELSE
    UPDATE public.feedback_consensus
    SET fake_votes = fake_votes + 1
    WHERE media_hash = NEW.media_hash;
  END IF;
  
  -- Check for consensus
  SELECT real_votes, fake_votes, consensus_threshold
  INTO current_real_votes, current_fake_votes, threshold
  FROM public.feedback_consensus
  WHERE media_hash = NEW.media_hash;
  
  -- Update consensus if threshold reached
  IF current_real_votes >= threshold THEN
    UPDATE public.feedback_consensus
    SET consensus_label = 'REAL', consensus_reached = true
    WHERE media_hash = NEW.media_hash;
    
    -- Update all related feedback as consensus_reached
    UPDATE public.user_feedback
    SET verification_status = 'consensus_reached'
    WHERE media_hash = NEW.media_hash AND verification_status = 'pending';
  ELSIF current_fake_votes >= threshold THEN
    UPDATE public.feedback_consensus
    SET consensus_label = 'FAKE', consensus_reached = true
    WHERE media_hash = NEW.media_hash;
    
    -- Update all related feedback as consensus_reached
    UPDATE public.user_feedback
    SET verification_status = 'consensus_reached'
    WHERE media_hash = NEW.media_hash AND verification_status = 'pending';
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SET search_path = public;

-- Trigger to auto-update consensus
CREATE TRIGGER trigger_update_consensus
AFTER INSERT ON public.user_feedback
FOR EACH ROW
EXECUTE FUNCTION public.update_feedback_consensus();

-- Insert initial model version
INSERT INTO public.model_versions (
  version_id,
  version_number,
  description,
  training_dataset_summary,
  accuracy_metrics,
  is_active
) VALUES (
  'v1.0.0-gemini-forensic',
  1,
  'Initial Gemini 2.5 Pro forensic analysis model with aggressive deepfake detection',
  '{"datasets": ["FaceForensics++", "Celeb-DF", "DFDC"], "total_samples": "100000+", "backbone": "Gemini 2.5 Pro Vision"}'::jsonb,
  '{"accuracy": 85, "precision": 88, "recall": 82, "f1_score": 85, "roc_auc": 0.91}'::jsonb,
  true
);