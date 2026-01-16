export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "14.1"
  }
  public: {
    Tables: {
      admin_users: {
        Row: {
          can_deploy_models: boolean
          can_trigger_training: boolean
          can_verify_feedback: boolean
          created_at: string
          id: string
          role: string
          user_id: string
        }
        Insert: {
          can_deploy_models?: boolean
          can_trigger_training?: boolean
          can_verify_feedback?: boolean
          created_at?: string
          id?: string
          role?: string
          user_id: string
        }
        Update: {
          can_deploy_models?: boolean
          can_trigger_training?: boolean
          can_verify_feedback?: boolean
          created_at?: string
          id?: string
          role?: string
          user_id?: string
        }
        Relationships: []
      }
      analysis_history: {
        Row: {
          ai_explanation: string | null
          artifact_detection: number | null
          confidence: number
          created_at: string
          facial_analysis: number | null
          file_name: string
          file_type: string
          id: string
          metadata_analysis: number | null
          temporal_consistency: number | null
          user_id: string | null
          verdict: string
        }
        Insert: {
          ai_explanation?: string | null
          artifact_detection?: number | null
          confidence: number
          created_at?: string
          facial_analysis?: number | null
          file_name: string
          file_type: string
          id?: string
          metadata_analysis?: number | null
          temporal_consistency?: number | null
          user_id?: string | null
          verdict: string
        }
        Update: {
          ai_explanation?: string | null
          artifact_detection?: number | null
          confidence?: number
          created_at?: string
          facial_analysis?: number | null
          file_name?: string
          file_type?: string
          id?: string
          metadata_analysis?: number | null
          temporal_consistency?: number | null
          user_id?: string | null
          verdict?: string
        }
        Relationships: []
      }
      feedback_audit_logs: {
        Row: {
          action: string
          actor_id: string | null
          actor_type: string
          created_at: string
          details: Json
          entity_id: string | null
          entity_type: string
          id: string
        }
        Insert: {
          action: string
          actor_id?: string | null
          actor_type?: string
          created_at?: string
          details?: Json
          entity_id?: string | null
          entity_type: string
          id?: string
        }
        Update: {
          action?: string
          actor_id?: string | null
          actor_type?: string
          created_at?: string
          details?: Json
          entity_id?: string | null
          entity_type?: string
          id?: string
        }
        Relationships: []
      }
      feedback_consensus: {
        Row: {
          consensus_label: string | null
          consensus_reached: boolean
          consensus_threshold: number
          created_at: string
          fake_votes: number
          id: string
          media_hash: string
          real_votes: number
          updated_at: string
        }
        Insert: {
          consensus_label?: string | null
          consensus_reached?: boolean
          consensus_threshold?: number
          created_at?: string
          fake_votes?: number
          id?: string
          media_hash: string
          real_votes?: number
          updated_at?: string
        }
        Update: {
          consensus_label?: string | null
          consensus_reached?: boolean
          consensus_threshold?: number
          created_at?: string
          fake_votes?: number
          id?: string
          media_hash?: string
          real_votes?: number
          updated_at?: string
        }
        Relationships: []
      }
      model_versions: {
        Row: {
          accuracy_metrics: Json
          created_at: string
          created_by: string | null
          deployed_at: string | null
          description: string | null
          feedback_samples_used: number
          id: string
          is_active: boolean
          is_rollback_available: boolean
          trained_at: string
          training_dataset_summary: Json
          version_id: string
          version_number: number
        }
        Insert: {
          accuracy_metrics?: Json
          created_at?: string
          created_by?: string | null
          deployed_at?: string | null
          description?: string | null
          feedback_samples_used?: number
          id?: string
          is_active?: boolean
          is_rollback_available?: boolean
          trained_at?: string
          training_dataset_summary?: Json
          version_id: string
          version_number: number
        }
        Update: {
          accuracy_metrics?: Json
          created_at?: string
          created_by?: string | null
          deployed_at?: string | null
          description?: string | null
          feedback_samples_used?: number
          id?: string
          is_active?: boolean
          is_rollback_available?: boolean
          trained_at?: string
          training_dataset_summary?: Json
          version_id?: string
          version_number?: number
        }
        Relationships: []
      }
      user_feedback: {
        Row: {
          analysis_id: string | null
          created_at: string
          feedback_text: string | null
          id: string
          is_correct: boolean
          media_hash: string
          original_confidence: number
          original_prediction: string
          updated_at: string
          user_id: string | null
          user_ip_hash: string | null
          user_label: string
          verification_status: string
          verified_at: string | null
          verified_by: string | null
        }
        Insert: {
          analysis_id?: string | null
          created_at?: string
          feedback_text?: string | null
          id?: string
          is_correct: boolean
          media_hash: string
          original_confidence: number
          original_prediction: string
          updated_at?: string
          user_id?: string | null
          user_ip_hash?: string | null
          user_label: string
          verification_status?: string
          verified_at?: string | null
          verified_by?: string | null
        }
        Update: {
          analysis_id?: string | null
          created_at?: string
          feedback_text?: string | null
          id?: string
          is_correct?: boolean
          media_hash?: string
          original_confidence?: number
          original_prediction?: string
          updated_at?: string
          user_id?: string | null
          user_ip_hash?: string | null
          user_label?: string
          verification_status?: string
          verified_at?: string | null
          verified_by?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "user_feedback_analysis_id_fkey"
            columns: ["analysis_id"]
            isOneToOne: false
            referencedRelation: "analysis_history"
            referencedColumns: ["id"]
          },
        ]
      }
      user_roles: {
        Row: {
          created_at: string
          id: string
          role: Database["public"]["Enums"]["app_role"]
          user_id: string
        }
        Insert: {
          created_at?: string
          id?: string
          role: Database["public"]["Enums"]["app_role"]
          user_id: string
        }
        Update: {
          created_at?: string
          id?: string
          role?: Database["public"]["Enums"]["app_role"]
          user_id?: string
        }
        Relationships: []
      }
    }
    Views: {
      model_versions_public: {
        Row: {
          created_at: string | null
          deployed_at: string | null
          id: string | null
          is_active: boolean | null
          version_id: string | null
          version_number: number | null
        }
        Insert: {
          created_at?: string | null
          deployed_at?: string | null
          id?: string | null
          is_active?: boolean | null
          version_id?: string | null
          version_number?: number | null
        }
        Update: {
          created_at?: string | null
          deployed_at?: string | null
          id?: string | null
          is_active?: boolean | null
          version_id?: string | null
          version_number?: number | null
        }
        Relationships: []
      }
    }
    Functions: {
      has_role: {
        Args: {
          _role: Database["public"]["Enums"]["app_role"]
          _user_id: string
        }
        Returns: boolean
      }
      is_admin: { Args: { _user_id: string }; Returns: boolean }
    }
    Enums: {
      app_role: "admin" | "moderator" | "user"
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {
      app_role: ["admin", "moderator", "user"],
    },
  },
} as const
