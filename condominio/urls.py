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
from django.urls import path, include
from condominio.views import home
from encomendas.views import get_apartamentos, get_moradores
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", home, name="home"),
    path('encomendas/', include('encomendas.urls')),
    path('morador/', include('morador.urls')),
    path("login/", auth_views.LoginView.as_view(
        template_name="login.html"
    ), name="login"),

    path("logout/", auth_views.LogoutView.as_view(
        next_page="login"
    ), name="logout"),

    path('ajax/blocos/<int:bloco_id>/apartamentos/', get_apartamentos, name='get_apartamentos'),
    path('ajax/apartamentos/<int:apto_id>/moradores/', get_moradores, name='get_moradores'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
