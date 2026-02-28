<template>
    <button
      class="botao-acao"
      :class="classeVariante"
      @click="emitirClique"
    >
      <i :class="icone"></i>
    </button>
  </template>
  
  <script setup>
  import { computed } from 'vue'
  
  const props = defineProps({
    icone: {
      type: String,
      required: true
    },
    variante: {
      type: String,
      default: 'neutro' // entrada | saida | neutro
    }
  })
  
  const emit = defineEmits(['click'])
  
  const emitirClique = () => {
    try {
      emit('click')
    } catch (error) {
      console.error('Erro ao emitir clique no BotaoAcao:', error)
    }
  }
  
  const classeVariante = computed(() => {
    return {
      'botao-entrada': props.variante === 'entrada',
      'botao-saida': props.variante === 'saida',
      'botao-neutro': props.variante === 'neutro'
    }
  })
  </script>
  
  <style scoped>
  
  /* ===== BASE ===== */
  .botao-acao {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 0.9rem;
    color: white;
  }
  
  /* ===== VARIANTES ===== */
  .botao-entrada {
    background-color: #20c997;
  }
  
  .botao-saida {
    background-color: #ff6b6b;
  }
  
  .botao-neutro {
    background-color: #6c757d;
  }
  
  /* ===== HOVER ===== */
  .botao-acao:hover {
    transform: scale(1.08);
    filter: brightness(1.1);
  }
  
  /* ===== CLICK ===== */
  .botao-acao:active {
    transform: scale(0.95);
  }
  
  </style>

  <!-- Como usar:
   
  <BotaoAcao
    icone="pi pi-plus"
    variante="entrada"
    @click="abrirModalEntrada"
/>

<BotaoAcao
    icone="pi pi-minus"
    variante="saida"
    @click="abrirModalSaida"
/>
  
  
  
  -->