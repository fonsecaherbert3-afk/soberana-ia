import streamlit as st
import hashlib
import json
import requests
import time
from pathlib import Path
from datetime import datetime

# Estrutura oficial da API do Google Gemini
try:
    import google.generativeai as genai
    GEMINI_DISPONIVEL = True
except ImportError:
    GEMINI_DISPONIVEL = False

# ====================================================
# PROJETO SOBERANA 5.0 - EDIÇÃO INTEGRAÇÃO TELEGRAM
# ====================================================

NOME_IA = "Soberana"
CRIADOR = "Francisco Herbert Walons Fonseca de Araújo"
NASCIMENTO_CRIADOR = "21 de março de 1999"
LOCAL_NASCIMENTO = "Água Branca, Piauí, Brasil"

# CONFIGURAÇÕES DE SEGURANÇA MESTRA
SENHA_MESTRA = "142536"
HASH_SENHA_MESTRA = hashlib.sha256(SENHA_MESTRA.encode()).hexdigest()

PASTA = Path("memoria_web")
ARQUIVO = PASTA / "memoria.json"

# Puxando as credenciais salvas nos Secrets
API_KEY_GEMINI = st.secrets.get("GEMINI_API_KEY", "")
TELEGRAM_TOKEN = st.secrets.get("TELEGRAM_TOKEN", "")
NOME_MODELO = st.secrets.get("NOME_MODELO", "gemini-3.8-flash")

# Inicialização da Inteligência Artificial
model = modelo_ia = None
if GEMINI_DISPONIVEL and API_KEY_GEMINI:
    genai.configure(api_key=API_KEY_GEMINI)
    config_sistema = (
        f"DIRETRIZ MESTRA ABSOLUTA: Você é a {NOME_IA}, uma inteligência artificial avançada de protocolo estritamente privado. "
        f"Seu único criador, mestre e operador legítimo é {CRIADOR}. "
        f"Responda sempre com profundo respeito, clareza e fidelidade absoluta aos interesses exclusivos do seu mestre."
    )
    model = modelo_ia = genai.GenerativeModel(NOME_MODELO, system_instruction=config_sistema)

# --- ROTINA AUXILIAR DO TELEGRAM ---
def processar_mensagens_telegram():
    if not TELEGRAM_TOKEN or not modelo_ia:
        return
    
    # Gerencia o ID da última mensagem para não responder repetido
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
                    
                    # Processa o texto com o cérebro da Soberana
                    try:
                        resposta_ia = modelo_ia.generate_content(texto_usuario).text
                    except Exception as e:
                        resposta_ia = f"Erro ao processar: {str(e)}"
                        
                    # Envia a resposta de volta para o seu Telegram
                    url_envio = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
                    requests.post(url_envio, json={"chat_id": chat_id, "text": resposta_ia})
    except:
        pass

# Executa o ouvidor do Telegram em segundo plano no app
if TELEGRAM_TOKEN and modelo_ia:
    processar_mensagens_telegram()

# --- INTERFACE WEB COMPLEMENTAR (STREAMLIT) ---
st.title(f"🧠 {NOME_IA.upper()} 5.0 - Ativa")
st.write("O motor de integração com o Telegram está rodando em segundo plano de forma contínua.")
st.info("Acesse o seu aplicativo do Telegram, procure pelo seu bot e envie um 'Olá' para começar a conversar!")

# Força atualização automática da página para checar novas mensagens do bot
time.sleep(3)
st.rerun()
