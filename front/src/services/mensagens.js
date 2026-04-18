import api from './APIService'

/**
 * Contagem de mensagens não lidas (caixa do contexto atual, incl. modo visualização).
 */
export async function getMensagensNaoLidasCount () {
  const { data } = await api.get('/avisos/mensagens/nao-lidas/')
  return Number(data?.count) || 0
}

/** Utilizadores permitidos como destino de uma nova mensagem (API auxiliar). */
export async function getDestinatariosMensagens () {
  const { data } = await api.get('/avisos/mensagens/destinatarios/')
  return Array.isArray(data?.results) ? data.results : []
}

/**
 * Lista conversas (inbox).
 * @param {{ nome?: string, q?: string, favorita?: boolean }} params
 */
export async function listConversas (params = {}) {
  const query = {}
  if (params.nome) query.nome = params.nome
  if (params.q) query.q = params.q
  if (params.favorita === true) query.favorita = 'true'
  const { data } = await api.get('/avisos/mensagens/conversas/', { params: query })
  return Array.isArray(data?.results) ? data.results : []
}

/**
 * Lista mensagens (filtros opcionais).
 * @param {Record<string, string|number|boolean>} params
 */
export async function listMensagens (params = {}) {
  const { data } = await api.get('/avisos/mensagens/', { params })
  return Array.isArray(data) ? data : data?.results || []
}

/**
 * @param {{ destino_id?: number, mensagem: string, resposta?: number|null }} payload
 */
export async function criarMensagem (payload) {
  const { data } = await api.post('/avisos/mensagens/', payload)
  return data
}

/**
 * @param {number} id
 * @param {Record<string, unknown>} patch
 */
export async function patchMensagem (id, patch) {
  const { data } = await api.patch(`/avisos/mensagens/${id}/`, patch)
  return data
}

export async function eliminarMensagem (id) {
  await api.delete(`/avisos/mensagens/${id}/`)
}

/** Marca como lidas todas as mensagens recebidas na thread. */
export async function marcarThreadLidas (threadRootId) {
  const { data } = await api.post(
    `/avisos/mensagens/threads/${threadRootId}/marcar-lidas/`
  )
  return data
}
