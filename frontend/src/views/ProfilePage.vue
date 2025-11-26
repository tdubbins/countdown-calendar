<template>
  <ion-page>
    <ion-header>
      <ion-toolbar color="primary">
        <!-- Desktop only: Back button -->
        <ion-buttons v-if="!isMobile()" slot="start">
          <ion-back-button default-href="/calendar" text="Back" color="light"></ion-back-button>
        </ion-buttons>
        <ion-title>My Profile</ion-title>
        <ion-buttons slot="end">
          <ion-button @click="handleLogout" fill="clear" color="light" aria-label="Logout">
            <ion-icon :slot="isMobile() ? 'icon-only' : 'start'" :icon="logOutOutline"></ion-icon>
            <span v-if="!isMobile()">Logout</span>
          </ion-button>
        </ion-buttons>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true" class="profile-content">
      <div class="profile-container">
        <!-- Loading State -->
        <div v-if="isLoading" class="loading-section">
          <ion-spinner name="circles"></ion-spinner>
          <p>Loading profile...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="error-section">
          <div class="error-content">
            <p class="error-message">{{ error }}</p>
            <ActionButton
              @click="loadProfile"
              fill="outline"
              color="primary"
              variant="secondary"
            >
              Try Again
            </ActionButton>
          </div>
        </div>

        <!-- Profile Content -->
        <div v-else-if="profile" class="profile-section">
          <!-- Profile Header -->
          <div class="profile-header">
            <div class="profile-icon">
              <ion-icon :icon="person"></ion-icon>
            </div>
            <h2>{{ profile.display_name || 'User Profile' }}</h2>
          </div>

          <!-- Profile Information -->
          <div class="profile-info-card">
            <div class="info-row">
              <span class="info-label">Email:</span>
              <span class="info-value">{{ profile.email }}</span>
            </div>

            <div class="info-row">
              <span class="info-label">Display Name:</span>
              <span class="info-value">{{ profile.display_name || 'Not set' }}</span>
            </div>

            <div class="info-row">
              <span class="info-label">Account Created:</span>
              <span class="info-value">{{ formatDate(profile.created_at) }}</span>
            </div>

            <div v-if="profile.last_login" class="info-row">
              <span class="info-label">Last Login:</span>
              <span class="info-value">{{ formatDate(profile.last_login) }}</span>
            </div>

            <div class="info-row">
              <span class="info-label">Email Verified:</span>
              <span class="info-value">
                <ion-icon
                  :icon="profile.email_verified ? checkmarkCircle : closeCircle"
                  :color="profile.email_verified ? 'success' : 'danger'"
                ></ion-icon>
                {{ profile.email_verified ? 'Yes' : 'No' }}
              </span>
            </div>
          </div>

          <!-- Actions -->
          <div class="profile-actions">
            <div class="primary-actions">
              <ActionButton
                @click="openEditModal"
                fill="solid"
                color="primary"
                variant="primary"
                :icon="create"
                icon-slot="start"
              >
                Edit Profile
              </ActionButton>

              <ActionButton
                @click="openPasswordModal"
                fill="solid"
                color="primary"
                variant="primary"
                :icon="lockClosed"
                icon-slot="start"
              >
                Change Password
              </ActionButton>
            </div>

            <ActionButton
              @click="openDeleteModal"
              fill="solid"
              color="danger"
              variant="primary"
              :icon="trashOutline"
              icon-slot="start"
            >
              Delete Account
            </ActionButton>
          </div>

          <!-- Additional Info -->
          <div class="additional-info">
            <p class="info-text">
              <ion-icon :icon="informationCircle"></ion-icon>
              You have {{ profile.calendar_ids?.length || 0 }} calendar(s)
            </p>
          </div>
        </div>
      </div>

      <!-- Profile Edit Modal -->
      <ProfileEditModal
        :is-open="isEditModalOpen"
        :profile="profile"
        :is-submitting="isSubmitting"
        @close="closeEditModal"
        @submit="handleProfileUpdate"
      />

      <!-- Password Change Modal -->
      <PasswordChangeModal
        :is-open="isPasswordModalOpen"
        :is-submitting="isSubmitting"
        @close="closePasswordModal"
        @submit="handlePasswordChange"
      />

      <!-- Account Delete Modal -->
      <AccountDeleteModal
        :is-open="isDeleteModalOpen"
        :calendar-count="profile?.calendar_ids?.length || 0"
        :is-submitting="isSubmitting"
        @close="closeDeleteModal"
        @submit="handleAccountDelete"
      />
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonButtons,
  IonButton,
  IonBackButton,
  IonSpinner,
  IonIcon,
} from '@ionic/vue';
import {
  person,
  create,
  informationCircle,
  checkmarkCircle,
  closeCircle,
  lockClosed,
  trashOutline,
  logOutOutline,
} from 'ionicons/icons';
import { useAuth } from '@/composables/useAuth';
import { useProfile } from '@/composables/useProfile';
import { useResponsive } from '@/composables/useResponsive';
import { useToast } from '@/composables/useToast';
import { useAlert } from '@/composables/useAlert';
import ActionButton from '@/components/ActionButton.vue';
import ProfileEditModal from '@/components/ProfileEditModal.vue';
import PasswordChangeModal from '@/components/PasswordChangeModal.vue';
import AccountDeleteModal from '@/components/AccountDeleteModal.vue';
import type { ProfileUpdateData } from '@/types/user';

// Composables
const { isAuthenticated, redirectToLogin, logout } = useAuth();
const { profile, isLoading, error, fetchProfile, updateProfile, changePassword, deleteAccount } = useProfile();
const { isMobile } = useResponsive();
const { showSuccess } = useToast();
const { showError } = useAlert();

