/**
 * Structured Logging Utility
 *
 * Provides consistent, structured logging across the frontend application.
 * Replaces scattered console.log() and console.error() calls with a centralized system.
 *
 * Benefits:
 * - Consistent log format across the app
 * - Easy to disable/enable logging by environment
 * - Structured data for easier debugging
 * - Can be extended to send logs to monitoring services
 * - Performance insights with timestamps
 * - Context-rich error reporting
 *
 * Usage:
 * ```typescript
 * import { logger } from '@/utils/logger';
 *
 * logger.info('User logged in', { userId: '123', email: 'user@example.com' });
 * logger.error('API call failed', { endpoint: '/api/calendars', error });
 * logger.debug('Rendering calendar', { calendarId: 'cal-456' });
 * ```
 */

/**
 * Log level enumeration
 */
export enum LogLevel {
  DEBUG = 'DEBUG',
  INFO = 'INFO',
  WARN = 'WARN',
  ERROR = 'ERROR'
}

/**
 * Log entry interface
 */
interface LogEntry {
  level: LogLevel;
  message: string;
  timestamp: string;
  data?: Record<string, unknown>;
  stack?: string;
}

/**
 * Logger configuration
 */
interface LoggerConfig {
  /** Whether logging is enabled */
  enabled: boolean;
  /** Minimum log level to display */
  minLevel: LogLevel;
  /** Whether to include timestamps */
  includeTimestamp: boolean;
  /** Whether to include stack traces for errors */
  includeStackTrace: boolean;
}

/**
 * Default logger configuration
 * - Enabled in development, disabled in production (can be overridden)
 * - INFO level and above in production
 * - DEBUG level and above in development
 */
const defaultConfig: LoggerConfig = {
  enabled: !import.meta.env.PROD,
  minLevel: import.meta.env.PROD ? LogLevel.INFO : LogLevel.DEBUG,
  includeTimestamp: true,
  includeStackTrace: true
};

/**
 * Current logger configuration
 */
let config: LoggerConfig = { ...defaultConfig };

/**
 * Log level priority (for filtering)
 */
const levelPriority: Record<LogLevel, number> = {
  [LogLevel.DEBUG]: 0,
  [LogLevel.INFO]: 1,
  [LogLevel.WARN]: 2,
  [LogLevel.ERROR]: 3
};

/**
 * Format log entry for console output
 */
function formatLogEntry(entry: LogEntry): string[] {
  const parts: string[] = [];

  // Timestamp
  if (config.includeTimestamp) {
    parts.push(`[${entry.timestamp}]`);
  }

  // Log level with color coding
  parts.push(`[${entry.level}]`);

  // Message
  parts.push(entry.message);

  return parts;
}

/**
 * Get console method for log level
 */
function getConsoleMethod(level: LogLevel): (...args: unknown[]) => void {
  switch (level) {
    case LogLevel.DEBUG:
      return console.debug;
    case LogLevel.INFO:
      return console.info;
    case LogLevel.WARN:
      return console.warn;
    case LogLevel.ERROR:
      return console.error;
    default:
      return console.log;
  }
}

/**
 * Get color for log level (for browser console)
 */
function getLogLevelColor(level: LogLevel): string {
  switch (level) {
    case LogLevel.DEBUG:
      return 'color: #9E9E9E'; // Gray
    case LogLevel.INFO:
      return 'color: #2196F3'; // Blue
    case LogLevel.WARN:
      return 'color: #FF9800'; // Orange
    case LogLevel.ERROR:
      return 'color: #F44336'; // Red
    default:
      return 'color: #000000'; // Black
  }
}

/**
 * Internal log function
 */
function log(level: LogLevel, message: string, data?: Record<string, unknown>): void {
  // Check if logging is enabled
  if (!config.enabled) {
    return;
  }

  // Check log level
  if (levelPriority[level] < levelPriority[config.minLevel]) {
    return;
  }

  // Create log entry
  const entry: LogEntry = {
    level,
    message,
    timestamp: new Date().toISOString(),
    data
  };

  // Add stack trace for errors
  if (level === LogLevel.ERROR && config.includeStackTrace) {
    entry.stack = new Error().stack;
  }

  // Format and output
  const formattedParts = formatLogEntry(entry);
  const consoleMethod = getConsoleMethod(level);

  // Use styled console output in browser
  if (typeof window !== 'undefined') {
    consoleMethod(
      `%c${formattedParts[0]} %c${formattedParts[1]} %c${formattedParts[2]}`,
      'color: #9E9E9E',
      getLogLevelColor(level),
      'color: inherit'
    );

    // Log data object if provided
    if (data && Object.keys(data).length > 0) {
      consoleMethod('Data:', data);
    }

    // Log stack trace if available
    if (entry.stack) {
      consoleMethod('Stack:', entry.stack);
    }
  } else {
    // Plain output for non-browser environments
    consoleMethod(...formattedParts);
    if (data) {
      consoleMethod('Data:', data);
    }
  }
}

/**
 * Logger class with public API
 */
class Logger {
  /**
   * Log debug message (lowest priority)
   * Use for detailed debugging information
   */
  debug(message: string, data?: Record<string, unknown>): void {
    log(LogLevel.DEBUG, message, data);
  }

  /**
   * Log info message (normal priority)
   * Use for general informational messages
   */
  info(message: string, data?: Record<string, unknown>): void {
    log(LogLevel.INFO, message, data);
  }

  /**
   * Log warning message (high priority)
   * Use for potentially harmful situations
   */
  warn(message: string, data?: Record<string, unknown>): void {
    log(LogLevel.WARN, message, data);
  }

  /**
   * Log error message (highest priority)
   * Use for error events that might still allow the app to continue
   */
  error(message: string, data?: Record<string, unknown>): void {
    log(LogLevel.ERROR, message, data);
  }

  /**
   * Update logger configuration
   */
  configure(newConfig: Partial<LoggerConfig>): void {
    config = { ...config, ...newConfig };
  }

  /**
   * Get current logger configuration
   */
  getConfig(): LoggerConfig {
    return { ...config };
  }

  /**
   * Reset logger configuration to defaults
   */
  resetConfig(): void {
    config = { ...defaultConfig };
  }

  /**
   * Enable logging
   */
  enable(): void {
    config.enabled = true;
  }

  /**
   * Disable logging
   */
  disable(): void {
    config.enabled = false;
  }
}

/**
 * Singleton logger instance
 */
export const logger = new Logger();

/**
 * Default export for convenience
 */
export default logger;
