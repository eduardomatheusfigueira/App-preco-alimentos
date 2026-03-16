# -*- coding: utf-8 -*-
"""
Banco de dados SQLite para armazenar o histórico de preços da cesta básica.
Suporta múltiplas coletas por dia usando timestamp completo (data_coleta).
"""

import sqlite3
from datetime import datetime
from config import DATABASE_PATH


def get_connection(db_path=None):
    """Retorna conexão com o banco SQLite."""
    if db_path is None:
        db_path = DATABASE_PATH
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path=None):
    """Cria as tabelas do banco de dados se não existirem."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    # Tabela de coletas individuais (suporta múltiplas por dia via timestamp)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS coletas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_coleta TEXT NOT NULL,
            cidade TEXT NOT NULL,
            produto_dieese TEXT NOT NULL,
            termo_busca TEXT,
            preco_mediana_kg REAL,
            preco_minimo_kg REAL,
            preco_maximo_kg REAL,
            num_amostras INTEGER,
            produto_desc TEXT,
            estabelecimento TEXT,
            gtin TEXT,
            quantidade_dieese REAL,
            custo_item REAL,
            UNIQUE(data_coleta, cidade, produto_dieese)
        )
    """)

    # Tabela de cestas resumidas (suporta múltiplas por dia via timestamp)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cestas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_coleta TEXT NOT NULL,
            cidade TEXT NOT NULL,
            custo_total_cesta REAL,
            num_produtos_encontrados INTEGER,
            UNIQUE(data_coleta, cidade)
        )
    """)

    # Tabela de detalhes individuais dos produtos filtrados
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detalhes_produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_coleta TEXT NOT NULL,
            cidade TEXT NOT NULL,
            produto_dieese TEXT NOT NULL,
            descricao TEXT,
            marca TEXT,
            preco_unitario REAL,
            preco_por_kg REAL,
            peso_kg REAL,
            estabelecimento TEXT,
            gtin TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Banco de dados inicializado.")


def salvar_coleta(data_coleta, cidade, produto_dieese, termo_busca,
                  stats, quantidade_dieese, db_path=None):
    """
    Salva o resultado da coleta de um produto.
    Usa INSERT OR REPLACE para atualizar se já existir coleta do mesmo
    timestamp (data_coleta inclui hora quando disponível).
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()

    preco_mediana = stats.get("mediana", 0)
    custo_item = preco_mediana * quantidade_dieese

    produto_mediana = stats.get("produto_mediana")
    produto_desc = ""
    estabelecimento = ""
    gtin = ""

    if produto_mediana:
        produto_desc = produto_mediana.get("desc", "")
        estab = produto_mediana.get("estabelecimento", {})
        estabelecimento = estab.get("nm_fan", "") or estab.get("nm_emp", "")
        gtin = produto_mediana.get("gtin", "")

    cursor.execute("""
        INSERT OR REPLACE INTO coletas
        (data_coleta, cidade, produto_dieese, termo_busca,
         preco_mediana_kg, preco_minimo_kg, preco_maximo_kg,
         num_amostras, produto_desc, estabelecimento, gtin,
         quantidade_dieese, custo_item)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data_coleta, cidade, produto_dieese, termo_busca,
        preco_mediana, stats.get("minimo", 0), stats.get("maximo", 0),
        stats.get("num_amostras", 0), produto_desc, estabelecimento, gtin,
        quantidade_dieese, custo_item,
    ))

    conn.commit()
    conn.close()

    return custo_item


def salvar_cesta(data_coleta, cidade, custo_total, num_produtos, db_path=None):
    """Salva o resumo da cesta básica completa."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO cestas
        (data_coleta, cidade, custo_total_cesta, num_produtos_encontrados)
        VALUES (?, ?, ?, ?)
    """, (data_coleta, cidade, custo_total, num_produtos))

    conn.commit()
    conn.close()


def consultar_coletas(cidade=None, data_inicio=None, data_fim=None, db_path=None):
    """Consulta coletas com filtros opcionais."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    query = "SELECT * FROM coletas WHERE 1=1"
    params = []

    if cidade:
        query += " AND cidade = ?"
        params.append(cidade)

    if data_inicio:
        query += " AND data_coleta >= ?"
        params.append(data_inicio)

    if data_fim:
        query += " AND data_coleta <= ?"
        params.append(data_fim)

    query += " ORDER BY data_coleta DESC, produto_dieese"

    cursor.execute(query, params)
    resultados = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return resultados


def consultar_cestas(cidade=None, db_path=None):
    """Consulta resumos de cestas com filtro opcional por cidade."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    if cidade:
        cursor.execute(
            "SELECT * FROM cestas WHERE cidade = ? ORDER BY data_coleta DESC",
            (cidade,)
        )
    else:
        cursor.execute("SELECT * FROM cestas ORDER BY data_coleta DESC")

    resultados = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return resultados


def consultar_cidades_disponiveis(db_path=None):
    """Retorna lista de cidades que possuem dados coletados."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT cidade FROM cestas ORDER BY cidade")
    cidades = [row["cidade"] for row in cursor.fetchall()]
    conn.close()

    return cidades


