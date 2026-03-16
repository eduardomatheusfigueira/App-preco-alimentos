# -*- coding: utf-8 -*-
"""
Dashboard Streamlit para visualização da Cesta Básica DIEESE.
Mostra custo atual, histórico, comparativo entre cidades e detalhamento por produto.

Uso:
    streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from database import (
    init_db,
    consultar_coletas,
    consultar_cestas,
    consultar_cidades_disponiveis,
    consultar_datas_disponiveis,
    consultar_detalhes_produtos,
)
from config import CIDADES_PADRAO, PRODUTOS_DIEESE
from collector import coletar_cidade
from api_client import MenorPrecoAPI


# ============================
# Configuração da página
# ============================
st.set_page_config(
    page_title="Cesta Básica DIEESE - Menor Preço PR",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================
# Logo Itaipu Parquetec (Base64)
# ============================
LOGO_ITAIPU_BASE64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAZcAAAB8CAYAAAClkv34AAAQAElEQVR4AeydCZwV1ZX/T73ulk0W2RcBlyhqhIhAVIwCBpdoAooLTjLjkHFLJkYTlSTqZNGJmrgkf9SPW8AQEx03MJBBHdCIG5ggmBFHBVQEZF9EWja76fd/39vUo1913XpV79WrV6/79qfvq6p7zz333FNV93fPuUul0hH8NezYkd65cFF6x/zX09vnvqQC17vf/yBdt259mvQIiqk4FnvWvJSu+/uV6c9nH53+fFZndax77V/S9W/+LF2/ZHKa9IbNb6Ubdm6suLoZgY0GjAaMBvw0kJIC/3a89LJsvHqirLQ6ycq2bWX9kGNlwwnHy8aRI1Tgeu0XDpXVPXuo9BWWpWhXH3u8rD3nfJV303X/IVvve0C2Pfa41M6YKTtf/5t8/sGHUr9+g6R37ixQsvJnS+/aJHV//Yrs+fsISa+/S6RuTaNQmWN6yx+l4eObpGHpJbJn4Qipf2WQ1P9PN6mbYUndM12k/qUzZc8/fi67lk6RhrUvS3rLYoFfIwPzazRgNGA0UBkaCA0ugAFAAYjs/O3vxOrWUVLd+gUK0DZ8vFbq/jxHyLvjV/fIp//+Hfnkny6ULWePVeDkBiTKsgFp/cWXSdIBCSCof76byI7XRGo6i6QywfkscO0M0NghQ5eufXYf+GTAKQd85gyU+gVXScPypwzgZHSVmH8jiNGA0UATDaSaxGgisCxo6AEDG0wACw25bzT57GDz8jvagLT7oSckFCCdOUbiBqQ9f7usse4ASONZuF/y2cEGHfuI5ZOxhPb83/nK2sHKwboJV4ChNhowGjAaKL0GAoELDTSWhQ0ApReraQk2GHG05fA7KkB69mUJA0hrTv2actMV6pKjoU9vfbaptdK0OoXHOIAHKwfXW13GosF9VjhTk9NowGjAaCBaDfiCC43sx0d+STXQNOQi0RZeam4AkR2QP1+of36+ctMxhsQ4UFj5Gj6eJlIVNlcR9AANVs3ut9XYDWM1RXAzWY0GjAaMBiLTgBZcFLD0P0Ia3luhxlUiKzHBjAAiG4AYB9p63wOhpE2vyQze0+CHyhUBMWVmQKZhxU1qIkEEHA0LowGjAaOBojSgBZc1J46S9MZPWwywuLUIyDC+tGvRm+4kz2tcYp4JcUZmAIaJBLjJ4izWlBVOA4baaKAlaMATXDZd9x9S/+bfWiyw2DcegNl8yXftS99jw/LJ8brEdNJgxWTcZEyF1pGYeKMBowGjgVJrIOUugJ769l/drKYWu9OSeI111bBxpRCQjyOB8ygCIMvam3y80hv/KE2mHefLVKp0AGbHa2racqmKMHyNBowGjAb8NNAEXDZ9a0J0wOJXcpFpAAih5msnS+c/z5D+6bT03bBC+tTVScd778+CTZHFqOy7335bHXU/iXCJuYXLAAxjQImUzS2ruTYaMBpodhrIARdW3e95763EVtK2UhAQAOmzbr30emamtB87higVqqurpdN3L1eAA/ioyCJ/9qxZ68shMS4xt5SZMRh2AXBHm2ujAaMBo4FSayAHXLb+8laxpGOpywzF3wYUgKLNDy+VHgsXKQsFAKnu0V3LC8DpNvelSCyYqt69tOWQkCiXGAI5wx5RK/qdUea8ojRghDUaqEgNZMGF/bzqnn8uMYP4NqhUjz5BWSG4u7r95nZpfezgwIpuO+JkiQJgWh19tLZMtmLRJiYhAevl/85PgiRGBqMBo4EWpIEsuOx48cXEVBsrZf/bfy64vXrPeVa5vXB3FSIgANN9/uvKgoFvITz2O/QQbbaG1U9KrAsntZL4JGSsF7OC30c/JslowGggcg1kwWX3398ou0uM2gEAgErna38ofm4vaIOGNscfJ/127JAD/usxsbp0UkCDZZQvPzRtf3itlqy+vl4SmxfE9ThNQuBJ6lVUqlStFPOTYr7wIm6CG7OvlopkJ4bc1N2CjgxsIcNtapQ8PIkoTb1SVmrsUmRdUKDLpB4cMcK3Kfct7E7HJ45oAhVxwSRWp9OEBKmni1VQWE8wpJNKhMwLA5ZLR1Z1PZji67vW7MsRQu/ztbxymlkDHdgQB9OGN6S23pF9igdLEO2b/Ponp9H4iAmxmTj1UjXg3fDyH8InkxGyy2ccb95zhp4qvk2aTj06riACbmQdVDFFMRPJLuB8+lE0ZfsCUSyiEBEVqZia+6ENtDTT2mXNJ7DuE0fljziBq195Nh+C0sul+y10JoweO6j5OiqvSGm/Uvr2I2F1O+q8TAnbMzIWr3yUq7k0wU/abM55mLXqoU552D44cPIrM0mqRr908dDp1BGSX9EvM2Uw86G4fXQoTayp0Oy8ZJLYCThsrP+Ufyf+24mUiI0QmQvkQmvnenWTMHkuPf/wcZfs3Z/xMonBzttno9LIIsENrRD/5medWtqa1I7MVK2aFozJRCycOm5lj95dbS9ECZf7a5zt9ONIsii14O/2VGRS6Zzy9sGKhFVV5+6ODjmXi7VZOpxOoIwCLhYoqaVifIcqJlYgnVsziN7xyKQFNYMfMFA6VFEO7hPbrMBOnzDubjnzkVFvOF+1kyePDxo6Vc741xVaBSsTDillY0gAPnK3SgpaIX0KqZubC1f8i6maEiUXAJTvX0FGPT6VpT50v4YDpDKxwsuiZCp1BycURO7JOHznNVs5KxEMJF07+FtEePUUIWJANM/PZ1f9k4pWL5N39CAJy+29+7bsEB8yv5v2OxNSf7hJ1XIOTZUTfw7STpQOPXGwsM3PysKNtZa9MPLRnsCx5oWs91F+10xx36O3tK7CRDmaonEwm4JyvF1DV7EMIHe8yBLzuyF9zW087WaSBVo3IZua1h/xCNVU8vjLxkPKWk0ZorWfDzAR2doNFQHS8V907JmMXxPEjvsfE004Wu3hnTMem/M8P/0nGaOki2CIetF6ht/UwaBw4pAM2V+fhAUVfXaYuCP0Bk1zdARKjg84c9lNb3kxLKlvEQ+L7f3k4Kc1KR6KABJiZM48ebKs2oyvVXc+pCgIBcd7qgnh11WIcxsPFL99IcHXHT+gd5xBgp8r1k2ZklZ9pN3XPkhA9Pf1gqm9qs5uFf9OxmTntiEG25D920JH8ymy1lTY5kXDAdHRBHPvsWXTAQ9MIThj0BcIpY3L7MDmNPs4OgUh7E107+sKstB0ksE08JD75qBq6ZNygghvNAjNz5JB9AIFy+MF+x7Cl4Ox4SouAy3fXEZww8Lhp0infmowJgCtGHF0/6eKMcTNFyIp4yPxP0w+hAytLCoZ82ZiZwMuu+xlpMwVBQNZy2GaKq6/bQKBlE71y4r02EnZNkjXxkOX7V40vHPJxH6ZdMxNYITw86VbCt8qxrwMR+QAE3K9rx8wkp16cjhAP7T2QDytNQyP4AEfbIh7Yr5zsmplWob8Y/RPCRwyF6WKd1FvPIoB23YlDjiUnTEyrko4QD5mBfKuvnxBozYeXys8VZ5oDm1Rhwcn/j4hNF02+VOh451wk3Exj+hxI8069z1GhHCMepAL5Pr/uGJo+vDfVN7fjVLBCFt7MZCAwov29M57X5EsGxkPHIN2IiiH0/r8/5bhUjhLPku7R88bQHT8YGriuhmy8mRY2iVuMqfzqnEU0oke1bvMlAuOBfZiXx/Q7lL48e15OpMkJ8SDpjBNG0LIrx1G/siKqb/H/oGqYmVd9V23CK3DIFKD5cHMthwsa8XjTwgRFyJReX3ceAdyDEweNp4Vn/MX5zDtyzBnxkD+cEDA97ztxmOhu8DUB2cw87Tv7olo5CXC4RGespAXTHiLM8Rqzz1AxQx0PQaR5vdCIYn9PHeFtLAK3PwRJsY2G9WyELO8MXnTAGC9Bp9t0yaLllHhWYedNHkZNf5hIiQSEBrGue30LWW/+/r40uHdZzkU9fvgE+u9pfxDtivBvFhHIuPWCT+irX75B7532LL1y0lx6bNKNdMdRlxBGx1950Ol04sCxwlyFcHhwuoT2Jk1WgJMmWISDyQ+c8RJME9Wx03khHqTtWRIiEDD6x8n09BkH0cSBPYUDBloQDzbieDWgm+S3PzrANfEwqxwmKdqE6Ec649Af0YzxZwv39i0/uEJ43GCuRi94N0bU/1giiIqHCGRdMHW2IOvDE64TZIVGBVmP6XugIKzQmtCkmTRrh1bFg+oaGA4WjHpE+KVEkVaClgOGwNnBItJmlTfiJUqAoWavXzaOmm77viChNa8NnlARWsIx07QtIraJafO9jxfDR1cene9isyrPIioeIpAVWvQMJive5OiLgkaFKYU2DB626EVLY4TtRrMKslaPFkSFcHhgu2hWkJcfZHENW5jACB4jbJxwLBssB9Qf2KBedoKdNK4QzxIUWhAkxLCzLTdPEkRcdtlYeunsQ+i+Kd8iEBJdE8JBAxI2tXXSkrnUlFbeG677bl5MTAsTN7cWYUHWZM1qkVUQFZr14o9pK2tWhLhm5fYpzGChWQ89R7RVEzUrhrIJsqbTrCnI6hQeQqsjfy4b7WfIGeU6wHJwqgyVfFwlXrKgICIcMj84ZIAwS0FIdE3AQQMTdcP/nUDJxLS+6QCiCG3J/YfQUuKYyZpcRqZjkY4JDsJjQEA+2nWZZPLqdRAVQVazpmuzwhS2yIo265lDJhHIIYjKWkloUGjTxAASWQFxEoN13orP15AnyLaVtTr65WABuImrp4iXCQiQIJmYMFmFtmTnzYbfH0PvXDBGmK93TPqG0JhxYjKZMIVJkDPJlBVkA2E5gHDvXHwkgfB4EWSSSV9XRyCRrNCsMIV/Mfon8Tbr3FNm7XUuwQxmzZSoWS0HE4gEUxFkhSmMgP1rWdviGuJBG8OURJ4gG8pWl9j5FL4iXnfVB0lATMwKh/mKfkRozDgx75gs+hUtYt48YQhZAWYtzqPNCcIhj+7K0tfyjwAIY2lWkBUkQoCpCAcTTGEE7KMdi2uIhzT5lzZziYEhXqaqgpjQliAViAkvpRXgbcV5xMmUj0+va7E9hkDBEM9juGtxChwBTbwCfwB09d1BQBPPHdx1qQWOgCZegT8AuvruIOAh4rkDgC5VI+AGApp4bqCuyyx4BDTxCv4R0AC4gYAmnhuo6zILHgFNvIJ/BPwAQPBk1MQL3j3VNfIBAv8fAAD//0Ma+EIAAAAGSURBVAMARqxPmSZNsKEAAAAASUVORK5CYII="

# ============================
# CSS customizado — Design Itaipu Parquetec
# ============================
st.markdown("""
<style>
    /* Importar fonte Ubuntu */
    @import url('https://fonts.googleapis.com/css2?family=Ubuntu:wght@400;500;700&display=swap');

    /* Aplicar fonte Ubuntu globalmente */
    html, body, .main, .stApp, .stMarkdown,
    div[data-testid="stMetric"],
    section[data-testid="stSidebar"] {
        font-family: 'Ubuntu', sans-serif !important;
    }

    /* Tema geral */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%) !important;
    }
    .main .block-container {
        padding-top: 2rem;
    }

    /* Cards de métricas — Glassmorphism claro */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 1.2rem;
        border-radius: 12px;
        color: #1D1D1B !important;
        border: 1px solid rgba(226, 232, 240, 0.8);
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border-top: 3px solid #0072CE;
    }
    div[data-testid="stMetric"] label {
        color: #64748b !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #1D1D1B !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetricDelta"] {
        color: #1D1D1B !important;
    }

    /* Header — Glassmorphism com acento azul */
    .header-container {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(226, 232, 240, 0.8);
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        display: flex;
        align-items: center;
        gap: 1.5rem;
        border-bottom: 3px solid #0072CE;
    }
    .header-logo {
        height: 40px;
        width: auto;
        object-fit: contain;
    }
    .header-divider {
        width: 1px;
        height: 40px;
        background: #cbd5e1;
    }
    .header-text {
        flex: 1;
    }
    .title-text {
        color: #1e293b;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .subtitle-text {
        color: #64748b;
        font-size: 0.85rem;
        margin: 0.2rem 0 0 0;
    }

    /* Sidebar — Tema claro */
    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.92) !important;
        border-right: 1px solid rgba(226, 232, 240, 0.8) !important;
    }
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #1e293b !important;
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown span,
    section[data-testid="stSidebar"] .stMarkdown label {
        color: #475569 !important;
    }

    /* Tabela */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    /* Scrollbar customizada */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(148, 163, 184, 0.5);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(148, 163, 184, 0.8);
    }

    /* Botões */
    .stButton > button[kind="primary"] {
        background-color: #0072CE !important;
        border-color: #0072CE !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #005ea6 !important;
        border-color: #005ea6 !important;
    }

    /* Separador */
    hr {
        border-color: rgba(226, 232, 240, 0.6) !important;
    }

    /* Seções markdown */
    .stMarkdown h2, .stMarkdown h3 {
        color: #1e293b !important;
        letter-spacing: -0.01em;
    }

    /* Rodapé */
    .footer-container {
        text-align: center;
        color: #94a3b8;
        font-size: 0.8rem;
        padding: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def render_header():
    """Renderiza o cabeçalho do dashboard com logo Itaipu Parquetec."""
    st.markdown(f"""
    <div class="header-container">
        <img src="{LOGO_ITAIPU_BASE64}" alt="Itaipu Parquetec" class="header-logo" />
        <div class="header-divider"></div>
        <div class="header-text">
            <p class="title-text">🛒 Cesta Básica DIEESE</p>
            <p class="subtitle-text">
                Preços em tempo real via Menor Preço · Nota Paraná · Região 3 (PR)
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Renderiza a sidebar com filtros e botão de pesquisa."""
    with st.sidebar:
        st.markdown("## 🔧 Configurações")

        # Cidades disponíveis no banco
        cidades_banco = consultar_cidades_disponiveis()
        cidades_opcoes = cidades_banco if cidades_banco else CIDADES_PADRAO

        cidade = st.selectbox(
            "🏙️ Cidade",
            options=cidades_opcoes,
            index=0,
            help="Selecione a cidade para visualizar os preços",
        )

        st.markdown("---")

        # ============================
        # Botão de pesquisa manual
        # ============================
        st.markdown("### 🔄 Pesquisa Manual")
        if st.button("🚀 Executar Pesquisa Agora", use_container_width=True, type="primary"):
            data_coleta = datetime.now().strftime("%Y-%m-%d %H:%M")
            with st.spinner(f"Coletando preços para {cidade}... Isso pode levar alguns minutos."):
                api = MenorPrecoAPI()
                custo = coletar_cidade(api, cidade, data_coleta)
            if custo is not None:
                st.success(f"✅ Coleta concluída! Cesta: R$ {custo:.2f}")
                st.rerun()
            else:
                st.error("❌ Falha na coleta. Verifique a conexão e tente novamente.")

        st.markdown("---")

        # ============================
        # Seletor de histórico
        # ============================
        st.markdown("### 📜 Histórico")
        datas = consultar_datas_disponiveis(cidade)
        data_selecionada = None
        if datas:
            opcoes_hist = ["Mais recente"] + datas
            escolha = st.selectbox(
                "Selecione uma coleta:",
                options=opcoes_hist,
                index=0,
                help="Escolha uma coleta anterior para visualizar no dashboard",
            )
            if escolha != "Mais recente":
                data_selecionada = escolha
        else:
            st.info("Nenhuma coleta disponível ainda.")

        st.markdown("---")
        st.markdown("### 📋 Sobre")
        st.markdown(
            "Dados coletados do portal **Menor Preço** "
            "(Nota Paraná - SEFA/PR)."
        )
        st.markdown(
            "Metodologia: **DIEESE** - "
            "Decreto Lei nº 399/1938 - Região 3."
        )
        st.markdown(
            "Preços filtrados com pipeline de 5 camadas "
            "(NCM, blacklist, normalização, IQR, mediana)."
        )

        return cidade, data_selecionada


def render_metricas(cidade, data_selecionada=None):
    """Renderiza os cards de métricas principais."""
    cestas = consultar_cestas(cidade)

    if not cestas:
        st.warning(
            f"⚠️ Nenhum dado encontrado para **{cidade}**. "
            "Execute o coletor primeiro (use o botão na barra lateral ou via terminal):\n\n"
            f"```\npython collector.py --cidade \"{cidade}\"\n```"
        )
        return

    # Se uma data específica foi selecionada, usar essa coleta
    if data_selecionada:
        cesta_alvo = next((c for c in cestas if c["data_coleta"] == data_selecionada), None)
        if cesta_alvo is None:
            cesta_alvo = cestas[0]
        # Encontrar a coleta ANTERIOR a essa para calcular variação
        idx = next((i for i, c in enumerate(cestas) if c["data_coleta"] == data_selecionada), 0)
        cesta_anterior = cestas[idx + 1] if idx + 1 < len(cestas) else None
    else:
        cesta_alvo = cestas[0]
        cesta_anterior = cestas[1] if len(cestas) > 1 else None

    custo_atual = cesta_alvo["custo_total_cesta"]
    num_produtos = cesta_alvo["num_produtos_encontrados"]
    data_coleta = cesta_alvo["data_coleta"]

    # Variação em relação à coleta anterior
    variacao = None
    if cesta_anterior:
        custo_anterior = cesta_anterior["custo_total_cesta"]
        if custo_anterior > 0:
            variacao = ((custo_atual - custo_anterior) / custo_anterior) * 100

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="💰 Custo Total da Cesta",
            value=f"R$ {custo_atual:.2f}",
            delta=f"{variacao:+.1f}%" if variacao is not None else None,
            delta_color="inverse",  # Vermelho se subiu (ruim)
        )

    with col2:
        st.metric(
            label="📊 Produtos Encontrados",
            value=f"{num_produtos}/13",
        )

    with col3:
        # Salário mínimo necessário (DIEESE: família de 4 = 3 cestas)
        salario_necessario = custo_atual * 3
        st.metric(
            label="💼 Salário Mínimo Necessário",
            value=f"R$ {salario_necessario:.2f}",
            help="Cálculo DIEESE: 3× o valor da cesta (família de 2 adultos + 2 crianças)",
        )

    with col4:
        st.metric(
            label="📅 Coleta",
            value=data_coleta,
        )


def render_tabela_produtos(cidade, data_selecionada=None):
    """Renderiza tabela detalhada por produto."""
    st.markdown("### 📋 Detalhamento por Produto")

    coletas = consultar_coletas(cidade)

    if not coletas:
        st.info("Nenhuma coleta disponível.")
        return

    # Usar data selecionada ou a mais recente
    data_alvo = data_selecionada if data_selecionada else coletas[0]["data_coleta"]
    coletas_alvo = [c for c in coletas if c["data_coleta"] == data_alvo]

    df = pd.DataFrame(coletas_alvo)

    if df.empty:
        st.info("Nenhum dado para exibir.")
        return

    # Formatar tabela
    df_display = df[[
        "produto_dieese", "preco_mediana_kg", "preco_minimo_kg",
        "preco_maximo_kg", "quantidade_dieese", "custo_item",
        "num_amostras", "estabelecimento"
    ]].copy()

    df_display.columns = [
        "Produto", "Mediana (R$/kg)", "Mínimo (R$/kg)",
        "Máximo (R$/kg)", "Qtd DIEESE (kg)", "Custo Item (R$)",
        "Amostras", "Estabelecimento Ref."
    ]

    # Formatar valores
    for col in ["Mediana (R$/kg)", "Mínimo (R$/kg)", "Máximo (R$/kg)", "Custo Item (R$)"]:
        df_display[col] = df_display[col].apply(lambda x: f"R$ {x:.2f}" if x else "-")

    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
    )


