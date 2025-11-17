from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredMiddleware:
    """
    Redireciona para a tela de login se o usuário não estiver autenticado,
    exceto nas URLs liberadas (login, admin login, static, media).
    """

    def __init__(self, get_response):
        self.get_response = get_response

        # URLs que não exigem login
        self.exempt_urls = {
            reverse("login"),
            reverse("admin:login"),
            reverse("admin:logout"),
        }

        # Se você tiver mais URLs públicas, adiciona aqui depois

    def __call__(self, request):
        path = request.path

        # Libera static e media
        if settings.STATIC_URL and path.startswith(settings.STATIC_URL):
            return self.get_response(request)

        if settings.MEDIA_URL and path.startswith(settings.MEDIA_URL):
            return self.get_response(request)

        # Se a URL estiver nas liberadas, segue
        if path in self.exempt_urls:
            return self.get_response(request)

        # Se não estiver autenticado, manda pro login
        if not request.user.is_authenticated:
            return redirect("%s?next=%s" % (reverse("login"), path))

        # Senão, continua normalmente
        return self.get_response(request)
