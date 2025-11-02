import streamlit as st
import requests
from dotenv import load_dotenv
import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import math
import json

from math import radians, sin, cos, sqrt, atan2
from analise_csv import processar_arquivo
from busca_google import buscar_fornecedores_google
from extrair_cnpj import extrair_cnpj_do_site
from avaliar_reputacao import avaliar_reputacao_snippet
from classificacao import classificar_fornecedor
from pagamento_garantido import calcular_custo_total, simular_comparativo_fornecedores
from relatorios import gerar_relatorio_comparativo_pdf
from datetime import datetime
from nfe_io_api import gerar_nota_ficticia_local
import random
from nfe_io_api import gerar_nota_ficticia_local, consultar_notas_por_cnpj
from nfe_io_api import consultar_notas_por_cnpj, gerar_nota_ficticia_local
from consulta_publica_cnpj import consultar_dados_cnpj

# -------------------------
# Função para consultar CNPJ
# -------------------------
def consultar_cnpj(cnpj):
    url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj}"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except:
        return None
    return None

# -------------------------
# Configuração da página
# -------------------------
st.set_page_config(page_title="Agente Fornecedor Inteligente", layout="centered")
st.title("🔎 Sistema Agente Fornecedor Inteligente")

# -------------------------
# Carregar API Key do .env
# -------------------------
load_dotenv()
api_key_env = os.getenv("SERPAPI_KEY")

st.markdown("### 🧠 Pesquisa Inteligente de Fornecedores")

busca = st.text_input("📌 Produto a pesquisar (ex: máquina de solda MIG/MAG):")
alcance = st.radio(
    "Selecione o alcance da busca:",
    ["Local", "Nacional"],
    horizontal=True,
    key="alcance_busca"  # Evita duplicação de ID
)

api_key_input = st.text_input("🔐 Chave SerpAPI (opcional, usa .env se vazio):", type="password")
api_key = api_key_input if api_key_input else api_key_env

if not api_key:
    st.warning("⚠️ API Key da SerpAPI não foi informada. Preencha ou defina no .env.")

st.divider()

# -------------------------
# Busca de fornecedores
# -------------------------
if st.button("🔍 Buscar fornecedores no Google"):
    if busca and api_key:
        if alcance == "Nacional":
            query = f"{busca} fornecedor no Brasil"
        else:
            query = f"fornecedor de {busca} em Porto Alegre"

        resultados = buscar_fornecedores_google(query, api_key)

        if resultados:
            st.subheader("📄 Resultados encontrados:")

            for fornecedor in resultados:
                with st.container():
                    st.markdown(f"### 📌 {fornecedor['nome']}")
                    st.markdown(f"[🌐 Acessar site]({fornecedor['link']})")
                    st.markdown(f"📝 *{fornecedor['descricao']}*")

                    nota_reputacao, positivas, negativas = avaliar_reputacao_snippet(fornecedor['descricao'])
                    estrelas = "⭐" * nota_reputacao + "☆" * (5 - nota_reputacao)
                    st.markdown(f"📊 **Reputação estimada:** {estrelas} ({nota_reputacao}/5)")

                    # após calcular nota_reputacao
                    fornecedor["Nota Reputação"] = nota_reputacao

                    if positivas:
                        st.markdown(f"🟢 Palavras positivas: `{', '.join(positivas)}`")
                    if negativas:
                        st.markdown(f"🔴 Palavras negativas: `{', '.join(negativas)}`")

                    cnpj = extrair_cnpj_do_site(fornecedor['link'])
                    if cnpj:
                        cnpj_limpo = re.sub(r'\D', '', cnpj)
                        st.markdown(f"🔢 **CNPJ detectado:** `{cnpj}`")

                        with st.spinner("🔄 Validando CNPJ e consultando a Receita..."):
                            dados = consultar_cnpj(cnpj_limpo)

                        if dados and dados.get("status") != "ERROR":
                            fornecedor["uf"] = dados.get("uf", "ND")
                            fornecedor["municipio"] = dados.get("municipio", "ND")
                            st.success(f"📍 Localização: {fornecedor['municipio']} / {fornecedor['uf']}")
                        else:
                            st.warning("⚠️ Não foi possível validar o CNPJ.")
                    else:
                        fornecedor["uf"] = "ND"
                        st.warning("⚠️ CNPJ não encontrado automaticamente.")

            st.session_state["fornecedores_encontrados"] = resultados
        else:
            st.warning("🔍 Nenhum resultado encontrado.")
    else:
        st.warning("⚠️ Preencha o produto e a API Key.")

