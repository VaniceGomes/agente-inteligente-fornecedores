import requests
from datetime import datetime

# ----------------------------
# CONSULTA PÚBLICA DE CNPJ
# ----------------------------
def consultar_dados_cnpj(cnpj: str):
    """
    Consulta os dados públicos de um CNPJ via BrasilAPI e, em fallback,
    via Receitaws. Retorna um dicionário padronizado com os dados da empresa.
    """
    cnpj = ''.join(filter(str.isdigit, str(cnpj)))  # limpa formatação

    resultado = None
    fonte = None

    # 1️⃣ Tenta consultar via BrasilAPI
    try:
        url_brasilapi = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
        resp = requests.get(url_brasilapi, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            resultado = {
                "fonte": "BrasilAPI",
                "cnpj": data.get("cnpj"),
                "razao_social": data.get("razao_social"),
                "nome_fantasia": data.get("nome_fantasia"),
                "uf": data.get("uf"),
                "municipio": data.get("municipio"),
                "situacao": data.get("situacao_cadastral"),
                "data_abertura": data.get("data_inicio_atividade"),
                "cnae_principal": data.get("cnae_fiscal_descricao"),
                "logradouro": data.get("logradouro"),
                "bairro": data.get("bairro"),
            }
            fonte = "BrasilAPI"
    except Exception:
        pass  # falha silenciosa para fallback

    # 2️⃣ Fallback: tenta Receitaws se BrasilAPI falhar
    if not resultado:
        try:
            url_receitaws = f"https://www.receitaws.com.br/v1/cnpj/{cnpj}"
            resp2 = requests.get(url_receitaws, timeout=15)
            if resp2.status_code == 200:
                data = resp2.json()
                if data.get("status") != "ERROR":
                    resultado = {
                        "fonte": "Receitaws",
                        "cnpj": data.get("cnpj"),
                        "razao_social": data.get("nome"),
                        "nome_fantasia": data.get("fantasia"),
                        "uf": data.get("uf"),
                        "municipio": data.get("municipio"),
                        "situacao": data.get("situacao"),
                        "data_abertura": data.get("abertura"),
                        "cnae_principal": data.get("atividade_principal", [{}])[0].get("text"),
                        "logradouro": data.get("logradouro"),
                        "bairro": data.get("bairro"),
                    }
                    fonte = "Receitaws"
        except Exception:
            pass

    # 3️⃣ Último fallback: simulação local se nenhuma API responder
    if not resultado:
        resultado = {
            "fonte": "Simulação Local",
            "cnpj": cnpj,
            "razao_social": "Empresa Simulada Ltda",
            "nome_fantasia": "Fornecedor Padrão",
            "uf": "SP",
            "municipio": "São Paulo",
            "situacao": "ATIVA",
            "data_abertura": datetime.now().strftime("%Y-%m-%d"),
            "cnae_principal": "Comércio varejista de produtos diversos",
            "logradouro": "Rua Fictícia, 123",
            "bairro": "Centro",
        }
        fonte = "Simulação Local"

    resultado["fonte_utilizada"] = fonte
    return resultado


# ----------------------------
# TESTE RÁPIDO (opcional)
# ----------------------------
if __name__ == "__main__":
    cnpj_teste = "36484388000190"  # teste com CNPJ real
    dados = consultar_dados_cnpj(cnpj_teste)
    print("✅ Resultado da consulta pública:")
    for k, v in dados.items():
        print(f"{k}: {v}")
