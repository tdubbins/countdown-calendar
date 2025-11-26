<template>
  <div class="error-help">
    <div v-if="errorMessage" class="error-message" role="alert" aria-live="assertive">
      <ion-icon name="alert-circle" class="error-icon" aria-hidden="true"></ion-icon>
      {{ errorMessage }}
    </div>
    
    <div class="help-section">
      <h3>{{ helpTitle }}</h3>
      <ul role="list">
        <li 
          v-for="(suggestion, index) in suggestions"
          :key="index"
          role="listitem"
        >
          {{ suggestion }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { IonIcon } from '@ionic/vue';

// Props
interface Props {
  errorMessage?: string;
  helpTitle?: string;
  suggestions: string[];
}

withDefaults(defineProps<Props>(), {
  helpTitle: 'What can you do?'
});
</script>

<style scoped>
.error-help {
  text-align: left;
  margin-bottom: 24px;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--color-error-bg);
  border: 1px solid var(--color-error-border);
  border-radius: 8px;
  padding: 16px;
  color: var(--color-error-text);
  font-weight: 500;
  margin-bottom: 20px;
}

.error-icon {
  font-size: 1.2rem;
  flex-shrink: 0;
}

.help-section {
  background: var(--color-background);
  border-radius: 8px;
  padding: 20px;
}

.help-section h3 {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--color-text-primary);
}

.help-section ul {
  margin: 0;
  padding-left: 20px;
}

.help-section li {
  margin-bottom: 8px;
  color: var(--color-text-secondary);
  line-height: 1.4;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .error-message {
    border-width: 2px;
  }

  .help-section {
    border: 2px solid var(--color-border);
  }
}
</style>