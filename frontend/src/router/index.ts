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
    },
    {
      path: '/result/:docId',
      name: 'result',
      component: () => import('@/pages/ResultPage.vue'),
    },
    {
      path: '/lawyer',
      component: () => import('@/layouts/LawyerLayout.vue'),
      meta: { requiresAuth: true, role: 'lawyer' },
      children: [
        {
          path: '',
          redirect: '/lawyer/leads',
        },
        {
          path: 'leads',
          name: 'lawyer-leads',
          component: () => import('@/pages/lawyer/LeadsPage.vue'),
        },
        {
          path: 'leads/:leadId',
          name: 'lawyer-lead-detail',
          component: () => import('@/pages/lawyer/LeadDetailPage.vue'),
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
