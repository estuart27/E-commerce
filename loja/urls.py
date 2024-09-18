from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),  # URL para o admin deve vir antes de outras URLs para evitar conflitos
    path('', include('produto.urls')),  # Inclui URLs do app 'produto'
    path('perfil/', include('perfil.urls')),  # Inclui URLs do app 'perfil'
    path('pedido/', include('pedido.urls')),  # Inclui URLs do app 'pedido'
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Serve arquivos de mídia durante o desenvolvimento
