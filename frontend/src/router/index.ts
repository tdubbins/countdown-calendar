import { createRouter, createWebHistory } from '@ionic/vue-router';
import { RouteRecordRaw } from 'vue-router';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    component: () => import('@/views/LoginPage.vue')
  },
  {
    path: '/register',
    component: () => import('@/views/RegisterPage.vue')
  },
  {
    path: '/verify-email/:token',
    component: () => import('@/views/EmailVerificationPage.vue')
  },
  {
    path: '/calendar',
    component: () => import('@/views/CalendarsPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/calendar/create',
    component: () => import('@/views/CalendarCreatePage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/calendar/:id/edit',
    component: () => import('@/views/CalendarEditPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/calendar/:id',
    name: 'PublicCalendar',
    component: () => import('@/views/CalendarViewPage.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/profile',
    component: () => import('@/views/ProfilePage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/help',
    component: () => import('@/views/HelpPage.vue'),
    meta: { requiresAuth: false }
  },
  // Legacy redirects for backwards compatibility
  {
    path: '/dashboard',
    redirect: '/calendar'
  },
  // Catch-all 404 - must be last
  {
    path: '/:pathMatch(.*)*',
    redirect: '/calendar'
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// Navigation guards for authentication
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('auth_token');
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);

  if (requiresAuth && !token) {
    // Route requires authentication but user is not logged in
    next('/login');
  } else if ((to.path === '/login' || to.path === '/register') && token) {
    // User is logged in but trying to access login/register pages
    next('/calendar');
  } else {
    // Allow navigation
    next();
  }
});

export default router
