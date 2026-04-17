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
import SignInPage from '../pages/auth/SignInPage.vue'
import SignUpPage from '../pages/auth/SignUpPage.vue'
import store from '../store'

const routes = [
  {
    path: '/',
    component: PublicLayout,
    children: [
      {
        path: '',
        name: 'signin',
        component: SignInPage
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
        component: SignUpPage
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
      },
      {
        path: '/perfil',
        name: 'perfil',
        component: () => import('../pages/conta/UsuarioAreaPage.vue'),
        meta: {
          title: 'Perfil',
          subtitulo: 'Seus dados e preferências da conta.',
          icone: 'pi pi-user'
        }
      },
      {
        path: '/assinatura',
        name: 'assinatura',
        component: () => import('../pages/conta/UsuarioAreaPage.vue'),
        meta: {
          title: 'Assinatura',
          subtitulo: 'Plano e pagamentos da sua assinatura.',
          icone: 'pi pi-id-card'
        }
      },
      {
        path: '/consultoria',
        name: 'consultoria',
        component: () => import('../pages/conta/UsuarioAreaPage.vue'),
        meta: {
          title: 'Consultoria',
          subtitulo: 'Acompanhamento e suporte consultivo.',
          icone: 'pi pi-comments'
        }
      },
      {
        path: '/configuracoes',
        name: 'configuracoes',
        component: () => import('../pages/conta/UsuarioAreaPage.vue'),
        meta: {
          title: 'Configurações',
          subtitulo: 'Opções administrativas e parâmetros do sistema.',
          icone: 'pi pi-cog',
          requiresStaff: true
        }
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

  const requiresStaff = to.matched.some(record => record.meta.requiresStaff)
  if (requiresStaff && isAuthenticated) {
    const u = store.getters.getUser
    if (!u?.is_staff && !u?.is_superuser) {
      return { name: 'home' }
    }
  }

  return true
})

export default router