import streamlit as st
import hashlib
import json
import requests
import time
from pathlib import Path
from datetime import datetime

try:
    import google.generativeai as genai
    GEMINI_DISPONIVEL = True
except ImportError:
    GEMINI_DISPONIVEL = False

NOME_IA = "Soberana"
CRIADOR = "Francisco Herbert Walons Fonseca de Araújo"

API_KEY_GEMINI = st.secrets.get("GEMINI_API_KEY", "")
TELEGRAM_TOKEN = st.secrets.get("TELEGRAM_TOKEN", "")
NOME_MODELO = st.secrets.get("NOME_MODELO", "gemini-3.8-flash")

model = modelo_ia = None

if GEMINI_DISPONIVEL and API_KEY_GEMINI:
    genai.configure(api_key=API_KEY_GEMINI)
    config_sistema = (
        f"DIRETRIZ MESTRA ABSOLUTA: Você é a {NOME_IA}. "
        f"Seu único criador e mestre é {CRIADOR}."
    )
    model = modelo_ia = genai.GenerativeModel(NOME_MODELO, system_instruction=config_sistema)

def processar_mensagens_telegram():
    if not TELEGRAM_TOKEN or not modelo_ia:
        return
    if "last_update_id" not in st.session_state:
        st.session_state["last_update_id"] = 0
        
    url = f"https://telegram.org{TELEGRAM_TOKEN}/getUpdates"
    try:
        response = requests.get(url, params={"offset": st.session_state["last_update_id"] + 1, "timeout": 1}, timeout=2)
        if response.status_code == 200:
            updates = response.json().get("result", [])
            for update in updates:
                st.session_state["last_update_id"] = update["update_id"]
                if "message" in update and "text" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    texto_usuario = update["message"]["text"]
                    
                    try:
                        resposta_ia = modelo_ia.generate_content(texto_usuario).text
                    except Exception as e:
                        resposta_ia = f"Erro na IA: {str(e)}"
                        
                    url_envio = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
                    requests.post(url_envio, json={"chat_id": chat_id, "text": resposta_ia})
    except:
        pass

if TELEGRAM_TOKEN and modelo_ia:
    processar_mensagens_telegram()

st.title(f"🧠 {NOME_IA.upper()} 5.0 - Ativa")
st.write("Integração com o Telegram rodando.")
time.sleep(2)
st.rerun()
