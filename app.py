import streamlit as st
import requests
import time

# Credenciais fixas e purificadas sem depender de Secrets corrompidos
API_KEY = "AQ.Ab8RN6IB3zDcZKUVT8fEYRM3-fva7o_aRjSgRU_1JnbrkMyBLQ"
TOKEN = "9102367881:AAGENcYpAh97hWSyg0AELxCMPONKAKzdP8s"

st.title("🧠 SOBERANA 5.0 - MONITOR DEFINITIVO")
st.success("🤖 Conexão direta estabelecida. Buscando mensagens no Telegram...")

if "last_id" not in st.session_state:
    st.session_state["last_id"] = 0

try:
    # Remove qualquer bloqueio anterior do Telegram
    requests.get(f"https://telegram.org{TOKEN}/deleteWebhook", timeout=3)
    
    # Busca novas mensagens
    url_updates = f"https://telegram.org{TOKEN}/getUpdates"
    res = requests.get(url_updates, params={"offset": st.session_state["last_id"] + 1, "timeout": 1}, timeout=3)
    
    if res.status_code == 200:
        for update in res.json().get("result", []):
            st.session_state["last_id"] = update["update_id"]
            if "message" in update and "text" in update["message"]:
                chat_id = update["message"]["chat"]["id"]
                msg_txt = update["message"]["text"]
                
                # Resposta direta do Gemini via HTTP estável
                url_gemini = f"https://googleapis.com{API_KEY}"
                payload = {"contents": [{"parts": [{"text": msg_txt}]}], "systemInstruction": {"parts": [{"text": "Você é a Soberana, IA do Francisco Herbert."}]}}
                res_gemini = requests.post(url_gemini, json=payload, timeout=10)
                
                resposta = res_gemini.json()["candidates"][0]["content"]["parts"][0]["text"] if res_gemini.status_code == 200 else "Erro na IA"
                
                # Envia de volta ao Telegram
                requests.post(f"https://telegram.org{TOKEN}/sendMessage", json={"chat_id": chat_id, "text": resposta}, timeout=5)
                st.info(f"📥 Respondido para o Telegram!")
except Exception as e:
    st.error(f"Aguardando sinal: {str(e)}")

time.sleep(2)
st.rerun()
