<template>
    <CardStatus
        tituloPrincipal="Entradas"
        subtitulo="Gerencie as suas receitas"
        icone="pi pi-wallet"
        :mostrarAcao="true"
        iconeAcao="pi pi-plus"
        @acao="abrirModalCategoria"
    />
</template>

<script setup>
import CardStatus from '../../components/CardStatus.vue'
</script>

<style scoped>

</style>