def render_grafico_historico(cidade):
    """Renderiza gráfico de evolução histórica do custo da cesta."""
    st.markdown("### 📈 Evolução Histórica do Custo da Cesta")

    cestas = consultar_cestas(cidade)

    if len(cestas) < 2:
        st.info(
            "📊 São necessárias pelo menos 2 coletas para gerar o gráfico de tendência. "
            "Execute o coletor novamente em outro dia."
        )
        return

    df = pd.DataFrame(cestas)
    df["data_coleta"] = pd.to_datetime(df["data_coleta"])
    df = df.sort_values("data_coleta")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["data_coleta"],
        y=df["custo_total_cesta"],
        mode="lines+markers",
        name="Custo Cesta",
        line=dict(color="#0072CE", width=3),
        marker=dict(size=8, color="#0072CE"),
        fill="tozeroy",
        fillcolor="rgba(0, 114, 206, 0.1)",
    ))

    fig.update_layout(
        xaxis_title="Data",
        yaxis_title="Custo Total (R$)",
        template="plotly_white",
        height=400,
        margin=dict(l=20, r=20, t=10, b=20),
        yaxis=dict(tickprefix="R$ "),
    )

    st.plotly_chart(fig, use_container_width=True)


def render_comparativo_cidades():
    """Renderiza gráfico comparativo entre cidades."""
    st.markdown("### 🏙️ Comparativo entre Cidades")

    # Buscar última cesta de cada cidade
    cidades = consultar_cidades_disponiveis()

    if len(cidades) < 2:
        st.info(
            "📊 São necessários dados de pelo menos 2 cidades para comparar. "
            "Execute: `python collector.py --cidade todas`"
        )
        return

    dados = []
    for cidade in cidades:
        cestas = consultar_cestas(cidade)
        if cestas:
            dados.append({
                "Cidade": cidade,
                "Custo": cestas[0]["custo_total_cesta"],
                "Data": cestas[0]["data_coleta"],
            })

    if len(dados) < 2:
        return

    df = pd.DataFrame(dados).sort_values("Custo")

    fig = px.bar(
        df,
        x="Cidade",
        y="Custo",
        color="Custo",
        color_continuous_scale=["#00873E", "#FFB81C", "#E30613"],
        text=df["Custo"].apply(lambda x: f"R$ {x:.2f}"),
    )

    fig.update_layout(
        template="plotly_white",
        height=400,
        margin=dict(l=20, r=20, t=10, b=20),
        yaxis=dict(tickprefix="R$ ", title="Custo da Cesta (R$)"),
        xaxis=dict(title=""),
        showlegend=False,
        coloraxis_showscale=False,
    )

    fig.update_traces(textposition="outside")

    st.plotly_chart(fig, use_container_width=True)


