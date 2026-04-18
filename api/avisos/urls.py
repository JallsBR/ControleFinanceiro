from django.urls import path

from avisos import views

urlpatterns = [
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
