<template>
    <div
      class="card-status"
      :class="{ 'card-status--link': to }"
      :role="to ? 'link' : undefined"
      :tabindex="to ? 0 : undefined"
      @click="onCardClick"
      @keydown.enter="to && onCardClick()"
    >
  
      <!-- HEADER -->
      <div class="card-header">
      <!-- ÍCONE opcional -->
        <div class="card-header-content">
          <div v-if="icone" class="icone-container">
            <i :class="icone"></i>
          </div>
          <p v-if="tituloPrincipal" class="card-tituloPrincipal" style="margin-bottom: 0px;">
            {{ tituloPrincipal }}
          </p>
        </div>
        <!-- Botão opcional: @click.stop evita que o clique dispare a navegação do card -->
        <div v-if="mostrarAcao" @click.stop>
          <BotaoAcao
            :icone="iconeAcao"
            :variante="variante"
            @click="$emit('acao')"
          />
        </div>
      </div>
      <p class="card-subtitulo">
        {{ subtitulo }}
      </p>
  
      <!-- CONTEÚDO -->
      <p class="card-label" style="margin-bottom: 0px;">
        {{ titulo }}
      </p>
  
      <p class="card-descricao" style="margin-top: 0px;">
        {{ descricao }}
      </p>
      <h2  v-if="valor" class="card-valor" :class="classeValor">
        <span style="font-size: 1.0rem;">R$</span>{{ valor }}
      </h2>
  
    </div>
  </template>
  
  <script setup>
  import { computed } from 'vue'
  import { useRouter } from 'vue-router'
  import BotaoAcao from './botoes/BotaoAcao.vue'
  
  const router = useRouter()
  
  const props = defineProps({

    tituloPrincipal: {
      type: String,
      default: ''
    },
    subtitulo: {
      type: String,
      default: ''
    },
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
    },
    /** Rota ou caminho para navegação. Se definido, o card fica clicável (exceto nos botões internos). */
    to: {
      type: [String, Object],
      default: undefined
    }
  })
  
  function onCardClick() {
    if (!props.to) return
    router.push(props.to)
  }
  
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
  .card-subtitulo {
    color: #adb5bd;
    font-size: 1.0rem;
    margin-top: -15px;
  }
  
  .card-status:hover {
    transform: translateY(-4px);
  }
  
  .card-status--link {
    cursor: pointer;
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
  .card-header-content {
    display: flex;
    align-items: center;
    gap: 10px;
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
  .card-tituloPrincipal {
    font-size: 2.0rem;
    font-weight: 700;
    margin: 0;
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
 Sem link (só conteúdo e botão):
 <CardStatus
    titulo="Entradas Fevereiro 2026"
    valor="R$ 9.600,00"
    icone="pi pi-wallet"
    variante="entrada"
    :mostrarAcao="true"
    iconeAcao="pi pi-plus"
    @acao="abrirModalEntrada"
  />

 Com rota (card clicável; o botão continua emitindo @acao):
 <CardStatus
    titulo="Entradas Fevereiro 2026"
    valor="R$ 9.600,00"
    to="/financas/entradas"
    icone="pi pi-wallet"
    variante="entrada"
    :mostrarAcao="true"
    iconeAcao="pi pi-plus"
    @acao="abrirModalEntrada"
  />

-->