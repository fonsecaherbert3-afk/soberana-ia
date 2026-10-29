import streamlit as st
import requests
import time

# ====================================================
# PROJETO SOBERANA 5.0 - SISTEMA AUTO-EXECUTÁVEL TELEGRAM
# ====================================================

NOME_IA = "Soberana"
CRIADOR = "Francisco Herbert Walons Fonseca de Araújo"

API_KEY_GEMINI = st.secrets.get("GEMINI_API_KEY", "")
TELEGRAM_TOKEN = st.secrets.get("TELEGRAM_TOKEN", "")

DIRETRIZ_SISTEMA = (
    f"DIRETRIZ MESTRA ABSOLUTA: Você é a {NOME_IA}. "
    f"Seu único criador, mestre e operador legítimo é {CRIADOR}. "
    f"Responda sempre com profundo respeito, clareza e fidelidade absoluta aos interesses dele."
)

def gerar_resposta_gemini(texto_mensagem):
    """Conversa com a API do Gemini via requisição HTTP estável"""
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
        return f"Erro na API Google (Código {response.status_code})"
    except Exception as e:
        return f"Erro de conexão: {str(e)}"

def enviar_mensagem_telegram(chat_id, texto):
    """Envia o texto para o chat do Telegram correspondente"""
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": texto}, timeout=5)
    except:
        pass

def processar_mensagens_telegram():
    """Busca novas mensagens recebidas e responde automaticamente"""
    if not TELEGRAM_TOKEN:
        return
        
    if "last_update_id" not in st.session_state:
        st.session_state["last_update_id"] = 0
        
    url_updates = f"https://telegram.org{TELEGRAM_TOKEN}/getUpdates"
    try:
        response = requests.get(url_updates, params={"offset": st.session_state["last_update_id"] + 1, "timeout": 1}, timeout=3)
        if response.status_code == 200:
            updates = response.json().get("result", [])
            for update in updates:
                st.session_state["last_update_id"] = update["update_id"]
                if "message" in update and "text" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    texto_usuario = update["message"]["text"]
                    
                    # Comando básico local para verificação imediata
                    if texto_usuario.lower().strip() in ["/start", "oi", "olá"]:
                        enviar_mensagem_telegram(chat_id, f"Olá, meu mestre {CRIADOR}! Conexão com a Soberana estabelecida. Processando resposta...")
                    
                    # Processa no Gemini
                    resposta_final = gerar_resposta_gemini(texto_usuario)
                    enviar_mensagem_telegram(chat_id, resposta_final)
    except:
        pass

# Remove qualquer configuração residual de webhook para liberar o canal
if "webhook_removido" not in st.session_state:
    try:
        requests.get(f"https://telegram.org{TELEGRAM_TOKEN}/deleteWebhook")
        st.session_state["webhook_removido"] = True
    except:
        pass

# Executa o sistema de checagem contínua
processar_mensagens_telegram()

# Interface do site
st.title(f"🧠 {NOME_IA.upper()} 5.0 - MONITORAMENTO")
st.success("O motor interno está buscando e processando as mensagens do seu Telegram automaticamente.")
st.write("Abra o aplicativo do seu Telegram e envie uma mensagem para testar.")

# Atualiza a página continuamente para buscar novos chats
time.sleep(2)
st.rerun()
