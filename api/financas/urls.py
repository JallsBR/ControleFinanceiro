from django.urls import path
from . import views


urlpatterns = [
    
    path('categorias/', views.CategoriaListCreateView.as_view(), name='categoria-list-create'),
    path('categorias/<int:pk>/', views.CategoriaRetrieveUpdateDestroyView.as_view(), name='categoria-retrieve-update-destroy'),

    path('movimentacoes/', views.MovimentacaoListCreateView.as_view(), name='movimentacao-list-create'),
    path('movimentacoes/<int:pk>/', views.MovimentacaoRetrieveUpdateDestroyView.as_view(), name='movimentacao-retrieve-update-destroy'),
    
    path('movimentacoes-recorrentes/', views.MovimentacaoRecorrenteListCreateView.as_view(), name='movimentacao-recorrente-list-create'),
    path('movimentacoes-recorrentes/<int:pk>/', views.MovimentacaoRecorrenteRetrieveUpdateDestroyView.as_view(), name='movimentacao-recorrente-retrieve-update-destroy'),

    path('metas/', views.MetaListCreateView.as_view(), name='meta-list-create'),
    path('metas/<int:pk>/', views.MetaRetrieveUpdateDestroyView.as_view(), name='meta-retrieve-update-destroy'),

    path('consolidados-mensais/', views.ConsolidadoMensalListCreateView.as_view(), name='consolidado-mensal-list-create'),
    path('consolidados-mensais/<int:pk>/', views.ConsolidadoMensalRetrieveUpdateDestroyView.as_view(), name='consolidado-mensal-retrieve-update-destroy'),

    path('icone/', views.IconeListCreateView.as_view(), name='icone-list-create'),
    path('icone/<int:pk>/', views.IconeRetrieveUpdateDestroyView.as_view(), name='icone-retrieve-update-destroy'),
    
]

