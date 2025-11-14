/**
 * Fisher-Yates Shuffle Algorithm for Door Ordering (Issue #81)
 *
 * This module provides functions for randomizing door positions in advent calendars.
 * Used when users select "random" door ordering for shared calendars.
 *
 * NFR Compliance:
 * - [P3] Performance: O(n) time complexity - very fast even for 31 days
 * - [SC3] Modularity: Pure functions with no side effects, highly reusable
 * - [S4] Input Validation: Validates duration parameter
 */

/**
 * Generate shuffled door positions using Fisher-Yates algorithm
 *
 * The Fisher-Yates shuffle is an unbiased shuffling algorithm that produces
 * a uniformly random permutation of an array in O(n) time.
 *
 * Algorithm steps:
 * 1. Start from the last element
 * 2. Pick a random element from the remaining unshuffled elements
 * 3. Swap it with the current element
 * 4. Move to the previous element and repeat
 *
 * @param duration Number of days in the calendar (1-31)
 * @returns Shuffled array of day numbers [1...duration] in random order
 * @throws Error if duration is invalid
 *
 * @example
 * generateShuffledPositions(5)
 * // Returns: [3, 1, 5, 2, 4] (example random order)
 *
 * generateShuffledPositions(24)
 * // Returns: [15, 3, 24, 1, 7, 19, ...] (example 24-day shuffle)
 *
 * NFR [P3]: Time Complexity: O(n), Space Complexity: O(n)
 * NFR [S4]: Validates input duration is between 1-31
 */
export function generateShuffledPositions(duration: number): number[] {
  // Input validation (NFR [S4]: Input validation)
  if (!Number.isInteger(duration) || duration < 1 || duration > 31) {
    throw new Error('Duration must be an integer between 1 and 31');
  }

  // Create sequential array [1, 2, 3, ..., duration]
  const positions = Array.from({ length: duration }, (_, i) => i + 1);

  // Fisher-Yates shuffle algorithm
  // Start from the end and swap with random earlier element
  for (let i = positions.length - 1; i > 0; i--) {
    // Pick random index from 0 to i (inclusive)
    const j = Math.floor(Math.random() * (i + 1));

    // Swap elements at positions i and j
    [positions[i], positions[j]] = [positions[j], positions[i]];
  }

  return positions;
}

/**
 * Check if door positions array represents sequential order
 *
 * Used to detect if "random" positions are actually sequential,
 * which might happen by chance or due to implementation bugs.
 *
 * @param positions Array of door positions to check
 * @param duration Expected length and maximum value
 * @returns true if positions are [1, 2, 3, ..., duration], false otherwise
 *
 * @example
 * arePositionsSequential([1, 2, 3, 4, 5], 5) // true
 * arePositionsSequential([3, 1, 5, 2, 4], 5) // false
 * arePositionsSequential([1, 2], 5)          // false (wrong length)
 *
 * NFR [P3]: Time Complexity: O(n)
 */
export function arePositionsSequential(positions: number[], duration: number): boolean {
  // Check array exists and has correct length
  if (!positions || !Array.isArray(positions) || positions.length !== duration) {
    return false;
  }

  // Check each position matches expected sequential value
  for (let i = 0; i < duration; i++) {
    if (positions[i] !== i + 1) {
      return false;
    }
  }

  return true;
}

/**
 * Validate door positions array for correctness
 *
 * Ensures door positions:
 * - Contains exactly `duration` elements
 * - Contains all numbers from 1 to `duration` (no duplicates, no missing)
 * - All elements are valid integers
 *
 * @param positions Array of door positions to validate
 * @param duration Expected length of array
 * @returns Object with isValid boolean and error message if invalid
 *
 * @example
 * validateDoorPositions([3, 1, 5, 2, 4], 5)
 * // { isValid: true, error: null }
 *
 * validateDoorPositions([1, 1, 2, 3], 4)
 * // { isValid: false, error: "Duplicate day number: 1" }
 *
 * validateDoorPositions([1, 2, 3], 5)
 * // { isValid: false, error: "Array length (3) does not match duration (5)" }
 *
 * NFR [S4]: Input validation for door positions
 * NFR [P3]: Time Complexity: O(n)
 */
export function validateDoorPositions(
  positions: number[],
  duration: number
): { isValid: boolean; error: string | null } {
  // Check if positions is an array
  if (!Array.isArray(positions)) {
    return { isValid: false, error: 'Door positions must be an array' };
  }

  // Check length matches duration
  if (positions.length !== duration) {
    return {
      isValid: false,
      error: `Array length (${positions.length}) does not match duration (${duration})`
    };
  }

  // Check all elements are valid integers between 1 and duration
  const seen = new Set<number>();
  for (let i = 0; i < positions.length; i++) {
    const day = positions[i];

    // Check if integer
    if (!Number.isInteger(day)) {
      return { isValid: false, error: `Invalid day number at position ${i}: ${day}` };
    }

    // Check if in valid range
    if (day < 1 || day > duration) {
      return {
        isValid: false,
        error: `Day number ${day} is out of range (1-${duration})`
      };
    }

    // Check for duplicates
    if (seen.has(day)) {
      return { isValid: false, error: `Duplicate day number: ${day}` };
    }

    seen.add(day);
  }

  // If we got here, all days from 1 to duration are present exactly once
  return { isValid: true, error: null };
}
