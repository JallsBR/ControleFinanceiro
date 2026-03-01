<template>
    <CardStatus
        tituloPrincipal="Metas"
        subtitulo="Gerencie as suas metas"
        icone="pi pi-bullseye"
        :mostrarAcao="true"
        iconeAcao="pi pi-plus"
        @acao="abrirModalMeta"
    />
</template>

<script setup>
import CardStatus from '../../components/CardStatus.vue'
</script>

<style scoped>

</style>