st.divider()

# -------------------------
# Comparativo de Fornecedores
# -------------------------
st.header("📊 Comparativo de Fornecedores")

fornecedores_salvos = st.session_state.get("fornecedores_encontrados", [])

if not fornecedores_salvos:
    st.info("🔍 Primeiro realize uma busca para comparar fornecedores.")
else:
    st.markdown("Selecione até **5 fornecedores** da lista para comparar:")

    selecionados = []
    for fornecedor in fornecedores_salvos:
        col1, col2 = st.columns([3, 1])
        with col1:
            marcado = st.checkbox(fornecedor["nome"], key=f"sel_{fornecedor['nome']}")
        with col2:
            st.markdown(f"[🌐 Site]({fornecedor['link']})")

        if marcado:
            selecionados.append({
                "nome": fornecedor["nome"],
                "valor": 50000,  # valor base para simulação
                "uf_origem": fornecedor.get("uf", "SP")
            })

    uf_destino_comp = st.text_input("UF de destino (entrega):", max_chars=2).upper()

    if st.button("🚀 Gerar Comparativo"):
        if len(selecionados) >= 2 and uf_destino_comp:
            df_comparativo = simular_comparativo_fornecedores(selecionados, uf_destino_comp)

            # mapear reputações a partir dos fornecedores salvos
            reput_map = {f["nome"]: f.get("Nota Reputação", 0) for f in fornecedores_salvos}
            df_comparativo["Nota Reputação"] = df_comparativo["Fornecedor"].map(reput_map).fillna(0).astype(int)

            # Agrupar por UF de origem
            df_comparativo_grouped = df_comparativo.groupby("UF Origem", as_index=False)["Custo Total"].mean()

            st.success("✅ Comparativo concluído!")
            st.dataframe(df_comparativo)

            # Gráfico de barras por fornecedor
            st.markdown("### 📈 Ranking de Custo Total por Fornecedor")
            st.bar_chart(df_comparativo.set_index("Fornecedor")["Custo Total"])

            # Gráfico agrupado por estado
            st.markdown("### 🌍 Média de Custo Total por UF de Origem")
            fig, ax = plt.subplots(figsize=(6, 3))
            ax.bar(df_comparativo_grouped["UF Origem"], df_comparativo_grouped["Custo Total"], color="#4C9F70")
            ax.set_xlabel("UF de Origem")
            ax.set_ylabel("Custo Total (R$)")
            ax.set_title("Média de Custo Total por Estado de Origem")
            st.pyplot(fig)

            # Melhor fornecedor
            melhor = df_comparativo.iloc[0]
            st.markdown(f"### 🏆 **Melhor Fornecedor: {melhor['Fornecedor']}**")
            st.markdown(f"- UF Origem: {melhor['UF Origem']}")
            st.markdown(f"- **Custo Total Final:** R$ {melhor['Custo Total']:,.2f}")

            df_comparativo = simular_comparativo_fornecedores(selecionados, uf_destino_comp)

            # INJETAR nota de reputação
            reput_map = {f["nome"]: f.get("Nota Reputação", 0) for f in fornecedores_salvos}
            df_comparativo["Nota Reputação"] = df_comparativo["Fornecedor"].map(reput_map).fillna(0).astype(int)

            st.success("✅ Comparativo concluído!")
          

            # Gerar PDF
            pdf_path = gerar_relatorio_comparativo_pdf(df_comparativo)
            with open(pdf_path, "rb") as f:
                st.download_button(
                    "📄 Baixar Relatório Comparativo em PDF",
                    data=f,
                    file_name="relatorio_comparativo.pdf",
                    mime="application/pdf"
                )
        else:
            st.warning("⚠️ Selecione pelo menos 2 fornecedores e informe a UF de destino.")

