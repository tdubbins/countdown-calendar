/**
 * Fisher-Yates Shuffle Algorithm for Door Ordering
 *
 * Provides functions for randomizing door positions in advent calendars.
 * Used when users select "random" door ordering for shared calendars.
 */

/**
 * Generate shuffled door positions using Fisher-Yates algorithm.
 *
 * @param duration Number of days in the calendar (1-31)
 * @returns Shuffled array of day numbers [1...duration] in random order
 * @throws Error if duration is invalid
 */
export function generateShuffledPositions(duration: number): number[] {
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
 * Check if door positions array represents sequential order.
 *
 * @param positions Array of door positions to check
 * @param duration Expected length and maximum value
 * @returns true if positions are [1, 2, 3, ..., duration], false otherwise
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
 * Validate door positions array for correctness.
 *
 * Ensures positions contains all numbers from 1 to duration exactly once.
 *
 * @param positions Array of door positions to validate
 * @param duration Expected length of array
 * @returns Object with isValid boolean and error message if invalid
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
