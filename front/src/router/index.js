import { createRouter, createWebHistory } from 'vue-router'

import AuthLayout from '../layouts/AuthLayout.vue'
import PublicLayout from '../layouts/PublicLayout.vue'
import LogoutPage from '../pages/auth/LogoutPage.vue'
import HomePage from '../pages/home/index.vue'
import EntradasPage from '../pages/entradas/index.vue'
import SaidasPage from '../pages/saidas/index.vue'
import SaldoPage from '../pages/saldo/index.vue'
import ReservasPage from '../pages/reservas/index.vue'
import InvestimentosPage from '../pages/investimentos/index.vue'
import MetasPage from '../pages/metas/index.vue'
import CategoriasPage from '../pages/categorias/index.vue'
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
    path: '/',
    component: AuthLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'home',
        component: HomePage
      },
      {
        path: '/entradas',
        name: 'entradas',
        component: EntradasPage
      },
      {
        path: '/saidas',
        name: 'saidas',
        component: SaidasPage
      },
      {
        path: '/saldo',
        name: 'saldo',
        component: SaldoPage
      },
      {
        path: '/reservas',
        name: 'reservas',
        component: ReservasPage
      },
      {
        path: '/investimentos',
        name: 'investimentos',
        component: InvestimentosPage
      },
      {
        path: '/metas',
        name: 'metas',
        component: MetasPage
      },
      {
        path: '/categorias',
        name: 'categorias',
        component: CategoriasPage
      }
    ]
  },
  
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

/* Navigation Guard */
router.beforeEach((to, from) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const isAuthenticated = store.getters.isAuthenticated

  if (requiresAuth && !isAuthenticated) {
    return { name: 'signin' }
  }
  if ((to.name === 'signin' || to.name === 'signup') && isAuthenticated) {
    return { name: 'home' }
  }
  return true
})

export default router