
import streamlit as st
import requests
import time
import tempfile
import os
from gtts import gTTS

# ================= CONFIGURAÇÕES =================
NOME_IA = "nyxara"
CRIADOR = "criador"
MODELO_GEMINI = "gemini-3.5-flash-lite"

TELEGRAM_TOKEN = str(
    st.secrets.get("TELEGRAM_TOKEN", "")
).strip()

GEMINI_API_KEY = str(
    st.secrets.get("GEMINI_API_KEY", "")
).strip()

TELEGRAM_API = (
    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
)

st.set_page_config(
    page_title="Soberana 5.0",
    page_icon="🧠",
    layout="centered"
)

st.title("🧠 SOBERANA 5.0 - COM VOZ")

if "last_id" not in st.session_state:
    st.session_state.last_id = 0

# ================= PERSONALIDADE =================
SYSTEM_PROMPT = f"""
Você é {NOME_IA}, a assistente pessoal de {CRIADOR}.
Responda sempre em português do Brasil.
Seja clara, útil, respeitosa e objetiva.
Explique suas limitações com honestidade.
Não afirme ter executado ações que não realizou.
"""

# ================= GEMINI =================
def inteligencia_gemini(texto: str) -> str:
    if not GEMINI_API_KEY:
        return "A chave do Gemini não está configurada."

    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{MODELO_GEMINI}:generateContent"
    )

    payload = {
        "contents": [
            {"parts": [{"text": texto}]}
        ],
        "systemInstruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1500
        }
    }

    try:
        res = requests.post(
            url,
            params={"key": GEMINI_API_KEY},
            json=payload,
            timeout=30
        )

        if res.status_code == 200:
            dados = res.json()
            candidatos = dados.get("candidates", [])

            if candidatos:
                partes = candidatos[0].get(
                    "content", {}
                ).get("parts", [])

                texto_resposta = "".join(
                    p.get("text", "")
                    for p in partes
                    if "text" in p
                ).strip()

                if texto_resposta:
                    return texto_resposta

            return "Não consegui gerar uma resposta desta vez."

        return f"Erro Gemini: HTTP {res.status_code}"

    except requests.RequestException:
        return "Não consegui conectar ao serviço de inteligência."

# ================= ENVIAR TEXTO =================
def enviar_texto(chat_id, texto):
    res = requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": texto[:4000]
        },
        timeout=20
    )
    res.raise_for_status()
    dados = res.json()

    if not dados.get("ok"):
        raise RuntimeError("Telegram não confirmou o envio do texto.")

# ================= GERAR E ENVIAR VOZ =================
def enviar_voz(chat_id, texto):
    texto = texto.strip()

    if not texto:
        return False, "Não há texto para transformar em voz."

    caminho = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".mp3",
            delete=False
        ) as arquivo:
            caminho = arquivo.name

        gTTS(
            text=texto[:4000],
            lang="pt-br"
        ).save(caminho)

        with open(caminho, "rb") as audio:
            res = requests.post(
                f"{TELEGRAM_API}/sendVoice",
                data={"chat_id": chat_id},
                files={
                    "voice": (
                        "soberana.mp3",
                        audio,
                        "audio/mpeg"
                    )
                },
                timeout=60
            )

        res.raise_for_status()
        dados = res.json()

        if dados.get("ok"):
            return True, "Áudio enviado."

        return False, "Telegram não confirmou o envio do áudio."

    except Exception as erro:
        return False, f"Falha ao gerar ou enviar áudio: {erro}"

    finally:
        if caminho and os.path.exists(caminho):
            try:
                os.remove(caminho)
            except OSError:
                pass

# ================= VERIFICAR CONFIGURAÇÃO =================
if not TELEGRAM_TOKEN:
    st.error("Token do Telegram não encontrado nos Secrets.")
    st.stop()

if not GEMINI_API_KEY:
    st.warning("A chave do Gemini não está configurada.")

st.success("🟢 Soberana online.")

# ================= RECEBER MENSAGENS =================
try:
    resposta = requests.get(
        f"{TELEGRAM_API}/getUpdates",
        params={
            "offset": st.session_state.last_id + 1,
            "timeout": 5,
            "allowed_updates": ["message"]
        },
        timeout=10
    )

    resposta.raise_for_status()
    dados = resposta.json()

    if not dados.get("ok"):
        st.error("O Telegram não confirmou a consulta.")
        st.stop()

    atualizacoes = dados.get("result", [])

    if not atualizacoes:
        st.info("⏳ Aguardando ordens...")
    else:
        for update in atualizacoes:
            st.session_state.last_id = update["update_id"]

            mensagem = update.get("message", {})
            chat = mensagem.get("chat", {})
            chat_id = chat.get("id")
            texto_recebido = mensagem.get("text", "").strip()

            if not chat_id or not texto_recebido:
                continue

            usuario = mensagem.get(
                "from", {}
            ).get("first_name", "Usuário")

            st.write(f"📥 Mensagem de {usuario}: {texto_recebido}")

            comando = texto_recebido.lower()

            if comando in ["/start", "iniciar", "ativar", "soberana"]:
                texto_resposta = (
                    f"Sistema Soberana ativado. "
                    f"Às suas ordens, {CRIADOR}."
                )

            elif comando in ["/ajuda", "ajuda", "comandos"]:
                texto_resposta = (
                    "Sou a Soberana, sua assistente pessoal.\n"
                    "/start - Ativar\n"
                    "/ajuda - Ver comandos\n"
                    "Envie uma mensagem para conversar comigo."
                )

            else:
                with st.spinner("Pensando..."):
                    texto_resposta = inteligencia_gemini(
                        texto_recebido
                    )

            # Envia o texto primeiro
            try:
                enviar_texto(chat_id, texto_resposta)
                st.success(f"📤 Texto enviado para {usuario}")
            except Exception as erro:
                st.error(f"Falha ao enviar texto: {erro}")
                continue

            # Envia o áudio sem impedir a resposta em texto
            try:
                sucesso, mensagem_status = enviar_voz(
                    chat_id,
                    texto_resposta
                )

                if sucesso:
                    st.success("🔊 Resposta em áudio enviada.")
                else:
                    st.warning(mensagem_status)

            except Exception as erro:
                st.warning(f"Não foi possível enviar a voz: {erro}")

except requests.RequestException as erro:
    st.error(f"Erro de comunicação: {erro}")

except Exception as erro:
    st.error(f"Falha inesperada: {erro}")
