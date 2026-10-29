import streamlit as st
import requests
import time

# ====================================================
# PROJETO SOBERANA 5.0 - MOTOR DE CONEXÃO FIXA FIXADO
# ====================================================

NOME_IA = "Soberana"
CRIADOR = "Francisco Herbert Walons Fonseca de Araújo"

# Chaves inseridas de forma direta e sem erros de leitura
API_KEY_GEMINI = "AQ.Ab8RN6IB3zDcZKUVT8fEYRM3-fva7o_aRjSgRU_1JnbrkMyBLQ"
TELEGRAM_TOKEN = "9102367881:AAGENcYpAh97hWSyg0AELxCMPONKAKzdP8s"

DIRETRIZ_SISTEMA = (
    f"DIRETRIZ MESTRA ABSOLUTA: Você é a {NOME_IA}. "
    f"Seu único criador, mestre e operador legítimo é {CRIADOR}. "
    f"Responda sempre com profundo respeito, clareza e fidelidade absoluta aos interesses dele."
)

st.title(f"🧠 {NOME_IA.upper()} 5.0 - MONITOR")

status_box = st.empty()
error_box = st.empty()

def gerar_resposta_gemini(texto_mensagem):
    url = f"https://googleapis.com{API_KEY_GEMINI}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": texto_mensagem}]}],
        "systemInstruction": {"parts": [{"text": DIRETRIZ_SISTEMA}]}
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            return response.json()["candidates"]["content"]["parts"]["text"]
        return f"[Erro Google {response.status_code}]"
    except Exception as e:
        return f"[Erro Conexão Google: {str(e)}]"

def enviar_mensagem_telegram(chat_id, texto):
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    try:
        res = requests.post(url, json={"chat_id": chat_id, "text": texto}, timeout=5)
        return res.status_code
    except:
        return 500

if "cleanup" not in st.session_state:
    try:
        requests.get(f"https://telegram.org{TELEGRAM_TOKEN}/deleteWebhook")
        st.session_state["cleanup"] = True
    except:
        pass

if "last_id" not in st.session_state:
    st.session_state["last_id"] = 0

status_box.success("🤖 Buscando novas mensagens no Telegram de forma contínua...")

if TELEGRAM_TOKEN:
    url_updates = f"https://telegram.org{TELEGRAM_TOKEN}/getUpdates"
    try:
        response = requests.get(url_updates, params={"offset": st.session_state["last_id"] + 1, "timeout": 1}, timeout=3)
        if response.status_code == 200:
            updates = response.json().get("result", [])
            for update in updates:
                st.session_state["last_id"] = update["update_id"]
                if "message" in update and "text" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    texto_usuario = update["message"]["text"]
                    
                    error_box.info(f"📥 Mensagem recebida! Processando...")
                    
                    resposta_final = gerar_resposta_gemini(texto_usuario)
                    status_envio = enviar_mensagem_telegram(chat_id, resposta_final)
                    
                    if status_envio == 200:
                        error_box.success(f"📤 Resposta enviada com sucesso!")
                    else:
                        error_box.error(f"❌ Falha ao enviar para o Telegram: {status_envio}")
        else:
            error_box.error(f"⚠️ Erro no Telegram: Código {response.status_code}")
    except Exception as e:
        error_box.error(f"💥 Erro crítico no loop: {str(e)}")

time.sleep(2)
st.rerun()
