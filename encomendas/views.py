from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.utils import timezone
from .forms import EncomendaForm, EntregaForm
from .models import Encomenda
from django.contrib import messages
from django.http import JsonResponse
from morador.models import Apartamento, Morador, Bloco
from django.db.models import Q
from django.core.files.base import ContentFile
import base64
from django.utils.dateparse import parse_date
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.db.models import Count
from urllib.parse import urlencode
import datetime
from datetime import date
import re
from django.core.paginator import Paginator


def ler_qrcode_view(request):
    return render(request, "encomendas/ler_qrcode.html")

def ler_identificador_view(request):
    return render(request, "encomendas/ler_identificador.html")

def ler_identificador_busca_view(request):
    return render(request, "encomendas/ler_identificador_busca.html")


def processar_qrcode_view(request):
    codigo = request.GET.get("codigo", "").strip()

    # Exemplo de QR: BLOCO-A-101-11
    match = re.search(r"(\d+)$", codigo)

    encomenda = None

    if match:
        encomenda_id = match.group(1)

        # confere se existe antes de redirecionar
        encomenda = Encomenda.objects.filter(pk=encomenda_id).first()

    if encomenda:
        return redirect("detalhes_encomenda", pk=encomenda.pk)

    # Se não tiver match ou não existir encomenda com esse ID
    return render(request, "encomendas/qr_invalido.html", {"codigo": codigo})


def entregar_encomenda(request, pk):
    encomenda = get_object_or_404(Encomenda, pk=pk)

    # se já foi entregue, não deixa mais registrar
    if encomenda.retirado:
        messages.warning(
            request,
            f"Esta encomenda já foi entregue em {encomenda.data_retirada:%d/%m/%Y %H:%M} para {encomenda.retirado_por}."
        )
        return redirect("detalhes_encomenda", pk=encomenda.pk)


    if request.method == "POST":
        form = EntregaForm(request.POST)
        # print("Dados do formulário recebidos:", request.POST)
        if form.is_valid():
            encomenda.retirado_por = form.cleaned_data["retirado_por"]
            encomenda.data_retirada = timezone.now()
            encomenda.retirado = True

            # Apaga o QR Code ao entregar
            if encomenda.qr_code:
                encomenda.qr_code.delete(save=False)  # apaga o arquivo do disco
                encomenda.qr_code = None              # limpa o campo no banco

            assinatura_base64 = form.cleaned_data.get("assinatura_base64", "")
            # print("Assinatura Base64 recebida:", assinatura_base64)

            # Apenas processa se veio algo válido
            if assinatura_base64 and ";base64," in assinatura_base64:
                try:
                    format, imgstr = assinatura_base64.split(";base64,")
                    file_data = ContentFile(
                        base64.b64decode(imgstr),
                        name=f"assinatura_{pk}.png"
                    )
                    encomenda.assinatura = file_data
                except Exception as e:
                    print("Erro ao salvar assinatura:", e)

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

    # -------------------------
    # 1) RECEBIDAS NOS ÚLTIMOS 7 DIAS
    # -------------------------
    recebidas_qs = Encomenda.objects.filter(
        data_recebimento__range=(sete_dias, hoje)
    ).order_by("data_recebimento")

    recebidas_dict = {sete_dias + datetime.timedelta(days=i): 0 for i in range(7)}
    for e in recebidas_qs:
        recebidas_dict[e.data_recebimento] += 1

    recebidas_labels = [dia.strftime("%d/%m") for dia in recebidas_dict]
    recebidas_totais = list(recebidas_dict.values())

    # -------------------------
    # 2) ENTREGUES NOS ÚLTIMOS 7 DIAS
    # -------------------------
    entregues_qs = Encomenda.objects.filter(
        data_retirada__date__range=(sete_dias, hoje),
        retirado=True
    ).order_by("data_retirada")

    entregues_dict = {sete_dias + datetime.timedelta(days=i): 0 for i in range(7)}
    for e in entregues_qs:
        dia = e.data_retirada.date()
        if dia in entregues_dict:
            entregues_dict[dia] += 1

    entregues_labels = [dia.strftime("%d/%m") for dia in entregues_dict]
    entregues_totais = list(entregues_dict.values())

    # -------------------------
    # 3) BIG NUMBERS
    # -------------------------
    pendentes_hoje = Encomenda.objects.filter(
        data_recebimento=hoje,
        retirado=False
    ).count()

    pendentes_total = Encomenda.objects.filter(
        retirado=False
    ).count()

    entregues_hoje = Encomenda.objects.filter(
        data_retirada__date=hoje
    ).count()

    recebidas_hoje = Encomenda.objects.filter(
        data_recebimento=hoje
    ).count()

    return render(request, "encomendas/dashboard.html", {
        "pendentes_hoje": pendentes_hoje,
        "pendentes_total": pendentes_total,
        "entregues_hoje": entregues_hoje,
        "recebidas_hoje": recebidas_hoje,
        "recebidas_labels": recebidas_labels,
        "recebidas_totais": recebidas_totais,
        "entregues_labels": entregues_labels,
        "entregues_totais": entregues_totais,
    })


