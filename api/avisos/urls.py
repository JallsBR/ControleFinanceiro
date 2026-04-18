from django.urls import path

from avisos import views

urlpatterns = [
    path(
        "mensagens/conversas/",
        views.MensagemConversasView.as_view(),
        name="avisos-mensagem-conversas",
    ),
    path(
        "mensagens/threads/<int:thread_root_id>/marcar-lidas/",
        views.MensagemMarcarThreadLidasView.as_view(),
        name="avisos-mensagem-thread-marcar-lidas",
    ),
    path(
        "mensagens/nao-lidas/",
        views.MensagemNaoLidasCountView.as_view(),
        name="avisos-mensagem-nao-lidas",
    ),
    path(
        "mensagens/destinatarios/",
        views.MensagemDestinatariosView.as_view(),
        name="avisos-mensagem-destinatarios",
    ),
    path(
        "mensagens/",
        views.MensagemListCreateView.as_view(),
        name="avisos-mensagem-list-create",
    ),
    path(
        "mensagens/<int:pk>/",
        views.MensagemRetrieveUpdateDestroyView.as_view(),
        name="avisos-mensagem-detail",
    ),
    path(
        "solicitacoes-consultoria/",
        views.SolicitacaoConsultoriaListCreateView.as_view(),
        name="avisos-solicitacao-list-create",
    ),
    path(
        "solicitacoes-consultoria/<int:pk>/",
        views.SolicitacaoConsultoriaRetrieveUpdateDestroyView.as_view(),
        name="avisos-solicitacao-detail",
    ),
]
