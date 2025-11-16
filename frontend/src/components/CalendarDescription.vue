<template>
  <p
    v-if="description"
    class="calendar-description"
    :class="{
      'calendar-description--editable': editable,
      'calendar-description--centered': centered
    }"
    @click="handleClick"
    :role="editable ? 'button' : undefined"
    :tabindex="editable ? 0 : undefined"
    :aria-label="editable ? 'Click to edit description' : undefined"
  >
    {{ description }}
  </p>
</template>

<script setup lang="ts">
interface Props {
  description?: string;
  editable?: boolean;
  centered?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  description: '',
  editable: false,
  centered: false
});

const emit = defineEmits<{
  'edit': [];
}>();

const handleClick = () => {
  if (props.editable) {
    emit('edit');
  }
};
</script>

<style scoped>
/* Base calendar description styles */
.calendar-description {
  font-size: clamp(0.85rem, 2vw, 0.95rem);
  color: var(--color-text-secondary);
  margin: var(--spacing-md) 0;
  line-height: 1.6;
  text-align: left;
  white-space: pre-wrap;
  word-wrap: break-word;
}

/* Centered variant (for viewer page) */
.calendar-description--centered {
  text-align: center;
  margin-left: auto;
  margin-right: auto;
  max-width: 40rem;
}

/* Editable variant (for edit page) */
.calendar-description--editable {
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--color-background);
  border-radius: var(--radius-md);
  border: 2px dashed var(--color-border);
  cursor: pointer;
  transition: all var(--transition-base);
}

.calendar-description--editable:hover {
  background: var(--color-surface);
  border-color: var(--color-focus);
  color: var(--color-text-primary);
}

.calendar-description--editable:focus {
  outline: 2px solid var(--color-focus);
  outline-offset: 2px;
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .calendar-description--editable {
    transition: none;
  }
}
</style>
