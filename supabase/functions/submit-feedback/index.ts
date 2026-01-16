import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

// Simple hash function for media identification
function simpleHash(str: string): string {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return Math.abs(hash).toString(16);
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    const {
      analysisId,
      fileName,
      originalPrediction,
      originalConfidence,
      userLabel,
      isCorrect,
      feedbackText,
      userId
    } = await req.json();

    // Validate required fields
    if (!fileName || !originalPrediction || !userLabel) {
      return new Response(
        JSON.stringify({ error: "Missing required fields" }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Validate prediction values
    if (!['REAL', 'FAKE'].includes(originalPrediction) || !['REAL', 'FAKE'].includes(userLabel)) {
      return new Response(
        JSON.stringify({ error: "Invalid prediction or label value" }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Generate media hash for duplicate detection and consensus tracking
    const mediaHash = simpleHash(fileName + originalPrediction + originalConfidence);

    // Get IP hash for rate limiting (privacy-preserving)
    const clientIP = req.headers.get('x-forwarded-for') || req.headers.get('cf-connecting-ip') || 'unknown';
    const ipHash = simpleHash(clientIP);

    // Check for duplicate feedback from same IP on same media
    const { data: existingFeedback } = await supabase
      .from('user_feedback')
      .select('id')
      .eq('media_hash', mediaHash)
      .eq('user_ip_hash', ipHash)
      .limit(1);

    if (existingFeedback && existingFeedback.length > 0) {
      return new Response(
        JSON.stringify({ 
          error: "You have already submitted feedback for this analysis",
          alreadySubmitted: true 
        }),
        { status: 409, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Insert feedback
    const { data: feedback, error: feedbackError } = await supabase
      .from('user_feedback')
      .insert({
        analysis_id: analysisId || null,
        media_hash: mediaHash,
        original_prediction: originalPrediction,
        original_confidence: originalConfidence,
        user_label: userLabel,
        is_correct: isCorrect,
        feedback_text: feedbackText || null,
        user_id: userId || null,
        user_ip_hash: ipHash,
        verification_status: 'pending'
      })
      .select()
      .single();

    if (feedbackError) {
      console.error("[Feedback] Database error:", feedbackError);
      throw new Error("Failed to save feedback");
    }

    // Log the action for audit
    await supabase.from('feedback_audit_logs').insert({
      action: 'FEEDBACK_SUBMITTED',
      entity_type: 'user_feedback',
      entity_id: feedback.id,
      actor_id: userId || null,
      actor_type: userId ? 'user' : 'user',
      details: {
        media_hash: mediaHash,
        original_prediction: originalPrediction,
        user_label: userLabel,
        is_correct: isCorrect
      }
    });

    // Check current consensus status
    const { data: consensus } = await supabase
      .from('feedback_consensus')
      .select('*')
      .eq('media_hash', mediaHash)
      .single();

    console.log(`[Feedback] Submitted: ${isCorrect ? 'Correct' : 'Incorrect'} - User says: ${userLabel}`);

    return new Response(
      JSON.stringify({
        success: true,
        feedbackId: feedback.id,
        message: "Thank you for your feedback! Your input helps improve our detection accuracy.",
        consensusStatus: consensus ? {
          realVotes: consensus.real_votes,
          fakeVotes: consensus.fake_votes,
          consensusReached: consensus.consensus_reached,
          consensusLabel: consensus.consensus_label
        } : null
      }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );

  } catch (error) {
    console.error("[Feedback] Error:", error);
    return new Response(
      JSON.stringify({ error: error instanceof Error ? error.message : "Unknown error" }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});
