from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm


def home(request):
    return render(request, "home.html")


class BootstrapAuthenticationForm(AuthenticationForm):
    """Form de login com as classes/placeholders do Bootstrap."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Seu usuário",
            "autofocus": True,
        })
        self.fields["password"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Sua senha",
        })


class BootstrapPasswordChangeForm(PasswordChangeForm):
    """PasswordChangeForm do Django, mas com as classes do Bootstrap nos campos."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control",
                "autocomplete": "off",
            })


def perfil(request):
    """Página de perfil do usuário com troca de senha."""
    if request.method == "POST":
        form = BootstrapPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            # Mantém o usuário logado mesmo após trocar a senha
            update_session_auth_hash(request, user)
            messages.success(request, "Senha alterada com sucesso!")
            return redirect("perfil")
        messages.error(request, "Não foi possível alterar a senha. Verifique os campos abaixo.")
    else:
        form = BootstrapPasswordChangeForm(user=request.user)

    return render(request, "perfil.html", {"form": form})
