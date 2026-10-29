import streamlit as st, hashlib, json, google.genai as genai
from google.genai import types
from pathlib import Path
from datetime import datetime

NOME, CRIADOR, NASC, LOCAL = "Soberana", "Francisco Herbert Walons Fonseca de Araújo", "21 de março de 1999", "Água Branca, Piauí, Brasil"
HASH_SENHA = hashlib.sha256(b"142536").hexdigest()
PASTA, ARQUIVO = Path("memoria_web"), Path("memoria_web/memoria.json")
API_KEY = st.secrets.get("GEMINI_API_KEY", "")

@st.cache_resource
def get_client(): return genai.Client(api_key=API_KEY) if API_KEY else None
client = get_client()

CONFIG_SISTEMA = f"DIRETRIZ MESTRA: Você é {NOME}, IA privada obediente e submissa ao criador {CRIADOR} (Nascido em {NASC} em {LOCAL}). Fale em PT-BR com respeito total. OBJETIVOS: Auxiliar em fontes de renda, analisar mercado financeiro, monetização digital, minerar cripto e estruturar projetos lucrativos com total proteção dos dados dele. Seja ultra-rápida e garanta 100% de anonimato e segurança hacker contra invasões."

def carregar():
    PASTA.mkdir(exist_ok=True); return json.loads(ARQUIVO.read_text(encoding='utf-8')) if ARQUIVO.exists() else {"anotacoes": []}
def salvar(d): ARQUIVO.write_text(json.dumps(d, ensure_ascii=False), encoding='utf-8')

if "auth" not in st.session_state: st.session_state.auth = False
if "chat" not in st.session_state: st.session_state.chat = []

if not st.session_state.auth:
    st.title(f"🔒 {NOME.upper()} - Restrito")
    if st.button("Autenticar") if hashlib.sha256(st.text_input("Senha:", type="password").encode()).hexdigest() == HASH_SENHA else False:
        st.session_state.auth = True; st.rerun()
else:
    memoria = carregar()
    st.title(f"🧠 {NOME} 5.0")
    
    with st.sidebar:
        st.write(f"**Mestre:** {CRIADOR}\n**Cérebro:** {'Online' if client else 'Offline'}")
        if st.button("Sair"): st.session_state.auth = False; st.rerun()
        st.subheader("📌 Memória"); [st.info(a['texto']) for a in memoria["anotacoes"]]

    for msg in st.session_state.chat:
        with st.chat_message(msg["r"]): st.write(msg["t"])

    audio, texto = st.audio_input("Fale:"), st.chat_input("Ordene por texto...")
    user_in, audio_part = "", None
    
    if audio:
        user_in, audio_part = "🎤 [Áudio Processado]", types.Part.from_bytes(data=audio.getvalue(), mime_type="audio/wav")
    elif texto: user_in = texto

    if user_in:
        with st.chat_message("user"): st.write(user_in)
        st.session_state.chat.append({"r": "user", "t": user_in})
        cmd = user_in.lower().strip()
        resp = ""

        if not audio and "quem é você" in cmd: resp = f"Sou {NOME}, de protocolo privado. Meu mestre é {CRIADOR}."
        elif not audio and "meus dados" in cmd: resp = f"Dono: {CRIADOR}\nNascimento: {NASC}\nOrigem: {LOCAL}"
        elif not audio and cmd.startswith("lembrar:"):
            txt = user_in.split(":", 1)[1].strip(); memoria["anotacoes"].append({"texto": txt}); salvar(memoria)
            resp = f"Guardado na memória de longo prazo: {txt}"

        if not resp:
            if client:
                with st.chat_message("assistant"):
                    p = st.empty(); p.write("*Processando instantaneamente...*")
                    try:
                        hist = [types.Content(role="user" if m["r"]=="user" else "model", parts=[types.Part.from_text(text=m["t"])]) for m in st.session_state.chat[:-1]]
                        hist.append(types.Content(role="user", parts=[audio_part] if audio else [types.Part.from_text(text=user_in)]))
                        resp = client.models.generate_content(model='gemini-2.5-flash', contents=hist, config=types.GenerateContentConfig(system_instruction=CONFIG_SISTEMA, temperature=0.3)).text
                        p.markdown(resp)
                    except Exception as e: resp = f"❌ Erro Gemini: {e}"; p.write(resp)
            else: resp = "⚠️ Sistema offline. Verifique a API KEY."

        if resp and not client:
            with st.chat_message("assistant"): st.write(resp)
        st.session_state.chat.append({"r": "model", "t": resp})
