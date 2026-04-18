<template>
  <div class="consultoria-page">
    <CardStatus
      tituloPrincipal="Consultoria"
      subtitulo="Acompanhamento por um consultor e canal de comunicação após aceite."
      icone="pi pi-comments"
      style="margin-bottom: 1rem;"
    />

    <Message
      v-if="modoMonitorVisualizacao"
      severity="info"
      :closable="false"
      class="consultoria-msg consultoria-msg--fora"
    >
      Modo de visualização administrativa: os dados de consultoria (vínculo, clientes ou pedidos em aguardo) correspondem ao utilizador que está a monitorizar, como na conta dele.
    </Message>

    <Message v-if="erroCarregar" severity="warn" :closable="false" class="consultoria-msg consultoria-msg--fora">
      {{ erroCarregar }}
    </Message>

    <div v-if="carregando" class="consultoria-panel consultoria-panel--loading">
      <ProgressSpinner style="width: 42px; height: 42px;" stroke-width="4" />
      <span>A carregar…</span>
    </div>

    <template v-else>
      <!-- Consultor (gerente): textos + grelha de cards (sem painel extra, padrão home) -->
      <div v-if="isConsultor" class="consultoria-consultor" aria-labelledby="titulo-consultor">
        <h2 id="titulo-consultor" class="consultoria-secao-titulo">Os seus clientes</h2>
        <p class="consultoria-secao-texto">
          Usuários com consultoria ativa.
        </p>
        <p v-if="!clientes.length" class="consultoria-secao-texto consultoria-secao-texto--muted">
          Ainda não tem clientes com consultoria ativa.
        </p>
        <div v-else class="consultoria-cards-grid">
          <ConsultorCard
            v-for="c in clientes"
            :key="c.consultoria_id ?? c.id"
            :nome="c.nome_exibicao || c.username"
            :subtitulo="c.email"
            :cliente-user-id="c.id"
            :consultoria-id="c.consultoria_id"
            :encerrando="
              encerrandoVinculoId != null &&
                Number(encerrandoVinculoId) === Number(c.consultoria_id)
            "
            @encerrar="() => solicitarEncerramentoVinculo(c.consultoria_id)"
          />
        </div>
      </div>

      <!-- Utilizador com consultor já vinculado -->
      <div
        v-else-if="vinculoConsultor"
        class="consultoria-vinculo"
        aria-labelledby="titulo-vinculo"
      >
        <h2 id="titulo-vinculo" class="consultoria-secao-titulo">O seu consultor</h2>
        <p class="consultoria-secao-texto">
          Tem consultoria ativa. O consultor tem acesso aos seus dados financeiros conforme o acordo de consultoria.
        </p>
        <ConsultorCard
          :nome="vinculoConsultor.nome_exibicao || vinculoConsultor.username"
          :subtitulo="vinculoConsultor.email"
          :mostrar-visualizar="false"
          :consultoria-id="vinculoConsultoriaId"
          :encerrando="
            encerrandoVinculoId != null &&
              Number(encerrandoVinculoId) === Number(vinculoConsultoriaId)
          "
          @encerrar="() => solicitarEncerramentoVinculo(vinculoConsultoriaId)"
        />
      </div>

      <!-- Formulário: solicitar consultoria -->
      <div v-else class="consultoria-panel" aria-labelledby="titulo-solicitar">
        <Message
          v-if="solicitacoesEnviadasPendentes.length"
          severity="warn"
          :closable="false"
          class="consultoria-msg"
        >
          <p class="consultoria-msg-pendente mb-0">
            Tem
            <template v-if="solicitacoesEnviadasPendentes.length === 1">
              um pedido de consultoria em aguardo
            </template>
            <template v-else>
              {{ solicitacoesEnviadasPendentes.length }} pedidos de consultoria em aguardo
            </template>
            (aguardam aceite ou recusa por parte do consultor)
            <template v-if="textoConsultoresPendentes">
              : <strong>{{ textoConsultoresPendentes }}</strong>
            </template>.
            Não é possível enviar outro pedido ao mesmo consultor enquanto existir um pedido pendente.
          </p>
        </Message>

        <h2 id="titulo-solicitar" class="consultoria-secao-titulo">Solicitar consultoria</h2>

        <Message v-if="erroEnvio" severity="error" :closable="true" class="consultoria-msg" @close="erroEnvio = ''">
          {{ erroEnvio }}
        </Message>

        <form class="consultoria-form" @submit.prevent="enviar">
          <div class="consultoria-form-grid">
            <div class="consultoria-form-col consultoria-form-col--esq">
              <div class="field mb-0">
                <label for="consultor-id" class="field-label">E-mail ou nome de utilizador do consultor</label>
                <InputText
                  id="consultor-id"
                  v-model="consultorIdentifier"
                  class="w-full"
                  type="text"
                  autocomplete="off"
                  placeholder="ex.: maria.silva ou consultor@empresa.com"
                  :disabled="enviando"
                />
                <small class="consultoria-hint">Não mostramos uma lista de consultores; identifique a pessoa que já lhe foi indicada.</small>
              </div>

              <Divider class="consultoria-divider-h" />

              <div class="consultoria-aviso-bloco">
                <p class="consultoria-aviso-titulo">Antes de enviar</p>
                <ul class="consultoria-aviso-lista">
                  <li>
                    <strong>Acesso aos dados:</strong> após aceitação, o consultor poderá aceder aos seus dados financeiros na plataforma (no âmbito da consultoria).
                  </li>
                  <li>
                    <strong>Comunicação:</strong> será aberto um canal direto de comunicação após o consultor aceitar o pedido (funcionalidade em evolução).
                  </li>
                </ul>
              </div>
            </div>

            <Divider
              layout="vertical"
              type="solid"
              class="consultoria-divider-v"
            />

            <div class="consultoria-form-col consultoria-form-col--dir">
              <div class="field consultoria-field-mensagem mb-0">
                <label for="consultoria-msg" class="field-label">Mensagem</label>
                <Textarea
                  id="consultoria-msg"
                  v-model="mensagem"
                  class="w-full consultoria-textarea"
                  fluid
                  rows="8"
                  :disabled="enviando"
                  placeholder="Explique brevemente o resultado que pretende (até 250 caracteres)."
                  :maxlength="250"
                />
              </div>
            </div>
          </div>

          <div class="consultoria-actions">
            <Button
              type="submit"
              label="Enviar pedido"
              icon="pi pi-send"
              :loading="enviando"
              :disabled="enviando"
            />
          </div>
        </form>
      </div>

      <DialogConfirma
        v-model="visibleConfirmaEncerrar"
        titulo="Encerrar consultoria?"
        mensagem="Tem a certeza de que pretende encerrar esta consultoria? O acesso na plataforma deixa de estar ativo para este vínculo."
        icone="pi pi-trash"
        tipo="danger"
        labelConfirmar="Encerrar"
        labelCancelar="Cancelar"
        iconeConfirmar="pi pi-trash"
        severityConfirmar="danger"
        :loading="encerrandoVinculoId != null"
        @confirm="confirmarEncerramentoVinculo"
        @cancel="cancelarEncerramentoVinculo"
      />
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import CardStatus from '@/components/CardStatus.vue'
import ConsultorCard from '@/components/ConsultorCard.vue'
import DialogConfirma from '@/components/DialogConfirma.vue'
import Message from 'primevue/message'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Button from 'primevue/button'
import Divider from 'primevue/divider'
import ProgressSpinner from 'primevue/progressspinner'
import * as consultoriaService from '@/services/consultoria'
import { useToast } from '@/utils/useToast'

