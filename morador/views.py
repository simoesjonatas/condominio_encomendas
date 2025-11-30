from django.shortcuts import render, redirect, get_object_or_404
from .models import Bloco, Apartamento, Morador
from .forms import BlocoForm, ApartamentoForm, MoradorForm
from django.db.models import Q
from django.http import JsonResponse


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
    bloco_id = request.GET.get("bloco", "")
    numero = request.GET.get("numero", "")

    apartamentos = Apartamento.objects.select_related("bloco").all()

    if bloco_id:
        apartamentos = apartamentos.filter(bloco_id=bloco_id)

    if numero:
        apartamentos = apartamentos.filter(numero__icontains=numero)

    blocos = Bloco.objects.all().order_by("id")

    return render(request, "morador/lista_apartamentos.html", {
        "apartamentos": apartamentos,
        "blocos": blocos,
        "bloco_id": bloco_id,
        "numero": numero,
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
    nome = request.GET.get("nome", "")
    bloco_id = request.GET.get("bloco", "")
    apartamento_id = request.GET.get("apartamento", "")

    moradores = Morador.objects.all().prefetch_related("apartamentos")

    if nome:
        moradores = moradores.filter(nome__icontains=nome)

    if bloco_id:
        moradores = moradores.filter(apartamentos__bloco_id=bloco_id).distinct()

    if apartamento_id:
        moradores = moradores.filter(apartamentos__id=apartamento_id).distinct()

    blocos = Bloco.objects.all().order_by("id")
    apartamentos = Apartamento.objects.all().order_by("numero")

    return render(request, "morador/lista_moradores.html", {
        "moradores": moradores,
        "nome": nome,
        "bloco_id": bloco_id,
        "apartamento_id": apartamento_id,
        "blocos": blocos,
        "apartamentos": apartamentos,
    })

def ajax_apartamentos_por_bloco(request, bloco_id):
    apartamentos = Apartamento.objects.filter(bloco_id=bloco_id).order_by("numero")
    data = [{"id": a.id, "numero": a.numero} for a in apartamentos]
    return JsonResponse(data, safe=False)
# Criar morador
def novo_morador(request):
    if request.method == "POST":
        print("aq")
        form = MoradorForm(request.POST)
        if form.is_valid():
            print("aq")
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