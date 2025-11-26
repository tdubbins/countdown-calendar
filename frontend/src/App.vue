<template>
  <ion-app :class="{ 'has-tab-bar': showTabBar }">
    <ion-router-outlet />

    <!-- Mobile Tab Bar - only for authenticated main pages -->
    <ion-tab-bar v-if="showTabBar" slot="bottom" class="mobile-tab-bar">
      <ion-tab-button tab="home" href="/calendar" :selected="isRoute('/calendar')">
        <ion-icon :icon="home" />
        <ion-label>Home</ion-label>
      </ion-tab-button>

      <ion-tab-button tab="create" href="/calendar/create" :selected="isRoute('/calendar/create')">
        <ion-icon :icon="addCircle" />
        <ion-label>New</ion-label>
      </ion-tab-button>

      <ion-tab-button tab="profile" href="/profile" :selected="isRoute('/profile')">
        <ion-icon :icon="personCircle" />
        <ion-label>Profile</ion-label>
      </ion-tab-button>

      <ion-tab-button tab="help" href="/help" :selected="isRoute('/help')">
        <ion-icon :icon="helpCircle" />
        <ion-label>Help</ion-label>
      </ion-tab-button>
    </ion-tab-bar>
  </ion-app>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { IonApp, IonRouterOutlet, IonTabBar, IonTabButton, IonIcon, IonLabel } from '@ionic/vue';
import { home, addCircle, personCircle, helpCircle } from 'ionicons/icons';
import { useResponsive } from '@/composables/useResponsive';
import { useAuth } from '@/composables/useAuth';

const route = useRoute();
const { isMobile } = useResponsive();
const { isAuthenticated } = useAuth();

// Main pages that show the tab bar (not sub-pages like edit/view)
const TAB_BAR_ROUTES = ['/calendar', '/calendar/create', '/profile', '/help'] as const;

const showTabBar = computed(() => {
  if (!isMobile()) return false;
  if (!isAuthenticated.value) return false;

  return TAB_BAR_ROUTES.includes(route.path as typeof TAB_BAR_ROUTES[number]);
});

const isRoute = (path: string) => route.path === path;
</script>

<style>
/* Tab bar height variable */
:root {
  --tab-bar-height: 64px;
}

/* Mobile Tab Bar Styling */
.mobile-tab-bar {
  --background: var(--ion-color-primary);
  --color: rgba(255, 255, 255, 0.7);
  --color-selected: white;
  border-top: none;
  height: var(--tab-bar-height);
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 999;
}

.mobile-tab-bar ion-tab-button {
  --color: rgba(255, 255, 255, 0.7);
  --color-selected: white;
  --padding-top: 8px;
  --padding-bottom: 8px;
}

.mobile-tab-bar ion-icon {
  font-size: 30px;
}

.mobile-tab-bar ion-label {
  font-size: 12px;
  font-weight: 500;
  margin-top: 4px;
}

/* Add bottom padding when tab bar is visible */
ion-app.has-tab-bar ion-page ion-content {
  --padding-bottom: calc(var(--tab-bar-height) + 16px);
}

/* Mobile header styling - larger title and consistent height */
@media (max-width: 767px) {
  ion-toolbar {
    --min-height: 56px;
  }

  ion-toolbar ion-title {
    font-size: 20px;
    font-weight: 600;
  }
}
</style>
