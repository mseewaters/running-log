// src/router/index.ts
import { createRouter, createWebHistory, type RouteLocationNormalized } from 'vue-router'
import LandingPage from '../components/LandingPage.vue'
import RegistrationPage from '../components/RegistrationPage.vue'
import TargetSettingPage from '../components/TargetSettingPage.vue'
import HomePage from '../components/HomePage.vue'
import MetricsPage from '../components/MetricsPage2.vue'
import ActivityPage from '@/components/ActivityPage.vue'



const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'landing',
      component: LandingPage
    },
    {
      path: '/register',
      name: 'register',
      component: RegistrationPage
    },
    {
      path: '/home',
      name: 'home',
      component: HomePage,
      meta: { requiresAuth: true }
    },
    {
      path: '/run',
      name: 'run',
      component: ActivityPage,
      meta: { requiresAuth: true }
    },
    {
      path: '/plan',
      name: 'plan',
      component: TargetSettingPage,
      meta: { requiresAuth: true }
    },
    {
      path: '/metrics',
      name: 'metrics',
      component: MetricsPage,
      meta: { requiresAuth: true }
    }
  ]
})

// JWTs are three base64url segments; the middle one carries the `exp` claim.
function isTokenValid(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')))
    return typeof payload.exp === 'number' && payload.exp * 1000 > Date.now()
  } catch {
    return false
  }
}

router.beforeEach((to: RouteLocationNormalized) => {
  if (!to.meta.requiresAuth) return true

  const token = localStorage.getItem('access_token')
  if (token && isTokenValid(token)) return true

  localStorage.removeItem('access_token')
  localStorage.removeItem('user_email')
  localStorage.removeItem('user_id')
  return { name: 'landing' }
})

export default router
