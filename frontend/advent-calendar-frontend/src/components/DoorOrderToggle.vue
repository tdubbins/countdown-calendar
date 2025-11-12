<template>
  <div class="door-order-toggle">
    <!-- Compact Label -->
    <label class="toggle-label">
      Door Order
      <ion-chip v-if="isLocked" color="warning" class="lock-chip">
        <ion-icon :icon="lockClosedOutline" aria-hidden="true"></ion-icon>
        <ion-label>Locked</ion-label>
      </ion-chip>
    </label>

    <!-- Chip-based Selection -->
    <div class="chip-group" role="radiogroup" aria-label="Door order selection">
      <!-- Sequential Chip -->
      <ion-chip
        :color="localDoorOrder === 'sequential' ? 'primary' : 'medium'"
        :outline="localDoorOrder !== 'sequential'"
        :disabled="isLocked"
        @click="selectOrder('sequential')"
        class="order-chip"
        role="radio"
        :aria-checked="localDoorOrder === 'sequential'"
        :aria-label="isLocked ? 'Sequential order (locked)' : 'Sequential order - doors appear in order 1, 2, 3'"
        tabindex="0"
        @keydown.enter="selectOrder('sequential')"
        @keydown.space.prevent="selectOrder('sequential')"
      >
        <ion-icon :icon="listOutline" aria-hidden="true"></ion-icon>
        <ion-label>Sequential</ion-label>
      </ion-chip>

      <!-- Random Chip -->
      <ion-chip
        :color="localDoorOrder === 'random' ? 'primary' : 'medium'"
        :outline="localDoorOrder !== 'random'"
        :disabled="isLocked"
        @click="selectOrder('random')"
        class="order-chip"
        role="radio"
        :aria-checked="localDoorOrder === 'random'"
        :aria-label="isLocked ? 'Random order (locked)' : 'Random order - doors appear shuffled'"
        tabindex="0"
        @keydown.enter="selectOrder('random')"
        @keydown.space.prevent="selectOrder('random')"
      >
        <ion-icon :icon="shuffleOutline" aria-hidden="true"></ion-icon>
        <ion-label>Random</ion-label>
      </ion-chip>

      <!-- Shuffle Button (only for random) -->
      <ion-chip
        v-if="localDoorOrder === 'random' && !isLocked"
        color="secondary"
        outline
        @click="handleShuffleAgain"
        :disabled="isShuffling"
        class="shuffle-chip"
        aria-label="Generate new random order for doors"
        tabindex="0"
        @keydown.enter="handleShuffleAgain"
        @keydown.space.prevent="handleShuffleAgain"
      >
        <ion-icon :icon="shuffleOutline" aria-hidden="true"></ion-icon>
        <ion-label>{{ isShuffling ? 'Shuffling...' : 'Shuffle' }}</ion-label>
      </ion-chip>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import {
  IonChip,
  IonLabel,
  IonIcon
} from '@ionic/vue';
import { listOutline, shuffleOutline, lockClosedOutline } from 'ionicons/icons';
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
 * Handle door order selection (chip click)
 *
 * When user selects sequential: Clear door positions
 * When user selects random: Generate new shuffled positions
 */
const selectOrder = (order: DoorOrder) => {
  if (props.isLocked || localDoorOrder.value === order) return;

  localDoorOrder.value = order;

  if (order === 'sequential') {
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
/* Minimal container */
.door-order-toggle {
  margin-bottom: var(--spacing-md);
}

/* Label with inline lock chip */
.toggle-label {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-xs);
}

.lock-chip {
  font-size: var(--font-size-xs);
  height: 24px;
}

/* Chip group - horizontal layout */
.chip-group {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
  align-items: center;
}

/* Order chips - clickable selection */
.order-chip {
  cursor: pointer;
  transition: transform 0.2s ease;
  min-height: 36px; /* NFR [U2]: Touch-friendly */
}

.order-chip:not([disabled]):hover {
  transform: scale(1.05);
}

.order-chip:not([disabled]):active {
  transform: scale(0.98);
}

/* Shuffle chip */
.shuffle-chip {
  cursor: pointer;
  transition: transform 0.2s ease;
  min-height: 36px; /* NFR [U2]: Touch-friendly */
}

.shuffle-chip:not([disabled]):hover {
  transform: scale(1.05);
}

.shuffle-chip:not([disabled]):active {
  transform: scale(0.98);
}

/* Disabled state (NFR [U5]: Accessibility) */
ion-chip[disabled] {
  opacity: 0.5;
  pointer-events: none;
  cursor: not-allowed;
}

/* Focus indicators for keyboard navigation (NFR [U5]) */
.order-chip:focus,
.shuffle-chip:focus {
  outline: 2px solid var(--ion-color-primary);
  outline-offset: 2px;
}

/* Responsive - ensure chips don't get too small */
@media (max-width: 480px) {
  .chip-group {
    gap: var(--spacing-xxs, 4px);
  }

  ion-chip {
    font-size: var(--font-size-xs);
  }
}
</style>
