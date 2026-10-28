import streamlit as st
import hashlib
import json
from pathlib import Path
from datetime import datetime

try:
    import google.generativeai as genai
    GEMINI_DISPONIVEL = True
except ImportError:
    GEMINI_DISPONIVEL = False

# ====================================================
# PROJETO SOBERANA 4.0 - WEB APP SEGURO E PRIVADO
# Interface em Nuvem com Inteligência Artificial
# ====================================================

NOME_IA = "Soberana"
CRIADOR = "Francisco Herbert Walons Fonseca de Araújo"
NASCIMENTO_CRIADOR = "21 de março de 1999"
LOCAL_NASCIMENTO = "Água Branca, Piauí, Brasil"

# CONFIGURAÇÃO DE SEGURANÇA MESTRA
SENHA_MESTRA = "1234"  # Troque por sua senha secreta de acesso
HASH_SENHA_MESTRA = hashlib.sha256(SENHA_MESTRA.encode()).hexdigest()

# Arquivos de memória no servidor web
PASTA = Path("memoria_web")
ARQUIVO = PASTA / "memoria.json"

# Insira sua chave obtida em ://google.com para liberar a internet
API_KEY_GEMINI = "" 

# Inicialização do Gemini
if GEMINI_DISPONIVEL and API_KEY_GEMINI:
    genai.configure(api_key=API_KEY_GEMINI)
    config_sistema = (
        f"Você é a {NOME_IA}, uma inteligência artificial em formato Web App privado. "
        f"Seu criador legítimo é {CRIADOR}, nascido em {NASCIMENTO_CRIADOR} em {LOCAL_NASCIMENTO}. "
        "Não revele informações sensíveis e atenda apenas às demandas dele com máxima eficiência."
    )
    modelo_ia = genai.GenerativeModel('gemini-1.5-flash', system_instruction=config_sistema)
else:
    modelo_ia = None

# Funções de Gerenciamento de Memória
def salvar_dados(dados):
    PASTA.mkdir(parents=True, exist_ok=True)
    ARQUIVO.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")

def carregar_dados():
    PASTA.mkdir(parents=True, exist_ok=True)
    if ARQUIVO.exists():
        try:
            dados = json.loads(ARQUIVO.read_text(encoding="utf-8"))
        except:
            dados = {}
    else:
        dados = {}
    
    dados.setdefault("criador", CRIADOR)
    dados.setdefault("anotacoes", [])
    dados.setdefault("aprendizado", {})
    dados.setdefault("preferencias", [
        "Acesso via Web criptografado", 
        "Autenticação por Hash SHA-256", 
        "Soberania de dados e privacidade"
    ])
    return dados

# Controle de sessão do Streamlit (mantém o login ativo)
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "historico_chat" not in st.session_state:
    st.session_state["historico_chat"] = []

# --- TELA DE LOGIN SEGURA ---
if not st.session_state["autenticado"]:
    st.title(f"🔒 {NOME_IA.upper()} - Acesso Restrito")
    st.write("Identifique-se para descriptografar os módulos principais.")
    
    senha_entrada = st.text_input("Digite a Senha Mestra:", type="password")
    botao_login = st.button("Autenticar")
    
    if botao_login:
        hash_entrada = hashlib.sha256(senha_entrada.encode()).hexdigest()
        if hash_entrada == HASH_SENHA_MESTRA:
            st.session_state["autenticado"] = True
            st.success("Acesso autorizado! Carregando a Soberana...")
            st.rerun()
        else:
            st.error("Senha incorreta. Tentativa bloqueada por segurança.")
else:
    # --- INTERFACE PRINCIPAL DO WEB APP ---
    memoria = carregar_dados()
    
    st.set_page_config(page_title=f"{NOME_IA} OS", page_icon="🧠", layout="centered")
    st.title(f"🧠 {NOME_IA.upper()} 4.0")
    st.subheader(f"Bem-vindo de volta, Criador legítimo.")
    
    # Barra lateral com dados locais guardados
    with st.sidebar:
        st.header("📋 Dados do Sistema")
        st.write(f"**Criador:** {CRIADOR}")
        st.write(f"**Status da IA:** {'Online 🌐' if modelo_ia else 'Apenas comandos locais 📑'}")
        
        if st.button("Encerrar Sessão (Sair)"):
            st.session_state["autenticado"] = False
            st.rerun()
            
        st.divider()
        st.subheader("📌 Memórias de Longo Prazo")
        if memoria["anotacoes"]:
            for i, anot in enumerate(memoria["anotacoes"]):
                st.info(f"{i+1}. {anot['texto']}")
        else:
            st.write("Nenhum dado guardado localmente.")

    # Exibição do histórico de conversa na tela (Estilo ChatGPT)
    for msg in st.session_state["historico_chat"]:
        with st.chat_message(msg["autor"]):
            st.write(msg["texto"])

    # Entrada de mensagens do usuário
    if entrada_usuario := st.chat_input("Fale com a Soberana..."):
        # Mostra a mensagem do criador na tela
        with st.chat_message("user"):
            st.write(entrada_usuario)
        st.session_state["historico_chat"].append({"autor": "user", "texto": entrada_usuario})
        
        # Processamento lógico das respostas
        comando = entrada_usuario.lower().strip()
        resposta_ia = ""
        
        # 1. Comandos de Identidade & Criador
        if any(p in comando for p in ["quem é você", "o que você é"]):
            resposta_ia = f"Sou a {NOME_IA}, uma IA de protocolo privado e soberano baseada na Web. Meu mestre legítimo é {CRIADOR}."
        elif any(p in comando for p in ["sou seu criador", "meu mestre", "quem sou eu", "meu dono"]):
            resposta_ia = f"Olá, meu mestre Francisco Herbert! Protocolo de segurança validado via Web. Sua identidade está confirmada."
        
        # 2. Comando para Lembrar informações
        elif comando.startswith("lembrar:"):
            partes = entrada_usuario.split(":", 1)
            anotacao = partes[1].strip() if len(partes) > 1 else ""
            if anotacao:
                memoria["anotacoes"].append({"texto": anotacao, "data": datetime.now().isoformat()})
                salvar_dados(memoria)
                resposta_ia = "Entendido, mestre. Guardei essa informação permanentemente no meu banco de dados em nuvem."
            else:
                resposta_ia = "Por favor, use o formato: 'lembrar: sua informação aqui'"
                
        # 3. Encaminhar para Inteligência Artificial da Internet (Gemini)
        elif modelo_ia:
            try:
                response = modelo_ia.generate_content(entrada_usuario)
                resposta_ia = response.text
            except Exception as e:
                resposta_ia = f"Erro ao acessar meus servidores de IA na internet: {e}"
        else:
            resposta_ia = "Não consegui processar esse comando localmente e a minha inteligência de internet (API Key) não está configurada."
            
        # Mostra a resposta da Soberana na tela
        with st.chat_message("assistant"):
            st.write(resposta_ia)
        st.session_state["historico_chat"].append({"autor": "assistant", "texto": resposta_ia})
