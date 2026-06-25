"""
URL configuration for condominio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from condominio.views import home, perfil, BootstrapAuthenticationForm
from encomendas.views import get_apartamentos, get_moradores, buscar_apartamentos, buscar_moradores
from morador.views import ajax_apartamentos_por_bloco
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", home, name="home"),
    path("perfil/", perfil, name="perfil"),
    path('encomendas/', include('encomendas.urls')),
    path('morador/', include('morador.urls')),
    path("login/", auth_views.LoginView.as_view(
        template_name="login.html",
        authentication_form=BootstrapAuthenticationForm,
        redirect_authenticated_user=True,
    ), name="login"),

    path("logout/", auth_views.LogoutView.as_view(
        next_page="login"
    ), name="logout"),

    path('ajax/blocos/<int:bloco_id>/apartamentos/', get_apartamentos, name='get_apartamentos'),
    path("ajax/buscar-apartamentos/", buscar_apartamentos, name="buscar_apartamentos"),
    path("ajax/buscar-moradores/", buscar_moradores, name="buscar_moradores"),
    path('ajax/apartamentos/<int:apto_id>/moradores/', get_moradores, name='get_moradores'),
    path("ajax/bloco/<int:bloco_id>/apartamentos/", ajax_apartamentos_por_bloco, name="ajax_apartamentos_bloco"),

]

# Arquivos de mídia (assinaturas e QR codes enviados pelos usuários).
# O WhiteNoise cuida apenas dos estáticos; a mídia é gerada em runtime, então
# precisamos servi-la pelo Django. O helper static() só funciona com DEBUG=True,
# por isso, em produção (DEBUG=False), servimos a mídia por uma rota explícita.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [
        re_path(
            r"^media/(?P<path>.*)$",
            serve,
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]