// Modal state
const isEditModalOpen = ref(false);
const isPasswordModalOpen = ref(false);
const isDeleteModalOpen = ref(false);
const isSubmitting = ref(false);

// Lifecycle
onMounted(async () => {
  if (!isAuthenticated.value) {
    redirectToLogin();
    return;
  }

  await loadProfile();
});

// Load profile data
const loadProfile = async () => {
  const result = await fetchProfile();
  if (!result.success) {
    console.error('Failed to load profile:', result.error);
  }
};

// Format date for display
const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

// Modal handlers
const openEditModal = () => {
  isEditModalOpen.value = true;
};

const closeEditModal = () => {
  isEditModalOpen.value = false;
};

const openPasswordModal = () => {
  isPasswordModalOpen.value = true;
};

const closePasswordModal = () => {
  isPasswordModalOpen.value = false;
};

const openDeleteModal = () => {
  isDeleteModalOpen.value = true;
};

const closeDeleteModal = () => {
  isDeleteModalOpen.value = false;
};

// Logout handler
const handleLogout = async () => {
  await logout();
};

// Profile update handler
const handleProfileUpdate = async (data: ProfileUpdateData) => {
  try {
    isSubmitting.value = true;

    // Only send fields that have actually changed
    const updateData: ProfileUpdateData = {};

    if (data.email !== profile.value?.email) {
      updateData.email = data.email;
    }

    if (data.display_name !== (profile.value?.display_name || null)) {
      updateData.display_name = data.display_name;
    }

    // Check if there are any changes
    if (Object.keys(updateData).length === 0) {
      await showError('No changes detected');
      isSubmitting.value = false;
      return;
    }

    const result = await updateProfile(updateData);

    if (result.success) {
      await showSuccess('Profile updated successfully!');
      closeEditModal();
      // Refresh profile data
      await loadProfile();
    } else {
      await showError(result.error || 'Failed to update profile');
    }
  } catch (error) {
    console.error('Profile update error:', error);
    await showError('An unexpected error occurred');
  } finally {
    isSubmitting.value = false;
  }
};

// Password change handler
const handlePasswordChange = async (data: {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}) => {
  try {
    isSubmitting.value = true;

    const result = await changePassword(
      data.currentPassword,
      data.newPassword,
      data.confirmPassword
    );

    if (result.success) {
      // Close modal
      closePasswordModal();

      // Show success message
      await showSuccess('Password changed successfully! Logging out...');

      // Wait a moment for the message to be visible
      await new Promise((resolve) => setTimeout(resolve, 1500));

      // Logout user (will redirect to login page)
      await logout();
    } else {
      await showError(result.error || 'Failed to change password');
    }
  } catch (error: any) {
    console.error('Password change error:', error);
    await showError('An unexpected error occurred');
  } finally {
    isSubmitting.value = false;
  }
};

// Account deletion handler
const handleAccountDelete = async (password: string) => {
  try {
    isSubmitting.value = true;

    const result = await deleteAccount(password);

    if (result.success) {
      // Close modal
      closeDeleteModal();

      // Show success message
      await showSuccess('Account deleted successfully. Goodbye!');

      // Wait a moment for the message to be visible
      await new Promise((resolve) => setTimeout(resolve, 2000));

      // Logout user (will redirect to login page)
      await logout();
    } else {
      await showError(result.error || 'Failed to delete account');
    }
  } catch (error: any) {
    console.error('Account deletion error:', error);
    await showError('An unexpected error occurred');
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.profile-content {
  --background: var(--color-background);
}

.profile-container {
  max-width: 600px;
  margin: 0 auto;
  padding: var(--spacing-md);
}

/* Loading State */
.loading-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  gap: var(--spacing-md);
}

.loading-section ion-spinner {
  --color: var(--ion-color-primary);
  width: 48px;
  height: 48px;
}

.loading-section p {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  margin: 0;
}

/* Error State */
.error-section {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.error-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
  text-align: center;
}

.error-message {
  font-size: var(--font-size-base);
  color: var(--ion-color-danger);
  margin: 0;
  padding: var(--spacing-md);
  background-color: rgba(var(--ion-color-danger-rgb), 0.1);
  border: 1px solid rgba(var(--ion-color-danger-rgb), 0.3);
  border-radius: var(--radius-md);
}

/* Profile Header */
.profile-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: var(--spacing-xl);
  padding: var(--spacing-lg) 0;
}

.profile-icon {
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--ion-color-primary), var(--ion-color-primary-shade));
  border-radius: 50%;
  margin-bottom: var(--spacing-md);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.profile-icon ion-icon {
  font-size: 60px;
  color: white;
}

.profile-header h2 {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

/* Profile Info Card */
.profile-info-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
  box-shadow: var(--shadow-md);
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md) 0;
  border-bottom: 1px solid var(--color-border);
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
}

.info-value {
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

/* Actions */
.profile-actions {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-lg);
}

.primary-actions {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

/* Additional Info */
.additional-info {
  margin-top: var(--spacing-xl);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--color-border);
}

.info-text {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
}

.info-text ion-icon {
  font-size: 20px;
  color: var(--ion-color-primary);
}

/* Responsive */
@media (min-width: 768px) {
  .profile-container {
    padding: var(--spacing-lg);
  }

  .profile-actions {
    align-items: center;
  }

  .primary-actions {
    flex-direction: row;
    justify-content: center;
  }

  .primary-actions > * {
    min-width: 200px;
  }
}
</style>
