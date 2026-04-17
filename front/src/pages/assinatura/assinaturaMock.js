/**
 * Mock de referência para a tela de Assinatura (substituir por API depois).
 */
export const mockAssinaturaReferencia = {
  planoAtual: {
    slug: 'comum',
    nome: 'Comum',
    descricao:
      'Acesso completo ao controle financeiro pessoal: movimentações, categorias, reservas e metas.',
    statusLabel: 'Ativa',
    proximaRenovacao: '2026-05-15',
    beneficios: [
      'Dashboard e relatórios do mês',
      'Categorias e movimentações ilimitadas',
      'Backup dos seus dados na sua conta'
    ]
  },
  /** Plano Premium: três períodos de cobrança (referência de UI). */
  premiumProdutos: [
    {
      id: 'premium-3m',
      periodoLabel: '3 meses',
      meses: 3,
      precoTotal: 59.9,
      destaque: false,
      resumo: 'Ideal para experimentar os recursos premium.'
    },
    {
      id: 'premium-6m',
      periodoLabel: '6 meses',
      meses: 6,
      precoTotal: 99.9,
      destaque: true,
      resumo: 'Melhor custo-benefício para quem já usa o app no dia a dia.'
    },
    {
      id: 'premium-12m',
      periodoLabel: '1 ano',
      meses: 12,
      precoTotal: 179.9,
      destaque: false,
      resumo: 'Economia máxima com compromisso anual.'
    }
  ],
  premiumBeneficiosComuns: [
    'Relatórios avançados e exportação',
    'Metas e alertas personalizados',
    'Suporte prioritário por e-mail'
  ]
}