def confirmar_entrega_view(request, pk):
    encomenda = get_object_or_404(Encomenda, pk=pk)

    if encomenda.retirado:
        return render(request, "encomendas/ja_entregue.html", {"e": encomenda})

    if request.method == "POST":
        encomenda.retirado = True
        encomenda.data_retirada = timezone.now()
        encomenda.retirado_por = "QR Code"
        encomenda.save()
        return redirect("detalhes_encomenda", pk=pk)

    return render(request, "encomendas/confirmar_entrega_qr.html", {"e": encomenda})


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
    page_number = request.GET.get("page", 1)

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

    # PAGINADOR
    paginator = Paginator(entregues, 10)  # 10 registros por página
    page_obj = paginator.get_page(page_number)

    return render(request, "encomendas/historico.html", {
        "page_obj": page_obj,
        "entregues": page_obj,  # mantém compatível com o template existente
        "termo": termo,
    })


def buscar_apartamentos(request):
    q = request.GET.get("q", "")
    bloco_id = request.GET.get("bloco")

    if not bloco_id or bloco_id == "None":
        return JsonResponse([], safe=False)

    apartamentos = Apartamento.objects.filter(
        bloco_id=bloco_id,
        numero__icontains=q
    )

    data = [{"id": ap.id, "numero": ap.numero} for ap in apartamentos]
    return JsonResponse(data, safe=False)


def buscar_moradores(request):
    q = request.GET.get("q", "")
    apt_id = request.GET.get("apartamento")

    qs = Morador.objects.all()

    if apt_id and apt_id != "None":
        qs = qs.filter(apartamentos=apt_id)

    if q:
        qs = qs.filter(nome__icontains=q)

    data = [{"id": m.id, "nome": m.nome} for m in qs.order_by("nome")]
    return JsonResponse(data, safe=False)


def buscar_encomendas(request):
    # termo = request.GET.get("q", "").strip() or None
    termo = request.GET.get("q", "").strip()

    page_number = request.GET.get("page", 1)

    resultados = Encomenda.objects.none()  # default vazio

    if termo:

        # --------------------------------------------------------------
        # 1) BUSCAR POR SEQUENCIAL (#123)
        # --------------------------------------------------------------
        if termo.startswith("#"):
            num = termo[1:]  # remove o '#'

            if num.isdigit():
                resultados = Encomenda.objects.filter(
                    retirado=False,
                    sequencial_do_dia=num
                ).select_related("apartamento", "morador", "apartamento__bloco")

            # aplica paginação e retorna
            return render_with_pagination(request, resultados, termo, page_number)

        # --------------------------------------------------------------
        # 2) BUSCAR POR BLOCO/APTO (ex: 25/201)
        # --------------------------------------------------------------
        match = re.match(r"^(\w+)[\s]*/[\s]*(\w+)$", termo)
        if match:
            bloco_val = match.group(1)
            apto_val = match.group(2)

            resultados = Encomenda.objects.filter(
                retirado=False,
                apartamento__bloco__nome__icontains=bloco_val,
                apartamento__numero__icontains=apto_val
            ).select_related("apartamento", "morador", "apartamento__bloco")

        else:
            # ----------------------------------------------------------
            # 3) BUSCA NORMAL
            # ----------------------------------------------------------
            resultados = Encomenda.objects.filter(
                retirado=False
            ).filter(
                Q(morador__nome__icontains=termo) |
                Q(apartamento__numero__icontains=termo) |
                Q(apartamento__bloco__nome__icontains=termo) |
                Q(descricao__icontains=termo) |
                Q(identificador_pacote__icontains=termo) |
                Q(sequencial_do_dia__icontains=termo)
            ).select_related("apartamento", "morador", "apartamento__bloco")

    # chamada final com paginação
    return render_with_pagination(request, resultados, termo, page_number)


