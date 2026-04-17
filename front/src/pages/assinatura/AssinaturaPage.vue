<template>
  <div class="assinatura-page">
    <CardStatus
      tituloPrincipal="Assinatura"
      subtitulo="Consulte seu plano atual e conheça as opções Premium (referência visual — dados mock)"
      icone="pi pi-id-card"
      style="margin-bottom: 1rem;"
    />

    <!-- Plano atual -->
    <section class="assinatura-secao" aria-labelledby="titulo-plano-atual">
      <h2 id="titulo-plano-atual" class="assinatura-secao-titulo">Plano atual</h2>

      <div class="assinatura-card assinatura-card--atual">
        <div class="assinatura-card-head">
          <div>
            <span class="assinatura-plano-nome">{{ mock.planoAtual.nome }}</span>
            <Tag severity="success" :value="mock.planoAtual.statusLabel" class="assinatura-tag" />
          </div>
          <span class="assinatura-slug">{{ mock.planoAtual.slug }}</span>
        </div>
        <p class="assinatura-descricao">
          {{ mock.planoAtual.descricao }}
        </p>
        <p class="assinatura-renovacao">
          <i class="pi pi-calendar" aria-hidden="true" />
          Próxima renovação (mock): <strong>{{ formatarDataIso(mock.planoAtual.proximaRenovacao) }}</strong>
        </p>
        <ul class="assinatura-lista">
          <li v-for="(b, i) in mock.planoAtual.beneficios" :key="'b-' + i">
            <i class="pi pi-check assinatura-lista-icone" aria-hidden="true" />
            {{ b }}
          </li>
        </ul>
        <p class="assinatura-aviso-mock">
          <i class="pi pi-info-circle" aria-hidden="true" />
          Na maioria das contas o plano ativo é <strong>Comum</strong>. Os valores abaixo são apenas ilustrativos.
        </p>
      </div>
    </section>

    <!-- Premium: 3 produtos -->
    <section class="assinatura-secao" aria-labelledby="titulo-premium">
      <h2 id="titulo-premium" class="assinatura-secao-titulo">Premium</h2>
      <p class="assinatura-secao-sub">
        Três períodos de assinatura: três meses, seis meses e um ano. Integração de pagamento em desenvolvimento.
      </p>

      <ul class="assinatura-premium-beneficios">
        <li v-for="(t, i) in mock.premiumBeneficiosComuns" :key="'pb-' + i">
          {{ t }}
        </li>
      </ul>

      <div class="assinatura-premium-grid">
        <div
          v-for="p in mock.premiumProdutos"
          :key="p.id"
          class="assinatura-premium-card"
          :class="{ 'assinatura-premium-card--destaque': p.destaque }"
        >
          <div v-if="p.destaque" class="assinatura-destaque-fita">
            Mais popular
          </div>
          <h3 class="assinatura-premium-titulo">{{ p.periodoLabel }}</h3>
          <p class="assinatura-premium-resumo">{{ p.resumo }}</p>
          <div class="assinatura-preco-bloco">
            <span class="assinatura-preco">{{ Money.format(p.precoTotal, { currency: true }) }}</span>
            <span class="assinatura-preco-det">
              total · {{ p.meses }} {{ p.meses === 1 ? 'mês' : 'meses' }}
            </span>
            <span class="assinatura-preco-equiv">
              ≈ {{ Money.format(precoMensalEquiv(p), { currency: true }) }}/mês
            </span>
          </div>
          <Button
            label="Escolher (mock)"
            :severity="p.destaque ? undefined : 'secondary'"
            class="assinatura-cta"
            icon="pi pi-shopping-cart"
            @click="onEscolherPremium(p)"
          />
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import CardStatus from '@/components/CardStatus.vue'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import Money from '@/utils/Money.js'
import { mockAssinaturaReferencia } from './assinaturaMock'
import { useToast } from '@/utils/useToast'

const mock = mockAssinaturaReferencia
const toast = useToast()

function formatarDataIso (iso) {
  if (!iso) return '—'
  const [y, m, d] = iso.split('-')
  if (!y || !m || !d) return iso
  return `${d}/${m}/${y}`
}

function precoMensalEquiv (produto) {
  if (!produto.meses) return 0
  return Math.round((produto.precoTotal / produto.meses) * 100) / 100
}