st.divider()

# -------------------------
# CONSULTA DE NOTAS FISCAIS
# -------------------------
st.sidebar.title("📑 Consultas Fiscais")

menu = st.sidebar.radio(
    "Escolha uma ação:",
    ["Busca de Fornecedores", "Simulação de Pagamento", "Comparativo", "Consulta NF-e"]
)

# -------------------------
# CONFIGURAÇÕES / PLACEHOLDERS
# -------------------------
# 🔑 Chave do OpenRouteService (substitui o Google Maps)
ORS_API_KEY = "COLE SUA CHAVE AQUI"
DEFAULT_FRETE_R_KM = 0.8  # custo por km usado no cálculo do frete (padrão)

# Coordenadas básicas para cálculo alternativo (capitais e cidades mais comuns)
COORDENADAS = {
    "São Paulo, SP": (-23.5505, -46.6333),
    "São Bernardo do Campo, SP": (-23.6898, -46.5649),
    "Rio de Janeiro, RJ": (-22.9068, -43.1729),
    "Curitiba, PR": (-25.4284, -49.2733),
    "Porto Alegre, RS": (-30.0331, -51.2300),
    "Florianópolis, SC": (-27.5954, -48.5480),
    "Belo Horizonte, MG": (-19.9167, -43.9345),
    "Salvador, BA": (-12.9714, -38.5014),
    "Brasília, DF": (-15.7939, -47.8828),
}

# -------------------------------
# 🧮 FUNÇÕES DE CÁLCULO
# -------------------------------
def estimate_tributos(valor, uf_origem, uf_destino):
    """Estima ICMS, PIS e COFINS com base em alíquotas médias."""
    icms = valor * 0.12 if uf_origem != uf_destino else valor * 0.07
    pis = valor * 0.0165
    cofins = valor * 0.076
    return icms, pis, cofins


def distancia_haversine(lat1, lon1, lat2, lon2):
    """Calcula a distância aproximada em km entre dois pontos (lat/lon)."""
    R = 6371  # raio da Terra em km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def calcular_distancia_ors(origem, destino):
    """
    Calcula a distância entre duas localidades (estado ou cidade)
    usando a API gratuita do OpenRouteService.
    Se não for possível calcular, retorna None.
    """
    try:
        # Endpoint de geocodificação para converter o nome em coordenadas
        geocode_url = "https://api.openrouteservice.org/geocode/search"
        
        # Função interna para obter latitude e longitude
        def obter_coordenadas(local):
            params = {"api_key": ORS_API_KEY, "text": local}
            r = requests.get(geocode_url, params=params)
            dados = r.json()
            if "features" in dados and len(dados["features"]) > 0:
                coords = dados["features"][0]["geometry"]["coordinates"]
                return coords[0], coords[1]
            return None, None

        lon_origem, lat_origem = obter_coordenadas(origem)
        lon_destino, lat_destino = obter_coordenadas(destino)

        if None in (lon_origem, lat_origem, lon_destino, lat_destino):
            return None  # não conseguiu converter as coordenadas

        # Endpoint de roteamento (calcula a distância real)
        rota_url = "https://api.openrouteservice.org/v2/directions/driving-car"
        rota_params = {
            "api_key": ORS_API_KEY,
            "start": f"{lon_origem},{lat_origem}",
            "end": f"{lon_destino},{lat_destino}",
        }

        rota_resp = requests.get(rota_url, params=rota_params)
        rota_dados = rota_resp.json()

        if "routes" in rota_dados:
            distancia_metros = rota_dados["routes"][0]["summary"]["distance"]
            distancia_km = distancia_metros / 1000
            return round(distancia_km, 2)
        else:
            return None
    except Exception as e:
        print(f"Erro ao calcular distância: {e}")
        return None
    
    # 2️⃣ Cálculo alternativo (gratuito via Haversine)
    if origem in COORDENADAS and destino in COORDENADAS:
        lat1, lon1 = COORDENADAS[origem]
        lat2, lon2 = COORDENADAS[destino]
        km = distancia_haversine(lat1, lon1, lat2, lon2)
        return km

    # 3️⃣ Caso falte alguma coordenada, tenta usar apenas a UF como aproximação
    uf_origem = origem.split(",")[-1].strip() if "," in origem else origem
    uf_destino = destino.split(",")[-1].strip() if "," in destino else destino

    if uf_origem == uf_destino:
        return 200.0  # estimativa média dentro do estado
    else:
        return 800.0  # estimativa média entre estados


