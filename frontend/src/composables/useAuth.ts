import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { API_ENDPOINTS } from '@/config/api';
import { clearCalendarData } from '@/composables/useCalendar';

const authToken = ref<string | null>(null);
const userData = ref<any>(null);
const isLoading = ref(false);

const initializeAuth = () => {
  const token = localStorage.getItem('auth_token');
  const user = localStorage.getItem('user_data');
  
  if (token) {
    authToken.value = token;
  }
  
  if (user) {
    try {
      userData.value = JSON.parse(user);
    } catch (error) {
      console.error('Failed to parse user data:', error);
      localStorage.removeItem('user_data');
    }
  }
};

initializeAuth();

export const useAuth = () => {
  const router = useRouter();

  const isAuthenticated = computed(() => !!authToken.value);
  const currentUser = computed(() => userData.value);

  const setAuthData = (token: string, user: any) => {
    authToken.value = token;
    userData.value = user;
    localStorage.setItem('auth_token', token);
    localStorage.setItem('user_data', JSON.stringify(user));
  };

  const clearAuthData = () => {
    authToken.value = null;
    userData.value = null;
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
  };

  const login = async (email: string, password: string): Promise<{ success: boolean; message: string }> => {
    isLoading.value = true;
    
    try {
      const response = await fetch(API_ENDPOINTS.LOGIN(), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Login failed');
      }
      
      const data = await response.json();
      setAuthData(data.token, data.user);
      
      return {
        success: true,
        message: 'Login successful'
      };
      
    } catch (error: any) {
      return {
        success: false,
        message: error.message
      };
    } finally {
      isLoading.value = false;
    }
  };

  const register = async (email: string, password: string, confirmPassword: string): Promise<{ success: boolean; message: string }> => {
    isLoading.value = true;

    try {
      const response = await fetch(API_ENDPOINTS.REGISTER(), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
          confirmPassword,
          frontendUrl: window.location.origin
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Registration failed');
      }

      const data = await response.json();

      return {
        success: true,
        message: data.message || 'Registration successful'
      };

    } catch (error: any) {
      return {
        success: false,
        message: error.message
      };
    } finally {
      isLoading.value = false;
    }
  };

  const resendVerificationEmail = async (email: string): Promise<{ success: boolean; message: string }> => {
    isLoading.value = true;

    try {
      const response = await fetch(API_ENDPOINTS.RESEND_VERIFICATION(), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          frontendUrl: window.location.origin
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to resend verification email');
      }

      return {
        success: true,
        message: data.message || 'Verification email sent successfully'
      };

    } catch (error: any) {
      return {
        success: false,
        message: error.message
      };
    } finally {
      isLoading.value = false;
    }
  };

  const logout = async (): Promise<void> => {
    try {
      if (authToken.value) {
        await fetch(API_ENDPOINTS.LOGOUT(), {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${authToken.value}`,
            'Content-Type': 'application/json',
          },
        });
      }
    } catch (error) {
      console.error('Logout API error:', error);
    } finally {
      clearAuthData();
      clearCalendarData();

      router.push('/login');
    }
  };

  const getAuthHeaders = (): Record<string, string> => {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    
    if (authToken.value) {
      headers['Authorization'] = `Bearer ${authToken.value}`;
    }
    
    return headers;
  };

  const checkAuth = (): boolean => {
    return !!authToken.value;
  };

  const redirectToDashboard = () => {
    if (isAuthenticated.value) {
      router.push('/calendar');
    }
  };

  const redirectToLogin = () => {
    if (!isAuthenticated.value) {
      router.push('/login');
    }
  };
  
  return {
    isAuthenticated,
    currentUser,
    isLoading,
    login,
    register,
    resendVerificationEmail,
    logout,
    getAuthHeaders,
    checkAuth,
    redirectToDashboard,
    redirectToLogin,
    setAuthData,
    clearAuthData
  };
};