# -*- coding: utf-8 -*-
"""
Script coletor principal.
Busca os 13 itens da cesta básica DIEESE na API do Menor Preço,
aplica o pipeline de filtragem e salva no banco de dados.

Uso:
    python collector.py                     # Coleta para Curitiba (padrão)
    python collector.py --cidade Londrina   # Coleta para Londrina
    python collector.py --cidade todas      # Coleta para todas as cidades configuradas
"""

import argparse
from datetime import datetime

from config import PRODUTOS_DIEESE, CIDADES_PADRAO, CIDADE_PADRAO
from api_client import MenorPrecoAPI
from filters import pipeline_filtragem
from database import init_db, salvar_coleta, salvar_cesta, salvar_detalhes_produtos


def coletar_cidade(api, cidade, data_coleta, progress_callback=None):
    """
    Executa a coleta completa para uma cidade.

    Args:
        api: Instância de MenorPrecoAPI
        cidade: Nome da cidade
        data_coleta: Data no formato YYYY-MM-DD
        progress_callback: Função callback(percent, msg) para progresso (Streamlit)

    Returns:
        Custo total da cesta ou None em caso de erro
    """
    print(f"\n{'='*60}")
    print(f"🏙️  Coletando preços para: {cidade}")
    print(f"📅 Data: {data_coleta}")
    print(f"{'='*60}")

    # Obter geohash da cidade
    geohash = api.buscar_geohash_cidade(cidade)
    if not geohash:
        print(f"❌ Não foi possível localizar a cidade '{cidade}'. Pulando...")
        return None

    custo_total = 0
    produtos_encontrados = 0

    num_total = len(PRODUTOS_DIEESE)
    for i, produto in enumerate(PRODUTOS_DIEESE):
        nome = produto["nome"]
        termos = produto["termo_busca"]
        if isinstance(termos, str):
            termos = [termos]
            
        quantidade = produto["quantidade_kg"]
        ncm_prefixos = produto["ncm_prefixos"]
        peso_padrao = produto["peso_padrao_kg"]

        percentual = (i / num_total)
        mensagem = f"Pesquisando {nome}..."
        if progress_callback:
            progress_callback(percentual, mensagem)

        print(f"\n  🔍 Buscando: {nome} (termos: {termos})")

        # Buscar na API (acumulando resultados de múltiplos termos)
        todos_resultados = []
        for termo in termos:
            print(f"    - Pesquisando termo: '{termo}'...")
            resultados_termo = api.buscar_produtos(termo, geohash)
            todos_resultados.extend(resultados_termo)
            
        # Deduplicação básica baseada em GTIN ou Descrição + Preço + Estabelecimento
        vistos = set()
        resultados_dedup = []
        for r in todos_resultados:
            # Criar uma chave única para o produto
            gtin = r.get("gtin")
            if gtin and gtin != "N/A":
                chave = f"gtin_{gtin}"
            else:
                desc = r.get("desc", "").upper()
                valor = r.get("valor", "")
                estab_id = r.get("estabelecimento", {}).get("id", "")
                chave = f"desc_{desc}_{valor}_{estab_id}"
            
            if chave not in vistos:
                vistos.add(chave)
                resultados_dedup.append(r)
        
        if len(todos_resultados) > len(resultados_dedup):
            print(f"    ✨ Deduplicação: removidos {len(todos_resultados) - len(resultados_dedup)} itens duplicados")

        # Aplicar pipeline de filtragem
        stats = pipeline_filtragem(resultados_dedup, ncm_prefixos, peso_padrao)

        if stats["num_amostras"] > 0:
            # Salvar no banco
            custo_item = salvar_coleta(
                data_coleta=data_coleta,
                cidade=cidade,
                produto_dieese=nome,
                termo_busca="; ".join(termos),
                stats=stats,
                quantidade_dieese=quantidade,
            )

            # Salvar detalhes de todos os produtos filtrados da amostra
            salvar_detalhes_produtos(
                data_coleta=data_coleta,
                cidade=cidade,
                produto_dieese=nome,
                produtos_filtrados=stats.get("produtos_filtrados", [])
            )

            custo_total += custo_item
            produtos_encontrados += 1

            print(
                f"  💰 {nome}: R${stats['mediana']:.2f}/kg "
                f"× {quantidade}kg = R${custo_item:.2f}"
                f" ({stats['num_amostras']} amostras)"
            )
        else:
            print(f"  ⚠️  {nome}: Nenhum resultado válido encontrado")

    # Salvar resumo da cesta
    salvar_cesta(data_coleta, cidade, custo_total, produtos_encontrados)

    print(f"\n{'='*60}")
    print(f"🛒 CESTA BÁSICA - {cidade}")
    print(f"   Custo Total: R$ {custo_total:.2f}")
    print(f"   Produtos encontrados: {produtos_encontrados}/{len(PRODUTOS_DIEESE)}")
    print(f"{'='*60}")

    # Finalizar progresso
    if progress_callback:
        progress_callback(1.0, "Coleta concluída!")

    return custo_total


def main():
    parser = argparse.ArgumentParser(
        description="Coletor de preços da Cesta Básica DIEESE via Menor Preço"
    )
    parser.add_argument(
        "--cidade",
        type=str,
        default=CIDADE_PADRAO,
        help=(
            f"Cidade para pesquisar (padrão: {CIDADE_PADRAO}). "
            "Use 'todas' para coletar de todas as cidades configuradas."
        ),
    )
    parser.add_argument(
        "--data",
        type=str,
        default=None,
        help="Data da coleta no formato YYYY-MM-DD (padrão: hoje)",
    )

    args = parser.parse_args()

    # Data da coleta
    if args.data:
        data_coleta = args.data
    else:
        data_coleta = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Inicializar banco
    init_db()

    # Inicializar API
    api = MenorPrecoAPI()

    # Determinar cidades
    if args.cidade.lower() == "todas":
        cidades = CIDADES_PADRAO
    else:
        cidades = [args.cidade]

    print(f"\n🚀 Iniciando coleta da Cesta Básica DIEESE")
    print(f"   Cidades: {', '.join(cidades)}")
    print(f"   Data: {data_coleta}")
    print(f"   Produtos: {len(PRODUTOS_DIEESE)}")

    # Coletar para cada cidade
    resultados = {}
    for cidade in cidades:
        custo = coletar_cidade(api, cidade, data_coleta)
        if custo is not None:
            resultados[cidade] = custo

    # Resumo final
    if resultados:
        print(f"\n\n{'='*60}")
        print("📊 RESUMO GERAL")
        print(f"{'='*60}")
        for cidade, custo in sorted(resultados.items(), key=lambda x: x[1]):
            print(f"   {cidade:.<30} R$ {custo:.2f}")
        print(f"{'='*60}")
    else:
        print("\n❌ Nenhum dado coletado.")


if __name__ == "__main__":
    main()
