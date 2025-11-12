<template>
  <div class="door-order-toggle">
    <!-- Section Header -->
    <div class="section-header">
      <h3>Door Ordering for Viewers</h3>
      <p v-if="!isLocked" class="help-text">
        Choose how doors appear in your shared calendar
      </p>
      <p v-if="isLocked" class="locked-message">
        🔒 Locked after sharing to ensure consistent viewer experience
      </p>
    </div>

    <!-- Toggle Segment (Sequential vs Random) -->
    <ion-segment
      :value="localDoorOrder"
      @ionChange="handleOrderChange"
      :disabled="isLocked"
      mode="md"
      class="door-order-segment"
    >
      <ion-segment-button
        value="sequential"
        :aria-label="isLocked ? 'Sequential order (locked)' : 'Sequential order - doors appear in order 1, 2, 3'"
      >
        <ion-label>
          <div class="segment-content">
            <ion-icon :icon="listOutline" aria-hidden="true"></ion-icon>
            <span>Sequential</span>
            <small>(1, 2, 3...)</small>
          </div>
        </ion-label>
      </ion-segment-button>

      <ion-segment-button
        value="random"
        :aria-label="isLocked ? 'Random order (locked)' : 'Random order - doors appear shuffled'"
      >
        <ion-label>
          <div class="segment-content">
            <ion-icon :icon="shuffleOutline" aria-hidden="true"></ion-icon>
            <span>Random</span>
            <small>(Shuffled)</small>
          </div>
        </ion-label>
      </ion-segment-button>
    </ion-segment>

    <!-- Shuffle Again Button (only visible for random order) -->
    <ion-button
      v-if="localDoorOrder === 'random' && !isLocked"
      expand="block"
      fill="outline"
      @click="handleShuffleAgain"
      class="shuffle-button"
      :disabled="isShuffling"
      aria-label="Generate new random order for doors"
    >
      <ion-icon slot="start" :icon="shuffleOutline" aria-hidden="true"></ion-icon>
      {{ isShuffling ? 'Shuffling...' : '🎲 Shuffle Again' }}
    </ion-button>

    <!-- Optional: Preview of first few door positions -->
    <div v-if="showPreview && localDoorOrder === 'random' && localDoorPositions" class="positions-preview">
      <small>Door order preview (first 5):</small>
      <div class="preview-chips">
        <span
          v-for="(day, index) in previewPositions"
          :key="index"
          class="preview-chip"
        >
          Door #{{ index + 1 }} → Day {{ day }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import {
  IonSegment,
  IonSegmentButton,
  IonLabel,
  IonButton,
  IonIcon
} from '@ionic/vue';
import { listOutline, shuffleOutline } from 'ionicons/icons';
import { generateShuffledPositions } from '@/utils/shuffle';
import type { DoorOrder } from '@/types/calendar';

/**
 * Door Order Toggle Component (Issue #81)
 *
 * Allows calendar creators to choose how doors appear in shared calendars:
 * - Sequential: Doors appear in order 1, 2, 3, ...
 * - Random: Doors appear in shuffled order using Fisher-Yates algorithm
 *
 * Design Decision: Locked after share token is generated to ensure consistent
 * viewer experience. All viewers see the same door order.
 *
 * NFR Compliance:
 * - [U5] WCAG 2.1 AA: ARIA labels, keyboard navigation
 * - [U2] Touch-friendly: 44px+ touch targets
 * - [U1] Responsive: Works on 320px+ screens
 * - [P3] Performance: Fast shuffle algorithm O(n)
 * - [SC3] Modular: Reusable component with props/events
 */

interface Props {
  doorOrder?: DoorOrder | null;         // Current door order setting
  doorPositions?: number[] | null;      // Current shuffled positions (if random)
  duration: number;                     // Calendar duration (1-31 days)
  isLocked?: boolean;                   // True if shareToken exists (locked)
  showPreview?: boolean;                // Show preview of door positions
}

interface Emits {
  (e: 'update', data: { doorOrder: DoorOrder; doorPositions: number[] | null }): void;
}

const props = withDefaults(defineProps<Props>(), {
  doorOrder: 'sequential',
  doorPositions: null,
  isLocked: false,
  showPreview: false
});

const emit = defineEmits<Emits>();

// Local reactive state
const localDoorOrder = ref<DoorOrder>(props.doorOrder || 'sequential');
const localDoorPositions = ref<number[] | null>(props.doorPositions);
const isShuffling = ref(false);

// Preview: Show first 5 door positions
const previewPositions = computed(() => {
  if (!localDoorPositions.value) return [];
  return localDoorPositions.value.slice(0, Math.min(5, localDoorPositions.value.length));
});

// Watch props for external changes (e.g., from API response)
watch(() => props.doorOrder, (newOrder) => {
  if (newOrder) localDoorOrder.value = newOrder;
});

watch(() => props.doorPositions, (newPositions) => {
  localDoorPositions.value = newPositions;
});

/**
 * Handle door order change (sequential <-> random toggle)
 *
 * When user selects sequential: Clear door positions
 * When user selects random: Generate new shuffled positions
 */
