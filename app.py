import streamlit as st
import requests
import time

# Configurações básicas fixas
NOME_IA = "Soberana"
CRIADOR = "Francisco Herbert Walons Fonseca de Araújo"

# CORREÇÃO CIRÚRGICA DE CABEÇALHO: Remove o texto incorreto caso ele venha do servidor
API_KEY = str(st.secrets.get("GEMINI_API_KEY", "")).strip().replace("telegram.org", "")
RAW_TOKEN = str(st.secrets.get("TELEGRAM_TOKEN", "")).strip()
TOKEN = RAW_TOKEN.replace("telegram.org", "").strip()

st.title("🧠 SOBERANA 5.0 - MONITOR DEFINITIVO")
st.success("🤖 Conexão limpa estabelecida. Buscando mensagens no Telegram...")

if "last_id" not in st.session_state:
    st.session_state["last_id"] = 0

def inteligenca_gemini(texto):
    url = f"https://googleapis.com{API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": texto}]}], 
        "systemInstruction": {"parts": [{"text": f"Você é a {NOME_IA}, inteligência artificial privada de {CRIADOR}."}]}
    }
    try:
        res = requests.post(url, json=payload, timeout=10)
        return res.json()["candidates"]["content"]["parts"]["text"] if res.status_code == 200 else "[Erro de Processamento]"
    except:
        return "[Erro de Conexão]"

if TOKEN:
    try:
        # Força o Telegram a esquecer conexões antigas travadas
        requests.get(f"https://telegram.org{TOKEN}/deleteWebhook", timeout=3)
        
        url_updates = f"https://telegram.org{TOKEN}/getUpdates"
        response = requests.get(url_updates, params={"offset": st.session_state["last_id"] + 1, "timeout": 1}, timeout=3)
        
        if response.status_code == 200:
            for update in response.json().get("result", []):
                st.session_state["last_id"] = update["update_id"]
                if "message" in update and "text" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    msg_txt = update["message"]["text"]
                    
                    st.info(f"📥 Recebido: '{msg_txt}'")
                    resposta = inteligenca_gemini(msg_txt)
                    
                    url_envio = f"https://telegram.org{TOKEN}/sendMessage"
                    requests.post(url_envio, json={"chat_id": chat_id, "text": resposta}, timeout=5)
                    st.success("📤 Respondido com sucesso!")
        else:
            st.error(f"Aguardando sinal válido do servidor. Código: {response.status_code}")
    except Exception as e:
        st.error(f"Falha de pareamento: {str(e)}")

time.sleep(2)
st.rerun()
