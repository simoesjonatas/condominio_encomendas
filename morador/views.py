from django.shortcuts import render, redirect, get_object_or_404
from .models import Bloco, Apartamento, Morador
from .forms import BlocoForm, ApartamentoForm, MoradorForm
from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator


# Listar blocos
def lista_blocos(request):
    termo = request.GET.get("q", "").strip() or None
    page_number = request.GET.get("page", 1)

    blocos = Bloco.objects.all()

    if termo:
        blocos = blocos.filter(nome__icontains=termo)

    blocos = blocos.order_by("nome")

    # PAGINADOR
    paginator = Paginator(blocos, 10)
    page_obj = paginator.get_page(page_number)

    # Criar querystring sem o "page"
    params = request.GET.copy()
    params.pop("page", None)
    querystring = params.urlencode()

    return render(request, "morador/lista_blocos.html", {
        "blocos": page_obj,       # mantém compatível com o template
        "page_obj": page_obj,
        "querystring": querystring,
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
    bloco_id = request.GET.get("bloco", "").strip() or None
    numero   = request.GET.get("numero", "").strip() or None
    page_number = request.GET.get("page", 1)

    apartamentos = Apartamento.objects.select_related("bloco")

    if bloco_id:
        apartamentos = apartamentos.filter(bloco_id=bloco_id)
    if numero:
        apartamentos = apartamentos.filter(numero__icontains=numero)

    apartamentos = apartamentos.order_by("bloco__nome", "numero")

    paginator = Paginator(apartamentos, 15)
    page_obj = paginator.get_page(page_number)

    params = request.GET.copy()
    params.pop('page', None)
    querystring = params.urlencode()

    blocos = Bloco.objects.all().order_by("id")

    return render(request, "morador/lista_apartamentos.html", {
        "apartamentos": page_obj,
        "page_obj": page_obj,
        "querystring": querystring,
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
    # --- PEGANDO E LIMANDO OS FILTROS ---
    nome = request.GET.get("nome", "").strip() or None
    bloco_id = request.GET.get("bloco", "").strip() or None
    apartamento_id = request.GET.get("apartamento", "").strip() or None
    page_number = request.GET.get("page", 1)

    moradores = Morador.objects.prefetch_related("apartamentos").all()

    # --- APLICANDO FILTROS ---
    if nome:
        moradores = moradores.filter(nome__icontains=nome)

    if bloco_id:
        moradores = moradores.filter(apartamentos__bloco_id=bloco_id).distinct()

    if apartamento_id:
        moradores = moradores.filter(apartamentos__id=apartamento_id).distinct()

    moradores = moradores.order_by("nome")

    # --- PAGINAÇÃO ---
    paginator = Paginator(moradores, 15)
    page_obj = paginator.get_page(page_number)

    # --- QUERYSTRING (para preservar filtros) ---
    params = request.GET.copy()
    params.pop("page", None)
    querystring = params.urlencode()

    # --- DADOS PARA OS SELECTS ---
    blocos = Bloco.objects.all().order_by("id")
    apartamentos = Apartamento.objects.all().order_by("numero")

    return render(request, "morador/lista_moradores.html", {
        "moradores": page_obj,
        "page_obj": page_obj,
        "querystring": querystring,
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