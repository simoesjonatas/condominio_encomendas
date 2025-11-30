from django.shortcuts import render, redirect, get_object_or_404
from .models import Bloco, Apartamento, Morador
from .forms import BlocoForm, ApartamentoForm, MoradorForm
from django.db.models import Q

# Listar blocos
def lista_blocos(request):
    termo = request.GET.get("q", "")  # pega ?q=...
    
    if termo:
        blocos = Bloco.objects.filter(nome__icontains=termo)
    else:
        blocos = Bloco.objects.all()

    return render(request, "morador/lista_blocos.html", {
        "blocos": blocos,
        "termo": termo,
    })



# Criar bloco
def novo_bloco(request):
    if request.method == "POST":
        form = BlocoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("lista_blocos")
    else:
        form = BlocoForm()

    return render(request, "morador/novo_bloco.html", {"form": form})


# Listar apartamentos
def lista_apartamentos(request):
    termo = request.GET.get("q", "")

    qs = Apartamento.objects.select_related("bloco")

    if termo:
        qs = qs.filter(
            Q(numero__icontains=termo) |
            Q(bloco__nome__icontains=termo)
        )

    return render(request, "morador/lista_apartamentos.html", {
        "apartamentos": qs,
        "termo": termo,
    })


# Criar apartamento
def novo_apartamento(request):
    if request.method == "POST":
        form = ApartamentoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("lista_apartamentos")
    else:
        form = ApartamentoForm()

    return render(request, "morador/novo_apartamento.html", {
        "form": form
    })


# Listar moradores
def lista_moradores(request):
    moradores = Morador.objects.all()
    return render(request, "morador/lista_moradores.html", {
        "moradores": moradores
    })


# Criar morador
def novo_morador(request):
    if request.method == "POST":
        form = MoradorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("lista_moradores")
    else:
        form = MoradorForm()

    return render(request, "morador/novo_morador.html", {
        "form": form
    })


# Editar morador
def editar_morador(request, pk):
    morador = get_object_or_404(Morador, pk=pk)

    if request.method == "POST":
        form = MoradorForm(request.POST, instance=morador)
        if form.is_valid():
            form.save()
            return redirect("lista_moradores")
    else:
        form = MoradorForm(instance=morador)

    return render(request, "morador/editar_morador.html", {
        "form": form,
        "morador": morador
    })