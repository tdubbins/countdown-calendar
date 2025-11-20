/**
 * Theme Configuration
 *
 * Centralized configuration for all calendar themes.
 * Each theme defines:
 * - Display metadata (name, description)
 * - CSS class for styling
 * - Theme identifier for API storage
 */

export interface ThemeConfig {
  id: string;
  name: string;
  description: string;
  cssClass: string;
}

export const THEMES: Record<string, ThemeConfig> = {
  christmas: {
    id: 'christmas',
    name: 'Christmas',
    description: 'Wooden cabin doors with falling snow',
    cssClass: 'theme-christmas'
  },
  birthday: {
    id: 'birthday',
    name: 'Birthday',
    description: 'Gift boxes with floating balloons',
    cssClass: 'theme-birthday'
  },
  // Future themes
  // generic: {
  //   id: 'generic',
  //   name: 'Generic',
  //   description: 'Clean and minimal design',
  //   cssClass: 'theme-generic'
  // }
};

export const DEFAULT_THEME = 'christmas';

/**
 * Get theme configuration by ID
 * @param themeId - Theme identifier
 * @returns Theme configuration or default theme
 */
export function getThemeConfig(themeId?: string | null): ThemeConfig {
  if (!themeId || !THEMES[themeId]) {
    return THEMES[DEFAULT_THEME];
  }
  return THEMES[themeId];
}

/**
 * Get all available themes as array
 * @returns Array of theme configurations
 */
export function getAllThemes(): ThemeConfig[] {
  return Object.values(THEMES);
}
