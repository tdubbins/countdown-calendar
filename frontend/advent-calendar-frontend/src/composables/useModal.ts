/**
 * useModal Composable
 *
 * Provides reusable modal state management for components.
 * Simplifies modal open/close logic and item selection patterns.
 *
 * Benefits:
 * - DRY principle: Eliminates repeated modal state boilerplate
 * - Type safety: Generic type parameter for selected items
 * - Consistency: Same modal patterns across the app
 * - Simplicity: Reduces ~15 lines of code per modal
 *
 * Usage example:
 * ```typescript
 * // Without item selection
 * const createModal = useModal();
 * createModal.open(); // Opens modal
 * createModal.close(); // Closes modal
 *
 * // With item selection (e.g., edit modal)
 * interface Calendar { id: string; title: string; }
 * const editModal = useModal<Calendar>();
 *
 * // Open with item
 * editModal.open({ id: '1', title: 'My Calendar' });
 *
 * // Access selected item in template
 * <CalendarForm v-if="editModal.selectedItem.value" :calendar="editModal.selectedItem.value" />
 *
 * // Close and clear
 * editModal.close(); // Clears selectedItem automatically
 * ```
 */

import { ref, type Ref } from 'vue';

/**
 * Modal state interface
 */
export interface ModalState<T = any> {
  isOpen: Ref<boolean>;
  selectedItem: Ref<T | null>;
  open: (item?: T) => void;
  close: () => void;
  toggle: (item?: T) => void;
}

/**
 * useModal Composable
 *
 * Creates a modal state manager with open/close functionality
 * and optional item selection.
 *
 * @template T - Type of item to select when opening modal
 * @returns Modal state object with reactive properties and methods
 *
 * @example
 * // Simple modal (no item selection)
 * const modal = useModal();
 * modal.open();
 * modal.close();
 *
 * @example
 * // Modal with item selection
 * interface User { id: number; name: string; }
 * const userModal = useModal<User>();
 *
 * // Open with specific user
 * userModal.open({ id: 1, name: 'John' });
 *
 * // In template
 * <ion-modal :is-open="userModal.isOpen.value" @didDismiss="userModal.close">
 *   <UserForm v-if="userModal.selectedItem.value" :user="userModal.selectedItem.value" />
 * </ion-modal>
 */
export function useModal<T = any>(): ModalState<T> {
  /**
   * Reactive state for modal visibility
   */
  const isOpen = ref(false);

  /**
   * Reactive state for selected item (if any)
   * Null when no item is selected or modal is closed
   */
  const selectedItem = ref(null) as Ref<T | null>;

  /**
   * Open the modal
   *
   * Optionally pass an item to select when opening.
   * Useful for edit modals where you need to know which item to edit.
   *
   * @param item - Optional item to select when opening modal
   */
  const open = (item?: T): void => {
    selectedItem.value = item || null;
    isOpen.value = true;
  };

  /**
   * Close the modal
   *
   * Automatically clears the selected item to prevent stale data.
   * Always call this method instead of directly setting isOpen to false.
   */
  const close = (): void => {
    isOpen.value = false;
    selectedItem.value = null;
  };

  /**
   * Toggle modal open/closed
   *
   * If opening, optionally pass an item to select.
   * If closing, automatically clears selected item.
   *
   * @param item - Optional item to select when toggling open
   */
  const toggle = (item?: T): void => {
    if (isOpen.value) {
      close();
    } else {
      open(item);
    }
  };

  return {
    isOpen,
    selectedItem,
    open,
    close,
    toggle
  };
}

/**
 * Usage Examples
 *
 * 1. Simple confirmation modal:
 * ```typescript
 * const deleteModal = useModal();
 *
 * <ion-button @click="deleteModal.open()">Delete</ion-button>
 * <ion-modal :is-open="deleteModal.isOpen.value" @didDismiss="deleteModal.close">
 *   <p>Are you sure?</p>
 * </ion-modal>
 * ```
 *
 * 2. Edit modal with item:
 * ```typescript
 * interface Calendar { id: string; title: string; }
 * const editModal = useModal<Calendar>();
 *
 * const handleEdit = (calendar: Calendar) => {
 *   editModal.open(calendar);
 * };
 *
 * <ion-modal :is-open="editModal.isOpen.value" @didDismiss="editModal.close">
 *   <CalendarForm
 *     v-if="editModal.selectedItem.value"
 *     :calendar="editModal.selectedItem.value"
 *     @submit="handleSubmit"
 *   />
 * </ion-modal>
 * ```
 *
 * 3. Upload modal with day selection:
 * ```typescript
 * const uploadModal = useModal<number>(); // number = day number
 *
 * const handleDayClick = (day: number) => {
 *   uploadModal.open(day);
 * };
 *
 * <ion-modal :is-open="uploadModal.isOpen.value" @didDismiss="uploadModal.close">
 *   <VideoUpload
 *     v-if="uploadModal.selectedItem.value !== null"
 *     :day="uploadModal.selectedItem.value"
 *   />
 * </ion-modal>
 * ```
 */
