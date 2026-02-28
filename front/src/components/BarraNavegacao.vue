<template>
    <Menubar class="custom-menubar">        
        <template #start>
            <div class="nav-left">
                <img src="/logoFinancasApp.png" alt="Logo Financas" class="logo-img" />
                <h2 class="brand-title">Finanças <span>APP</span></h2>

                <RouterLink to="/" class="nav-item">
                    <i class="pi pi-home"></i>
                    <span>Início</span>
                </RouterLink>

                <RouterLink to="/entrada" class="nav-item">
                    <i class="pi pi-wallet"></i>
                    <span>Entrada</span>
                </RouterLink>

                <RouterLink to="/saida" class="nav-item">
                    <i class="pi pi-credit-card"></i>
                    <span>Saídas</span>
                </RouterLink>

                <RouterLink to="/recorrencia" class="nav-item">
                    <i class="pi pi-refresh"></i>
                    <span>Recorrências</span>
                </RouterLink>

                <RouterLink to="/categoria" class="nav-item">
                    <i class="pi pi-tags"></i>
                    <span>Categoria</span>
                </RouterLink>
            </div>
        </template>        

        <template #end>
            <div class="nav-user">
                <i class="pi pi-user"></i>
                <span class="username">
                    {{ user?.username || 'Visitante' }}
                </span>

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
import { ref, computed } from 'vue'
import { useStore } from 'vuex'

const store = useStore()
const router = useRouter()

const user = computed(() => store.getters.getUser)

const logout = () => {
    store.dispatch('logout')
    router.push('/login')
}
</script>

<style scoped>

/* ===== MENUBAR BASE ===== */
.custom-menubar {
    background-color: #212529 !important;
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
    color: #adb5bd;
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
    background-color: #343a40;
    color: white;
}

/* ===== USER AREA ===== */
.nav-user {
    display: flex;
    align-items: center;
    gap: 12px;
    color: #adb5bd;
}

.username {
    font-size: 0.95rem;
}

/* Logout */
.logout-btn {
    background: none;
    border: none;
    color: #dc3545;
    cursor: pointer;
    padding: 8px;
    border-radius: 6px;
    transition: all 0.2s ease;
}

.logout-btn:hover {
    background-color: rgba(220, 53, 69, 0.1);
}

.brand-title {
    font-size: 1.6rem;
    font-weight: 600;
    color: #f8f9fa;
    letter-spacing: 1px;
    margin: 0;
}

.brand-title span {
    color: #20c997; /* verde moderno */
    font-weight: 700;
}
</style>