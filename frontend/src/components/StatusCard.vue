<template>
  <div class="status-card" :class="statusClass">
    <div class="logo-section">
      <div class="logo-icon">📅</div>
      <h1>Countdown Calendar</h1>
    </div>
    
    <div class="status-content">
      <!-- Loading State -->
      <div v-if="status === 'loading'" class="loading-section">
        <ion-spinner 
          name="crescent" 
          class="large-spinner" 
          :aria-label="loadingText"
        ></ion-spinner>
        <h2>{{ title }}</h2>
        <p>{{ message }}</p>
      </div>

      <!-- Success/Error State -->
      <div v-else class="result-section">
        <div class="status-icon">
          <ion-icon :icon="iconName" aria-hidden="true"></ion-icon>
        </div>
        <h2>{{ title }}</h2>
        <p>{{ message }}</p>
        
        <!-- Additional content slot -->
        <slot name="additional-content"></slot>
        
        <!-- Action buttons -->
        <div v-if="$slots.actions" class="action-buttons">
          <slot name="actions"></slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { IonIcon, IonSpinner } from '@ionic/vue';
import { checkmarkCircle, alertCircle, informationCircle } from 'ionicons/icons';

// Props
interface Props {
  status: 'loading' | 'success' | 'error';
  title: string;
  message: string;
  loadingText?: string;
}

const props = withDefaults(defineProps<Props>(), {
  loadingText: 'Loading'
});

// Computed properties
const statusClass = computed(() => `${props.status}-card`);

const iconName = computed(() => {
  switch (props.status) {
    case 'success': return checkmarkCircle;
    case 'error': return alertCircle;
    default: return informationCircle;
  }
});
</script>

<style scoped>
.status-card {
  max-width: 500px;
  width: 100%;
  background: white;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
  padding: 40px 32px;
  text-align: center;
  animation: fadeInUp 0.6s ease-out;
}

/* Header styling */
.logo-section {
  margin-bottom: 32px;
}

.logo-icon {
  font-size: 3.5rem;
  margin-bottom: 12px;
}

.status-card h1 {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 8px;
  color: #333;
}

/* Loading state */
.loading-section {
  padding: 20px 0;
}

.large-spinner {
  width: 48px;
  height: 48px;
  margin-bottom: 24px;
  color: var(--ion-color-primary);
}

.loading-section h2 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 12px;
  color: #333;
}

.loading-section p {
  color: #666;
  font-size: 1rem;
  margin: 0;
}

/* Result sections */
.result-section {
  padding: 20px 0;
}

.result-section h2 {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 16px;
  color: #333;
}

.result-section p {
  font-size: 1.1rem;
  line-height: 1.5;
  margin-bottom: 24px;
  color: #555;
}

/* Status icons */
.status-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.success-card .status-icon {
  color: var(--ion-color-success);
}

.success-card .result-section h2 {
  color: var(--ion-color-success);
}

.error-card .status-icon {
  color: var(--ion-color-danger);
}

.error-card .result-section h2 {
  color: var(--ion-color-danger);
}

/* Action buttons */
.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 24px;
}

/* Responsive design */
@media (max-width: 480px) {
  .status-card {
    padding: 32px 24px;
  }
  
  .status-card h1 {
    font-size: 1.6rem;
  }
  
  .result-section h2 {
    font-size: 1.5rem;
  }
  
  .logo-icon {
    font-size: 3rem;
  }
}

@media (max-width: 320px) {
  .status-card {
    padding: 24px 20px;
  }
  
  .status-card h1 {
    font-size: 1.4rem;
  }
  
  .result-section h2 {
    font-size: 1.3rem;
  }
}

/* Animation */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .status-card {
    border: 3px solid #333;
  }
}
</style>