const store = useStore()
const toast = useToast()

const modoMonitorVisualizacao = computed(() => store.getters.subjectViewAdminActive)
const user = computed(() => store.getters.getUser)
const monitored = computed(() => store.getters.getSubjectMonitoredUser)
/** Painel de consultor só para gerente real ou staff a ver um gerente. */
const isConsultor = computed(() => {
  if (store.getters.subjectViewConsultorActive) return false
  if (user.value?.is_gerente) return true
  return Boolean(
    modoMonitorVisualizacao.value && monitored.value?.is_gerente
  )
})

const carregando = ref(true)
const erroCarregar = ref('')

const vinculoConsultor = ref(null)
/** PK ``Consultoria`` quando o utilizador é cliente com vínculo ativo. */
const vinculoConsultoriaId = ref(null)
const clientes = ref([])
const encerrandoVinculoId = ref(null)
const visibleConfirmaEncerrar = ref(false)
/** PK ``Consultoria`` escolhida no diálogo antes de confirmar. */
const consultoriaIdPendenteEncerrar = ref(null)

const consultorIdentifier = ref('')
const mensagem = ref('')
const enviando = ref(false)
const erroEnvio = ref('')
/** Pedidos enviados por este utilizador ainda sem aceite nem eliminação (lista API). */
const solicitacoesEnviadasPendentes = ref([])

