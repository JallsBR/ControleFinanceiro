from users.views.signin import Signin
from users.views.signup import Signup
from users.views.user import UserProfileView
from users.views.logout import Logout
from users.views.token_refresh import TokenRefreshViewDefaultDB
from users.views.admin_groups import (
    AdminGroupDetailView,
    AdminGroupListCreateView,
    AdminGroupOptionsView,
    AdminGroupPermissionsView,
    AdminPermissionTreeView,
)
from users.views.admin_users import AdminUserDetailView, AdminUserListView
from users.views.consultoria import (
    ConsultoriaClientesView,
    ConsultoriaSolicitacoesPendentesCountView,
    ConsultoriaVinculoAtualView,
    ConsultoriaVinculoEncerrarView,
)

from django.urls import path

urlpatterns = [
    path('signin', Signin.as_view()),
    path('signup', Signup.as_view()),
    path('logout', Logout.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshViewDefaultDB.as_view(), name='token_refresh'),
    path('user', UserProfileView.as_view(), name='user'),

    path('consultoria/vinculo-atual', ConsultoriaVinculoAtualView.as_view(), name='consultoria_vinculo_atual'),
    path('consultoria/clientes', ConsultoriaClientesView.as_view(), name='consultoria_clientes' ),
    path('consultoria/solicitacoes-pendentes-count', ConsultoriaSolicitacoesPendentesCountView.as_view(), name='consultoria_solicitacoes_pendentes_count' ),
    path('consultoria/vinculos/<int:pk>', ConsultoriaVinculoEncerrarView.as_view(), name='consultoria_vinculo_encerrar' ),

    path('admin/users', AdminUserListView.as_view(), name='admin_users'),
    path('admin/users/<int:pk>', AdminUserDetailView.as_view(), name='admin_user_detail'),
    path('admin/permissions/tree', AdminPermissionTreeView.as_view(), name='admin_permissions_tree'),
    path('admin/groups/<int:pk>/permissions', AdminGroupPermissionsView.as_view(), name='admin_group_permissions' ),
    path('admin/groups/options', AdminGroupOptionsView.as_view(), name='admin_group_options'),
    path('admin/groups/<int:pk>', AdminGroupDetailView.as_view(), name='admin_group_detail'),
    path('admin/groups', AdminGroupListCreateView.as_view(), name='admin_groups'),
]