function onEscolherPremium (produto) {
  toast.info(
    'Em breve',
    `Checkout não integrado. Produto mock: Premium ${produto.periodoLabel} (${Money.format(produto.precoTotal, { currency: true })}).`
  )
}
</script>

<style scoped>
.assinatura-page {
  margin-bottom: 1.5rem;
}

.assinatura-secao {
  margin-bottom: 1.75rem;
}

.assinatura-secao-titulo {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--texto-primario);
}

.assinatura-secao-sub {
  margin: 0 0 1rem 0;
  font-size: 0.9rem;
  line-height: 1.45;
  color: var(--texto-secundario);
}

.assinatura-card {
  background: var(--bg-secundario);
  border-radius: 18px;
  padding: 1.25rem 1.5rem;
  border: 1px solid color-mix(in srgb, var(--texto-secundario) 18%, transparent);
}

.assinatura-card--atual {
  border-color: color-mix(in srgb, var(--sucesso) 35%, transparent);
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--sucesso) 12%, transparent);
}

.assinatura-card-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.assinatura-card-head > div:first-child {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
}

.assinatura-plano-nome {
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--texto-primario);
}

.assinatura-tag {
  font-size: 0.75rem;
}

.assinatura-slug {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--texto-secundario);
}

.assinatura-descricao {
  margin: 0 0 0.75rem 0;
  font-size: 0.95rem;
  line-height: 1.5;
  color: var(--texto-primario);
}

.assinatura-renovacao {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin: 0 0 1rem 0;
  font-size: 0.9rem;
  color: var(--texto-secundario);
}

.assinatura-renovacao i {
  color: var(--sucesso);
}

.assinatura-lista {
  margin: 0;
  padding: 0 0 0 0.25rem;
  list-style: none;
}

.assinatura-lista li {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  margin-bottom: 0.45rem;
  font-size: 0.9rem;
  color: var(--texto-primario);
}

.assinatura-lista-icone {
  color: var(--sucesso);
  margin-top: 0.15rem;
  flex-shrink: 0;
}

.assinatura-aviso-mock {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  margin: 1rem 0 0 0;
  padding: 0.65rem 0.75rem;
  font-size: 0.82rem;
  line-height: 1.45;
  color: var(--texto-secundario);
  background: var(--bg-primario);
  border-radius: 10px;
  border: 1px solid color-mix(in srgb, var(--texto-secundario) 15%, transparent);
}

.assinatura-aviso-mock i {
  color: var(--texto-secundario);
  margin-top: 0.1rem;
}

.assinatura-premium-beneficios {
  margin: 0 0 1.25rem 0;
  padding-left: 1.15rem;
  color: var(--texto-secundario);
  font-size: 0.88rem;
  line-height: 1.5;
}

.assinatura-premium-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
}

@media (max-width: 900px) {
  .assinatura-premium-grid {
    grid-template-columns: 1fr;
  }
}

.assinatura-premium-card {
  position: relative;
  background: var(--bg-secundario);
  border-radius: 18px;
  padding: 1.25rem 1.25rem 1.35rem;
  border: 1px solid color-mix(in srgb, var(--texto-secundario) 18%, transparent);
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

.assinatura-premium-card--destaque {
  border-color: color-mix(in srgb, var(--sucesso) 45%, transparent);
  box-shadow: 0 4px 20px color-mix(in srgb, var(--sucesso) 10%, transparent);
}

.assinatura-destaque-fita {
  position: absolute;
  top: 0.65rem;
  right: 0.65rem;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  background: color-mix(in srgb, var(--sucesso) 22%, var(--bg-secundario));
  color: var(--sucesso);
}

.assinatura-premium-titulo {
  margin: 0 0 0.35rem 0;
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--texto-primario);
  padding-right: 4.5rem;
}

.assinatura-premium-resumo {
  margin: 0 0 1rem 0;
  font-size: 0.85rem;
  line-height: 1.45;
  color: var(--texto-secundario);
  flex: 1;
}

.assinatura-preco-bloco {
  margin-bottom: 1rem;
}

.assinatura-preco {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--texto-primario);
}

.assinatura-preco-det {
  display: block;
  font-size: 0.8rem;
  color: var(--texto-secundario);
  margin-top: 0.15rem;
}

.assinatura-preco-equiv {
  display: block;
  font-size: 0.82rem;
  color: var(--texto-secundario);
  margin-top: 0.35rem;
}

.assinatura-cta {
  width: 100%;
  margin-top: auto;
}
</style>
