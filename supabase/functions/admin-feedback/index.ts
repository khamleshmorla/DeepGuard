import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

/**
 * Validates the authorization header and returns the authenticated user.
 * Also verifies the user has admin privileges.
 */
async function validateAdminAuth(req: Request, supabase: any): Promise<{ user: any; adminUser: any } | Response> {
  const authHeader = req.headers.get('Authorization');
  
  if (!authHeader) {
    return new Response(
      JSON.stringify({ error: "Unauthorized - No authorization header" }),
      { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }

  const token = authHeader.replace('Bearer ', '');
  
  // Verify the JWT token and get user
  const { data: { user }, error: authError } = await supabase.auth.getUser(token);
  
  if (authError || !user) {
    console.error("[Admin Auth] Token verification failed:", authError);
    return new Response(
      JSON.stringify({ error: "Unauthorized - Invalid token" }),
      { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }

  // Check if user is an admin
  const { data: adminUser, error: adminError } = await supabase
    .from('admin_users')
    .select('id, role, can_verify_feedback, can_trigger_training, can_deploy_models')
    .eq('user_id', user.id)
    .single();

  if (adminError || !adminUser) {
    console.error("[Admin Auth] User is not an admin:", user.id);
    return new Response(
      JSON.stringify({ error: "Forbidden - Admin access required" }),
      { status: 403, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }

  return { user, adminUser };
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    // Validate admin authentication
    const authResult = await validateAdminAuth(req, supabase);
    if (authResult instanceof Response) {
      return authResult;
    }
    const { user, adminUser } = authResult;

    const url = new URL(req.url);

    // GET: Fetch pending feedback for review
    if (req.method === 'GET') {
      const status = url.searchParams.get('status') || 'pending';
      const limit = parseInt(url.searchParams.get('limit') || '50');

      const { data: feedbackList, error } = await supabase
        .from('user_feedback')
        .select(`
          *,
          analysis_history:analysis_id (
            file_name,
            file_type,
            verdict,
            confidence,
            ai_explanation
          )
        `)
        .eq('verification_status', status)
        .order('created_at', { ascending: false })
        .limit(limit);

      if (error) throw error;

      // Get feedback statistics
      const { data: stats } = await supabase
        .from('user_feedback')
        .select('verification_status')
        .then(({ data }) => {
          const counts = {
            pending: 0,
            verified: 0,
            rejected: 0,
            consensus_reached: 0,
            total: data?.length || 0
          };
          data?.forEach(item => {
            counts[item.verification_status as keyof typeof counts]++;
          });
          return { data: counts };
        });

      // Get model versions
      const { data: models } = await supabase
        .from('model_versions')
        .select('*')
        .order('version_number', { ascending: false });

      console.log(`[Admin] ${user.email} fetched ${feedbackList?.length || 0} ${status} feedback items`);

      return new Response(
        JSON.stringify({
          feedback: feedbackList,
          statistics: stats,
          models: models,
          admin: { id: adminUser.id, role: adminUser.role }
        }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // POST: Verify or reject feedback
    if (req.method === 'POST') {
      // Check if admin has permission to verify feedback
      if (!adminUser.can_verify_feedback) {
        return new Response(
          JSON.stringify({ error: "Forbidden - You don't have permission to verify feedback" }),
          { status: 403, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
      }

      const { feedbackId, action: feedbackAction, reason } = await req.json();

      if (!feedbackId || !feedbackAction) {
        return new Response(
          JSON.stringify({ error: "Missing feedbackId or action" }),
          { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
      }

      if (!['verify', 'reject'].includes(feedbackAction)) {
        return new Response(
          JSON.stringify({ error: "Invalid action. Use 'verify' or 'reject'" }),
          { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
      }

      const newStatus = feedbackAction === 'verify' ? 'verified' : 'rejected';

      const { data: updatedFeedback, error: updateError } = await supabase
        .from('user_feedback')
        .update({
          verification_status: newStatus,
          verified_by: user.id,  // Use authenticated user's ID
          verified_at: new Date().toISOString()
        })
        .eq('id', feedbackId)
        .select()
        .single();

      if (updateError) throw updateError;

      // Log the admin action
      await supabase.from('feedback_audit_logs').insert({
        action: feedbackAction === 'verify' ? 'FEEDBACK_VERIFIED' : 'FEEDBACK_REJECTED',
        entity_type: 'user_feedback',
        entity_id: feedbackId,
        actor_id: user.id,
        actor_type: 'admin',
        details: {
          new_status: newStatus,
          reason: reason || null,
          admin_email: user.email
        }
      });

      console.log(`[Admin] ${user.email} ${feedbackAction}ed feedback ${feedbackId}`);

      return new Response(
        JSON.stringify({
          success: true,
          feedback: updatedFeedback,
          message: `Feedback ${feedbackAction === 'verify' ? 'verified' : 'rejected'} successfully`
        }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    return new Response(
      JSON.stringify({ error: "Method not allowed" }),
      { status: 405, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );

  } catch (error) {
    console.error("[Admin] Error:", error);
    return new Response(
      JSON.stringify({ error: error instanceof Error ? error.message : "Unknown error" }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});
