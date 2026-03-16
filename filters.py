# -*- coding: utf-8 -*-
"""
Pipeline de filtragem de preços em 5 camadas.
Remove outliers e normaliza preços para obter valores representativos.
"""

import re
import numpy as np
from config import BLACKLIST_DESCRICAO, BLACKLIST_ESTABELECIMENTO


def filtrar_por_ncm(produtos, ncm_prefixos):
    """
    Camada 1: Filtra produtos pelo código NCM (fiscal).
    Mantém apenas produtos cujo NCM começa com um dos prefixos permitidos.
    """
    filtrados = []
    for p in produtos:
        ncm = p.get("ncm", "")
        if any(ncm.startswith(prefixo) for prefixo in ncm_prefixos):
            filtrados.append(p)

    removidos = len(produtos) - len(filtrados)
    if removidos > 0:
        print(f"    🔹 NCM: removidos {removidos} itens não-alimentícios")

    return filtrados


def filtrar_por_blacklist(produtos):
    """
    Camada 2: Remove produtos com palavras proibidas na descrição
    ou no nome do estabelecimento (restaurantes, farmácias, etc).
    """
    filtrados = []
    for p in produtos:
        desc = p.get("desc", "").upper()
        estab = p.get("estabelecimento", {})
        nome_estab = (
            estab.get("nm_fan", "") + " " + estab.get("nm_emp", "")
        ).upper()

        # Verificar blacklist de descrição
        desc_bloqueada = any(
            termo in desc for termo in BLACKLIST_DESCRICAO
        )

        # Verificar blacklist de estabelecimento
        estab_bloqueado = any(
            termo in nome_estab for termo in BLACKLIST_ESTABELECIMENTO
        )

        if not desc_bloqueada and not estab_bloqueado:
            filtrados.append(p)

    removidos = len(produtos) - len(filtrados)
    if removidos > 0:
        print(f"    🔹 Blacklist: removidos {removidos} itens (restaurantes/farmácias/etc)")

    return filtrados


def extrair_peso_kg(descricao, peso_padrao_kg=1.0):
    """
    Extrai o peso em kg da descrição do produto.
    Lida com padrões comuns de gramatura rural e industrial.
    Ex: "ARROZ BURITI 5KG" → 5.0
        "CAFÉ MELITTA 500G" → 0.5
        "LEITE INTEGRAL 1L" → 1.0
        "MANTEIGA 200 GR" → 0.2
        "2 X 200G" → 0.4
    Se "UN" estiver presente isolado sem medidas e o item costuma ser unitário 
    mas ter peso padrão (ex: manteiga de 200g), assume o peso_padrao_kg.
    """
    descricao = descricao.upper()

    # Tratamento para multiplicadores (ex: "LEITE 12X1L", "MOLHO 3 X 340G")
    multiplicador = 1.0
    match_mult = re.search(r"(\d+)\s*[X\*]\s*(\d)", descricao)
    if match_mult:
        try:
            multiplicador = float(match_mult.group(1))
            # Remove a parte do multiplicador da string para não confundir o regex principal
            descricao = re.sub(r"(\d+)\s*[X\*]\s*", "", descricao, count=1)
        except ValueError:
            pass

    # Padrões: número + unidade (KG, G, GR, ML, L)
    padroes = [
        (r"(\d+(?:[.,]\d+)?)\s*KG", 1.0),       # kg
        (r"(\d+(?:[.,]\d+)?)\s*(?:GR?)\b", 0.001),  # gramas → kg
        (r"(\d+(?:[.,]\d+)?)\s*ML", 0.001),      # ml → kg (aprox)
        (r"(\d+(?:[.,]\d+)?)\s*L\b", 1.0),       # litros → kg (aprox)
    ]

    for padrao, fator in padroes:
        match = re.search(padrao, descricao)
        if match:
            valor = float(match.group(1).replace(",", "."))
            peso_total = valor * fator * multiplicador
            # Validação: peso razoável (10g a 50kg)
            if 0.01 <= peso_total <= 50:
                return peso_total

    # Se a descrição indicar explicitamente que é unidade/peça mas sem peso
    if re.search(r"\b(UN|UNID|UND|PCT|PACOTE|SACO)\b", descricao):
        # Muitas vezes o "peso padrão" do produto no config já expressa essa unidade
        return peso_padrao_kg

    return peso_padrao_kg


