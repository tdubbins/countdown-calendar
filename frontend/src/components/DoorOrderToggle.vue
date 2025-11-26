<template>
  <div class="door-order-toggle">
    <!-- Unlocked: Interactive segment control -->
    <template v-if="!isLocked">
      <ion-segment
        :value="localDoorOrder"
        @ionChange="handleOrderChange"
      >
        <ion-segment-button value="sequential">
          <ion-label>Sequential</ion-label>
        </ion-segment-button>
        <ion-segment-button value="random">
          <ion-label>Random</ion-label>
        </ion-segment-button>
      </ion-segment>
    </template>

    <!-- Locked: Read-only display with lock indicator -->
    <template v-else>
      <ion-chip color="warning" outline class="locked-chip">
        <ion-icon :icon="lockClosedOutline" aria-hidden="true"></ion-icon>
        <ion-label>
          Door Order: {{ localDoorOrder === 'sequential' ? 'Sequential' : 'Random' }} (locked after sharing)
        </ion-label>
      </ion-chip>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import {
  IonSegment,
  IonSegmentButton,
  IonChip,
  IonLabel,
  IonIcon
} from '@ionic/vue';
import { lockClosedOutline } from 'ionicons/icons';
import { generateShuffledPositions } from '@/utils/shuffle';
import type { DoorOrder } from '@/types/calendar';

/**
 * Door Order Toggle Component
 *
 * Allows calendar creators to choose how doors appear in shared calendars:
 * - Sequential: Doors appear in order 1, 2, 3, ...
 * - Random: Doors appear in shuffled order
 *
 * Locked after share token is generated for consistent viewer experience.
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


// Watch props for external changes (e.g., from API response)
watch(() => props.doorOrder, (newOrder) => {
  if (newOrder) localDoorOrder.value = newOrder;
});

watch(() => props.doorPositions, (newPositions) => {
  localDoorPositions.value = newPositions;
});

/**
 * Handle door order change (segment selection)
 *
 * When user selects sequential: Clear door positions
 * When user selects random: Generate new shuffled positions
 */
const handleOrderChange = (event: CustomEvent) => {
  const newOrder = event.detail.value as DoorOrder;
  localDoorOrder.value = newOrder;

  if (newOrder === 'sequential') {
    localDoorPositions.value = null;
    emit('update', { doorOrder: 'sequential', doorPositions: null });
  } else {
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
/* Container */
.door-order-toggle {
  margin-bottom: var(--spacing-md);
}

/* Ionic Segment Styling (Unlocked state) */
ion-segment {
  min-height: 40px;
  max-width: 300px;
}

/* Segment buttons - ensure touch-friendly size */
ion-segment-button {
  min-height: 40px;
  font-size: var(--font-size-base);
}

/* Locked chip - single chip with all info (non-interactive) */
.locked-chip {
  cursor: default !important;
  pointer-events: none !important; /* Disable all hover/click effects */
  font-size: var(--font-size-sm);
}
</style>
