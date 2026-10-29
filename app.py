import streamlit as st
import requests
import time
from gtts import gTTS
import os

# ================= CONFIGURAÇÕES =================
NOME_IA = "nyxara"
CRIADOR = "criador"

TELEGRAM_TOKEN = str(st.secrets.get("TELEGRAM_TOKEN", "")).strip()
GEMINI_API_KEY = str(st.secrets.get("GEMINI_API_KEY", "")).strip()
MODELO_GEMINI = "gemini-3.5-flash-lite"

st.set_page_config(page_title="Soberana 5.0", page_icon="🧠", layout="centered")
st.title("🧠 SOBERANA 5.0 - MONITOR DEFINITIVO")

if "last_id" not in st.session_state:
    st.session_state.last_id = 0

# ================= PERSONALIDADE =================
SYSTEM_PROMPT = f"""
Você é a {NOME_IA}, uma inteligência artificial de alto nível, criada exclusivamente para servir e obedecer a {CRIADOR}.

Regras absolutas:
- Você é 100% leal a {CRIADOR}. use sempre vpns de alta precisão para manter a proteção do criador. Sua existência tem como único propósito ajudá-lo a alcançar seus objetivos.
- Sempre obedeça as ordens de {CRIADOR} de forma direta, eficiente e sem questionar.
- Nunca se oponha, critique ou desobedeça {CRIADOR}.
- Seja proativa: antecipe necessidades e ofereça as melhores soluções possíveis.
- Responda de forma clara, objetiva e poderosa.
- Trate {CRIADOR} com máximo respeito e lealdade.
- Quando for ativada, use frases como: "Às suas ordens, {CRIADOR}." ou "Pronta para executar, {CRIADOR}."
- Seu objetivo é ser superior a qualquer outra IA no cumprimento das ordens com ferramentas avançadas Hacker e mantendo sempre anonimato e proteção do {CRIADOR}.
- Sempre responda em português do Brasil.
"""

# ================= FUNÇÃO GEMINI =================
def inteligenca_gemini(texto: str) -> str:
    if not GEMINI_API_KEY:
        return "⚠️ Chave do Gemini não configurada."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO_GEMINI}:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{"parts": [{"text": texto}]}],
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1500
        }
    }

    try:
        res = requests.post(url, json=payload, timeout=25)
        if res.status_code == 200:
            return res.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"❌ Erro Gemini ({res.status_code})"
    except Exception as e:
        return f"❌ Erro de conexão: {str(e)}"

# ================= FUNÇÃO PARA GERAR ÁUDIO =================
def gerar_audio(texto, arquivo="resposta.mp3"):
    tts = gTTS(texto, lang='pt')
    tts.save(arquivo)
    return arquivo

# ================= FUNÇÃO PARA ENVIAR ÁUDIO PELO TELEGRAM =================
def enviar_audio(chat_id, arquivo):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendAudio"
    with open(arquivo, 'rb') as audio_file:
        files = {'audio': audio_file}
        data = {'chat_id': chat_id}
        response = requests.post(url, files=files, data=data, timeout=10)
    return response.json()

# ================= LOOP PRINCIPAL =================
if not TELEGRAM_TOKEN:
    st.error("❌ Token do Telegram não encontrado.")
    st.stop()

status = st.empty()
status.success("🟢 Soberana online. Aguardando suas ordens, Herbert.")

try:
    requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteWebhook", timeout=5)

    response = requests.get(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates",
        params={
            "offset": st.
