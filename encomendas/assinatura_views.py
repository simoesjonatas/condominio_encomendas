from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404,redirect
import base64
from .models import Encomenda
from django.utils.timezone import make_aware
from datetime import datetime
from django.contrib import messages
import io
import zipfile
from django.urls import reverse
from django.core.paginator import Paginator


def listar_assinaturas(request):

    data_inicio = request.GET.get("data_inicio")
    data_fim = request.GET.get("data_fim")
    page = request.GET.get("page", 1)

    encomendas = Encomenda.objects.filter(
        retirado=True,
        assinatura__isnull=False
    ).order_by("-data_retirada").select_related("apartamento", "apartamento__bloco")

    # FILTROS
    if data_inicio and data_inicio != "None":
        try:
            dt_inicio = make_aware(datetime.strptime(data_inicio, "%Y-%m-%d"))
            encomendas = encomendas.filter(data_retirada__gte=dt_inicio)
        except ValueError:
            pass   # ignora valores inválidos

    if data_fim and data_fim != "None":
        try:
            dt_fim = make_aware(datetime.strptime(data_fim, "%Y-%m-%d"))
            encomendas = encomendas.filter(data_retirada__lte=dt_fim)
        except ValueError:
            pass

    # PAGINAÇÃO
    paginator = Paginator(encomendas, 15)
    page_obj = paginator.get_page(page)

    return render(request, "encomendas/listar_assinaturas.html", {
        "encomendas": page_obj,
        "page_obj": page_obj,
        "data_inicio": data_inicio if data_inicio != "None" else "",
        "data_fim": data_fim if data_fim != "None" else "",
    })



def download_assinatura(request, pk):
    encomenda = get_object_or_404(Encomenda, pk=pk)

    if not encomenda.assinatura:
        raise Http404("Assinatura não encontrada.")

    file = encomenda.assinatura
    response = HttpResponse(file.open("rb"), content_type="image/png")
    response["Content-Disposition"] = f'attachment; filename="assinatura_{pk}.png"'
    return response

def baixar_assinaturas_zip(request):
    # FILTROS
    data_inicio = request.GET.get("data_inicio")
    data_fim = request.GET.get("data_fim")

    encomendas = Encomenda.objects.filter(
        retirado=True,
        assinatura__isnull=False
    ).select_related("apartamento", "apartamento__bloco")

    if data_inicio:
        data_inicio_dt = make_aware(datetime.strptime(data_inicio, "%Y-%m-%d"))
        encomendas = encomendas.filter(data_retirada__gte=data_inicio_dt)

    if data_fim:
        data_fim_dt = make_aware(datetime.strptime(data_fim, "%Y-%m-%d"))
        encomendas = encomendas.filter(data_retirada__lte=data_fim_dt)

    # CRIAR ZIP NA MEMÓRIA
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:

        for e in encomendas:
            try:
                # NOME FORMATADO
                bloco = e.apartamento.bloco.nome.replace(" ", "")
                apto = e.apartamento.numero.replace(" ", "")
                nome = (e.retirado_por or "SemNome").replace(" ", "_")
                data_fmt = e.data_retirada.strftime("%Y-%m-%d_%H-%M")

                filename = f"assinatura_{e.id}_{bloco}_{apto}_{nome}_{data_fmt}.png"

                # TENTAR LER O ARQUIVO
                with e.assinatura.open("rb") as f:
                    image_data = f.read()

                zip_file.writestr(filename, image_data)

            except FileNotFoundError:
                # IGNORA SE ARQUIVO NÃO EXISTIR
                continue
            except Exception:
                # QUALQUER OUTRO ERRO — APENAS PULA TAMBÉM
                continue

    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/zip")
    response["Content-Disposition"] = "attachment; filename=assinaturas.zip"

    return response


def confirmar_apagar_assinaturas(request):
    data_inicio = request.GET.get("data_inicio")
    data_fim = request.GET.get("data_fim")

    encomendas = Encomenda.objects.filter(
        retirado=True,
        assinatura__isnull=False
    )

    if data_inicio:
        try:
            dt_inicio = make_aware(datetime.strptime(data_inicio, "%Y-%m-%d"))
            encomendas = encomendas.filter(data_retirada__gte=dt_inicio)
        except:
            pass

    if data_fim:
        try:
            dt_fim = make_aware(datetime.strptime(data_fim, "%Y-%m-%d"))
            encomendas = encomendas.filter(data_retirada__lte=dt_fim)
        except:
            pass

    return render(request, "encomendas/confirmar_apagar_assinaturas.html", {
        "encomendas": encomendas,
        "data_inicio": data_inicio,
        "data_fim": data_fim
    })


def executar_apagar_assinaturas(request):
    if request.method != "POST":
        return HttpResponse("Método inválido.", status=405)

    data_inicio = request.POST.get("data_inicio")
    data_fim = request.POST.get("data_fim")
    confirm_text = request.POST.get("confirm_text", "").strip()

    # 🔒 validação obrigatória
    if confirm_text != "CONFIRMAR":
        messages.error(
            request,
            "Você precisa digitar CONFIRMAR exatamente para autorizar a exclusão das assinaturas."
        )
        url = reverse("confirmar_apagar_assinaturas")
        return redirect(f"{url}?data_inicio={data_inicio or ''}&data_fim={data_fim or ''}")

    encomendas = Encomenda.objects.filter(
        retirado=True,
        assinatura__isnull=False
    )

    if data_inicio:
        try:
            dt_inicio = make_aware(datetime.strptime(data_inicio, "%Y-%m-%d"))
            encomendas = encomendas.filter(data_retirada__gte=dt_inicio)
        except:
            pass

    if data_fim:
        try:
            dt_fim = make_aware(datetime.strptime(data_fim, "%Y-%m-%d"))
            encomendas = encomendas.filter(data_retirada__lte=dt_fim)
        except:
            pass

    total = 0

    for e in encomendas:
        try:
            if e.assinatura:
                e.assinatura.delete(save=False)  # apaga arquivo físico
            e.assinatura = None
            e.save(update_fields=["assinatura"])
            total += 1
        except:
            continue

    messages.success(request, f"{total} assinaturas apagadas com sucesso (registros de entrega foram mantidos).")
    return redirect("listar_assinaturas")