<template>
  <div 
    v-if="password"
    class="password-requirements"
    id="password-requirements"
    role="region"
    aria-label="Password requirements"
    aria-live="polite"
    aria-atomic="true"
  >
    <!-- Show summary when all requirements are met -->
    <div v-if="allRequirementsMet" class="requirements-summary">
      <ion-icon :icon="checkmarkCircle" class="success-icon" aria-hidden="true"></ion-icon>
      <span>Password requirements met</span>
    </div>

    <!-- Show detailed requirements when password is incomplete -->
    <div v-else>
      <p class="requirements-title">Password requirements:</p>
      <div class="requirements-grid" role="list">
        <div
          v-for="requirement in requirements"
          :key="requirement.key"
          :class="{'requirement-met': requirement.met, 'requirement': true}"
          role="listitem"
          :aria-label="requirement.met ? 'Requirement met: ' + requirement.text : 'Requirement not met: ' + requirement.text"
        >
          <ion-icon
            :icon="requirement.met ? checkmarkCircle : ellipseOutline"
            aria-hidden="true"
          ></ion-icon>
          {{ requirement.text }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { IonIcon } from '@ionic/vue';
import { checkmarkCircle, ellipseOutline } from 'ionicons/icons';

// Props
interface Props {
  password: string;
}

const props = defineProps<Props>();

// Password validation computed properties
const hasMinLength = computed(() => props.password.length >= 8);
const hasUppercase = computed(() => /[A-Z]/.test(props.password));
const hasLowercase = computed(() => /[a-z]/.test(props.password));
const hasNumber = computed(() => /\d/.test(props.password));

const allRequirementsMet = computed(() => 
  hasMinLength.value && hasUppercase.value && hasLowercase.value && hasNumber.value
);

const requirements = computed(() => [
  { key: 'length', met: hasMinLength.value, text: '8+ characters' },
  { key: 'uppercase', met: hasUppercase.value, text: 'Uppercase letter' },
  { key: 'lowercase', met: hasLowercase.value, text: 'Lowercase letter' },
  { key: 'number', met: hasNumber.value, text: 'Number' }
]);

// Expose computed for parent component
defineExpose({
  isValid: allRequirementsMet
});
</script>

<style scoped>
.password-requirements {
  margin: 20px 0;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e9ecef;
  animation: fadeInUp 0.6s ease-out;
}

.requirements-title {
  font-weight: 600;
  margin-bottom: 12px;
  font-size: 0.9rem;
  color: #495057;
}

.requirements-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.requirement {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: #6c757d;
  padding: 4px 0;
  transition: all 0.3s ease;
}

.requirement ion-icon {
  font-size: 1rem;
  color: #dee2e6;
}

.requirement-met {
  color: var(--ion-color-success) !important;
  font-weight: 600;
}

.requirement-met ion-icon {
  color: var(--ion-color-success) !important;
}

/* Requirements summary when complete */
.requirements-summary {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #d1f2d1;
  color: #0f5132;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  border: 1px solid #a3d977;
  animation: fadeInScale 0.3s ease-out;
}

.success-icon {
  font-size: 1.2rem;
  color: var(--ion-color-success);
}

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

@keyframes fadeInScale {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>