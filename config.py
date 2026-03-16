# -*- coding: utf-8 -*-
"""
Configurações do App Cesta Básica - Menor Preço + DIEESE
"""

# ============================
# API do Menor Preço
# ============================
API_BASE_URL = "https://menorpreco.notaparana.pr.gov.br/api/v1"
API_PRODUTOS = f"{API_BASE_URL}/produtos"
API_CATEGORIAS = f"{API_BASE_URL}/categorias"
API_GEOCODING = "https://menorpreco.notaparana.pr.gov.br/mapa/search"

# Raio de busca padrão (km)
RAIO_BUSCA_KM = 30

# Pausa entre requisições (segundos) — respeitar o servidor
DELAY_MIN = 2
DELAY_MAX = 5

# ============================
# Cidades do Paraná (pré-configuradas)
# Geohashes serão obtidos automaticamente via API
# ============================
CIDADES_PADRAO = [
    "Curitiba",
    "Londrina",
    "Maringá",
    "Ponta Grossa",
    "Cascavel",
    "Foz do Iguaçu",
    "São José dos Pinhais",
    "Colombo",
    "Guarapuava",
    "Paranaguá",
]

CIDADE_PADRAO = "Foz do Iguaçu"

# ============================
# Produtos da Cesta Básica DIEESE - Região 3 (PR, SC, RS)
# Decreto Lei nº 399/1938
# ============================
PRODUTOS_DIEESE = [
    {
        "nome": "Carne",
        "quantidade_kg": 6.6,
        "unidade": "kg",
        "termo_busca": ["coxao mole", "coxao duro", "patinho", "alcatra"],
        "ncm_prefixos": ["0201", "0202"],  # Carne bovina fresca/congelada
        "peso_padrao_kg": 1.0,
    },
    {
        "nome": "Leite",
        "quantidade_kg": 7.5,
        "unidade": "L",
        "termo_busca": ["Leite integral", "lactose 1l"],
        "ncm_prefixos": ["0401"],  # Leite não concentrado
        "peso_padrao_kg": 1.0,  # 1L ≈ 1kg
    },
    {
        "nome": "Feijão",
        "quantidade_kg": 4.5,
        "unidade": "kg",
        "termo_busca": "Feijão preto",
        "ncm_prefixos": ["0713"],  # Leguminosas secas
        "peso_padrao_kg": 1.0,
    },
    {
        "nome": "Arroz",
        "quantidade_kg": 3.0,
        "unidade": "kg",
        "termo_busca": "Arroz 5kg",
        "ncm_prefixos": ["1006"],  # Arroz
        "peso_padrao_kg": 5.0, # Saco de 5kg é o mais comum, ajustado peso padrão
    },
    {
        "nome": "Farinha",
        "quantidade_kg": 1.5,
        "unidade": "kg",
        "termo_busca": "Farinha de trigo",
        "ncm_prefixos": ["1101"],  # Farinha de trigo
        "peso_padrao_kg": 1.0,
    },
    {
        "nome": "Batata",
        "quantidade_kg": 6.0,
        "unidade": "kg",
        "termo_busca": "Batata",
        "ncm_prefixos": ["0701", "0710", "2005"],  # Batatas e preparações
        "peso_padrao_kg": 1.0,
    },
    {
        "nome": "Tomate",
        "quantidade_kg": 9.0,
        "unidade": "kg",
        "termo_busca": "Tomate kg",
        "ncm_prefixos": ["0702"],  # Tomates
        "peso_padrao_kg": 1.0,
    },
    {
        "nome": "Pão Francês",
        "quantidade_kg": 6.0,
        "unidade": "kg",
        "termo_busca": "Pão francês",
        "ncm_prefixos": ["1905"],  # Produtos de padaria
        "peso_padrao_kg": 1.0,
    },
    {
        "nome": "Café em Pó",
        "quantidade_kg": 0.6,
        "unidade": "kg",
        "termo_busca": "Café em pó",
        "ncm_prefixos": ["0901", "2101"],  # Café / extratos de café
        "peso_padrao_kg": 0.5,  # Embalagem típica 500g
    },
    {
        "nome": "Banana",
        "quantidade_kg": 10.8,  # 90 unidades ≈ 10.8kg (120g/un)
        "unidade": "kg",
        "termo_busca": ["Caturra", "banana prata", "banana nanica"],
        "ncm_prefixos": ["0803"],  # Bananas
        "peso_padrao_kg": 1.0,
    },
    {
        "nome": "Açúcar",
        "quantidade_kg": 3.0,
        "unidade": "kg",
        "termo_busca": "Açúcar cristal",
        "ncm_prefixos": ["1701"],  # Açúcar de cana
        "peso_padrao_kg": 1.0,
    },
    {
        "nome": "Óleo",
        "quantidade_kg": 0.9,
        "unidade": "L",
        "termo_busca": "Óleo de soja",
        "ncm_prefixos": ["1507"],  # Óleo de soja
        "peso_padrao_kg": 0.9,  # 900ml
    },
    {
        "nome": "Manteiga",
        "quantidade_kg": 0.75,
        "unidade": "kg",
        "termo_busca": "Manteiga sem sal",
        "ncm_prefixos": ["0405"],  # Manteiga
        "peso_padrao_kg": 0.2,  # Embalagem típica 200g
    },
]

