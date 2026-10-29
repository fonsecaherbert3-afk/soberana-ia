import streamlit as st
import requests
import time

# ====================================================
# PROJETO SOBERANA 5.0 - CONEXÃO HTTP OFICIAL E CORRETA
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
    """Conversa direto com a API do Gemini via HTTP estruturado"""
    # Usando o endpoint oficial padrão do gemini-1.5-flash
    url = f"https://googleapis.com{API_KEY_GEMINI}"
    headers = {"Content-Type": "application/json"}
    
    # Estrutura JSON exata exigida pela API do Google
    payload = {
        "contents": [{
            "parts": [{"text": texto_mensagem}]
        }],
        "systemInstruction": {
            "parts": [{"text": DIRETRIZ_SISTEMA}]
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            resultado = response.json()
            # Extrai o texto da resposta corretamente do JSON do Google
            return resultado["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"Erro na API Google (Código {response.status_code}). Verifique se a sua API Key nos Secrets está correta ou se expirou."
    except Exception as e:
        return f"Erro de conexão com o cérebro da IA: {str(e)}"

def processar_mensagens_telegram():
    if not TELEGRAM_TOKEN or not API_KEY_GEMINI:
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
                    
                    # Comando de teste rápido local para verificar se o Telegram está ativo
                    if texto_usuario.lower().strip() in ["/start", "oi", "olá"]:
                        resposta_final = f"Olá, meu mestre {CRIADOR}! Estou ativa no Telegram e pronta para operar. Processando conexão com o Gemini..."
                        url_envio = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
                        requests.post(url_envio, json={"chat_id": chat_id, "text": resposta_final})
                    
                    # Processa perguntas normais no Gemini
                    resposta_final = gerar_resposta_gemini(texto_usuario)
                        
                    url_envio = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
                    requests.post(url_envio, json={"chat_id": chat_id, "text": resposta_final})
    except:
        pass

processar_mensagens_telegram()

st.title(f"🧠 {NOME_IA.upper()} 5.0 - NUVEM PRIVADA")
st.success("O motor de escuta direta do Telegram está ativado e operando de forma contínua.")
st.write("Abra o chat do seu robô no Telegram e envie uma mensagem de teste.")

time.sleep(2)
st.rerun()
