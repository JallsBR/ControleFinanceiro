<template>

    <h1 class="page-title">Dashboard</h1>
    <DiaHoje :mostrarHora="true" />

    <div class="cards-grid">

      <CardStatus
        :titulo="'Entradas ' + mesAtualLabel"
        :valor="Money.format(dashboard.entradas)"
        icone="pi pi-wallet"
        variante="entrada"
        to="/entradas"
        :mostrarAcao="true"
        iconeAcao="pi pi-plus"
        @acao="abrirModalEntrada"
      />

      <CardStatus
        :titulo="'Saídas ' + mesAtualLabel"
        :valor="Money.format(dashboard.saidas)"
        icone="pi pi-credit-card"
        variante="saida"
        to="/saidas"
        :mostrarAcao="true"
        iconeAcao="pi pi-minus"
        @acao="abrirModalSaida"
      />

      <CardStatus
        :titulo="'Saldo ' + mesAtualLabel"
        :valor="Money.format(dashboard.saldo)"
        icone="pi pi-dollar"
        :variante="getVarianteByValor(dashboard.saldo)"
        to="/saldo"
      />
      <CardStatus
        :titulo="'Reserva Total '"
        :valor="Money.format(dashboard.reservas)"
        icone="pi pi-folder-plus"
        :variante="getVarianteByValor(dashboard.reservas)"
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
    :titulo="'Consolidado ' + mesPassadoLabel"
    :valor="Money.format(dashboard.consolidado)"
    :variante="getVarianteByValor(dashboard.consolidado)"
  />
  
  <CardStatus
    icone="pi pi-money-bill"
    titulo="Gasto dos últimos 7 dias"
    :valor="Money.format(dashboard.ultimos7dias)"
    variante="saida"
  />

  <CardStatus
    icone="pi pi-money-bill"
    titulo="Gasto dos últimos 30 dias"
    :valor="Money.format(dashboard.ultimos30dias)"
    variante="saida"
  />

  <CardStatus
        titulo="Maior Gasto do mês"
        :descricao="dashboard.descricao_maior_saida"
        :valor="Money.format(dashboard.maior_saida)"
        variante="saida"
  />

  <CardStatus
        titulo="Investimentos"
        :valor="Money.format(dashboard.investimentos)"
        icone="pi pi-chart-line"
        :variante="getVarianteByValor(dashboard.investimentos)"
        to="/investimentos"
  />

  <CardStatus
        titulo="Meta Geral"
        :valor="Money.format(dashboard.meta_geral)"
        icone="pi pi-bullseye"
        to="/metas"
        variante="neutro"
  />


</div>

<DialogEntradas v-model:visible="visibleEntrada" @saved="onEntradaSalva" />
<DialogSaida v-model:visible="visibleSaida" @saved="onSaidaSalva" />
</template>

<script setup>
import CardStatus from '@/components/CardStatus.vue'
import DiaHoje from '@/components/DiaHoje.vue'
import dayjs from 'dayjs'
import 'dayjs/locale/pt-br'
import { ref, computed, onMounted } from 'vue'
import financasService from '@/services/financasService'
import Money from '@/utils/Money'
import { useToast } from '@/utils/useToast'
import DialogEntradas from '@/pages/home/DialogEntradas.vue'
import DialogSaida from '@/pages/home/DialogSaida.vue'

const toast = useToast()

dayjs.locale('pt-br')

const visibleEntrada = ref(false)
const visibleSaida = ref(false)
const dashboard = ref({
  entradas: 0,
  saidas: 0,
  saldo: 0,
  reservas: 0,
  consolidado: 0,
  ultimos7dias: 0,
  ultimos30dias: 0,
  maior_saida: 0,
  descricao_maior_saida: '',
  investimentos: 0,
  meta_geral: 0
})

const mesAtualLabel = computed(() => dayjs().format('MMMM'))
const mesPassadoLabel = computed(() => dayjs().subtract(1, 'month').format('MMMM'))

const getVarianteByValor = (valor) => {
  const num = Number(valor || 0)
  if (num > 0) return 'entrada'
  if (num < 0) return 'saida'
  return 'neutro'
}

const carregarDashboard = async () => {
  try {
    const data = await financasService.dashboard.getDashboard()
    dashboard.value = data
  } catch (error) {
    console.error('Erro ao carregar dashboard:', error)
    toast.error('Erro', 'Não foi possível carregar o dashboard.')
  }
}

const onEntradaSalva = () => {
  carregarDashboard()
  toast.success('Entrada salva', 'Os dados do dashboard foram atualizados.')
}

const onSaidaSalva = () => {
  carregarDashboard()
  toast.success('Saída salva', 'Os dados do dashboard foram atualizados.')
}

onMounted(() => {
  carregarDashboard()
})


const abrirModalEntrada = () => {
  try {
    console.log('Abrir modal entrada')
    visibleEntrada.value = true
  } catch (error) {
    console.error('Erro ao abrir modal entrada:', error)
  }
}

const abrirModalSaida = () => {
  try {
    console.log('Abrir modal saída')
    visibleSaida.value = true
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