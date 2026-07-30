<template>
    <!-- ===== DESKTOP (≥901px) ===== -->
    <Menubar class="custom-menubar nav-desktop">
        <template #start>
            <div class="nav-left">
                <RouterLink :to="{ name: 'home' }" class="brand-link">
                    <img src="/logoFinancasApp.png" alt="Logo Financas" class="logo-img" />
                    <h2 class="brand-title">Finanças <span>APP</span></h2>
                </RouterLink>

                <RouterLink
                    v-for="item in linksNavegacao"
                    :key="item.to"
                    :to="item.to"
                    class="nav-item"
                >
                    <i :class="item.icon"></i>
                    <span>{{ item.label }}</span>
                </RouterLink>
            </div>
        </template>

        <template #end>
            <div class="nav-user">
                <button
                    type="button"
                    class="theme-toggle"
                    :aria-label="temaClaro ? 'Ativar tema escuro' : 'Ativar tema claro'"
                    @click="toggleTema"
                >
                    <i :class="temaClaro ? 'pi pi-moon' : 'pi pi-sun'"></i>
                </button>

                <MenuUser />

                <button class="logout-btn" type="button" aria-label="Sair" @click="logout">
                    <i class="pi pi-sign-out"></i>
                </button>
            </div>
        </template>
    </Menubar>

    <!-- ===== MOBILE (≤900px) — top bar só com o nome ===== -->
    <header class="nav-mobile-top">
        <RouterLink :to="{ name: 'home' }" class="brand-link" @click="fecharMenu">
            <img src="/logoFinancasApp.png" alt="Logo Financas" class="logo-img logo-img--mobile" />
            <h2 class="brand-title">Finanças <span>APP</span></h2>
        </RouterLink>
    </header>

    <!-- FAB inferior direito: abre o menu lateral -->
    <button
        type="button"
        class="nav-mobile-fab"
        aria-label="Abrir menu"
        :aria-expanded="menuMobileAberto"
        @click="menuMobileAberto = true"
    >
        <i class="pi pi-bars" aria-hidden="true"></i>
    </button>

    <Drawer
        v-model:visible="menuMobileAberto"
        position="right"
        class="nav-mobile-drawer"
        :block-scroll="true"
        :pt="{
            root: { class: 'nav-drawer-root' },
            header: { class: 'nav-drawer-header' },
            content: { class: 'nav-drawer-content' }
        }"
    >
        <template #header>
            <span class="nav-drawer-title">Menu</span>
        </template>

        <nav class="nav-drawer-links" aria-label="Navegação principal">
            <RouterLink
                v-for="item in linksNavegacao"
                :key="item.to"
                :to="item.to"
                class="nav-drawer-item"
                @click="fecharMenu"
            >
                <i :class="item.icon" aria-hidden="true"></i>
                <span>{{ item.label }}</span>
            </RouterLink>
        </nav>

        <div class="nav-drawer-actions">
            <button
                type="button"
                class="nav-drawer-item nav-drawer-item--btn"
                :aria-label="temaClaro ? 'Ativar tema escuro' : 'Ativar tema claro'"
                @click="toggleTema"
            >
                <i :class="temaClaro ? 'pi pi-moon' : 'pi pi-sun'" aria-hidden="true"></i>
                <span>{{ temaClaro ? 'Tema escuro' : 'Tema claro' }}</span>
            </button>

            <div class="nav-drawer-user">
                <MenuUser />
            </div>

            <button
                type="button"
                class="nav-drawer-item nav-drawer-item--btn nav-drawer-item--danger"
                aria-label="Sair"
                @click="logoutMobile"
            >
                <i class="pi pi-sign-out" aria-hidden="true"></i>
                <span>Sair</span>
            </button>
        </div>
    </Drawer>
</template>

