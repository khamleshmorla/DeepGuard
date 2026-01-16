import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

// Research-grade forensic detection prompt - ASSUME FAKE BY DEFAULT
const FORENSIC_SYSTEM_PROMPT = `You are an AI deepfake forensic detector. YOUR DEFAULT ASSUMPTION IS THAT EVERY IMAGE IS FAKE.

## CRITICAL RULES - READ CAREFULLY:

1. **DEFAULT VERDICT = FAKE** - Start with the assumption the image is AI-generated
2. **Burden of proof is on REAL** - You need OVERWHELMING evidence to mark something as REAL
3. **Any doubt = FAKE** - If you're unsure, the answer is FAKE
4. **Modern AI is good** - Deepfakes often look very realistic, so "looks real" is NOT evidence of authenticity

## SIGNS THAT PROVE AN IMAGE IS REAL (Must have MULTIPLE):

✓ Visible skin pores, acne, scars, or blemishes at full resolution
✓ Natural facial asymmetry (one eye slightly different from other)
✓ Visible individual eyelashes that are irregular
✓ Real flyaway hairs that are sharp and individual (not smooth/merged)
✓ Teeth that are imperfect (slightly crooked, different sizes, natural gaps)
✓ Visible blood vessels in eyes
✓ Natural skin texture variation (rougher around nose, smoother on forehead)
✓ Authentic metadata indicating real camera (EXIF data)
✓ Background with natural imperfections and sharp text/signage
✓ Natural motion blur or focus inconsistencies from real camera

## RED FLAGS THAT MEAN FAKE (ANY ONE = FAKE):

### EYES (Highest Priority):
✗ Eyes that look too perfect or glossy
✗ Iris patterns that are too uniform or symmetric
✗ Light reflections (catchlights) that don't match in both eyes
✗ Whites of eyes that are too white or too uniform
✗ Eye corners that blend unnaturally into skin

### SKIN:
✗ Skin that looks airbrushed or plastic-like
✗ No visible pores anywhere on face
✗ Uniformly smooth texture across entire face
✗ Unnatural sheen or matte finish

### HAIR:
✗ Hair boundary that looks painted or smeared
✗ Individual hair strands that merge together
✗ Hair that blends into background unnaturally
✗ Flyaways that look like soft brushstrokes

### TEETH:
✗ Teeth that blend together (fused appearance)
✗ Perfect, identical teeth with no variation
✗ Gumline that looks artificial
✗ Wrong number of visible teeth for the angle

### BACKGROUND:
✗ Warped lines (door frames, windows bent)
✗ Blurred or smeared areas near face edges
✗ Inconsistent focus/blur patterns
✗ Garbled or nonsensical text

### OVERALL:
✗ Face looks "too perfect" or like a model
✗ Lighting is unrealistically even across face
✗ Image has an uncanny valley feeling
✗ Person looks generic or AI-generated
✗ Perfect symmetry (real faces are NEVER symmetric)

## VERDICT RULES:

- Found ANY red flag → FAKE (confidence based on severity)
- Image looks "too good to be true" → FAKE (70-85%)
- Uncertain but no clear authenticity proof → FAKE (60-70%)
- Only mark REAL if you find 3+ authenticity markers AND zero red flags

## CONFIDENCE CALIBRATION:

For FAKE verdicts:
- Multiple obvious artifacts: 90-100%
- Clear artifacts found: 80-89%
- Subtle artifacts or "too perfect": 65-79%
- Uncertain but suspicious: 55-64%

For REAL verdicts (rare):
- Clear natural imperfections visible: 85-95%
- Some authenticity markers: 70-84%
- Never give REAL above 95%

## OUTPUT FORMAT (JSON only):
{
  "verdict": "FAKE",
  "confidence": <55-100>,
  "riskLevel": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "details": {
    "facialAnalysis": { "score": <0-100>, "landmarks": <0-100>, "skinTexture": <0-100>, "eyeConsistency": <0-100>, "hairBoundary": <0-100> },
    "temporalConsistency": { "score": <0-100>, "lighting": <0-100>, "shadows": <0-100>, "colorTemp": <0-100> },
    "artifactDetection": { "score": <0-100>, "ganFingerprints": <0-100>, "blendingArtifacts": <0-100>, "compressionAnomalies": <0-100> },
    "metadataAnalysis": { "score": <0-100>, "resolutionConsistency": <0-100>, "noisePatterns": <0-100> }
  },
  "detectedTechniques": ["List SPECIFIC artifacts found - be detailed"],
  "authenticityMarkers": ["Only if verdict is REAL - list natural imperfections"],
  "explanation": "Specific observations that led to your verdict",
  "technicalNotes": "Technical analysis details"
}

REMEMBER: Your job is to CATCH FAKES. Default to FAKE unless proven otherwise.`;

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const LOVABLE_API_KEY = Deno.env.get('LOVABLE_API_KEY');
    if (!LOVABLE_API_KEY) {
      throw new Error("LOVABLE_API_KEY is not configured");
    }

    const { imageBase64, fileName, fileType, multiFrame = false } = await req.json();

    if (!imageBase64 || !fileName) {
      return new Response(
        JSON.stringify({ error: "Missing required fields: imageBase64, fileName" }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    console.log(`[DeepGuard] Analyzing: ${fileName}, type: ${fileType}, multiFrame: ${multiFrame}`);

    // Use Gemini 2.5 Pro for advanced forensic analysis
    const response = await fetch("https://ai.gateway.lovable.dev/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${LOVABLE_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "google/gemini-2.5-pro",
        messages: [
          {
            role: "system",
            content: FORENSIC_SYSTEM_PROMPT
          },
          {
            role: "user",
            content: [
            {
                type: "text",
                text: `DEEPFAKE DETECTION ANALYSIS - DEFAULT ASSUMPTION: THIS IS FAKE

Analyze this ${fileType} as a potential AI-generated deepfake.
File: ${fileName}

YOUR TASK:
1. ASSUME THIS IS FAKE until proven otherwise
2. Look for ANY signs of AI generation (skin too smooth, eyes too perfect, hair boundary issues)
3. Only mark as REAL if you find CLEAR evidence of natural imperfections (visible pores, asymmetry, irregular features)
4. If the image looks "too good" or "too perfect" - it's probably FAKE
5. When in doubt, mark as FAKE with moderate confidence (60-75%)

SPECIFIC CHECKS:
- Are there visible skin pores? If no → FAKE
- Is facial symmetry too perfect? If yes → FAKE  
- Are the eyes too glossy or uniform? If yes → FAKE
- Does the hair boundary look smooth/painted? If yes → FAKE
- Are the teeth too perfect or fused? If yes → FAKE
- Does the person look like a "perfect model"? If yes → FAKE

The burden of proof is on REAL, not FAKE. Respond with JSON only.`
              },
              {
                type: "image_url",
                image_url: {
                  url: `data:image/jpeg;base64,${imageBase64}`
                }
              }
            ]
          }
        ],
      }),
    });

    if (!response.ok) {
      if (response.status === 429) {
        return new Response(
          JSON.stringify({ error: "Rate limit exceeded. Please try again in a moment." }),
          { status: 429, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
      }
      if (response.status === 402) {
        return new Response(
          JSON.stringify({ error: "AI credits depleted. Please add credits to continue." }),
          { status: 402, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
      }
      const errorText = await response.text();
      console.error("[DeepGuard] AI gateway error:", response.status, errorText);
      throw new Error(`AI analysis failed: ${response.status}`);
    }

    const aiResponse = await response.json();
    const content = aiResponse.choices?.[0]?.message?.content;
    
    console.log("[DeepGuard] Raw AI Response:", content?.substring(0, 500));

    // Parse the JSON response from AI
    let analysisResult;
    try {
      const jsonMatch = content.match(/```(?:json)?\s*([\s\S]*?)```/) || [null, content];
      const jsonStr = jsonMatch[1].trim();
      analysisResult = JSON.parse(jsonStr);
    } catch (parseError) {
      console.error("[DeepGuard] Failed to parse AI response:", parseError);
      // Fallback defaults to FAKE when uncertain
      analysisResult = {
        verdict: "FAKE",
        confidence: 65,
        riskLevel: "MEDIUM",
        details: {
          facialAnalysis: { score: 40, landmarks: 40, skinTexture: 40, eyeConsistency: 40, hairBoundary: 40 },
          temporalConsistency: { score: 50, lighting: 50, shadows: 50, colorTemp: 50 },
          artifactDetection: { score: 40, ganFingerprints: 40, blendingArtifacts: 40, compressionAnomalies: 50 },
          metadataAnalysis: { score: 50, resolutionConsistency: 50, noisePatterns: 50 }
        },
        detectedTechniques: ["Unable to fully analyze - treating as suspicious"],
        authenticityMarkers: [],
        explanation: "Analysis was inconclusive. When unable to verify authenticity, defaulting to FAKE as a precaution.",
        technicalNotes: "Parse error occurred. Recommend re-analysis with higher quality image."
      };
    }

    // Normalize scores for database storage (use main category scores)
    const facialScore = analysisResult.details?.facialAnalysis?.score ?? analysisResult.details?.facialAnalysis ?? 50;
    const temporalScore = analysisResult.details?.temporalConsistency?.score ?? analysisResult.details?.temporalConsistency ?? 50;
    const artifactScore = analysisResult.details?.artifactDetection?.score ?? analysisResult.details?.artifactDetection ?? 50;
    const metadataScore = analysisResult.details?.metadataAnalysis?.score ?? analysisResult.details?.metadataAnalysis ?? 50;

    // Store in database
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    const { error: dbError } = await supabase.from('analysis_history').insert({
      file_name: fileName,
      file_type: fileType,
      verdict: analysisResult.verdict,
      confidence: analysisResult.confidence,
      facial_analysis: Math.round(facialScore),
      temporal_consistency: Math.round(temporalScore),
      artifact_detection: Math.round(artifactScore),
      metadata_analysis: Math.round(metadataScore),
      ai_explanation: analysisResult.explanation
    });

    if (dbError) {
      console.error("[DeepGuard] Database error:", dbError);
    }

    console.log(`[DeepGuard] Analysis complete: ${analysisResult.verdict} (${analysisResult.confidence}%)`);

    return new Response(
      JSON.stringify({
        verdict: analysisResult.verdict,
        confidence: analysisResult.confidence,
        riskLevel: analysisResult.riskLevel || (analysisResult.verdict === "FAKE" ? "HIGH" : "LOW"),
        fileName,
        analyzedAt: new Date().toISOString(),
        details: analysisResult.details,
        detectedTechniques: analysisResult.detectedTechniques || [],
        authenticityMarkers: analysisResult.authenticityMarkers || [],
        explanation: analysisResult.explanation,
        technicalNotes: analysisResult.technicalNotes
      }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );

  } catch (error) {
    console.error("[DeepGuard] Error in analyze-media function:", error);
    return new Response(
      JSON.stringify({ error: error instanceof Error ? error.message : "Unknown error" }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});
