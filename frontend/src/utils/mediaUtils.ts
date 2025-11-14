/**
 * Media Utilities
 *
 * Shared utility functions for handling media files (video/audio).
 * Provides consistent formatting for file sizes, durations, and other media metadata.
 *
 * Benefits:
 * - DRY principle: Single source of truth for media formatting
 * - Consistency: Same formatting across all components
 * - Maintainability: Update formatting logic in one place
 * - Testability: Easy to unit test isolated functions
 */

/**
 * Format file size from bytes to human-readable format
 *
 * Converts byte values to appropriate units (Bytes, KB, MB, GB)
 * with 2 decimal precision.
 *
 * @param bytes - File size in bytes
 * @returns Formatted string (e.g., "1.5 MB", "320 KB")
 *
 * @example
 * formatFileSize(0)           // "0 Bytes"
 * formatFileSize(1024)        // "1 KB"
 * formatFileSize(1572864)     // "1.5 MB"
 * formatFileSize(1073741824)  // "1 GB"
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
};

/**
 * Format video duration from seconds to MM:SS format
 *
 * Converts duration in seconds to a human-readable time format.
 * Minutes are not zero-padded, seconds are always 2 digits.
 *
 * @param seconds - Duration in seconds
 * @returns Formatted string (e.g., "0:00", "1:30", "12:45")
 *
 * @example
 * formatDuration(0)    // "0:00"
 * formatDuration(30)   // "0:30"
 * formatDuration(90)   // "1:30"
 * formatDuration(3665) // "61:05"
 */
export const formatDuration = (seconds: number): string => {
  if (seconds === 0) return '0:00';

  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);

  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

/**
 * Format file size specifically for MB display (simplified version)
 *
 * Always returns size in MB, rounded to nearest integer.
 * Useful when you always want MB units for consistency.
 *
 * @param bytes - File size in bytes
 * @returns Formatted string (e.g., "0 MB", "15 MB", "250 MB")
 *
 * @example
 * formatFileSizeMB(0)          // "0 MB"
 * formatFileSizeMB(5242880)    // "5 MB"
 * formatFileSizeMB(52428800)   // "50 MB"
 */
export const formatFileSizeMB = (bytes: number): string => {
  if (bytes === 0) return '0 MB';
  const mb = bytes / (1024 * 1024);
  return `${Math.round(mb)} MB`;
};
