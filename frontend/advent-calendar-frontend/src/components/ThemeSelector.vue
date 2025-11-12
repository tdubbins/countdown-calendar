<template>
  <!-- Unlocked: Single line dropdown -->
  <ion-select
    v-if="!isLocked"
    :value="localTheme"
    @ionChange="handleThemeChange"
    interface="popover"
    aria-label="Select calendar theme"
    class="theme-select"
  >
    <ion-select-option
      v-for="option in themeOptions"
      :key="option.value"
      :value="option.value"
    >
      {{ option.label }} Theme
    </ion-select-option>
  </ion-select>

  <!-- Locked: Read-only chip display -->
  <ion-chip v-else color="warning" outline class="locked-chip">
    <ion-icon :icon="lockClosedOutline" aria-hidden="true"></ion-icon>
    <ion-label>
      Theme: {{ themeDisplayName }} (locked after sharing)
    </ion-label>
  </ion-chip>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import {
  IonSelect,
  IonSelectOption,
  IonChip,
  IonLabel,
  IonIcon
} from '@ionic/vue';
import { lockClosedOutline } from 'ionicons/icons';
import { THEME_OPTIONS, DEFAULT_THEME } from '@/utils/constants';

/**
 * Theme Selector Component (Issue #82)
 *
 * Allows calendar creators to choose visual theme for shared calendars.
 * Currently supports single "Christmas" theme with architecture prepared
 * for future theme expansion (birthday, holiday, custom).
 *
 * Design Decision: Locked after share token is generated to ensure consistent
 * viewer experience. Theme styling applied in SharedCalendar viewer (Issue #86).
 *
 * NFR Compliance:
 * - [U5] WCAG 2.1 AA: ARIA labels, keyboard navigation
 * - [U2] Touch-friendly: 44px+ touch targets
 * - [U1] Responsive: Works on 320px+ screens
 * - [SC3] Modular: Architecture prepared for future themes
 */

interface Props {
  theme?: string | null;      // Current theme value
  isLocked?: boolean;         // True if shareToken exists (locked)
}

interface Emits {
  (e: 'update', theme: string): void;
}

const props = withDefaults(defineProps<Props>(), {
  theme: DEFAULT_THEME,
  isLocked: false
});

const emit = defineEmits<Emits>();

// Local reactive state
const localTheme = ref<string>(props.theme || DEFAULT_THEME);

// Theme options for dropdown (Issue #82)
// NFR [SC3]: Prepared for future theme expansion
const themeOptions = [
  { value: THEME_OPTIONS.CHRISTMAS, label: 'Christmas' }
  // Future: { value: 'birthday', label: 'Birthday' },
  // Future: { value: 'holiday', label: 'Holiday' },
  // Future: { value: 'custom', label: 'Custom' }
];

// Display name for locked state
const themeDisplayName = computed(() => {
  const option = themeOptions.find(opt => opt.value === localTheme.value);
  return option?.label || 'Christmas';
});

// Watch props for external changes (e.g., from API response)
watch(() => props.theme, (newTheme) => {
  if (newTheme) localTheme.value = newTheme;
});

/**
 * Handle theme change (dropdown selection)
 * Emits update event to parent component for API call
 */
const handleThemeChange = (event: CustomEvent) => {
  const newTheme = event.detail.value as string;
  localTheme.value = newTheme;
  emit('update', newTheme);
};
</script>

<style scoped>
/* Minimal styling - single line dropdown */
.theme-select {
  margin-bottom: var(--spacing-md);
  max-width: 300px;
  --placeholder-color: var(--ion-color-medium);
}

.locked-chip {
  margin-bottom: var(--spacing-md);
  cursor: default !important;
  pointer-events: none !important;
}
</style>
