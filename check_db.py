# -*- coding: utf-8 -*-
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
import sqlite3

conn = sqlite3.connect('cesta_basica.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Check coletas
c.execute("SELECT COUNT(*) as total FROM coletas")
total_coletas = c.fetchone()['total']
print(f"Total coletas: {total_coletas}")

c.execute("SELECT produto_dieese, preco_mediana_kg, quantidade_dieese, custo_item, num_amostras FROM coletas ORDER BY produto_dieese")
for row in c.fetchall():
    print(f"  {row['produto_dieese']:<15} med={row['preco_mediana_kg']:.2f}/kg qty={row['quantidade_dieese']} custo=R${row['custo_item']:.2f} amostras={row['num_amostras']}")

# Check cestas
c.execute("SELECT * FROM cestas")
for row in c.fetchall():
    print(f"\nCesta: {row['cidade']} em {row['data_coleta']} = R${row['custo_total_cesta']:.2f} ({row['num_produtos_encontrados']}/13)")

conn.close()
