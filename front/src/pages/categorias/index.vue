<template>
    <CardStatus
        tituloPrincipal="Categorias"
        subtitulo="Gerencie as categorias de suas movimentações"
        icone="pi pi-tags"
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