def calcular_custo_total(valor_produto, icms, pis, cofins, distancia_km):
    """Soma produto + tributos + frete."""
    tributos_total = icms + pis + cofins
    frete_total = (distancia_km or 0) * DEFAULT_FRETE_R_KM
    custo_total = valor_produto + tributos_total + frete_total
    return tributos_total, frete_total, custo_total

# -------------------------------
# 🧭 INTERFACE STREAMLIT
# -------------------------------
from consulta_publica_cnpj import consultar_dados_cnpj  # 👈 novo import para consultas reais

st.title("🧾 Agente Inteligente de Fornecedores")
st.write("Versão híbrida — alterna entre simulação local e consulta pública real via APIs oficiais")

modo = st.radio("Selecione o modo de operação:", ["Simulado", "Real"])

with st.form("dados_nf"):
    st.subheader("📋 Dados para consulta / geração de nota")
    cnpj = st.text_input("CNPJ do fornecedor (destinatário):", "66.018.441/0001-29")
    nome = st.text_input("Nome do fornecedor:", "Coopermetal")
    valor = st.number_input("Valor da nota (R$):", min_value=100.0, value=50000.0, step=100.0)
    uf_origem = st.text_input("UF Origem (logística)", "SP")
    uf_destino = st.text_input("UF Destino (logística)", "RS")
    submit = st.form_submit_button("Consultar / Gerar Nota")

