<template>
    <CardStatus
        tituloPrincipal="Investimentos"
        subtitulo="Gerencie os seus investimentos"
        icone="pi pi-chart-line"
        :mostrarAcao="true"
        iconeAcao="pi pi-plus"
        @acao="abrirModalInvestimento"
    />
</template>

<script setup>
import CardStatus from '../../components/CardStatus.vue'
</script>

<style scoped>

</style>