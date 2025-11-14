import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { API_ENDPOINTS } from '@/config/api';
import { useCalendar } from '@/composables/useCalendar';

// Global authentication state
const authToken = ref<string | null>(null);
const userData = ref<any>(null);
const isLoading = ref(false);

// Initialize auth state from localStorage
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

// Initialize on first load
initializeAuth();

export const useAuth = () => {
  const router = useRouter();
  
  // Computed properties
  const isAuthenticated = computed(() => !!authToken.value);
  const currentUser = computed(() => userData.value);
  
  // Store authentication data
  const setAuthData = (token: string, user: any) => {
    authToken.value = token;
    userData.value = user;
    localStorage.setItem('auth_token', token);
    localStorage.setItem('user_data', JSON.stringify(user));
  };
  
  // Clear authentication data
  const clearAuthData = () => {
    authToken.value = null;
    userData.value = null;
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
  };
  
  // Login user
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
  
  // Register user
  const register = async (email: string, password: string, confirmPassword: string): Promise<{ success: boolean; message: string }> => {
    isLoading.value = true;
    
    try {
      const response = await fetch(API_ENDPOINTS.REGISTER(), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, confirmPassword }),
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
  
  // Logout user
  const logout = async (): Promise<void> => {
    try {
      // Call logout API if token exists
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
      // Always clear local data and redirect
      clearAuthData();

      // Clear all calendar data to prevent data leakage between users
      const { clearCalendarData } = useCalendar();
      clearCalendarData();

      router.push('/login');
    }
  };
  
  // Get authorization headers for API requests
  const getAuthHeaders = (): Record<string, string> => {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    
    if (authToken.value) {
      headers['Authorization'] = `Bearer ${authToken.value}`;
    }
    
    return headers;
  };
  
  // Check if user is authenticated (for route guards)
  const checkAuth = (): boolean => {
    return !!authToken.value;
  };
  
  // Redirect to calendar overview if authenticated
  const redirectToDashboard = () => {
    if (isAuthenticated.value) {
      router.push('/calendar');
    }
  };
  
  // Redirect to login if not authenticated
  const redirectToLogin = () => {
    if (!isAuthenticated.value) {
      router.push('/login');
    }
  };
  
  return {
    // State
    isAuthenticated,
    currentUser,
    isLoading,
    
    // Actions
    login,
    register,
    logout,
    
    // Utilities
    getAuthHeaders,
    checkAuth,
    redirectToDashboard,
    redirectToLogin,
    setAuthData,
    clearAuthData
  };
};