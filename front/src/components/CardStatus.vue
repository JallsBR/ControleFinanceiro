<template>
    <div class="card-status">
  
      <!-- HEADER -->
      <div class="card-header">
      <!-- ÍCONE opcional -->
      <div v-if="icone" class="icone-container">
        <i :class="icone"></i>
      </div>
  
        <!-- Botão opcional -->
        <BotaoAcao
          v-if="mostrarAcao"
          :icone="iconeAcao"
          :variante="variante"
          @click="$emit('acao')"
        />
      </div>
  
      <!-- CONTEÚDO -->
      <p class="card-label" style="margin-bottom: 0px;">
        {{ titulo }}
      </p>
  
      <p class="card-descricao" style="margin-top: 0px;">
        {{ descricao }}
      </p>
      <h2 class="card-valor" :class="classeValor">
        {{ valor }}
      </h2>
  
    </div>
  </template>
  
  <script setup>
  import { computed } from 'vue'
  import BotaoAcao from './botoes/BotaoAcao.vue'
  
  const props = defineProps({
    titulo: {
      type: String,
      required: true
    },
    valor: {
      type: [String, Number],
      required: true
    },
    descricao: {
      type: String,
      default: ''
    },
    icone: {
      type: String,
      default: ''
    },
    variante: {
      type: String,
      default: 'neutro' // entrada | saida | neutro
    },
    mostrarAcao: {
      type: Boolean,
      default: false
    },
    iconeAcao: {
      type: String,
      default: 'pi pi-plus'
    }
  })
  
  const classeValor = computed(() => {
    return {
      'valor-entrada': props.variante === 'entrada',
      'valor-saida': props.variante === 'saida',
      'valor-neutro': props.variante === 'neutro'
    }
  })
  </script>
  
  <style scoped>
  
  /* ===== CARD BASE ===== */
  .card-status {
    background: #1f242d;
    border-radius: 18px;
    padding: 25px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    transition: all 0.2s ease;
  }
  
  .card-status:hover {
    transform: translateY(-4px);
  }
  
  .card-descricao {
    color: #adb5bd;
    font-size: 1.3rem;
    margin-bottom: 8px;
  }
  
  /* ===== HEADER ===== */
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
  }
  
  .icone-container {
    width: 38px;
    height: 38px;
    background-color: #343a40;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .icone-container i {
    color: #adb5bd;
    font-size: 1.1rem;
  }
  
  /* ===== TEXTOS ===== */
  .card-label {
    color: #adb5bd;
    font-size: 0.8rem;
    margin-bottom: 8px;
  }
  
  .card-valor {
    font-size: 1.5rem;
    font-weight: 700;
    margin: 0;
  }
  
  /* ===== VARIANTES DE VALOR ===== */
  .valor-entrada {
    color: #20c997;
  }
  
  .valor-saida {
    color: #ff6b6b;
  }
  
  .valor-neutro {
    color: #e9ecef;
  }
  
  </style>

<!-- Como usar:
 <CardStatus
    titulo="Entradas Fevereiro 2026"
    valor="R$ 9.600,00"
    icone="pi pi-wallet"
    variante="entrada"
    :mostrarAcao="true"
    iconeAcao="pi pi-plus"
    @acao="abrirModalEntrada"
  />



-->