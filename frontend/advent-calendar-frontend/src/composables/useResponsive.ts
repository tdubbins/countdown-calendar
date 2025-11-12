import { ref, onMounted, onUnmounted } from 'vue';
import { BREAKPOINTS } from '@/utils/constants';

// Screen size type
export type ScreenSize = 'mobile' | 'tablet' | 'desktop';

export const useResponsive = () => {
  const screenWidth = ref(window.innerWidth);
  
  // Current screen size
  const screenSize = ref<ScreenSize>(getScreenSize(screenWidth.value));
  
  // Responsive display limits for different components
  const calendarDisplayLimit = ref(getCalendarDisplayLimit(screenWidth.value));
  
  // Update values when window resizes
  const updateScreenData = () => {
    screenWidth.value = window.innerWidth;
    screenSize.value = getScreenSize(screenWidth.value);
    calendarDisplayLimit.value = getCalendarDisplayLimit(screenWidth.value);
  };
  
  // Set up resize listener
  onMounted(() => {
    window.addEventListener('resize', updateScreenData);
  });
  
  // Clean up resize listener
  onUnmounted(() => {
    window.removeEventListener('resize', updateScreenData);
  });
  
  return {
    screenWidth,
    screenSize,
    calendarDisplayLimit,
    isMobile: () => screenSize.value === 'mobile',
    isTablet: () => screenSize.value === 'tablet',
    isDesktop: () => screenSize.value === 'desktop'
  };
};

// Helper functions
function getScreenSize(width: number): ScreenSize {
  if (width < BREAKPOINTS.MOBILE) return 'mobile';
  if (width < BREAKPOINTS.TABLET) return 'tablet';
  return 'desktop';
}

function getCalendarDisplayLimit(width: number): number {
  if (width < BREAKPOINTS.MOBILE) return 4;      // Mobile: 4 calendars
  if (width < BREAKPOINTS.TABLET) return 6;      // Tablet: 6 calendars  
  return 9;                                       // Desktop: 9 calendars
}