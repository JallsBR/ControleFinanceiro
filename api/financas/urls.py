from django.urls import path
from . import views


urlpatterns = [
    
    path('categorias/', views.CategoriaListCreateView.as_view(), name='categoria-list-create'),
    path('categorias/<int:pk>/', views.CategoriaRetrieveUpdateDestroyView.as_view(), name='categoria-retrieve-update-destroy'),

    path('movimentacoes/', views.MovimentacaoListCreateView.as_view(), name='movimentacao-list-create'),
    path('movimentacoes/<int:pk>/', views.MovimentacaoRetrieveUpdateDestroyView.as_view(), name='movimentacao-retrieve-update-destroy'),
    
    path('movimentacoes-recorrentes/', views.MovimentacaoRecorrenteListCreateView.as_view(), name='movimentacao-recorrente-list-create'),
    path('movimentacoes-recorrentes/<int:pk>/', views.MovimentacaoRecorrenteRetrieveUpdateDestroyView.as_view(), name='movimentacao-recorrente-retrieve-update-destroy'),

]

