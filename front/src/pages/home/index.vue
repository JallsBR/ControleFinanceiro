<template>

    <h1 class="page-title">Dashboard</h1>
    <DiaHoje :mostrarHora="true" />

    <div class="cards-grid">

      <CardStatus
        :titulo="'Entradas ' + data().mesAtual"
        :valor="'9.600,00'"
        icone="pi pi-wallet"
        variante="entrada"
        to="/entradas"
        :mostrarAcao="true"
        iconeAcao="pi pi-plus"
        @acao="abrirModalEntrada"
      />

      <CardStatus
        :titulo="'Saídas ' + data().mesAtual"
        :valor="'1.600,00'"
        icone="pi pi-credit-card"
        variante="saida"
        to="/saidas"
        :mostrarAcao="true"
        iconeAcao="pi pi-minus"
        @acao="abrirModalSaida"
      />

      <CardStatus
        :titulo="'Saldo ' + data().mesAtual"
        :valor="'7.000,00'"
        icone="pi pi-dollar"
        variante="entrada"
        to="/saldo"
      />
      <CardStatus
        :titulo="'Reserva Total '"
        :valor="'17.000,00'"
        icone="pi pi-folder-plus"
        variante="entrada"
        to="/reservas"
      />



    </div>

    <!-- ===== DIVISOR ===== -->
<div class="resumo-divider" style="margin-top: 30px; margin-bottom: 20px;">
  <span style="color: var(--texto-secundario); font-size: 1.2rem; font-weight: 500;">Resumo Financeiro</span>
</div>

<!-- ===== RESUMO ===== -->
<div class="cards-grid">

  <CardStatus
    icone="pi pi-money-bill"
    :titulo="'Consolidado ' + data().mesPassado"
    :valor="data().ConsolidadoMesPassado"
    variante="neutro"
  />
  
  <CardStatus
    icone="pi pi-money-bill"
    titulo="Gasto dos últimos 7 dias"
    :valor="data().resumoSemana"
    variante="saida"
  />

  <CardStatus
    icone="pi pi-money-bill"
    titulo="Gasto dos últimos 30 dias"
    :valor="data().resumoMes"
    variante="saida"
  />

  <CardStatus
        titulo="Maior Gasto do mês"
        :descricao="'Aluguel'"
        :valor="'2.700,00'"
        variante="saida"
  />

  <CardStatus
        titulo="Investimentos"
        :valor="'1.600,00'"
        icone="pi pi-chart-line"
        variante="entrada"
        to="/investimentos"
  />

  <CardStatus
        titulo="Meta Geral"
        :valor="'103.000,00'"
        icone="pi pi-bullseye"
        to="/metas"
        variante="neutro"
  />


</div>


</template>

<script setup>
import CardStatus from '@/components/CardStatus.vue'
import DiaHoje from '@/components/DiaHoje.vue'
import dayjs from 'dayjs'
import 'dayjs/locale/pt-br'
import { ref } from 'vue'

dayjs.locale('pt-br')

const data = () => {
  return {    
    mesAtual: dayjs().format('MMMM YYYY'),
    mesPassado: dayjs().subtract(1, 'month').format('MMMM'),
    resumoSemana: '1.600,00',
    resumoMes: '7.600,00',
    ConsolidadoMesPassado: '10.000,00',
  }
}


const abrirModalEntrada = () => {
  try {
    console.log('Abrir modal entrada')
  } catch (error) {
    console.error('Erro ao abrir modal entrada:', error)
  }
}

const abrirModalSaida = () => {
  try {
    console.log('Abrir modal saída')
  } catch (error) {
    console.error('Erro ao abrir modal saída:', error)
  }
}
</script>

<style scoped>

.page-title {
  color: var(--texto-primario);
  margin-bottom: 10px;
}

.cards-grid {
  margin-top: 25px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 25px;
}

</style>