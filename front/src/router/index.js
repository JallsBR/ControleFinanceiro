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
import PerfilPage from '../pages/perfil/PerfilPage.vue'
import AssinaturaPage from '../pages/assinatura/AssinaturaPage.vue'
import AdministrarPage from '../pages/administrar/index.vue'
import SignInPage from '../pages/auth/SignInPage.vue'
import SignUpPage from '../pages/auth/SignUpPage.vue'
import store from '../store'
import {
  FINANCAS_VIEW_AS_DISPLAY_QUERY,
  FINANCAS_VIEW_AS_KIND_QUERY,
  FINANCAS_VIEW_AS_USER_QUERY,
  SUBJECT_VIEW_KIND
} from '@/constants/financasViewAs'

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
        component: PerfilPage
      },
      {
        path: '/assinatura',
        name: 'assinatura',
        component: AssinaturaPage
      },
      {
        path: '/consultoria',
        name: 'consultoria',
        component: () => import('../pages/consultoria/index.vue'),
        meta: {
          title: 'Consultoria',
          subtitulo: 'Acompanhamento e suporte consultivo.',
          icone: 'pi pi-comments'
        }
      },
      {
        path: '/consultoria/solicitacoes',
        name: 'consultoria-solicitacoes',
        component: () => import('../pages/consultoria/SolicitacoesConsultoriaPage.vue'),
        meta: { requiresConsultor: true }
      },
      {
        path: '/administrar',
        name: 'administrar',
        component: AdministrarPage,
        meta: { requiresStaff: true }
      },
      {
        path: '/configuracoes',
        redirect: { name: 'administrar' }
      }
    ]
  },
  
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

function parseViewAsDisplay (raw) {
  if (raw === undefined || raw === null) return null
  const s = String(raw).trim()
  if (!s) return null
  try {
    const d = decodeURIComponent(s)
    return d.length > 160 ? d.slice(0, 160) : d
  } catch (_) {
    return s.length > 160 ? s.slice(0, 160) : s
  }
}

/** Grava modo “ver como utilizador” (staff ou consultor) e limpa a query. */
function consumeViewAsUserQuery (to) {
  const raw = to.query?.[FINANCAS_VIEW_AS_USER_QUERY]
  if (raw === undefined || raw === null || String(raw).trim() === '') {
    return null
  }
  const id = parseInt(String(raw), 10)
  const q = { ...to.query }
  delete q[FINANCAS_VIEW_AS_USER_QUERY]
  delete q[FINANCAS_VIEW_AS_KIND_QUERY]
  delete q[FINANCAS_VIEW_AS_DISPLAY_QUERY]
  const dest =
    Object.keys(q).length > 0
      ? { path: to.path, query: q, hash: to.hash, replace: true }
      : { path: to.path, hash: to.hash, replace: true }

  if (!store.getters.isAuthenticated || Number.isNaN(id) || id <= 0) {
    return dest
  }

  const kindParam = String(to.query[FINANCAS_VIEW_AS_KIND_QUERY] || '')
    .trim()
    .toLowerCase()
  const wantsConsultor = kindParam === SUBJECT_VIEW_KIND.CONSULTOR
  const displayName = parseViewAsDisplay(to.query[FINANCAS_VIEW_AS_DISPLAY_QUERY])

  const u = store.getters.getUser
  const sid = String(id)

  if (wantsConsultor) {
    if (u?.is_gerente) {
      store.commit('SET_SUBJECT_VIEW_MODE', {
        kind: SUBJECT_VIEW_KIND.CONSULTOR,
        userId: sid,
        displayName
      })
    }
  } else if (u?.is_staff || u?.is_superuser) {
    store.commit('SET_SUBJECT_VIEW_MODE', {
      kind: SUBJECT_VIEW_KIND.ADMIN,
      userId: sid,
      displayName: null
    })
  }

  return dest
}

/** Sessão “ver como” inválida para o utilizador atual (ex.: mudou de conta). */
function invalidateSubjectViewIfNeeded () {
  const m = store.state.subjectViewMode
  if (!m?.userId) return
  const u = store.getters.getUser
  if (!u) return
  if (m.kind === SUBJECT_VIEW_KIND.CONSULTOR && !u.is_gerente) {
    store.commit('SET_SUBJECT_VIEW_MODE', null)
    return
  }
  if (
    m.kind === SUBJECT_VIEW_KIND.ADMIN &&
    !u.is_staff &&
    !u.is_superuser
  ) {
    store.commit('SET_SUBJECT_VIEW_MODE', null)
  }
}

/* Navigation Guard */
router.beforeEach((to, from) => {
  const redirected = consumeViewAsUserQuery(to)
  if (redirected) {
    return redirected
  }

  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const isAuthenticated = store.getters.isAuthenticated

  if (isAuthenticated) {
    invalidateSubjectViewIfNeeded()
  }

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

  const requiresConsultor = to.matched.some(
    (record) => record.meta.requiresConsultor
  )
  if (requiresConsultor && isAuthenticated) {
    const u = store.getters.getUser
    const staffComVisaoAdmin =
      (u?.is_staff || u?.is_superuser) &&
      store.getters.subjectViewAdminActive &&
      store.state.subjectViewMode?.userId
    if (!u?.is_gerente && !staffComVisaoAdmin) {
      return { name: 'consultoria' }
    }
  }

  /* Modo visualização (admin ou consultor): não aceder ao painel Administrar */
  if (
    to.name === 'administrar' &&
    (store.getters.subjectViewAdminActive ||
      store.getters.subjectViewConsultorActive)
  ) {
    return { name: 'home' }
  }

  return true
})

export default router