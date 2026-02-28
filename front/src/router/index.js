import { createRouter, createWebHistory } from 'vue-router'

import AuthLayout from '../layouts/AuthLayout.vue'
import PublicLayout from '../layouts/PublicLayout.vue'
import LogoutPage from '../pages/auth/LogoutPage.vue'
import HomePage from '../pages/home/HomePage.vue'
import SiginPage from '../pages/auth/SiginPage.vue'
import SigupPage from '../pages/auth/SigupPage.vue'
import store from '../store'

const routes = [
  {
    path: '/',
    component: PublicLayout,
    children: [
      {
        path: '',
        name: 'signin',
        component: SiginPage
      }
    ]
  },
  {
    path: '/signup',
    component: PublicLayout,
    children: [
      {
        path: '',
        name: 'signup',
        component: SigupPage
      }
    ]
  },
  {
    path: '/logout',
    name: 'logout',
    component: LogoutPage
  },
  {
    path: '/homepage',
    component: AuthLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'home',
        component: HomePage
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

/* Navigation Guard */
router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const isAuthenticated = store.getters.isAuthenticated

  if (requiresAuth && !isAuthenticated) {
    next({ name: 'signin' })
  } 
  else if ((to.name === 'signin' || to.name === 'signup') && isAuthenticated) {
    next({ name: 'home' })
  } 
  else {
    next()
  }
})

export default router