function nomeConsultorBreve (c) {
  if (!c) return ''
  if (c.nome_exibicao) return c.nome_exibicao
  const n = `${c.first_name || ''} ${c.last_name || ''}`.trim()
  return n || c.username || c.email || ''
}

const textoConsultoresPendentes = computed(() =>
  solicitacoesEnviadasPendentes.value
    .map((s) => nomeConsultorBreve(s.consultor))
    .filter(Boolean)
    .join(', ')
)

async function refreshSolicitacoesPendentesCliente () {
  solicitacoesEnviadasPendentes.value = []
  if (isConsultor.value || vinculoConsultor.value) {
    return
  }
  let uid = user.value?.id
  if (modoMonitorVisualizacao.value) {
    const sid = Number(store.state.subjectViewMode?.userId)
    uid = Number.isFinite(sid) ? sid : null
  }
  if (!uid) return
  try {
    const sol = await consultoriaService.listSolicitacoes({
      usuario: uid,
      estado: 'pendente',
      page: 1
    })
    solicitacoesEnviadasPendentes.value = Array.isArray(sol?.results)
      ? sol.results
      : []
  } catch (e) {
    console.log('[consultoria] refreshSolicitacoesPendentesCliente', e)
  }
}

function extrairMensagemErro (error) {
  const d = error?.response?.data
  if (!d) return 'Não foi possível concluir o pedido. Tente novamente.'
  if (typeof d.detail === 'string') return d.detail
  if (Array.isArray(d.detail)) return d.detail.map(String).join(' ')
  const firstKey = Object.keys(d)[0]
  if (firstKey && Array.isArray(d[firstKey])) return d[firstKey].join(' ')
  if (firstKey && typeof d[firstKey] === 'string') return d[firstKey]
  return 'Não foi possível concluir o pedido. Verifique os dados.'
}

async function carregar () {
  carregando.value = true
  erroCarregar.value = ''
  try {
    if (isConsultor.value) {
      const data = await consultoriaService.getClientesDoConsultor()
      clientes.value = Array.isArray(data?.results) ? data.results : []
      vinculoConsultor.value = null
      vinculoConsultoriaId.value = null
      solicitacoesEnviadasPendentes.value = []
    } else {
      const data = await consultoriaService.getVinculoAtual()
      vinculoConsultor.value = data?.consultor || null
      vinculoConsultoriaId.value = data?.consultoria_id ?? null
      clientes.value = []
      await refreshSolicitacoesPendentesCliente()
    }
  } catch (e) {
    console.log('[consultoria] carregar', e)
    erroCarregar.value = extrairMensagemErro(e)
  } finally {
    carregando.value = false
  }
}

function solicitarEncerramentoVinculo (consultoriaId) {
  const id =
    consultoriaId != null && consultoriaId !== ''
      ? Number(consultoriaId)
      : NaN
  if (!Number.isFinite(id) || encerrandoVinculoId.value != null) return
  consultoriaIdPendenteEncerrar.value = id
  visibleConfirmaEncerrar.value = true
}

function cancelarEncerramentoVinculo () {
  consultoriaIdPendenteEncerrar.value = null
  visibleConfirmaEncerrar.value = false
}

async function confirmarEncerramentoVinculo () {
  const id = consultoriaIdPendenteEncerrar.value
  if (id == null || !Number.isFinite(Number(id))) {
    cancelarEncerramentoVinculo()
    return
  }
  encerrandoVinculoId.value = Number(id)
  try {
    await consultoriaService.encerrarVinculoConsultoria(Number(id))
    toast.success('Consultoria', 'O vínculo foi encerrado.')
    visibleConfirmaEncerrar.value = false
    consultoriaIdPendenteEncerrar.value = null
    await carregar()
    await store.dispatch('fetchConsultoriaResumo')
  } catch (e) {
    console.log('[consultoria] confirmarEncerramentoVinculo', e)
    toast.error('Consultoria', extrairMensagemErro(e))
  } finally {
    encerrandoVinculoId.value = null
  }
}

async function enviar () {
  erroEnvio.value = ''
  const idf = consultorIdentifier.value.trim()
  const msg = mensagem.value.trim()
  if (!idf || !msg) {
    erroEnvio.value = 'Preencha o identificador do consultor e a mensagem.'
    return
  }
  enviando.value = true
  try {
    await consultoriaService.createSolicitacaoConsultoria({
      consultor_identifier: idf,
      mensagem: msg
    })
    toast.success(
      'Consultoria',
      'Pedido enviado. O consultor será notificado quando a área de solicitações estiver disponível.'
    )
    consultorIdentifier.value = ''
    mensagem.value = ''
    await refreshSolicitacoesPendentesCliente()
    await store.dispatch('fetchConsultoriaResumo')
  } catch (e) {
    console.log('[consultoria] enviar', e)
    erroEnvio.value = extrairMensagemErro(e)
  } finally {
    enviando.value = false
  }
}

