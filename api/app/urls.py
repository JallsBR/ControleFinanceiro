from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static


def root_redirect(request):
    """Raiz (/) redireciona para o admin; evita servir app desktop/build antigo."""
    return redirect('/admin/')


urlpatterns = [
    path('', root_redirect),
    path('api-auth/', include('rest_framework.urls')),
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('users.urls')),
    path('api/v1/financas/', include('financas.urls')),


]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
