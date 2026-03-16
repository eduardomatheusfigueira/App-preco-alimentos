# 🛒 App Preço Alimentos - Itaipu Parquetec

Aplicação robusta em Python para monitoramento de preços de alimentos em tempo real, utilizando a API do portal **Menor Preço (Nota Paraná)**. O sistema segue a metodologia do **DIEESE** para o cálculo da Cesta Básica, mas permite total personalização pelo usuário.

---

## 🏗️ O que há de novo?

- **📦 Cestas Personalizadas**: Monte sua própria lista de compras (ex: "Churrasco", "Cesta Vegana"), defina termos de busca, NCMs e quantidades. O App gerencia históricos independentes para cada cesta.
- **🥩 Coleta Inteligente de Carne**: Sistema multi-termo que contorna o limite de 50 itens da API, buscando cortes específicos (Coxão Mole, Alcatra, etc.) e removendo duplicatas automaticamente.
- **📊 Barra de Progresso Real-time**: Feedback visual no dashboard durante a coleta manual, mostrando percentual e status de cada produto.
- **📐 Design Itaipu Parquetec**: Interface moderna com Glassmorphism, tipografia Ubuntu e paleta de cores institucional.
- **🔍 Pipeline de Refinamento**: 5 camadas de filtragem (NCM, blacklist de miúdos, normalização de peso, limpeza de outliers via IQR e cálculo de mediana).

---

## 🚀 Instalação e Configuração

### 1. Preparar Ambiente
```bash
# Criar e ativar ambiente virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Instalar dependências
pip install -r requirements.txt
```

### 2. Execução
```bash
# Iniciar o Dashboard Streamlit
streamlit run dashboard.py
```

---

## 🛠️ Arquitetura do Sistema

| Arquivo | Função |
|---------|-----------|
| `dashboard.py` | Interface principal Steamlit com gestão de cestas e relatórios. |
| `collector.py` | Motor de coleta dinâmico com suporte a progress_callback. |
| `database.py` | Camada de persistência SQLite com suporte a múltiplas configurações. |
| `api_client.py` | Integração com Menor Preço PR (SSL seguro, retries, rate-limit). |
| `filters.py` | Lógica de normalização de gramatura (ex: UN -> KG) e filtragem estatística. |
| `config.py` | Configurações DIEESE e constantes globais do App. |
| `ncm_constants.py` | Catálogo de NCMs p/ facilitar a criação de itens customizados. |

---

## 📋 Como Usar: Cesta Personalizada

1. No Dashboard, vá na barra lateral e selecione o modo **"Personalizada"**.
2. Clique em **"🛠️ Editar Itens da Cesta"**.
3. Adicionar o nome do produto e o termo de busca (ex: "Chocolate Meio Amargo").
4. Use o **Dropdown de NCM** para garantir que você só pesquise itens da categoria correta.
5. Defina a quantidade e salve.
6. Clique em **🚀 Pesquisar [Sua Cesta]**.

---

## ⚠️ Aviso Legal e Metodologia

Este é um projeto desenvolvido com propósitos acadêmicos/técnicos. A coleta respeita a infraestrutura do portal Nota Paraná através do uso de delays controlados. Os dados refletem as notas fiscais emitidas no estado do Paraná (Região 3 DIEESE).