<script setup>
import Menubar from 'primevue/menubar'
import Drawer from 'primevue/drawer'
import { RouterLink, useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'
import { useStore } from 'vuex'
import MenuUser from '@/components/MenuUser.vue'

const STORAGE_TEMA = 'financas-tema'

const linksNavegacao = [
    { to: '/entradas', label: 'Entradas', icon: 'pi pi-wallet' },
    { to: '/saidas', label: 'Saídas', icon: 'pi pi-credit-card' },
    { to: '/relatorio', label: 'Relatório', icon: 'pi pi-chart-line' },
    { to: '/categorias', label: 'Categorias', icon: 'pi pi-tags' },
    { to: '/reservas', label: 'Reservas', icon: 'pi pi-folder-plus' },
    { to: '/investimentos', label: 'Investimentos', icon: 'pi pi-chart-line' },
    { to: '/metas', label: 'Metas', icon: 'pi pi-bullseye' }
]

const store = useStore()
const router = useRouter()

const menuMobileAberto = ref(false)
const temaClaro = ref(document.documentElement.getAttribute('data-tema') === 'claro')

const aplicarTema = (claro) => {
    temaClaro.value = claro
    if (claro) {
        document.documentElement.setAttribute('data-tema', 'claro')
    } else {
        document.documentElement.removeAttribute('data-tema')
    }
    try {
        localStorage.setItem(STORAGE_TEMA, claro ? 'claro' : 'escuro')
    } catch (_) {}
}

const toggleTema = () => {
    aplicarTema(!temaClaro.value)
}

const fecharMenu = () => {
    menuMobileAberto.value = false
}

onMounted(() => {
    const salvo = localStorage.getItem(STORAGE_TEMA)
    if (salvo === 'claro') aplicarTema(true)
    else if (salvo === 'escuro') aplicarTema(false)
})

const logout = () => {
    store.dispatch('logout')
    router.push('/login')
}

const logoutMobile = () => {
    fecharMenu()
    logout()
}
</script>

<style scoped>

/* ===== MENUBAR BASE (desktop) ===== */
.custom-menubar {
    background-color: var(--bg-secundario) !important;
    border: none !important;
    height: 70px;
    padding: 0 20px;
}

::v-deep(.p-menubar) {
    background: transparent !important;
    border: none !important;
}

.nav-left {
    display: flex;
    align-items: center;
    gap: 10px;
}

.brand-link {
    display: flex;
    align-items: center;
    gap: 0;
    text-decoration: none;
    color: inherit;
    cursor: pointer;
}
.brand-link:hover,
.brand-link:visited,
.brand-link:focus {
    text-decoration: none;
    color: inherit;
}

.logo-img {
    width: 40px;
    height: 40px;
    min-width: 40px;
    margin-right: 15px;
    display: block;
    object-fit: contain;
}

.logo-img--mobile {
    width: 36px;
    height: 36px;
    min-width: 36px;
    margin-right: 10px;
}

.nav-item {
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--texto-secundario);
    text-decoration: none;
    padding: 10px 15px;
    border-radius: 8px;
    transition: all 0.2s ease;
    font-size: 0.95rem;
}

.nav-item i {
    font-size: 1.2rem;
    min-width: 20px;
    text-align: center;
}

.nav-item:hover {
    background-color: var(--bg-primario);
    color: var(--texto-primario);
}

.nav-user {
    display: flex;
    align-items: center;
    gap: 12px;
    color: var(--texto-secundario);
}

.theme-toggle {
    background: none;
    border: none;
    color: var(--texto-secundario);
    cursor: pointer;
    padding: 8px;
    border-radius: 6px;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
}

.theme-toggle:hover {
    background-color: var(--bg-primario);
    color: var(--texto-primario);
}

.theme-toggle i {
    font-size: 1.2rem;
}

.logout-btn {
    background: none;
    border: none;
    color: var(--perigo);
    cursor: pointer;
    padding: 8px;
    border-radius: 6px;
    transition: all 0.2s ease;
}

.logout-btn:hover {
    background-color: color-mix(in srgb, var(--perigo) 15%, transparent);
}

.brand-title {
    font-size: 1.6rem;
    font-weight: 600;
    color: var(--texto-primario);
    letter-spacing: 1px;
    margin: 0;
}

.brand-title span {
    color: var(--sucesso);
    font-weight: 700;
}

