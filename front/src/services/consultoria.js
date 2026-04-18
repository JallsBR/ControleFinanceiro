import api from './APIService'

/**
 * Serviço HTTP para consultoria (vínculos, solicitações em avisos).
 * Todas as funções usam try/catch e console.log para depuração.
 */

export async function getVinculoAtual () {
  try {
    const { data } = await api.get('/auth/consultoria/vinculo-atual')
    console.log('[consultoria] getVinculoAtual ok', data)
    return data
  } catch (error) {
    console.log('[consultoria] getVinculoAtual erro', error)
    throw error
  }
}

export async function getClientesDoConsultor () {
  try {
    const { data } = await api.get('/auth/consultoria/clientes')
    console.log('[consultoria] getClientesDoConsultor ok', data)
    return data
  } catch (error) {
    console.log('[consultoria] getClientesDoConsultor erro', error)
    throw error
  }
}

/** Encerra vínculo ativo (cliente ou consultor). ``consultoriaId``: PK de ``Consultoria``. */
export async function encerrarVinculoConsultoria (consultoriaId) {
  try {
    const { data } = await api.delete(
      `/auth/consultoria/vinculos/${consultoriaId}`
    )
    console.log('[consultoria] encerrarVinculoConsultoria ok', data)
    return data
  } catch (error) {
    console.log('[consultoria] encerrarVinculoConsultoria erro', error)
    throw error
  }
}

export async function getSolicitacoesPendentesCount () {
  try {
    const { data } = await api.get('/auth/consultoria/solicitacoes-pendentes-count')
    console.log('[consultoria] getSolicitacoesPendentesCount ok', data)
    return data
  } catch (error) {
    console.log('[consultoria] getSolicitacoesPendentesCount erro', error)
    throw error
  }
}

/**
 * @param {{ consultor_identifier: string, mensagem: string }} payload
 */
export async function createSolicitacaoConsultoria (payload) {
  try {
    const { data } = await api.post('/avisos/solicitacoes-consultoria/', payload)
    console.log('[consultoria] createSolicitacaoConsultoria ok', data)
    return data
  } catch (error) {
    console.log('[consultoria] createSolicitacaoConsultoria erro', error)
    throw error
  }
}

/**
 * Lista solicitações (paginação DRF). Útil para evolução da página Solicitações.
 * @param {Record<string, string|number|boolean>} [params] query, ex.: aceito=false
 */
export async function listSolicitacoes (params = {}) {
  try {
    const { data } = await api.get('/avisos/solicitacoes-consultoria/', { params })
    console.log('[consultoria] listSolicitacoes ok', data)
    return data
  } catch (error) {
    console.log('[consultoria] listSolicitacoes erro', error)
    throw error
  }
}

/**
 * Lista paginada (mesmo contrato que `financasService.*.getPage`).
 * @param {number|string} consultorId
 * @param {number} [page=1]
 * @param {{ search?: string, estado?: 'pendente'|'aceito'|'encerrada' }} [filtros]
 *   `estado`: query `estado` na API (pendente / aceito com vínculo ativo / encerrada).
 * @returns {{ data: array, total: number }}
 */
export async function getSolicitacoesRecebidasPage (
  consultorId,
  page = 1,
  filtros = {}
) {
  try {
    const params = { consultor: consultorId, page }
    const s = (filtros.search || '').trim()
    if (s) {
      params.search = s
    }
    const est = filtros.estado
    if (est === 'pendente' || est === 'aceito' || est === 'encerrada') {
      params.estado = est
    }
    const { data: body } = await api.get('/avisos/solicitacoes-consultoria/', {
      params
    })
    console.log('[consultoria] getSolicitacoesRecebidasPage ok', body)
    return {
      data: Array.isArray(body?.results) ? body.results : [],
      total: Number(body?.count) || 0
    }
  } catch (error) {
    console.log('[consultoria] getSolicitacoesRecebidasPage erro', error)
    throw error
  }
}

export async function aceitarSolicitacao (id) {
  try {
    const { data } = await api.patch(`/avisos/solicitacoes-consultoria/${id}/`, {
      aceito: true
    })
    console.log('[consultoria] aceitarSolicitacao ok', data)
    return data
  } catch (error) {
    console.log('[consultoria] aceitarSolicitacao erro', error)
    throw error
  }
}

/** Recusa: remove o registo na API (DELETE). */
export async function recusarSolicitacao (id) {
  try {
    const { data } = await api.delete(`/avisos/solicitacoes-consultoria/${id}/`)
    console.log('[consultoria] recusarSolicitacao ok', data)
    return data
  } catch (error) {
    console.log('[consultoria] recusarSolicitacao erro', error)
    throw error
  }
}
