import { ref } from 'vue';
import { API_ENDPOINTS } from '@/config/api';
import { useAuth } from '@/composables/useAuth';
import type { UserProfile, ProfileUpdateData, ProfileUpdateResponse } from '@/types/user';

// Global profile state
const profile = ref<UserProfile | null>(null);
const isLoading = ref(false);
const error = ref<string>('');

export const useProfile = () => {
  const { getAuthHeaders, currentUser, setAuthData } = useAuth();

  /**
   * Fetch current user's profile from API
   */
  const fetchProfile = async (): Promise<{ success: boolean; error?: string }> => {
    isLoading.value = true;
    error.value = '';

    try {
      const response = await fetch(API_ENDPOINTS.PROFILE(), {
        method: 'GET',
        headers: getAuthHeaders(),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to fetch profile');
      }

      const data = await response.json();
      profile.value = data.user;

      return { success: true };
    } catch (err: any) {
      error.value = err.message;
      return { success: false, error: err.message };
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * Update user profile (email and/or display name)
   */
  const updateProfile = async (updateData: ProfileUpdateData): Promise<{ success: boolean; error?: string; message?: string }> => {
    isLoading.value = true;
    error.value = '';

    try {
      const response = await fetch(API_ENDPOINTS.UPDATE_PROFILE(), {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(updateData),
      });

      const data: ProfileUpdateResponse = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Failed to update profile');
      }

      // Update local profile state
      profile.value = data.user;

      // Update auth user data if available (to keep currentUser in sync)
      if (currentUser.value) {
        const token = localStorage.getItem('auth_token');
        if (token) {
          setAuthData(token, data.user);
        }
      }

      return {
        success: true,
        message: data.message
      };
    } catch (err: any) {
      error.value = err.message;
      return {
        success: false,
        error: err.message
      };
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * Change user password
   */
  const changePassword = async (
    currentPassword: string,
    newPassword: string,
    confirmPassword: string
  ): Promise<{ success: boolean; error?: string; message?: string }> => {
    isLoading.value = true;
    error.value = '';

    try {
      const response = await fetch(API_ENDPOINTS.CHANGE_PASSWORD(), {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
          confirm_password: confirmPassword,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to change password');
      }

      return {
        success: true,
        message: data.message || 'Password changed successfully'
      };
    } catch (err: any) {
      error.value = err.message;
      return {
        success: false,
        error: err.message
      };
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * Delete user account permanently
   */
  const deleteAccount = async (password: string): Promise<{ success: boolean; error?: string; message?: string }> => {
    isLoading.value = true;
    error.value = '';

    try {
      const response = await fetch(API_ENDPOINTS.DELETE_ACCOUNT(), {
        method: 'DELETE',
        headers: getAuthHeaders(),
        body: JSON.stringify({ password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to delete account');
      }

      return {
        success: true,
        message: data.message || 'Account deleted successfully'
      };
    } catch (err: any) {
      error.value = err.message;
      return {
        success: false,
        error: err.message
      };
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * Clear profile data
   */
  const clearProfile = () => {
    profile.value = null;
    error.value = '';
  };

  return {
    // State
    profile,
    isLoading,
    error,

    // Actions
    fetchProfile,
    updateProfile,
    changePassword,
    deleteAccount,
    clearProfile,
  };
};
