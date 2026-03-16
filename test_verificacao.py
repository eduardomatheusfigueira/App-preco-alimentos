# -*- coding: utf-8 -*-
"""Script de verificacao rapida dos dados coletados."""

import sys
import os
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding='utf-8')

from database import init_db, consultar_coletas, consultar_cestas

init_db()

coletas = consultar_coletas("Curitiba")
cestas = consultar_cestas("Curitiba")

print(f"Coletas encontradas: {len(coletas)}")
print(f"Cestas encontradas: {len(cestas)}")

if coletas:
    print("\n--- Detalhamento por Produto ---")
    for c in coletas:
        print(
            f"  {c['produto_dieese']:<20} "
            f"R$ {c['preco_mediana_kg']:.2f}/kg "
            f"x {c['quantidade_dieese']}kg "
            f"= R$ {c['custo_item']:.2f} "
            f"({c['num_amostras']} amostras)"
        )

if cestas:
    print("\n--- Resumo da Cesta ---")
    for c in cestas:
        print(
            f"  {c['data_coleta']}: "
            f"R$ {c['custo_total_cesta']:.2f} "
            f"({c['num_produtos_encontrados']}/13 produtos)"
        )
else:
    print("\nNenhum dado encontrado. Execute primeiro: python collector.py")