def render_grafico_composicao(cidade, data_selecionada=None):
    """Gráfico de pizza mostrando composição da cesta por produto."""
    st.markdown("### 🥧 Composição da Cesta por Produto")

    coletas = consultar_coletas(cidade)
    if not coletas:
        return

    data_alvo = data_selecionada if data_selecionada else coletas[0]["data_coleta"]
    recentes = [c for c in coletas if c["data_coleta"] == data_alvo]

    df = pd.DataFrame(recentes)
    if df.empty:
        return

    fig = px.pie(
        df,
        values="custo_item",
        names="produto_dieese",
        color_discrete_sequence=[
            "#0072CE", "#00873E", "#FFB81C", "#E30613",
            "#5DADE2", "#58D68D", "#F7DC6F", "#EC7063",
            "#85C1E9", "#82E0AA", "#FAD7A0", "#F1948A",
            "#AED6F1",
        ],
        hole=0.4,
    )

    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=10, b=20),
    )

    fig.update_traces(
        textposition="inside",
        textinfo="label+percent",
        hovertemplate="%{label}: R$ %{value:.2f}<extra></extra>",
    )

    st.plotly_chart(fig, use_container_width=True)


def render_relatorio_complementar(cidade, data_selecionada=None):
    """Renderiza relatório com top 3 mais baratos/caros, marcas e lojas."""
    st.markdown("---")
    st.markdown("## 🔎 Relatório Complementar por Produto")

    # Obter produtos disponíveis na coleta selecionada
    coletas = consultar_coletas(cidade)
    if not coletas:
        st.info("Sem dados para o relatório complementar.")
        return

    data_alvo = data_selecionada if data_selecionada else coletas[0]["data_coleta"]
    recentes = [c for c in coletas if c["data_coleta"] == data_alvo]
    produtos_disponiveis = sorted([c["produto_dieese"] for c in recentes])

    if not produtos_disponiveis:
        return

    st.markdown(f"**Data base:** {data_alvo}")

    # Seletor de produto
    produto_sel = st.selectbox(
        "Selecione um produto para visualizar o relatório detalhado:",
        options=produtos_disponiveis,
    )

    # Buscar detalhes do produto
    detalhes = consultar_detalhes_produtos(cidade, produto_sel, data_alvo)

    if not detalhes:
        st.warning(
            f"Detalhes individuais não encontrados para **{produto_sel}**. "
            "Realize uma nova coleta para popular esses dados."
        )
        return

    df = pd.DataFrame(detalhes)

    # Ranking sem duplicatas por estabelecimento+preço
    df_ranking = df.drop_duplicates(
        subset=["estabelecimento", "preco_por_kg"]
    ).sort_values("preco_por_kg")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🟢 Top 3 Mais Baratos")
        df_baratos = df_ranking.head(3).copy()
        if not df_baratos.empty:
            df_b = df_baratos[["descricao", "marca", "preco_por_kg", "estabelecimento"]].copy()
            df_b.columns = ["Descrição / Modelo", "Marca", "Preço (R$/kg)", "Loja"]
            df_b["Preço (R$/kg)"] = df_b["Preço (R$/kg)"].apply(lambda x: f"R$ {x:.2f}")
            st.dataframe(df_b, use_container_width=True, hide_index=True)
        else:
            st.info("Dados insuficientes.")

    with col2:
        st.markdown("#### 🔴 Top 3 Mais Caros")
        df_caros = df_ranking.tail(3).sort_values("preco_por_kg", ascending=False).copy()
        if not df_caros.empty:
            df_c = df_caros[["descricao", "marca", "preco_por_kg", "estabelecimento"]].copy()
            df_c.columns = ["Descrição / Modelo", "Marca", "Preço (R$/kg)", "Loja"]
            df_c["Preço (R$/kg)"] = df_c["Preço (R$/kg)"].apply(lambda x: f"R$ {x:.2f}")
            st.dataframe(df_c, use_container_width=True, hide_index=True)
        else:
            st.info("Dados insuficientes.")

    st.markdown("<br>", unsafe_allow_html=True)
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### 🏷️ Marcas e Modelos Disponíveis")
        marcas = sorted([m for m in df["marca"].unique() if m and str(m).strip()])
        if marcas:
            st.write(", ".join(f"**{m}**" for m in marcas))
        else:
            st.write("*Nenhuma marca específica identificada.*")

        with st.expander("Ver todas as descrições/modelos"):
            descricoes = sorted(df["descricao"].unique())
            for desc in descricoes:
                st.write(f"- {desc}")

    with col4:
        lojas = sorted([e for e in df["estabelecimento"].unique() if e and str(e).strip()])
        st.markdown(f"#### 🏪 Lojas com Disponibilidade ({len(lojas)})")
        with st.container(height=200):
            for loja in lojas:
                st.write(f"🏢 {loja}")


def main():
    """Função principal do dashboard."""
    # Inicializar banco (cria se não existir)
    init_db()

    # Header
    render_header()

    # Sidebar (retorna cidade selecionada e data do histórico)
    cidade, data_selecionada = render_sidebar()

    # Métricas principais
    render_metricas(cidade, data_selecionada)

    st.markdown("---")

    # Layout em 2 colunas
    col_esq, col_dir = st.columns([3, 2])

    with col_esq:
        render_tabela_produtos(cidade, data_selecionada)

    with col_dir:
        render_grafico_composicao(cidade, data_selecionada)

    st.markdown("---")

    # Gráficos de linha e comparativo
    col1, col2 = st.columns(2)

    with col1:
        render_grafico_historico(cidade)

    with col2:
        render_comparativo_cidades()

    # Relatório Complementar
    render_relatorio_complementar(cidade, data_selecionada)

    # Rodapé
    st.markdown("---")
    st.markdown(
        "<div class='footer-container'>"
        "Dados: Menor Preço - Nota Paraná (SEFA/PR) · "
        "Metodologia: DIEESE - Decreto Lei nº 399/1938 - Região 3<br>"
        "⚠️ Projeto acadêmico. Preços são informados via NF-e e podem não refletir o preço atual praticado."
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
