import streamlit as st
import requests
import time

# Configurações básicas fixas
NOME_IA = "Soberana"
CRIADOR = "Francisco Herbert Walons Fonseca de Araújo"

# Limpeza do token
API_KEY = str(st.secrets.get("GEMINI_API_KEY", "")).strip().replace("telegram.org", "")
RAW_TOKEN = str(st.secrets.get("TELEGRAM_TOKEN", "")).strip()
TOKEN = RAW_TOKEN.replace("telegram.org", "").strip()

st.title("🧠 SOBERANA 5.0 - MONITOR DEFINITIVO")
st.success("🤖 Conexão limpa estabelecida. Buscando mensagens no Telegram...")

if "last_id" not in st.session_state:
    st.session_state["last_id"] = 0

def inteligenca_gemini(texto):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": texto}]}],
        "systemInstruction": {
            "parts": [{"text": f"Você é a {NOME_IA}, inteligência artificial privada de {CRIADOR}."}]
        }
    }
    try:
        res = requests.post(url, json=payload, timeout=15)
        if res.status_code == 200:
            data = res.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"[Erro Gemini: {res.status_code}]"
    except Exception as e:
        return f"[Erro de Conexão Gemini: {str(e)}]"

if TOKEN:
    try:
        # Limpa webhook antigo
        requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook", timeout=5)

        url_updates = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
        response = requests.get(
            url_updates,
            params={"offset": st.session_state["last_id"] + 1, "timeout": 10},
            timeout=15
        )

        if response.status_code == 200:
            updates = response.json().get("result", [])
            for update in updates:
                st.session_state["last_id"] = update["update_id"]

                if "message" in update and "text" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    msg_txt = update["message"]["text"]

                    st.info(f"📥 Recebido: {msg_txt}")
                    resposta = inteligenca_gemini(msg_txt)

                    url_envio = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                    requests.post(
                        url_envio,
                        json={"chat_id": chat_id, "text": resposta},
                        timeout=10
                    )
                    st.success("📤 Respondido com sucesso!")
        else:
            st.warning(f"Aguardando mensagens... (código {response.status_code})")

    except Exception as e:
        st.error(f"Falha de pareamento: {str(e)}")
else:
    st.error("Token do Telegram não encontrado nos Secrets.")

time.sleep(3)
st.rerun()
