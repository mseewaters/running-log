// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import LandingPage from '../components/LandingPage.vue'
import QuickLogPage from '@/components/QuickLogPage.vue'
import RegistrationPage from '../components/RegistrationPage.vue'
import TargetSettingPage from '../components/TargetSettingTable.vue'
import HomePage from '../components/HomePage.vue'
import MetricsPage from '../components/MetricsPage.vue'


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
      component: HomePage
    },
    {
      path: '/run',
      name: 'run',
      component: QuickLogPage
    },
    {
      path: '/plan',
      name: 'plan',
      component: TargetSettingPage
    },
    {
      path: '/metrics',
      name: 'metrics',
      component: MetricsPage
    }
  ]
})

export default router
