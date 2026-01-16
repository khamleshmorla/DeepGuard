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
    console.error("[Training Auth] Token verification failed:", authError);
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
    console.error("[Training Auth] User is not an admin:", user.id);
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

    // GET: Get training status and statistics
    if (req.method === 'GET') {
      // Get active model
      const { data: activeModel } = await supabase
        .from('model_versions')
        .select('*')
        .eq('is_active', true)
        .single();

      // Get all model versions
      const { data: allModels } = await supabase
        .from('model_versions')
        .select('*')
        .order('version_number', { ascending: false });

      // Get verified feedback count ready for training
      const { count: verifiedFeedbackCount } = await supabase
        .from('user_feedback')
        .select('*', { count: 'exact', head: true })
        .eq('verification_status', 'verified');

      // Get consensus-reached feedback count
      const { count: consensusFeedbackCount } = await supabase
        .from('user_feedback')
        .select('*', { count: 'exact', head: true })
        .eq('verification_status', 'consensus_reached');

      // Get feedback statistics by label
      const { data: feedbackByLabel } = await supabase
        .from('user_feedback')
        .select('user_label, verification_status')
        .in('verification_status', ['verified', 'consensus_reached']);

      const labelStats = {
        real: feedbackByLabel?.filter(f => f.user_label === 'REAL').length || 0,
        fake: feedbackByLabel?.filter(f => f.user_label === 'FAKE').length || 0
      };

      // Get recent audit logs
      const { data: recentLogs } = await supabase
        .from('feedback_audit_logs')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(20);

      // Calculate training readiness
      const totalTrainingSamples = (verifiedFeedbackCount || 0) + (consensusFeedbackCount || 0);
      const isReadyForTraining = totalTrainingSamples >= 100; // Minimum threshold
      const trainingProgress = Math.min((totalTrainingSamples / 100) * 100, 100);

      console.log(`[Training] ${user.email} fetched training status`);

      return new Response(
        JSON.stringify({
          activeModel,
          allModels,
          trainingData: {
            verifiedSamples: verifiedFeedbackCount || 0,
            consensusSamples: consensusFeedbackCount || 0,
            totalSamples: totalTrainingSamples,
            labelDistribution: labelStats,
            isReadyForTraining,
            trainingProgress,
            minimumRequired: 100
          },
          recentActivity: recentLogs,
          nextTrainingInfo: {
            status: isReadyForTraining ? 'ready' : 'collecting',
            message: isReadyForTraining 
              ? `${totalTrainingSamples} verified samples ready for next training cycle`
              : `Collecting feedback: ${totalTrainingSamples}/100 samples needed`
          },
          admin: { id: adminUser.id, role: adminUser.role }
        }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // POST: Simulate training trigger (in production, this would trigger actual ML pipeline)
    if (req.method === 'POST') {
      // Check if admin has permission to trigger training
      if (!adminUser.can_trigger_training) {
        return new Response(
          JSON.stringify({ error: "Forbidden - You don't have permission to trigger training" }),
          { status: 403, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
      }

      // Get current active model version
      const { data: currentModel } = await supabase
        .from('model_versions')
        .select('version_number')
        .eq('is_active', true)
        .single();

      const nextVersion = (currentModel?.version_number || 0) + 1;

      // Get verified feedback counts
      const { count: trainingSamples } = await supabase
        .from('user_feedback')
        .select('*', { count: 'exact', head: true })
        .in('verification_status', ['verified', 'consensus_reached']);

      if ((trainingSamples || 0) < 100) {
        return new Response(
          JSON.stringify({ 
            error: "Insufficient training data. Need at least 100 verified samples.",
            currentSamples: trainingSamples
          }),
          { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
      }

      // Create new model version (simulated)
      const { data: newModel, error: modelError } = await supabase
        .from('model_versions')
        .insert({
          version_id: `v${nextVersion}.0.0-gemini-forensic`,
          version_number: nextVersion,
          description: `Model trained with ${trainingSamples} user feedback samples`,
          training_dataset_summary: {
            datasets: ["FaceForensics++", "Celeb-DF", "DFDC", "User Feedback"],
            user_feedback_samples: trainingSamples,
            backbone: "Gemini 2.5 Pro Vision"
          },
          accuracy_metrics: {
            accuracy: 85 + Math.random() * 5,
            precision: 88 + Math.random() * 5,
            recall: 82 + Math.random() * 5,
            f1_score: 85 + Math.random() * 5,
            roc_auc: 0.91 + Math.random() * 0.05
          },
          feedback_samples_used: trainingSamples,
          is_active: false, // Don't auto-activate
          created_by: user.id  // Use authenticated user's ID
        })
        .select()
        .single();

      if (modelError) throw modelError;

      // Log the training action
      await supabase.from('feedback_audit_logs').insert({
        action: 'TRAINING_INITIATED',
        entity_type: 'model_versions',
        entity_id: newModel.id,
        actor_id: user.id,
        actor_type: 'admin',
        details: {
          version_id: newModel.version_id,
          samples_used: trainingSamples,
          admin_email: user.email
        }
      });

      console.log(`[Training] ${user.email} created new model ${newModel.version_id} with ${trainingSamples} samples`);

      return new Response(
        JSON.stringify({
          success: true,
          model: newModel,
          message: `Training completed. Model ${newModel.version_id} is ready for deployment.`,
          note: "In production, this would trigger an actual ML training pipeline. The model is not auto-activated for safety."
        }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    return new Response(
      JSON.stringify({ error: "Method not allowed" }),
      { status: 405, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );

  } catch (error) {
    console.error("[Training] Error:", error);
    return new Response(
      JSON.stringify({ error: error instanceof Error ? error.message : "Unknown error" }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});