# ============================
# Blacklists para filtragem de outliers
# ============================

# Palavras na DESCRIÇÃO do produto que indicam não ser item de varejo
BLACKLIST_DESCRICAO = [
    "ADICIONAL",
    "PORÇÃO",
    "PORCAO",
    "KIDS",
    "COMBO",
    "REFEIÇÃO",
    "REFEICAO",
    "PRATO ",
    "MARMITA",
    "CÁPSULA",
    "CAPSULA",
    "SACHÊ",
    "SACHE",
    "RAÇÃO",
    "RACAO",
    "PET ",
    "ANIMAL",
    "ADUBO",
    "SEMENTE",
    "SABONETE",
    "SHAMPOO",
    "FIGADO",
    "FÍGADO",
    "CORAÇÃO",
    "LÍNGUA",
    "LINGUA",
    "COSMÉTICO",
    "COSMETICO",
    "CHUMBO",
    "MIÇANGA",
    "MICANGA",
    "ENTREMEIO",
    "BIJOUTERIA",
    "CHIPS",
    "PALHA",
    "PRÉ-FRITA",
    "PRE-FRITA",
    "CONGELAD",
    "SALGADINHO",
    "FRITA",
    "PRINGLES",
    "SNACK",
    "PRONTO",
    "MOLHO",
    "EXTRATO",
    "KETCHUP",
    "CATCHUP",
    "MASSA",
    "MACARRAO",
    "POLPA",
    "PURÊ",
    "PURE",
    "DOCE",
    "BALA",
    "BOMBOM",
    "CEREAL",
    "IOGURTE",
    "BEBIDA",
    "ACAI",
    "AÇAÍ",
    "AÇAI",
    "SORVETE",
    "GELATINA",
    "PASTILHA",
    "BISCOITO",
    "MISTURA",
    "BOLO",
    "CALDO",
]

# Palavras no NOME do estabelecimento que indicam preços atípicos
BLACKLIST_ESTABELECIMENTO = [
    "FARMACIA",
    "FARMÁCIA",
    "DROGARIA",
    "RESTAURANTE",
    "CAFETERIA",
    "LANCHONETE",
    "PET SHOP",
    "PETSHOP",
    "AVIARIO",
    "AVIÁRIO",
    "ARMARINHO",
    "BIJOUTERIA",
    "PAPELARIA",
    "POSTO",  # Posto de gasolina
]

# ============================
# Configuração do banco de dados
# ============================
DATABASE_PATH = "cesta_basica.db"