def consultar_datas_disponiveis(cidade, db_path=None):
    """Retorna lista de todas as datas/timestamps de coleta para uma cidade."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT DISTINCT data_coleta FROM cestas WHERE cidade = ? ORDER BY data_coleta DESC",
        (cidade,)
    )
    datas = [row["data_coleta"] for row in cursor.fetchall()]
    conn.close()

    return datas


def consultar_ultima_coleta(cidade, db_path=None):
    """Retorna a data da última coleta para uma cidade."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT MAX(data_coleta) as ultima FROM cestas WHERE cidade = ?",
        (cidade,)
    )
    row = cursor.fetchone()
    conn.close()

    return row["ultima"] if row else None


def salvar_detalhes_produtos(data_coleta, cidade, produto_dieese,
                             produtos_filtrados, db_path=None):
    """
    Salva os detalhes individuais dos produtos filtrados.
    Remove dados anteriores do mesmo produto/cidade/data antes de salvar.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()

    # Remover dados anteriores para este produto/cidade/data
    cursor.execute("""
        DELETE FROM detalhes_produtos
        WHERE data_coleta = ? AND cidade = ? AND produto_dieese = ?
    """, (data_coleta, cidade, produto_dieese))

    for p in produtos_filtrados:
        desc = p.get("desc", "")
        marca = extrair_marca(desc)
        estab = p.get("estabelecimento", {})
        nome_estab = estab.get("nm_fan", "") or estab.get("nm_emp", "")

        cursor.execute("""
            INSERT INTO detalhes_produtos
            (data_coleta, cidade, produto_dieese, descricao, marca,
             preco_unitario, preco_por_kg, peso_kg, estabelecimento, gtin)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data_coleta, cidade, produto_dieese, desc, marca,
            float(p.get("valor", 0)),
            p.get("preco_por_kg", 0),
            p.get("peso_extraido_kg", 0),
            nome_estab,
            p.get("gtin", ""),
        ))

    conn.commit()
    conn.close()


def extrair_marca(descricao):
    """
    Extrai a marca da descrição do produto via heurística.
    Geralmente a marca é a segunda palavra (ex: 'ARROZ BURITI 1KG' → 'BURITI').
    Ignora palavras genéricas comuns.
    """
    import re
    if not descricao:
        return ""

    # Remover caracteres especiais e dividir
    palavras = re.sub(r'[^\w\s]', '', descricao.upper()).split()

    # Palavras genéricas que NÃO são marcas
    genericas = {
        "TIPO", "TP", "T1", "T2", "KG", "GR", "G", "ML", "LT", "L", "UN",
        "PCT", "PACOTE", "SACO", "FARDO", "CX", "CAIXA", "EMB", "UND",
        "COM", "SEM", "DE", "DO", "DA", "EM", "PARA", "POR", "E",
        "INTEGRAL", "DESNATADO", "SEMIDESNATADO", "CRISTAL", "REFINADO",
        "ESPECIAL", "PREMIUM", "EXTRA", "VIRGEM", "COMUM", "TRADICIONAL",
        "PRETO", "BRANCO", "VERMELHO", "CARIOCA",
        "BOVINA", "SUINA", "FRANGO", "FRANCÊS", "FRANCES",
        "TRIGO", "SOJA", "MILHO", "MANDIOCA",
        "1", "2", "3", "5", "10", "500", "900", "1000",
    }

    # A marca geralmente vem após o tipo do produto (2ª ou 3ª palavra)
    for palavra in palavras[1:]:
        if palavra not in genericas and len(palavra) > 1 and not palavra.isdigit():
            return palavra.title()

    return ""


def consultar_detalhes_produtos(cidade, produto_dieese=None,
                                data_coleta=None, db_path=None):
    """
    Consulta detalhes individuais dos produtos filtrados.
    Pode filtrar por produto e/ou data.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()

    query = "SELECT * FROM detalhes_produtos WHERE cidade = ?"
    params = [cidade]

    if produto_dieese:
        query += " AND produto_dieese = ?"
        params.append(produto_dieese)

    if data_coleta:
        query += " AND data_coleta = ?"
        params.append(data_coleta)
    else:
        # Pegar a data mais recente
        query += " AND data_coleta = (SELECT MAX(data_coleta) FROM detalhes_produtos WHERE cidade = ?)"
        params.append(cidade)

    query += " ORDER BY preco_por_kg ASC"

    cursor.execute(query, params)
    resultados = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return resultados
