if TOKEN:
    try:
        # Força o Telegram a esquecer conexões antigas travadas
        requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook", timeout=3)
        
        url_updates = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
        response = requests.get(url_updates, params={"offset": st.session_state["last_id"] + 1, "timeout": 1}, timeout=5)
        
        if response.status_code == 200:
            for update in response.json().get("result", []):
                st.session_state["last_id"] = update["update_id"]
                if "message" in update and "text" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    msg_txt = update["message"]["text"]
                    
                    st.info(f"📥 Recebido: '{msg_txt}'")
                    resposta = inteligenca_gemini(msg_txt)
                    
                    url_envio = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                    requests.post(url_envio, json={"chat_id": chat_id, "text": resposta}, timeout=5)
                    st.success("📤 Respondido com sucesso!")
        else:
            st.error(f"Aguardando sinal válido do servidor. Código: {response.status_code}")
    except Exception as e:
        st.error(f"Falha de pareamento: {str(e)}")
