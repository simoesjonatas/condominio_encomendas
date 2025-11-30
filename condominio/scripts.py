from morador.models import Bloco, Apartamento

def criar_blocos_e_apartamentos_por_quantidade(qtd_blocos, lista_apartamentos):
    """
    Cria blocos numerados de 1 até qtd_blocos
    e cria todos os apartamentos informados para cada bloco.
    """
    for i in range(1, qtd_blocos + 1):
        nome_bloco = str(i)  # se quiser, pode ser f"Bloco {i}"
        bloco, created_bloco = Bloco.objects.get_or_create(nome=nome_bloco)

        for numero in lista_apartamentos:
            Apartamento.objects.get_or_create(
                bloco=bloco,
                numero=str(numero),
            )

    print("✔ Blocos e apartamentos criados com sucesso!")

def gerar_apartamentos(qtd_andares=4, qtd_por_andar=4):
    apartamentos = []
    for andar in range(1, qtd_andares + 1):
        for num in range(1, qtd_por_andar + 1):
            apto = f"{andar}{num:02d}"  # 1 + 01 → "101"
            apartamentos.append(apto)
    return apartamentos

# apartamentos = gerar_apartamentos(qtd_andares=4, qtd_por_andar=4)

# apartamentos = [
#     "101", "102", "103", "104",
#     "201", "202", "203", "204",
#     "301", "302", "303", "304",
#     "401", "402", "403", "404",
# ]

# from condominio.scripts import criar_blocos_e_apartamentos_por_quantidade
# # ↑ troque "condominio" pelo nome real do seu app

# qtd_blocos = 4
# apartamentos = [101, 102, 103, 104, 201, 202, 203, 204]

# criar_blocos_e_apartamentos_por_quantidade(qtd_blocos, apartamentos)
