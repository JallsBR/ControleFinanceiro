<template>
    <div class="card-data">
      <i class="pi pi-calendar"></i>
      <span>{{ dataFormatada }}</span>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, onUnmounted } from 'vue'
  import dayjs from 'dayjs'
  import 'dayjs/locale/pt-br'
  
  dayjs.locale('pt-br')
  
  const props = defineProps({
    mostrarHora: {
      type: Boolean,
      default: false
    }
  })
  
  const dataFormatada = ref('')
  
  let intervalo = null
  
  const atualizarData = () => {
    try {
      const formato = props.mostrarHora
        ? 'dddd, DD [de] MMMM [de] YYYY  - HH:mm'
        : 'dddd, DD [de] MMMM [de] YYYY'
  
      const data = dayjs().format(formato)
  
      // Primeira letra maiúscula
      dataFormatada.value =
        data.charAt(0).toUpperCase() + data.slice(1)
  
    } catch (error) {
      console.error('Erro ao atualizar data em DiaHoje:', error)
    }
  }
  
  onMounted(() => {
    atualizarData()
  
    if (props.mostrarHora) {
      intervalo = setInterval(atualizarData, 60000)
    }
  })
  
  onUnmounted(() => {
    if (intervalo) clearInterval(intervalo)
  })
  </script>
  
  <style scoped>
  
  /* ===== CARD BASE ===== */
  .card-data {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    background: var(--bg-secundario);
    color: var(--texto-secundario);
    padding: 8px 14px;
    border-radius: 12px;
    font-size: 0.9rem;
    margin-bottom: 25px;
    box-shadow: 0 3px 12px rgba(0,0,0,0.25);
    transition: all 0.2s ease;
  }
  
  /* Ícone */
  .card-data i {
    color: var(--sucesso);
    font-size: 1rem;
  }
  
  /* Hover */
  .card-data:hover {
    transform: translateY(-2px);
    color: var(--texto-primario);
  }
  
  </style>

  <!-- Como usar:
   
  <DiaHoje />
  ou com hora:
  <DiaHoje :mostrarHora="true" />
  
  -->