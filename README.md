# 🛒 Cesta Básica DIEESE - Menor Preço PR

Aplicação Python que coleta automaticamente os preços dos 13 itens da cesta básica (metodologia DIEESE, Região 3) a partir da API do portal **Menor Preço** (Nota Paraná), armazena em SQLite e exibe em um dashboard interativo via Streamlit.

## 📌 Funcionalidades

- **Coleta automatizada** dos 13 produtos da cesta básica
- **Filtragem inteligente** de outliers em 5 camadas (NCM, blacklist, normalização, IQR, mediana)
- **Seleção de cidade** — qualquer município do Paraná
- **Dashboard interativo** com gráficos de tendência, comparativo entre cidades e detalhamento por produto
- **Automação** via GitHub Actions (coleta diária)

## 🚀 Instalação

```bash
# Criar ambiente virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Instalar dependências
pip install -r requirements.txt
```

## 📊 Uso

### Coletar preços

```bash
# Coleta para Curitiba (padrão)
python collector.py

# Coleta para uma cidade específica
python collector.py --cidade "Londrina"

# Coleta para todas as cidades configuradas
python collector.py --cidade todas
```

### Abrir o dashboard

```bash
streamlit run dashboard.py
```

## 🏗️ Arquitetura

| Arquivo | Descrição |
|---------|-----------|
| `config.py` | Configurações: 13 produtos DIEESE, NCMs, blacklists, cidades |
| `api_client.py` | Cliente HTTP com rate limiting e retry |
| `filters.py` | Pipeline de filtragem em 5 camadas |
| `collector.py` | Script coletor com CLI `--cidade` |
| `database.py` | Camada de persistência SQLite |
| `dashboard.py` | Dashboard Streamlit interativo |

## 📋 Metodologia

Segue o Decreto Lei nº 399/1938 regulamentado pelo DIEESE para Região 3 (PR, SC, RS).

## ⚠️ Aviso Legal

Projeto **acadêmico/pessoal**. O script implementa pausas entre requisições para não sobrecarregar os servidores da SEFA/PR. Os preços são informativos e extraídos de NF-e.
