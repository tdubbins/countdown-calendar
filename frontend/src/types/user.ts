// User Profile Types

export interface UserProfile {
  id: string;
  email: string;
  display_name?: string | null;
  email_verified: boolean;
  created_at: string;
  email_verified_at?: string;
  last_login?: string;
  updated_at?: string;
  calendar_ids?: string[];
}

export interface ProfileUpdateData {
  email?: string;
  display_name?: string | null;
}

export interface ProfileUpdateResponse {
  success: boolean;
  message: string;
  user: UserProfile;
}
