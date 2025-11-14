<template>
  <div class="empty-state">
    <div class="empty-icon">{{ icon }}</div>
    <h2>{{ title }}</h2>
    
    <!-- Optional description content -->
    <div v-if="$slots.description || description" class="description-content">
      <slot name="description">
        <p v-if="description">{{ description }}</p>
      </slot>
    </div>
    
    <!-- Optional action button -->
    <div v-if="$slots.action || (actionText && onAction)" class="action-section">
      <slot name="action">
        <ActionButton 
          v-if="actionText && onAction"
          @click="onAction"
          fill="solid"
          color="primary"
          size="large"
          icon="add"
          icon-slot="start"
          expand="block"
        >
          {{ actionText }}
        </ActionButton>
      </slot>
    </div>
    
    <!-- Additional content slot -->
    <div v-if="$slots.additional" class="additional-content">
      <slot name="additional"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { EmptyStateProps } from '@/types/calendar';
import ActionButton from '@/components/ActionButton.vue';

// Props with defaults
withDefaults(defineProps<EmptyStateProps>(), {
  description: undefined,
  actionText: undefined,
  onAction: undefined
});
</script>

<style scoped>
.empty-state {
  text-align: center;
  padding: 40px 20px;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  opacity: 0.6;
}

.empty-state h2 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 24px;
  color: #333;
}

.description-content {
  background: white;
  padding: 24px 20px;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  margin-bottom: 20px;
}

.description-content p {
  font-size: 0.95rem;
  color: #555;
  margin-bottom: 12px;
  line-height: 1.4;
  text-align: left;
}

.description-content p:last-child {
  margin-bottom: 0;
}

.action-section {
  margin-bottom: 20px;
}

.additional-content {
  margin-top: 20px;
}

/* Tablet improvements */
@media (min-width: 768px) {
  .empty-state {
    padding: 60px 40px;
  }
  
  .description-content p {
    font-size: 1rem;
  }
}

/* High contrast support */
@media (prefers-contrast: high) {
  .description-content {
    border-width: 2px;
    border-color: #333;
  }
}
</style>