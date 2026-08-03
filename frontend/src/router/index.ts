import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/pages/HomePage.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/pages/LoginPage.vue'),
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/pages/RegisterPage.vue'),
    },
    {
      path: '/chat/:sessionId',
      name: 'chat',
      component: () => import('@/pages/ChatPage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/result/:docId',
      name: 'result',
      component: () => import('@/pages/ResultPage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/lawyer',
      component: () => import('@/layouts/LawyerLayout.vue'),
      meta: { requiresAuth: true, role: 'lawyer' },
      children: [
        {
          path: '',
          redirect: '/lawyer/dashboard',
        },
        {
          path: 'dashboard',
          name: 'lawyer-dashboard',
          component: () => import('@/pages/lawyer/DashboardPage.vue'),
        },
        {
          path: 'market',
          name: 'lawyer-market',
          component: () => import('@/pages/lawyer/MarketPage.vue'),
        },
        {
          path: 'my-cases',
          name: 'lawyer-my-cases',
          component: () => import('@/pages/lawyer/MyCasesPage.vue'),
        },
        {
          path: 'leads/:leadId',
          name: 'lawyer-lead-detail',
          component: () => import('@/pages/lawyer/LeadDetailPage.vue'),
        },
      ],
    },
    {
      path: '/admin',
      component: () => import('@/layouts/AdminLayout.vue'),
      meta: { requiresAuth: true, role: 'admin' },
      children: [
        {
          path: '',
          redirect: '/admin/overview',
        },
        {
          path: 'overview',
          name: 'admin-overview',
          component: () => import('@/pages/admin/OverviewPage.vue'),
        },
        {
          path: 'users',
          name: 'admin-users',
          component: () => import('@/pages/admin/UsersPage.vue'),
        },
        {
          path: 'leads',
          name: 'admin-leads',
          component: () => import('@/pages/admin/LeadsPage.vue'),
        },
        {
          path: 'sessions',
          name: 'admin-sessions',
          component: () => import('@/pages/admin/SessionsPage.vue'),
        },
      ],
    },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  const user = auth.user
  if (to.meta.requiresAuth && !user) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.meta.role && user && user.role !== to.meta.role) {
    return { name: 'home' }
  }
})

export default router
