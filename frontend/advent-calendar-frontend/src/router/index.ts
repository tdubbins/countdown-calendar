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
    path: '/dashboard',
    component: () => import('@/views/DashboardPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboard/create-calendar',
    component: () => import('@/views/CalendarCreatePage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/test-video-upload',
    component: () => import('@/views/VideoUploadTest.vue')
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
    next('/dashboard');
  } else {
    // Allow navigation
    next();
  }
});

export default router