onMounted(async () => {
  try {
    await store.dispatch('refreshUserProfile')
  } catch (e) {
    console.log('[consultoria] refreshUserProfile', e)
  }
  if (modoMonitorVisualizacao.value && store.state.subjectViewMode?.userId) {
    try {
      await store.dispatch('fetchSubjectMonitoredProfile')
    } catch (e) {
      console.log('[consultoria] fetchSubjectMonitoredProfile', e)
    }
  }
  await carregar()
})
</script>

<style scoped>
.consultoria-page {
  margin-bottom: 1.5rem;
}

.consultoria-msg--fora {
  margin-bottom: 0.75rem;
}

.consultoria-msg {
  margin-bottom: 1rem;
}

.consultoria-msg-pendente {
  line-height: 1.5;
}

.consultoria-panel {
  background: var(--bg-secundario);
  border-radius: 18px;
  padding: 1.25rem 1.5rem;
  width: 100%;
  box-sizing: border-box;
}

.consultoria-panel--loading {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: var(--texto-secundario);
}

.consultoria-secao-titulo {
  margin: 0 0 1rem;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--texto-primario);
}

.consultoria-secao-texto {
  margin: 0 0 1rem;
  line-height: 1.5;
  color: var(--texto-primario);
}

.consultoria-secao-texto--muted {
  color: var(--texto-secundario);
}

.consultoria-consultor .consultoria-secao-titulo,
.consultoria-vinculo .consultoria-secao-titulo {
  margin-top: 0;
}

/* ~1/5 da largura útil por card (5 colunas); menos colunas em ecrãs estreitos */
.consultoria-cards-grid {
  margin-top: 1.25rem;
  display: grid;
  gap: 0.4rem;
  grid-template-columns: repeat(5, minmax(0, 1fr));
}

@media (max-width: 1024px) {
  .consultoria-cards-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

@media (max-width: 780px) {
  .consultoria-cards-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 560px) {
  .consultoria-cards-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 340px) {
  .consultoria-cards-grid {
    grid-template-columns: minmax(0, 1fr);
  }
}

.consultoria-form {
  margin-top: 0.25rem;
}

.consultoria-form-grid {
  display: flex;
  align-items: stretch;
  width: 100%;
  gap: 0;
}

.consultoria-form-col {
  flex: 1 1 0;
  min-width: 0;
  padding: 0 1rem;
}

.consultoria-form-col--esq {
  padding-left: 0;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.consultoria-form-col--dir {
  padding-right: 0;
  display: flex;
  flex-direction: column;
}

.consultoria-field-mensagem {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
}

.consultoria-textarea {
  width: 100%;
  min-height: 12rem;
  box-sizing: border-box;
}

.consultoria-divider-h {
  margin: 1rem 0;
  width: 100%;
}

.consultoria-divider-v {
  flex: 0 0 auto;
  align-self: stretch;
  margin: 0;
}

.consultoria-aviso-bloco {
  margin-top: 0;
}

.consultoria-aviso-titulo {
  margin: 0 0 0.5rem;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--texto-primario);
}

.consultoria-aviso-lista {
  margin: 0;
  padding-left: 1.2rem;
  line-height: 1.55;
  color: var(--texto-primario);
}

.consultoria-hint {
  display: block;
  margin-top: 0.35rem;
  color: var(--texto-secundario);
  font-size: 0.85rem;
}

.field-label {
  display: block;
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--texto-primario);
  margin-bottom: 0.35rem;
}

.consultoria-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.25rem;
  padding-top: 1rem;
  border-top: 1px solid color-mix(in srgb, var(--texto-secundario) 18%, transparent);
}

.w-full {
  width: 100%;
}

@media (max-width: 768px) {
  .consultoria-form-grid {
    flex-direction: column;
  }

  .consultoria-divider-v {
    display: none;
  }

  .consultoria-form-col {
    padding: 0;
  }

  .consultoria-form-col--dir {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid color-mix(in srgb, var(--texto-secundario) 22%, transparent);
  }
}

:deep(.consultoria-divider-v.p-divider-vertical) {
  min-height: 100%;
}

:deep(.consultoria-textarea.p-textarea) {
  width: 100%;
  min-height: 12rem;
  box-sizing: border-box;
}
</style>
