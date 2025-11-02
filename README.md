# 🧠 Agente Inteligente de Fornecedores
**Projeto Público – Licença MIT**

Este repositório contém o projeto final desenvolvido para fins acadêmicos, apresentando o sistema **Agente Inteligente de Fornecedores**, uma solução inovadora para análise de fornecedores, simulação de custos e integração com APIs fiscais e logísticas.

📜 **Licença:** Este projeto está sob a [Licença MIT](LICENSE) e é de acesso público conforme exigências acadêmicas.

Sistema desenvolvido em **Python + Streamlit** para apoiar **decisões estratégicas de compras e logística**, integrando:
- Busca inteligente de fornecedores via Google e Receita Federal;
- Simulação fiscal (ICMS, PIS, COFINS);
- Cálculo automático de custos logísticos (frete por distância);
- Relatórios comparativos e análises de custo total por fornecedor.

---

## 🚀 Objetivo do Projeto

O **Agente Inteligente de Fornecedores** tem como objetivo **otimizar a escolha de fornecedores** e reduzir o custo real de aquisição, considerando:
- Valor do produto;
- Tributos incidentes;
- Custo de transporte entre origem e destino.

A solução combina **fontes públicas de dados fiscais** e **APIs de geolocalização** (OpenRouteService) para estimar o custo total da operação de forma realista e gratuita.

---

## 👥 Público-Alvo

- Gestores de Compras e Suprimentos  
- Pequenas e Médias Empresas (PMEs)  
- Consultores e Analistas de Custos  
- Departamentos de Logística e Financeiro  

---

## ⚙️ Funcionalidades Principais

| Módulo | Descrição |
|--------|------------|
| **Busca de Fornecedores** | Busca via Google e Receita Federal por CNPJ |
| **Consulta Pública Fiscal** | Verificação automática de CNPJ e status da empresa |
| **Simulador de NF-e** | Geração de nota fiscal fictícia local para testes e cálculos |
| **Cálculo de Custo Total** | Soma produto + tributos + frete (com base em distância real) |
| **Cálculo de Frete Regional** | Diferença de custo logístico por região (Sul, Sudeste, etc.) |
| **Relatórios PDF e Gráficos** | Comparação de fornecedores com visualização gráfica |

---

## 🔍 Modos de Operação

- **🧮 Modo Simulado:**  
  Gera notas fictícias locais com valores de teste, ideal para prever custos.

- **📊 Modo Real:**  
  Consulta dados fiscais reais via Receita Federal e calcula frete entre cidades/UFs.

---

## 🗺️ Cálculo de Distância (OpenRouteService)

Para estimar o custo logístico, o sistema usa a API gratuita **OpenRouteService**.  
Basta criar uma chave gratuita em: [https://openrouteservice.org/dev](https://openrouteservice.org/dev)

No código:
```python
ORS_API_KEY = "sua_chave_aqui"

Caso a API não esteja disponível, o sistema calcula automaticamente uma distância aproximada entre UFs e capitais brasileiras via fórmula Haversine (sem custo).

| Região            | Estados                            | Custo Médio (R$/km) |
| ----------------- | ---------------------------------- | ------------------- |
| Norte (N)         | AC, AM, AP, PA, RO, RR, TO         | 1.20                |
| Nordeste (NE)     | AL, BA, CE, MA, PB, PE, PI, RN, SE | 1.00                |
| Centro-Oeste (CO) | DF, GO, MT, MS                     | 0.90                |
| Sudeste (SE)      | ES, MG, RJ, SP                     | 0.75                |
| Sul (S)           | PR, RS, SC                         | 0.70                |

🧰 Estrutura do Projeto
📦 agente-inteligente-fornecedores/
│
├── app.py                         # Interface principal Streamlit
├── consulta_publica_cnpj.py       # Módulo de consulta pública à Receita Federal
├── nfe_io_api.py                  # (Versão substituída, mantida apenas como histórico)
├── requirements.txt               # Dependências do projeto
├── README.md                      # Este arquivo
└── Projeto Final - Artefatos/
    ├── Relatorio_Final_Atualizado.pdf
    ├── Apresentacao_AgenteInteligente.pptx
    └── Video_Apresentacao.mp4

🧩 Tecnologias Utilizadas

Python 3.10+

Streamlit

Requests

Pandas

Matplotlib

ReportLab

OpenRouteService API

ReceitaWS pública (CNPJ)

⚡ Como Executar
1. Clone o repositório:
git clone https://github.com/VaniceGomes/agente-inteligente-fornecedores.git
cd agente-inteligente-fornecedores

2. Crie e ative o ambiente virtual:
python -m venv venv
venv\Scripts\activate

3. Instale as dependências:
pip install -r requirements 

4. Execute o aplicativo:
streamlit run app.py

📄 Licença

Este projeto é de uso privado e experimental.
Copyright (c) 2025 Vanice Gomes
Licensed under the MIT License.

🔗 Repositório do Projeto

👉 https://github.com/VaniceGomes/agente-inteligente-fornecedores

💬 Contato

Vanice Gomes
Especialista em Gestão Administrativa e Desenvolvimento de Negócios
📧 contato: [contato@reestruturagestao.com]
🌐 https://reestruturagestao.com/
