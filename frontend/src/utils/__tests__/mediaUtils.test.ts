/**
 * Unit Tests for Media Utilities
 *
 * Tests all media formatting functions with comprehensive edge cases.
 * These tests ensure reliable file size and duration formatting across the app.
 *
 * Coverage targets:
 * - formatFileSize(): Converts bytes to human-readable format (Bytes, KB, MB, GB)
 * - formatDuration(): Converts seconds to MM:SS format
 * - formatFileSizeMB(): Always displays file size in MB
 *
 * Run with: npm run test:unit src/utils/__tests__/mediaUtils.test.ts
 */

import {
  formatFileSize,
  formatDuration,
  formatFileSizeMB
} from '../mediaUtils';

describe('Media Utilities', () => {
  /**
   * Test Suite: formatFileSize()
   *
   * This function converts byte values to human-readable format.
   * It automatically selects the appropriate unit (Bytes, KB, MB, GB).
   */
  describe('formatFileSize', () => {
    describe('Zero and small values', () => {
      it('should format zero bytes correctly', () => {
        expect(formatFileSize(0)).toBe('0 Bytes');
      });

      it('should format bytes less than 1 KB', () => {
        expect(formatFileSize(100)).toBe('100 Bytes');
        expect(formatFileSize(512)).toBe('512 Bytes');
        expect(formatFileSize(1023)).toBe('1023 Bytes');
      });
    });

    describe('Kilobyte values', () => {
      it('should format KB values correctly', () => {
        expect(formatFileSize(1024)).toBe('1 KB'); // Exactly 1 KB
        expect(formatFileSize(2048)).toBe('2 KB'); // Exactly 2 KB
        expect(formatFileSize(10240)).toBe('10 KB'); // 10 KB
      });

      it('should format KB with decimal precision', () => {
        expect(formatFileSize(1536)).toBe('1.5 KB'); // 1.5 KB
        expect(formatFileSize(2560)).toBe('2.5 KB'); // 2.5 KB
      });
    });

    describe('Megabyte values', () => {
      it('should format MB values correctly', () => {
        expect(formatFileSize(1048576)).toBe('1 MB'); // Exactly 1 MB
        expect(formatFileSize(5242880)).toBe('5 MB'); // 5 MB
        expect(formatFileSize(52428800)).toBe('50 MB'); // 50 MB
      });

      it('should format MB with decimal precision', () => {
        expect(formatFileSize(1572864)).toBe('1.5 MB'); // 1.5 MB
        expect(formatFileSize(10485760)).toBe('10 MB'); // 10 MB
      });
    });

    describe('Gigabyte values', () => {
      it('should format GB values correctly', () => {
        expect(formatFileSize(1073741824)).toBe('1 GB'); // Exactly 1 GB
        expect(formatFileSize(2147483648)).toBe('2 GB'); // 2 GB
      });

      it('should format GB with decimal precision', () => {
        expect(formatFileSize(1610612736)).toBe('1.5 GB'); // 1.5 GB
      });
    });

    describe('Edge cases', () => {
      it('should handle very small positive values', () => {
        expect(formatFileSize(1)).toBe('1 Bytes');
      });

      it('should handle large file sizes', () => {
        // 10 GB
        const tenGB = 10 * 1024 * 1024 * 1024;
        expect(formatFileSize(tenGB)).toBe('10 GB');
      });

      it('should round to 2 decimal places', () => {
        // 1.234 MB = 1294131 bytes
        expect(formatFileSize(1294131)).toBe('1.23 MB');
      });
    });
  });

  /**
   * Test Suite: formatDuration()
   *
   * This function converts seconds to MM:SS format.
   * Minutes are not zero-padded, seconds always have 2 digits.
   */
  describe('formatDuration', () => {
    describe('Zero and small values', () => {
      it('should format zero seconds correctly', () => {
        expect(formatDuration(0)).toBe('0:00');
      });

      it('should format seconds less than a minute', () => {
        expect(formatDuration(5)).toBe('0:05');
        expect(formatDuration(30)).toBe('0:30');
        expect(formatDuration(59)).toBe('0:59');
      });
    });

    describe('Minute values', () => {
      it('should format exactly one minute', () => {
        expect(formatDuration(60)).toBe('1:00');
      });

      it('should format multiple minutes without seconds', () => {
        expect(formatDuration(120)).toBe('2:00');
        expect(formatDuration(300)).toBe('5:00');
        expect(formatDuration(600)).toBe('10:00');
      });

      it('should format minutes with seconds', () => {
        expect(formatDuration(90)).toBe('1:30');
        expect(formatDuration(125)).toBe('2:05');
        expect(formatDuration(185)).toBe('3:05');
      });
    });

    describe('Hour values (displayed as large minutes)', () => {
      it('should format duration over an hour', () => {
        expect(formatDuration(3600)).toBe('60:00'); // 1 hour
        expect(formatDuration(3665)).toBe('61:05'); // 1 hour 1 min 5 sec
        expect(formatDuration(7200)).toBe('120:00'); // 2 hours
      });
    });

    describe('Video length examples (realistic use cases)', () => {
      it('should format typical video durations', () => {
        expect(formatDuration(15)).toBe('0:15'); // 15-second clip
        expect(formatDuration(45)).toBe('0:45'); // 45-second intro
        expect(formatDuration(180)).toBe('3:00'); // 3-minute video (max allowed)
      });
    });

    describe('Edge cases', () => {
      it('should handle 1 second', () => {
        expect(formatDuration(1)).toBe('0:01');
      });

      it('should pad single-digit seconds with zero', () => {
        expect(formatDuration(61)).toBe('1:01');
        expect(formatDuration(605)).toBe('10:05');
      });

      it('should handle large durations', () => {
        expect(formatDuration(6000)).toBe('100:00'); // 100 minutes
      });
    });
  });

  /**
   * Test Suite: formatFileSizeMB()
   *
   * This function always displays file size in MB (megabytes).
   * Useful for consistent display in upload limits.
   */
  describe('formatFileSizeMB', () => {
    describe('Zero and small values', () => {
      it('should format zero bytes as 0 MB', () => {
        expect(formatFileSizeMB(0)).toBe('0 MB');
      });

      it('should format small byte values as MB', () => {
        expect(formatFileSizeMB(1024)).toBe('0 MB'); // Less than 1 MB rounds to 0
        expect(formatFileSizeMB(524288)).toBe('1 MB'); // 0.5 MB rounds to 1
      });
    });

    describe('Megabyte values', () => {
      it('should format exact MB values', () => {
        expect(formatFileSizeMB(1048576)).toBe('1 MB'); // Exactly 1 MB
        expect(formatFileSizeMB(5242880)).toBe('5 MB'); // Exactly 5 MB
        expect(formatFileSizeMB(10485760)).toBe('10 MB'); // Exactly 10 MB
      });

      it('should format upload limit values', () => {
        expect(formatFileSizeMB(52428800)).toBe('50 MB'); // Max upload size
      });
    });

    describe('Rounding behavior', () => {
      it('should round to nearest integer', () => {
        expect(formatFileSizeMB(1572864)).toBe('2 MB'); // 1.5 MB rounds to 2
        expect(formatFileSizeMB(2097152)).toBe('2 MB'); // Exactly 2 MB
        expect(formatFileSizeMB(2621440)).toBe('3 MB'); // 2.5 MB rounds to 3 (standard rounding)
        expect(formatFileSizeMB(3145728)).toBe('3 MB'); // 3 MB
      });
    });

    describe('Large file sizes', () => {
      it('should handle very large files', () => {
        expect(formatFileSizeMB(104857600)).toBe('100 MB'); // 100 MB
        expect(formatFileSizeMB(1073741824)).toBe('1024 MB'); // 1 GB displayed as MB
      });
    });

    describe('Edge cases', () => {
      it('should handle 1 byte', () => {
        expect(formatFileSizeMB(1)).toBe('0 MB');
      });

      it('should handle values just under 1 MB', () => {
        expect(formatFileSizeMB(1048575)).toBe('1 MB'); // 1 byte less than 1 MB
      });
    });
  });

  /**
   * Cross-function consistency tests
   *
   * These tests ensure the functions work well together and
   * produce consistent results for the same inputs.
   */
  describe('Cross-function consistency', () => {
    it('formatFileSize and formatFileSizeMB should be consistent for MB values', () => {
      const fiveMB = 5242880;
      expect(formatFileSize(fiveMB)).toBe('5 MB');
      expect(formatFileSizeMB(fiveMB)).toBe('5 MB');
    });

    it('should handle realistic video file scenarios', () => {
      // Typical 3-minute video at 50 MB (max allowed)
      const maxVideoSize = 52428800;
      expect(formatFileSize(maxVideoSize)).toBe('50 MB');
      expect(formatFileSizeMB(maxVideoSize)).toBe('50 MB');

      const videoDuration = 180; // 3 minutes
      expect(formatDuration(videoDuration)).toBe('3:00');
    });
  });
});
