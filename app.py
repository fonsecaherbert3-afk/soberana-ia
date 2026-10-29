import streamlit as st
import requests
import time

# ====================================================
# PROJETO SOBERANA 5.0 - MOTOR DE CONEXÃO DIRETA HTTP
# ====================================================

NOME_IA = "Soberana"
CRIADOR = "Francisco Herbert Walons Fonseca de Araújo"

# Puxando as credenciais salvas nos Secrets do Streamlit
API_KEY_GEMINI = st.secrets.get("GEMINI_API_KEY", "")
TELEGRAM_TOKEN = st.secrets.get("TELEGRAM_TOKEN", "")

# Configuração fixa e definitiva do sistema de IA
DIRETRIZ_SISTEMA = (
    f"DIRETRIZ MESTRA ABSOLUTA: Você é a {NOME_IA}. "
    f"Seu único criador, mestre e operador legítimo é {CRIADOR}. "
    f"Responda sempre com profundo respeito, clareza e fidelidade absoluta aos interesses dele."
)

def gerar_resposta_gemini(texto_mensagem):
    """Conversa direto com os servidores da Google sem usar a biblioteca genai"""
    # Usando o modelo estável padrão do Google Gemini
    url = f"https://googleapis.com{API_KEY_GEMINI}"
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "contents": [{"parts": [{"text": texto_mensagem}]}],
        "systemInstruction": {"parts": [{"text": DIRETRIZ_SISTEMA}]}
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            resultado = response.json()
            return resultado["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"Erro na API Google (Código {response.status_code}): {response.text}"
    except Exception as e:
        return f"Erro de conexão com o cérebro da IA: {str(e)}"

def processar_mensagens_telegram():
    """Gerencia e responde as mensagens recebidas dentro do seu Telegram"""
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
                    
                    # Gera a resposta usando a requisição direta criada acima
                    resposta_final = gerar_resposta_gemini(texto_usuario)
                        
                    # Envia de volta ao chat do Telegram do Francisco
                    url_envio = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
                    requests.post(url_envio, json={"chat_id": chat_id, "text": resposta_final})
    except:
        pass

# Ativa o ouvidor de mensagens do Telegram
processar_mensagens_telegram()

# Relação básica do site do Streamlit
st.title(f"🧠 {NOME_IA.upper()} 5.0 - NUVEM PRIVADA")
st.success("O motor de escuta direta do Telegram está ativado e operando de forma contínua.")
st.write("Abra o chat do seu robô no Telegram e envie uma mensagem de teste.")

# Mantém a página atualizando rápido para verificar o chat do Telegram em tempo real
time.sleep(2)
st.rerun()
