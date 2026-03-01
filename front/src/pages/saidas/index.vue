<template>
    <CardStatus
        tituloPrincipal="Saídas"
        subtitulo="Gerencie as seus gastos"
        icone="pi pi-credit-card"
        :mostrarAcao="true"
        iconeAcao="pi pi-plus"
        @acao="abrirModalSaida"
    />
</template>

<script setup>
import CardStatus from '../../components/CardStatus.vue'
</script>

<style scoped>

</style>