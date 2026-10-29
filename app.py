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

# ================= FUNÇÃO PARA GERAR ÁUDIO ==================
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
                    
                    # Gerar áudio
                    arquivo_audio = gerar_audio(resposta)
                    
                    # Enviar áudio
                    enviar_audio(chat_id, arquivo_audio)
                    
                    st.success(f"📤 Ordem executada para {user}")
    else:
        st.error(f"❌ Erro Telegram: {response.status_code}")

except Exception as e:
    st.error(f"Falha: {str(e)}")

time.sleep(1)
st.rerun()
