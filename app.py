import streamlit as st
import requests
import time

# ================= CONFIGURAÇÕES =================
NOME_IA = "nyxara"
CRIADOR = "criador"

TELEGRAM_TOKEN = str(st.secrets.get("TELEGRAM_TOKEN", "")).strip()
GEMINI_API_KEY = str(st.secrets.get("GEMINI_API_KEY", "")).strip()
MODELO_GEMINI = "gemini-3.8-flash"

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
            "offset": st.session_state.last_id + 1,
            "timeout": 20,
            "allowed_updates": ["message"]
        },
        timeout=25
    )

    if response.status_code == 200:
        updates = response.json().get("result", [])
        
        if not updates:
            status.info("⏳ Aguardando ordens...")
        else:
            for update in updates:
                st.session_state.last_id = update["update_id"]

                if "message" in update and "text" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    msg_txt = update["message"]["text"].strip()
                    user = update["message"].get("from", {}).get("first_name", "Usuário")

                    st.info(f"📥 **{user}**: {msg_txt}")

                    if msg_txt.lower() in ["/start", "iniciar", "ativar", "soberana"]:
                        resposta = f"Sistema Soberana ativado.\nÀs suas ordens, {CRIADOR}."
                    elif msg_txt.lower() in ["/ajuda", "ajuda", "comandos"]:
                        resposta = (
                            "Estou pronta para executar qualquer ordem sua.\n\n"
                            "Comandos:\n"
                            "/start - Ativa a Soberana\n"
                            "/ajuda - Mostra esta mensagem\n\n"
                            "Pode me enviar qualquer ordem diretamente."
                        )
                    else:
                        with st.spinner("Executando ordem..."):
                            resposta = inteligenca_gemini(msg_txt)

                    requests.post(
                        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                        json={"chat_id": chat_id, "text": resposta},
                        timeout=10
                    )
                    st.success(f"📤 Ordem executada para {user}")
    else:
        st.error(f"❌ Erro Telegram: {response.status_code}")

except Exception as e:
    st.error(f"Falha: {str(e)}")

time.sleep(1)
st.rerun()