def normalizar_preco_por_kg(produtos, peso_padrao_kg=1.0):
    """
    Camada 3: Normaliza todos os preços para R$/kg.
    Extrai o peso da descrição e calcula preço unitário.
    """
    for p in produtos:
        desc = p.get("desc", "")
        valor = float(p.get("valor", 0))
        peso = extrair_peso_kg(desc, peso_padrao_kg)

        p["peso_extraido_kg"] = peso
        p["preco_por_kg"] = valor / peso if peso > 0 else valor

    return produtos


def filtrar_por_iqr(produtos, campo="preco_por_kg"):
    """
    Camada 4: Remove outliers estatísticos via método IQR (Interquartil).
    Remove valores abaixo de Q1 - 1.5*IQR ou acima de Q3 + 1.5*IQR.
    """
    if len(produtos) < 4:
        # Poucos dados, não aplicar IQR
        return produtos

    precos = [p[campo] for p in produtos if campo in p]

    if not precos:
        return produtos

    q1 = np.percentile(precos, 25)
    q3 = np.percentile(precos, 75)
    iqr = q3 - q1

    # Limites
    limite_inferior = q1 - 1.5 * iqr
    limite_superior = q3 + 1.5 * iqr

    filtrados = [
        p for p in produtos
        if limite_inferior <= p.get(campo, 0) <= limite_superior
    ]

    removidos = len(produtos) - len(filtrados)
    if removidos > 0:
        print(
            f"    🔹 IQR: removidos {removidos} outliers "
            f"(limites: R${limite_inferior:.2f} - R${limite_superior:.2f}/kg)"
        )

    return filtrados


def calcular_estatisticas(produtos, campo="preco_por_kg"):
    """
    Camada 5: Calcula estatísticas finais dos preços filtrados.
    Retorna mediana (preço representativo), mínimo e máximo.
    """
    if not produtos:
        return {
            "mediana": 0,
            "minimo": 0,
            "maximo": 0,
            "num_amostras": 0,
            "produto_mediana": None,
        }

    precos = sorted([p[campo] for p in produtos])

    mediana = float(np.median(precos))
    minimo = min(precos)
    maximo = max(precos)

    # Encontrar o produto mais próximo da mediana
    produto_mediana = min(produtos, key=lambda p: abs(p.get(campo, 0) - mediana))

    return {
        "mediana": mediana,
        "minimo": minimo,
        "maximo": maximo,
        "num_amostras": len(precos),
        "produto_mediana": produto_mediana,
    }


def pipeline_filtragem(produtos, ncm_prefixos, peso_padrao_kg=1.0):
    """
    Executa o pipeline completo de filtragem em 5 camadas.

    Args:
        produtos: Lista de produtos da API
        ncm_prefixos: Lista de prefixos NCM permitidos
        peso_padrao_kg: Peso padrão se não extraído da descrição

    Returns:
        Dicionário com estatísticas e lista de produtos filtrados
    """
    print(f"    📊 Total bruto da API: {len(produtos)} resultados")

    if not produtos:
        return calcular_estatisticas([])

    # Camada 1: NCM
    produtos = filtrar_por_ncm(produtos, ncm_prefixos)
    if not produtos:
        return calcular_estatisticas([])

    # Camada 2: Blacklist
    produtos = filtrar_por_blacklist(produtos)
    if not produtos:
        return calcular_estatisticas([])

    # Camada 3: Normalizar preço/kg
    produtos = normalizar_preco_por_kg(produtos, peso_padrao_kg)

    # Camada 4: IQR
    produtos = filtrar_por_iqr(produtos)
    if not produtos:
        return calcular_estatisticas([])

    # Camada 5: Estatísticas
    stats = calcular_estatisticas(produtos)
    stats["produtos_filtrados"] = produtos

    print(
        f"    ✅ Após filtragem: {stats['num_amostras']} amostras | "
        f"Mediana: R${stats['mediana']:.2f}/kg | "
        f"Min: R${stats['minimo']:.2f}/kg | "
        f"Max: R${stats['maximo']:.2f}/kg"
    )

    return stats
