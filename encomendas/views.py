from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.utils import timezone
from .forms import EncomendaForm, EntregaForm
from .models import Encomenda
from django.http import JsonResponse
from morador.models import Apartamento, Morador, Bloco
from django.db.models import Q
from django.core.files.base import ContentFile
import base64
from django.utils.dateparse import parse_date
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.db.models import Count
import datetime




def entregar_encomenda(request, pk):
    encomenda = get_object_or_404(Encomenda, pk=pk)

    if request.method == "POST":
        form = EntregaForm(request.POST)

        if form.is_valid():
            encomenda.retirado_por = form.cleaned_data["retirado_por"]
            encomenda.data_retirada = timezone.now()
            encomenda.retirado = True

            # Converter assinatura base64 para arquivo PNG
            assinatura_base64 = form.cleaned_data["assinatura_base64"]

            if assinatura_base64:
                format, imgstr = assinatura_base64.split(";base64,")
                file_data = ContentFile(base64.b64decode(imgstr), name=f"assinatura_{pk}.png")
                encomenda.assinatura = file_data

            encomenda.save()

            return redirect("detalhes_encomenda", pk=encomenda.pk)

    else:
        form = EntregaForm()

    return render(request, "encomendas/entrega.html", {
        "form": form,
        "e": encomenda
    })

def dashboard_view(request):
    hoje = timezone.now().date()
    sete_dias = hoje - datetime.timedelta(days=6)

    # 1) Buscar encomendas dos últimos 7 dias
    qs = Encomenda.objects.filter(
        data_recebimento__range=(sete_dias, hoje)
    ).order_by("data_recebimento")

    # 2) Criar dicionário base com 0 para todos os dias
    dias_labels = []
    dias_totais = []
    dias_dict = {}

    for i in range(7):
        dia = sete_dias + datetime.timedelta(days=i)
        dias_dict[dia] = 0

    # 3) Contabilizar manualmente
    for e in qs:
        dias_dict[e.data_recebimento] += 1

    # 4) Preparar listas para o Chart.js
    for dia, total in dias_dict.items():
        dias_labels.append(dia.strftime("%d/%m"))
        dias_totais.append(total)

    # --- RESTO DA VIEW FICA IGUAL ---
    pendentes_hoje = Encomenda.objects.filter(data_recebimento=hoje, retirado=False).count()
    entregues_hoje = Encomenda.objects.filter(data_retirada__date=hoje).count()

    top_moradores = (
        Encomenda.objects
        .filter(morador__isnull=False)
        .values("morador__nome")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )

    moradores_labels = [item["morador__nome"] for item in top_moradores]
    moradores_totais = [item["total"] for item in top_moradores]

    return render(request, "encomendas/dashboard.html", {
        "dias_labels": dias_labels,
        "dias_totais": dias_totais,
        "pendentes_hoje": pendentes_hoje,
        "entregues_hoje": entregues_hoje,
        "moradores_labels": moradores_labels,
        "moradores_totais": moradores_totais,
    })

def imprimir_etiquetas_lote(request):
    if request.method != "POST":
        return redirect("lista_encomendas")

    ids = request.POST.getlist("ids")

    encomendas = Encomenda.objects.filter(id__in=ids).select_related(
        "apartamento", "apartamento__bloco", "morador"
    )

    return render(request, "encomendas/etiquetas_lote.html", {
        "encomendas": encomendas
    })



def etiqueta_encomenda(request, pk):
    encomenda = get_object_or_404(
        Encomenda.objects.select_related(
            "apartamento",
            "apartamento__bloco",
            "morador"
        ),
        pk=pk
    )

    return render(request, "encomendas/etiqueta.html", {
        "e": encomenda
    })


