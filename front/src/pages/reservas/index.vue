<template>
    <CardStatus
        tituloPrincipal="Reservas"
        subtitulo="Gerencie as suas reservas"
        icone="pi pi-folder-plus"
        :mostrarAcao="true"
        iconeAcao="pi pi-plus"
        @acao="abrirModalReserva"
    />
</template>

<script setup>
import CardStatus from '../../components/CardStatus.vue'
</script>

<style scoped>

</style>