const handleOrderChange = (event: CustomEvent) => {
  const newOrder = event.detail.value as DoorOrder;
  localDoorOrder.value = newOrder;

  if (newOrder === 'sequential') {
    // Sequential: No positions array needed
    localDoorPositions.value = null;
    emit('update', { doorOrder: 'sequential', doorPositions: null });
  } else {
    // Random: Generate shuffled positions immediately
    handleShuffleAgain();
  }
};

/**
 * Handle shuffle again button click
 *
 * Generates new random door positions using Fisher-Yates algorithm.
 * Adds small delay for visual feedback.
 */
const handleShuffleAgain = () => {
  isShuffling.value = true;

  // Small delay for visual feedback (shows "Shuffling..." state)
  setTimeout(() => {
    try {
      // Generate new shuffled positions using Fisher-Yates algorithm
      const shuffled = generateShuffledPositions(props.duration);
      localDoorPositions.value = shuffled;

      // Emit update event to parent component
      emit('update', {
        doorOrder: 'random',
        doorPositions: shuffled
      });
    } catch (error) {
      console.error('Error shuffling positions:', error);
      // On error, fallback to sequential
      localDoorOrder.value = 'sequential';
      localDoorPositions.value = null;
      emit('update', { doorOrder: 'sequential', doorPositions: null });
    } finally {
      isShuffling.value = false;
    }
  }, 200);
};
</script>

<style scoped>
/* Container styling */
.door-order-toggle {
  padding: var(--spacing-md);
  background: var(--color-surface);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-border);
  margin-bottom: var(--spacing-md);
}

/* Section header */
.section-header {
  margin-bottom: var(--spacing-md);
}

.section-header h3 {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-xs) 0;
}

.help-text {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.5;
}

.locked-message {
  font-size: var(--font-size-sm);
  color: var(--color-warning);
  margin: 0;
  font-weight: var(--font-weight-medium);
  line-height: 1.5;
}

/* Segment styling */
.door-order-segment {
  margin-bottom: var(--spacing-md);
  --background: var(--color-background);
}

.segment-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-xs) 0;
  min-height: 44px; /* NFR [U2]: Touch-friendly */
  justify-content: center;
}

.segment-content ion-icon {
  font-size: 24px;
  color: var(--color-text-secondary);
}

.segment-content span {
  font-weight: var(--font-weight-medium);
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
}

.segment-content small {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

/* Active segment styling */
ion-segment-button::part(indicator-background) {
  background: var(--ion-color-primary);
}

ion-segment-button.segment-button-checked .segment-content ion-icon {
  color: var(--ion-color-primary);
}

ion-segment-button.segment-button-checked .segment-content span {
  color: var(--ion-color-primary);
  font-weight: var(--font-weight-bold);
}

/* Shuffle button */
.shuffle-button {
  --padding-top: 12px;
  --padding-bottom: 12px;
  --border-radius: var(--border-radius-md);
  font-weight: var(--font-weight-medium);
  margin-top: var(--spacing-sm);
  min-height: 44px; /* NFR [U2]: Touch-friendly */
}

.shuffle-button ion-icon {
  margin-right: var(--spacing-xs);
}

/* Positions preview */
.positions-preview {
  margin-top: var(--spacing-md);
  padding: var(--spacing-sm);
  background: var(--color-background);
  border-radius: var(--border-radius-md);
  border: 1px dashed var(--color-border);
}

.positions-preview small {
  display: block;
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-xs);
  font-weight: var(--font-weight-medium);
}

.preview-chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
}

.preview-chip {
  display: inline-block;
  padding: 4px 8px;
  background: var(--ion-color-primary-tint);
  color: var(--ion-color-primary);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  white-space: nowrap;
}

/* Accessibility - disabled state (NFR [U5]) */
ion-segment[disabled] {
  opacity: 0.5;
  pointer-events: none;
  cursor: not-allowed;
}

ion-segment-button[disabled] {
  opacity: 0.5;
}

/* Responsive design (NFR [U1]: 320px+ screens) */
@media (max-width: 480px) {
  .door-order-toggle {
    padding: var(--spacing-sm);
  }

  .segment-content {
    padding: var(--spacing-xs);
  }

  .segment-content ion-icon {
    font-size: 20px;
  }

  .segment-content span {
    font-size: var(--font-size-sm);
  }

  .segment-content small {
    font-size: 10px;
  }

  .preview-chips {
    font-size: 11px;
  }
}

@media (min-width: 768px) {
  .door-order-toggle {
    padding: var(--spacing-lg);
  }
}

/* Focus indicators for keyboard navigation (NFR [U5]: Accessibility) */
ion-segment-button:focus {
  outline: 2px solid var(--ion-color-primary);
  outline-offset: 2px;
}

.shuffle-button:focus {
  outline: 2px solid var(--ion-color-primary);
  outline-offset: 2px;
}

/* Dark theme support */
@media (prefers-color-scheme: dark) {
  .door-order-toggle {
    background: var(--ion-color-step-50);
    border-color: var(--ion-color-step-150);
  }

  .positions-preview {
    background: var(--ion-color-step-100);
    border-color: var(--ion-color-step-200);
  }
}
</style>