if submit:
    st.divider()

    # -------------------------------
    # 🔍 MODO SIMULADO OU REAL
    # -------------------------------
    if modo == "Simulado":
        st.info("🔧 Modo **Simulado** — gerando nota fictícia e cálculo estimado.")
        nota = gerar_nota_ficticia_local(cnpj, nome, valor)

    else:
        st.info("🔍 Modo **Real** — consultando dados públicos de CNPJ (BrasilAPI / Receitaws).")
        dados_cnpj = consultar_dados_cnpj(cnpj)

        if dados_cnpj:
            st.success(f"✅ Dados reais encontrados via {dados_cnpj.get('fonte_utilizada')}")
            st.json(dados_cnpj)
            nota = {
                "number": "REAL-001",
                "recipientCnpj": cnpj,
                "total": valor,
                "issuedOn": datetime.now().strftime("%Y-%m-%d"),
                "issuer": {"companyName": dados_cnpj.get("razao_social", nome)},
            }
        else:
            st.warning("Nenhum dado público encontrado. Gerando nota fictícia.")
            nota = gerar_nota_ficticia_local(cnpj, nome, valor)

    # -------------------------------
    # 📄 MOSTRAR RESULTADOS DA NOTA
    # -------------------------------
    st.subheader("📄 Nota Fiscal Retornada / Simulada")
    st.json(nota)

    valor_produto = nota.get("total", valor)
    fornecedor = nota.get("issuer", {}).get("companyName", nome)
    cnpj_nf = nota.get("recipientCnpj", cnpj)
    emitida_em = nota.get("issuedOn", datetime.now().strftime("%Y-%m-%d"))

    # -------------------------------
    # 🧮 CÁLCULO DE CUSTO TOTAL
    # -------------------------------
    icms, pis, cofins = estimate_tributos(valor_produto, uf_origem, uf_destino)

    # 🔹 Cálculo da distância entre origem e destino (usando ORS)
    distancia_km = calcular_distancia_ors(f"{uf_origem}", f"{uf_destino}")

    # 🔹 Caso não consiga calcular via API, tenta estimar via fallback interno
    if not distancia_km:
        if uf_origem in COORDENADAS and uf_destino in COORDENADAS:
            lat1, lon1 = COORDENADAS[uf_origem]
            lat2, lon2 = COORDENADAS[uf_destino]
            distancia_km = distancia_haversine(lat1, lon1, lat2, lon2)
        else:
            uf_origem_sigla = uf_origem.split(",")[-1].strip() if "," in uf_origem else uf_origem
            uf_destino_sigla = uf_destino.split(",")[-1].strip() if "," in uf_destino else uf_destino
            distancia_km = 200.0 if uf_origem_sigla == uf_destino_sigla else 800.0

    # -------------------------------
    # 🚚 FRETE DIFERENCIADO POR MODO
    # -------------------------------
    if modo == "Simulado":
        custo_por_km = 0.8  # valor fixo genérico
    else:
        # Modo real — custo dinâmico por região (simula variação real)
        regioes_custo = {
            "N": 1.2,   # Norte
            "NE": 1.0,  # Nordeste
            "CO": 0.9,  # Centro-Oeste
            "SE": 0.75, # Sudeste
            "S": 0.7    # Sul
        }

        uf_regioes = {
            "AC": "N", "AM": "N", "AP": "N", "PA": "N", "RO": "N", "RR": "N", "TO": "N",
            "AL": "NE", "BA": "NE", "CE": "NE", "MA": "NE", "PB": "NE", "PE": "NE", "PI": "NE", "RN": "NE", "SE": "NE",
            "DF": "CO", "GO": "CO", "MT": "CO", "MS": "CO",
            "ES": "SE", "MG": "SE", "RJ": "SE", "SP": "SE",
            "PR": "S", "RS": "S", "SC": "S"
        }

        reg_origem = uf_regioes.get(uf_origem.strip()[-2:], "SE")
        reg_destino = uf_regioes.get(uf_destino.strip()[-2:], "SE")
        custo_por_km = (regioes_custo[reg_origem] + regioes_custo[reg_destino]) / 2

    # 🔹 Cálculo final
    tributos_total, frete_total, custo_total = calcular_custo_total(
        valor_produto, icms, pis, cofins, distancia_km
    )
    frete_total = distancia_km * custo_por_km
    custo_total = valor_produto + tributos_total + frete_total

    # -------------------------------
    # 📊 EXIBIÇÃO DOS RESULTADOS
    # -------------------------------
    st.subheader("📊 Resultado do cálculo de custo total da aquisição")

    st.write(f"**Fornecedor:** {fornecedor}")
    st.write(f"**CNPJ:** {cnpj_nf}")
    st.write(f"**Valor do Produto:** R$ {valor_produto:,.2f}")
    st.write(f"**Tributos (ICMS + PIS + COFINS):** R$ {tributos_total:,.2f}")

    if distancia_km:
        st.write(f"**Custo Logístico ({distancia_km:.0f} km):** R$ {frete_total:,.2f}")
    else:
        st.write("**Custo Logístico:** Não calculado (erro ao obter distância).")

    st.success(f"➡️ **Custo Total da Aquisição:** R$ {custo_total:,.2f}")

    # Rodapé explicativo
    st.caption(
        "🧮 No modo Real, os dados vêm de APIs públicas (BrasilAPI / Receitaws). "
        "Quando a integração oficial com a NFe.io for reativada, os tributos e frete serão substituídos por valores oficiais."
    )