# -------------------------------------------------------------------------
# FUNÇÃO UTILITÁRIA PARA PAGINAR E RENDERIZAR
# -------------------------------------------------------------------------
def render_with_pagination(request, queryset, termo, page_number):
    total = queryset.count()  # total real antes da paginação

    paginator = Paginator(queryset.order_by("-data_recebimento"), 2)
    page_obj = paginator.get_page(page_number)

    params = request.GET.copy()
    params.pop("page", None)
    querystring = params.urlencode()

    return render(request, "encomendas/busca.html", {
        "termo": termo,
        "resultados": page_obj,
        "page_obj": page_obj,
        "querystring": querystring,
        "total_resultados": total,
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
    blocos = Bloco.objects.all()

    # recuperar os valores enviados de volta
    selected_bloco = request.GET.get("bloco")
    selected_apto = request.GET.get("apartamento")
    selected_morador = request.GET.get("morador")
    descricao = request.GET.get("descricao")
    local = request.GET.get("local")

    codigo_scaneado = request.GET.get("codigo", "")

    if request.method == "POST":
        form = EncomendaForm(request.POST)

        if form.is_valid():
            encomenda = form.save(commit=False)

            encomenda.apartamento_id = request.POST.get("apartamento")
            encomenda.morador_id = request.POST.get("morador")

            ultimo = Encomenda.objects.filter(
                data_recebimento=hoje
            ).order_by('-sequencial_do_dia').first()

            encomenda.sequencial_do_dia = (ultimo.sequencial_do_dia + 1) if ultimo else 1

            encomenda.data_recebimento = hoje
            encomenda.recebido_por = request.user

            if codigo_scaneado:
                encomenda.identificador_pacote = codigo_scaneado

            encomenda.save()
            return redirect("lista_encomendas")

    else:
        form = EncomendaForm()

        # repopular campos normais
        if descricao:
            form.fields["descricao"].initial = descricao
        if local:
            form.fields["local_armazenado"].initial = local
        if codigo_scaneado:
            form.fields["identificador_pacote"].initial = codigo_scaneado

    return render(request, "encomendas/nova_encomenda.html", {
        "form": form,
        "blocos": blocos,
        "selected_bloco": selected_bloco,
        "selected_apto": selected_apto,
        "selected_morador": selected_morador,
    })


def processar_identificador_view(request):
    codigo = request.GET.get("codigo")

    # resgatar parâmetros para não perder o formulário
    bloco = request.GET.get("bloco", "")
    apartamento = request.GET.get("apartamento", "")
    morador = request.GET.get("morador", "")
    descricao = request.GET.get("descricao", "")
    local = request.GET.get("local", "")

    params = urlencode({
        "codigo": codigo,
        "bloco": bloco,
        "apartamento": apartamento,
        "morador": morador,
        "descricao": descricao,
        "local": local,
    })

    return redirect(f"/encomendas/nova/?{params}")

def editar_encomenda(request, pk):
    encomenda = get_object_or_404(Encomenda, pk=pk)

    if request.method == "POST":
        form = EncomendaForm(request.POST, instance=encomenda)

        if form.is_valid():
            obj = form.save(commit=False)

            # força relacionamento correto
            obj.apartamento_id = request.POST.get("apartamento")
            obj.morador_id = request.POST.get("morador")

            obj.save()
            messages.success(request, "Encomenda atualizada com sucesso!")
            return redirect("detalhes_encomenda", pk=pk)

    else:
        form = EncomendaForm(instance=encomenda)

    # Pré-povoar selects (bloco, apto, morador)
    blocos = Bloco.objects.all()
    selected_bloco = encomenda.apartamento.bloco.id
    selected_apto = encomenda.apartamento.id
    selected_morador = encomenda.morador.id if encomenda.morador else ""

    return render(request, "encomendas/editar_encomenda.html", {
        "form": form,
        "e": encomenda,
        "blocos": blocos,
        "selected_bloco": selected_bloco,
        "selected_apto": selected_apto,
        "selected_morador": selected_morador,
    })




def lista_encomendas(request):
    encomendas = Encomenda.objects.filter(retirado=False)

    # filtros
    bloco = request.GET.get("bloco", "").strip() or None
    apto  = request.GET.get("apto", "").strip() or None
    data  = request.GET.get("data", "").strip() or None
    busca = request.GET.get("busca", "").strip()
    page_number = request.GET.get("page", 1)

    if bloco:
        encomendas = encomendas.filter(apartamento__bloco__id=bloco)

    if apto:
        encomendas = encomendas.filter(apartamento__id=apto)

    if data:
        encomendas = encomendas.filter(data_recebimento=data)

    if busca:
        encomendas = encomendas.filter(
            Q(morador__nome__icontains=busca) |
            Q(descricao__icontains=busca)
        )

    encomendas = encomendas.order_by('-data_recebimento', '-sequencial_do_dia')

    # PAGINADOR
    paginator = Paginator(encomendas, 10)   # 10 itens por página
    page_obj = paginator.get_page(page_number)

    blocos = Bloco.objects.all()
    apartamentos = Apartamento.objects.all()

    return render(request, 'encomendas/lista_encomendas.html', {
        'encomendas': page_obj,   # substitui pelo objeto paginado
        'page_obj': page_obj,

        # filtros
        'blocos': blocos,
        'apartamentos': apartamentos,
        'f_bloco': bloco,
        'f_apto': apto,
        'f_data': data,
        'f_busca': busca,
    })

def get_apartamentos(request, bloco_id):
    aps = Apartamento.objects.filter(bloco_id=bloco_id).values('id', 'numero')
    return JsonResponse(list(aps), safe=False)

def get_moradores(request, apto_id):
    moradores = Morador.objects.filter(apartamentos__id=apto_id).values('id', 'nome')
    return JsonResponse(list(moradores), safe=False)



def selecao_impressao(request):
    hoje = date.today()

    data = request.GET.get("data", str(hoje))
    pendentes = request.GET.get("pendentes", "on") == "on"
    bloco = request.GET.get("bloco", "")

    encomendas = Encomenda.objects.select_related(
        "apartamento", "apartamento__bloco", "morador"
    ).all()

    if data:
        encomendas = encomendas.filter(data_recebimento=data)

    if pendentes:
        encomendas = encomendas.filter(retirado=False)

    if bloco:
        encomendas = encomendas.filter(apartamento__bloco__id=bloco)

    blocos = Bloco.objects.all()

    return render(request, "encomendas/selecao_impressao.html", {
        "encomendas": encomendas,
        "data": data,
        "pendentes": pendentes,
        "blocos": blocos,
        "bloco_selecionado": bloco,
    })

def imprimir_encomendas(request):
    if request.method == "POST":
        ids = request.POST.getlist("ids")
        tipo = request.POST.get("tipo", "a4")
        # filtros da URL
        bloco = request.GET.get("bloco", "")
        apto = request.GET.get("apto", "")
        data = request.GET.get("data", "")
        busca = request.GET.get("busca", "")

        # Busca apenas as encomendas selecionadas
        encomendas = Encomenda.objects.filter(id__in=ids)


        if bloco:
            encomendas = encomendas.filter(apartamento__bloco__id=bloco)

        if apto:
            encomendas = encomendas.filter(apartamento__id=apto)

        if data:
            encomendas = encomendas.filter(data_recebimento=data)

        if busca:
            encomendas = encomendas.filter(
                Q(morador__nome__icontains=busca) |
                Q(descricao__icontains=busca)
            )

        # Escolhe o template conforme o tipo
        if tipo == "termica":
            template_name = "encomendas/impressao_termica.html"
        else:
            template_name = "encomendas/impressao_a4.html"

        return render(request, template_name, {
            "lista": encomendas
        })

    # Acesso inválido
    return redirect("selecao_impressao")
