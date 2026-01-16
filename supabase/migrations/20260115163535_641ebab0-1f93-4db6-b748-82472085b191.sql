-- Create app_role enum if not exists
DO $$ BEGIN
  CREATE TYPE public.app_role AS ENUM ('admin', 'moderator', 'user');
EXCEPTION
  WHEN duplicate_object THEN null;
END $$;

-- Create user_roles table for proper role management
CREATE TABLE IF NOT EXISTS public.user_roles (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  role app_role NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  UNIQUE (user_id, role)
);

ALTER TABLE public.user_roles ENABLE ROW LEVEL SECURITY;

-- Create security definer function to check roles (prevents RLS recursion)
CREATE OR REPLACE FUNCTION public.has_role(_user_id uuid, _role app_role)
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT EXISTS (
    SELECT 1
    FROM public.user_roles
    WHERE user_id = _user_id
      AND role = _role
  )
$$;

-- Create function to check if user is admin (using admin_users table for backward compat)
CREATE OR REPLACE FUNCTION public.is_admin(_user_id uuid)
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT EXISTS (
    SELECT 1
    FROM public.admin_users
    WHERE user_id = _user_id
  )
$$;

-- RLS for user_roles table
CREATE POLICY "Users can view own roles"
ON public.user_roles FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Admins can manage roles"
ON public.user_roles FOR ALL
USING (public.is_admin(auth.uid()));

-- =====================================================
-- FIX: admin_users - Only admins can view admin list
-- =====================================================
DROP POLICY IF EXISTS "Admins can view admin list" ON public.admin_users;

CREATE POLICY "Admins can view admin list"
ON public.admin_users FOR SELECT
USING (public.is_admin(auth.uid()));

-- =====================================================
-- FIX: analysis_history - Users can only view their own
-- =====================================================
DROP POLICY IF EXISTS "Allow public select" ON public.analysis_history;

CREATE POLICY "Users view own analyses"
ON public.analysis_history FOR SELECT
USING (
  -- Allow viewing if user owns the record
  auth.uid() = user_id 
  -- OR if it's an anonymous analysis (null user_id) - for current session
  OR user_id IS NULL
  -- OR if user is admin
  OR public.is_admin(auth.uid())
);

-- =====================================================
-- FIX: user_feedback - Users can only view their own
-- =====================================================
DROP POLICY IF EXISTS "Anyone can view own feedback" ON public.user_feedback;

CREATE POLICY "Users view own feedback"
ON public.user_feedback FOR SELECT
USING (
  auth.uid() = user_id 
  OR public.is_admin(auth.uid())
);

-- =====================================================
-- FIX: feedback_audit_logs - Only admins can view
-- =====================================================
DROP POLICY IF EXISTS "Anyone can view audit logs" ON public.feedback_audit_logs;

CREATE POLICY "Admins view audit logs"
ON public.feedback_audit_logs FOR SELECT
USING (public.is_admin(auth.uid()));

-- =====================================================
-- FIX: model_versions - Public only sees active, admins see all
-- =====================================================
DROP POLICY IF EXISTS "Anyone can view active models" ON public.model_versions;

-- Create a public view that hides sensitive details
CREATE OR REPLACE VIEW public.model_versions_public
WITH (security_invoker = on) AS
SELECT 
  id,
  version_id,
  version_number,
  is_active,
  deployed_at,
  created_at
FROM public.model_versions
WHERE is_active = true;

-- Policy for base table - admins only
CREATE POLICY "Admins view all models"
ON public.model_versions FOR SELECT
USING (public.is_admin(auth.uid()));

-- Grant select on public view
GRANT SELECT ON public.model_versions_public TO anon, authenticated;

-- =====================================================
-- FIX: feedback_consensus - Keep public read (needed for UI)
-- =====================================================
-- This one can stay public as it only shows aggregated votes