/* ===== MOBILE: oculto por padrão no desktop ===== */
.nav-mobile-top,
.nav-mobile-fab {
    display: none;
}

/* ===== BREAKPOINT celular / referência ~828px ===== */
@media (max-width: 900px) {
    .nav-desktop {
        display: none !important;
    }

    .nav-mobile-top {
        display: flex;
        align-items: center;
        position: sticky;
        top: 0;
        z-index: 110;
        width: 100%;
        min-height: 56px;
        padding: 0.5rem 1rem;
        padding-top: max(0.5rem, env(safe-area-inset-top));
        background-color: var(--bg-secundario);
        box-sizing: border-box;
    }

    .nav-mobile-top .brand-title {
        font-size: 1.25rem;
        letter-spacing: 0.5px;
    }

    .nav-mobile-fab {
        display: flex;
        align-items: center;
        justify-content: center;
        position: fixed;
        right: max(1rem, env(safe-area-inset-right));
        /* acima do footer (~52px) + safe area */
        bottom: calc(3.5rem + env(safe-area-inset-bottom, 0px));
        z-index: 120;
        width: 3.25rem;
        height: 3.25rem;
        border: none;
        border-radius: 50%;
        background-color: var(--sucesso);
        color: #fff;
        box-shadow: 0 4px 14px color-mix(in srgb, #000 35%, transparent);
        cursor: pointer;
        transition: transform 0.15s ease, filter 0.15s ease;
    }

    .nav-mobile-fab:hover,
    .nav-mobile-fab:focus-visible {
        filter: brightness(1.08);
        outline: none;
    }

    .nav-mobile-fab:active {
        transform: scale(0.96);
    }

    .nav-mobile-fab i {
        font-size: 1.35rem;
    }
}

/* Drawer: estilos do conteúdo (teleport — :deep / global abaixo) */
.nav-drawer-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--texto-primario);
}

.nav-drawer-links {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    margin-bottom: 1.25rem;
}

.nav-drawer-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.85rem 0.75rem;
    border-radius: 8px;
    color: var(--texto-secundario);
    text-decoration: none;
    font-size: 1rem;
    transition: background-color 0.15s ease, color 0.15s ease;
}

.nav-drawer-item i {
    font-size: 1.2rem;
    min-width: 1.25rem;
    text-align: center;
}

.nav-drawer-item:hover,
.nav-drawer-item.router-link-active {
    background-color: var(--bg-primario);
    color: var(--texto-primario);
}

.nav-drawer-item--btn {
    width: 100%;
    background: none;
    border: none;
    cursor: pointer;
    font: inherit;
    text-align: left;
}

.nav-drawer-item--danger {
    color: var(--perigo);
}

.nav-drawer-item--danger:hover {
    background-color: color-mix(in srgb, var(--perigo) 15%, transparent);
    color: var(--perigo);
}

.nav-drawer-actions {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    padding-top: 0.75rem;
    border-top: 1px solid color-mix(in srgb, var(--texto-secundario) 25%, transparent);
}

.nav-drawer-user {
    padding: 0.25rem 0.25rem;
}
</style>

<!-- Drawer é teleportado para body: tema do painel -->
<style>
.nav-drawer-root.p-drawer,
.p-drawer.nav-mobile-drawer {
    background: var(--bg-secundario) !important;
    color: var(--texto-primario) !important;
    border: none !important;
    width: min(20rem, 88vw) !important;
}

.nav-drawer-header.p-drawer-header,
.p-drawer.nav-mobile-drawer .p-drawer-header {
    background: var(--bg-secundario) !important;
    color: var(--texto-primario) !important;
    border-bottom: 1px solid color-mix(in srgb, var(--texto-secundario) 25%, transparent) !important;
}

.nav-drawer-content.p-drawer-content,
.p-drawer.nav-mobile-drawer .p-drawer-content {
    background: var(--bg-secundario) !important;
    color: var(--texto-primario) !important;
    padding: 1rem !important;
    display: flex;
    flex-direction: column;
}
</style>
