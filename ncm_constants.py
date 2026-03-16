# -*- coding: utf-8 -*-
"""
Dicionário de NCMs (Nomenclatura Comum do Mercosul) comuns para alimentos.
Utilizado para o dropdown de criação de cestas personalizadas.
"""

NCM_ALIMENTOS = [
    ("0201", "Carne bovina (fresca ou refrigerada)"),
    ("0202", "Carne bovina (congelada)"),
    ("0203", "Carne suína"),
    ("0204", "Carne de ovino/caprino"),
    ("0206", "Miúdos comestíveis (fígado, coração, etc)"),
    ("0207", "Aves (frango, peru, etc)"),
    ("0302", "Peixes frescos"),
    ("0303", "Peixes congelados"),
    ("0304", "Filés de peixe"),
    ("0401", "Leite e nata (não concentrados)"),
    ("0402", "Leite e nata (concentrados ou em pó)"),
    ("0405", "Manteiga e óleos de leite"),
    ("0406", "Queijos e requeijão"),
    ("0407", "Ovos de aves"),
    ("0409", "Mel natural"),
    ("0701", "Batatas frescas"),
    ("0702", "Tomates frescos"),
    ("0703", "Cebolas, alhos e alho-poró"),
    ("0704", "Couve, repolho, couve-flor"),
    ("0706", "Cenouras e nabos"),
    ("0713", "Feijão e outras leguminosas secas"),
    ("0803", "Bananas"),
    ("0804", "Tâmaras, figos, abacaxis, abacates"),
    ("0805", "Cítricos (laranja, limão)"),
    ("0806", "Uvas"),
    ("0807", "Melões e melancias"),
    ("0808", "Maçãs e peras"),
    ("0901", "Café"),
    ("0902", "Chá"),
    ("1001", "Trigo"),
    ("1005", "Milho"),
    ("1006", "Arroz"),
    ("1101", "Farinha de trigo"),
    ("1102", "Farinha de cereais (exceto trigo)"),
    ("1507", "Óleo de soja"),
    ("1509", "Azeite de oliva"),
    ("1701", "Açúcar de cana ou beterraba"),
    ("1901", "Preparações p/ alimentação infantil"),
    ("1902", "Massas alimentícias (macarrão, lasanha)"),
    ("1905", "Pães, bolos, biscoitos"),
    ("2002", "Tomates preparados/conservas"),
    ("2101", "Extratos de café e chá"),
    ("2103", "Molhos e condimentos"),
    ("2201", "Águas minerais"),
    ("2202", "Refrigerantes e sucos"),
    ("2203", "Cervejas"),
]

# Formata para uso no Streamlit selectbox: "0201 - Carne bovina..."
NCM_OPTIONS = [f"{n[0]} - {n[1]}" for n in NCM_ALIMENTOS]
NCM_MAP = {n[0]: n[1] for n in NCM_ALIMENTOS}
