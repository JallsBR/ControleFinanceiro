<template>
    <Menubar class="custom-menubar">        
        <template #start>
            <div class="nav-left">
                <RouterLink to="/" class="brand-link">
                    <img src="/logoFinancasApp.png" alt="Logo Financas" class="logo-img" />
                    <h2 class="brand-title">Finanças <span>APP</span></h2>
                </RouterLink>

                <RouterLink to="/entradas" class="nav-item">
                    <i class="pi pi-wallet"></i>
                    <span>Entradas</span>
                </RouterLink>

                <RouterLink to="/saidas" class="nav-item">
                    <i class="pi pi-credit-card"></i>
                    <span>Saídas</span>
                </RouterLink>

                <RouterLink to="/relatorio" class="nav-item">
                    <i class="pi pi-chart-line"></i>
                    <span>Relatório</span>
                </RouterLink>

                <RouterLink to="/categorias" class="nav-item">
                    <i class="pi pi-tags"></i>
                    <span>Categorias</span>
                </RouterLink>

                <RouterLink to="/reservas" class="nav-item">
                    <i class="pi pi-folder-plus"></i>
                    <span>Reservas</span>
                </RouterLink>

                <RouterLink to="/investimentos" class="nav-item">
                    <i class="pi pi-chart-line"></i>
                    <span>Investimentos</span>
                </RouterLink>

                <RouterLink to="/metas" class="nav-item">
                    <i class="pi pi-bullseye"></i>
                    <span>Metas</span>
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

                <button class="logout-btn" @click="logout">
                    <i class="pi pi-sign-out"></i>
                </button>
            </div>
        </template>

    </Menubar>
</template>

<script setup>
import Menubar from 'primevue/menubar'
import { RouterLink, useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'
import { useStore } from 'vuex'
import MenuUser from '@/components/MenuUser.vue'

const STORAGE_TEMA = 'financas-tema'

const store = useStore()
const router = useRouter()

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

onMounted(() => {
    const salvo = localStorage.getItem(STORAGE_TEMA)
    if (salvo === 'claro') aplicarTema(true)
    else if (salvo === 'escuro') aplicarTema(false)
})

const logout = () => {
    store.dispatch('logout')
    router.push('/login')
}
</script>

<style scoped>

/* ===== MENUBAR BASE ===== */
.custom-menubar {
    background-color: var(--bg-secundario) !important;
    border: none !important;
    height: 70px;
    padding: 0 20px;
}

/* Remove fundo branco padrão do Prime */
::v-deep(.p-menubar) {
    background: transparent !important;
    border: none !important;
}

/* ===== LADO ESQUERDO ===== */
.nav-left {
    display: flex;
    align-items: center;
    gap: 10px;
}

/* Link do logo + título: mesma aparência, sem estilo de link */
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

/* ===== ITENS ===== */
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

/* Hover */
.nav-item:hover {
    background-color: var(--bg-primario);
    color: var(--texto-primario);
}

/* ===== USER AREA ===== */
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

/* Logout */
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
</style>