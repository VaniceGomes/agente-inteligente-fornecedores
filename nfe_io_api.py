import requests
from datetime import datetime
import streamlit as st

# ----------------------------------------------------------
# 🔐 CONFIGURAÇÕES DA API NFe.io
# ----------------------------------------------------------
# Insira suas credenciais reais (modo Development funciona normalmente)
NFEIO_COMPANY_ID = "COLOQUE AQUI SEU ID"   # <-- Seu Company ID
NFEIO_API_KEY = "COLOQUE AQUI SUA CHAVE "  # <-- Substitua pela sua chave da NFe.io
NFEIO_BASE_URL = "https://api.nfe.io/v1"


# ----------------------------------------------------------
# 🧾 FUNÇÃO PRINCIPAL: CONSULTAR NOTAS POR CNPJ
# ----------------------------------------------------------
def consultar_notas_por_cnpj(cnpj):
    """
    Consulta notas fiscais eletrônicas de um determinado CNPJ via NFe.io.
    Caso a API não esteja acessível ou não haja notas, ativa o modo simulado.
    """

    headers = {
        "Authorization": f"Basic {NFEIO_API_KEY}",
        "Content-Type": "application/json",
    }

    url = f"{NFEIO_BASE_URL}/companies/{NFEIO_COMPANY_ID}/serviceinvoices"

    try:
        st.info("🔍 Consultando notas fiscais na NFe.io...")

        # Requisição GET à API
        response = requests.get(url, headers=headers, timeout=20)

        # Verifica se a API respondeu corretamente
        if response.status_code == 200:
            data = response.json()

            # Filtra as notas que correspondem ao CNPJ pesquisado
            notas = []
            for nota in data.get("data", []):
                recipient = nota.get("recipient", {})
                recipient_cnpj = recipient.get("cnpj") or recipient.get("cpf")

                if recipient_cnpj and cnpj.replace(".", "").replace("/", "").replace("-", "") in recipient_cnpj:
                    notas.append({
                        "number": nota.get("number", "N/D"),
                        "recipientCnpj": recipient_cnpj,
                        "total": nota.get("servicesAmount", 0.0),
                        "issuedOn": nota.get("createdOn", datetime.now().strftime("%Y-%m-%d")),
                        "issuer": {
                            "companyName": nota.get("company", {}).get("name", "Desconhecido")
                        }
                    })

            # Retorno normal (encontrou notas)
            if notas:
                return {"status": "ok", "data": notas}

            # Nenhuma nota encontrada
            return {"status": "empty", "data": []}

        elif response.status_code == 404:
            st.warning("⚠️ Nenhuma nota encontrada para o CNPJ informado.")
            return {"status": "empty", "data": []}

        else:
            st.error(f"Erro {response.status_code} ao consultar NFe.io: {response.text}")
            return {"status": "error", "data": [], "error": response.text}

    except Exception as e:
        # Caso haja erro de rede ou chave incorreta → fallback automático
        st.warning(f"❌ Falha na API da NFe.io ({e}). Usando modo simulado.")
        return gerar_nota_ficticia_local(cnpj, "Fornecedor Teste", 5000.00)


# ----------------------------------------------------------
# 🧩 FUNÇÃO DE BACKUP: GERAR NOTA FICTÍCIA LOCAL
# ----------------------------------------------------------
def gerar_nota_ficticia_local(cnpj, nome, valor):
    """
    Cria uma nota fictícia local para fins de simulação,
    usada como fallback quando a NFe.io não responde.
    """
    st.info("🧮 Gerando nota fictícia local (modo simulado).")

    nota_ficticia = {
        "number": "TEST-001",
        "recipientCnpj": cnpj,
        "total": float(valor),
        "issuedOn": datetime.now().strftime("%Y-%m-%d"),
        "issuer": {
            "companyName": nome
        }
    }

    return {"status": "simulated", "data": [nota_ficticia]}


# ----------------------------------------------------------
# 🧠 TESTE LOCAL OPCIONAL
# ----------------------------------------------------------
if __name__ == "__main__":
    # Teste rápido fora do Streamlit (executar via terminal: python nfe_io_api.py)
    cnpj_teste = "36484388000190"
    resultado = consultar_notas_por_cnpj(cnpj_teste)
    print(resultado)