def historico_entregas(request):
    termo = request.GET.get("q", "").strip()

    entregues = Encomenda.objects.filter(retirado=True).select_related(
        "apartamento",
        "apartamento__bloco",
        "morador"
    )

    if termo:
        entregues = entregues.filter(
            Q(morador__nome__icontains=termo) |
            Q(apartamento__numero__icontains=termo) |
            Q(apartamento__bloco__nome__icontains=termo) |
            Q(descricao__icontains=termo) |
            Q(retirado_por__icontains=termo) |
            Q(sequencial_do_dia__icontains=termo) |
            Q(data_retirada__date__icontains=termo) |
            Q(data_recebimento__icontains=termo)
        )

    entregues = entregues.order_by("-data_retirada")

    return render(request, "encomendas/historico.html", {
        "entregues": entregues,
        "termo": termo,
    })
    

def buscar_apartamentos(request):
    q = request.GET.get("q", "")
    bloco_id = request.GET.get("bloco")

    apartamentos = Apartamento.objects.filter(bloco_id=bloco_id, numero__icontains=q)

    data = [{"id": ap.id, "numero": ap.numero} for ap in apartamentos]
    return JsonResponse(data, safe=False)


def buscar_moradores(request):
    q = request.GET.get("q", "")
    apt_id = request.GET.get("apartamento")

    qs = Morador.objects.all()
    if apt_id:
        qs = qs.filter(apartamentos=apt_id)
    if q:
        qs = qs.filter(nome__icontains=q)

    data = [{"id": m.id, "nome": m.nome} for m in qs.order_by("nome")]
    return JsonResponse(data, safe=False)



def buscar_encomendas(request):
    termo = request.GET.get("q", "").strip()

    resultados = []

    if termo:
        resultados = Encomenda.objects.filter(
            retirado=False
        ).filter(
            Q(morador__nome__icontains=termo) |
            Q(apartamento__numero__icontains=termo) |
            Q(apartamento__bloco__nome__icontains=termo) |
            Q(descricao__icontains=termo) |
            Q(sequencial_do_dia__icontains=termo)
        ).select_related("apartamento", "morador", "apartamento__bloco")

    return render(request, "encomendas/busca.html", {
        "termo": termo,
        "resultados": resultados
    })

def detalhes_encomenda(request, pk):
    encomenda = get_object_or_404(
        Encomenda.objects.select_related(
            "apartamento",
            "apartamento__bloco",
            "morador"
        ),
        pk=pk
    )

    return render(request, "encomendas/detalhes.html", {
        "e": encomenda
    })

def nova_encomenda(request):
    hoje = timezone.now().date()

    blocos = Bloco.objects.all()  # <-- adicionar

    if request.method == "POST":
        form = EncomendaForm(request.POST)
        if form.is_valid():
            encomenda = form.save(commit=False)

            # Obtém apartamento e morador enviados via select AJAX
            encomenda.apartamento_id = request.POST.get("apartamento")
            encomenda.morador_id = request.POST.get("morador")

            # Sequencial diário
            ultimo = Encomenda.objects.filter(data_recebimento=hoje).order_by('-sequencial_do_dia').first()
            encomenda.sequencial_do_dia = (ultimo.sequencial_do_dia + 1) if ultimo else 1

            encomenda.data_recebimento = hoje
            encomenda.recebido_por = request.user
            encomenda.save()

            return redirect("lista_encomendas")

    else:
        form = EncomendaForm()

    return render(request, "encomendas/nova_encomenda.html", {
        "form": form,
        "blocos": blocos,
        "hoje": hoje,
    })



def lista_encomendas(request):
    encomendas = Encomenda.objects.filter(retirado=False).order_by('-data_recebimento', '-sequencial_do_dia')

    return render(request, 'encomendas/lista_encomendas.html', {
        'encomendas': encomendas
    })

def get_apartamentos(request, bloco_id):
    aps = Apartamento.objects.filter(bloco_id=bloco_id).values('id', 'numero')
    return JsonResponse(list(aps), safe=False)

def get_moradores(request, apto_id):
    moradores = Morador.objects.filter(apartamentos__id=apto_id).values('id', 'nome')
    return JsonResponse(list(moradores), safe=False)