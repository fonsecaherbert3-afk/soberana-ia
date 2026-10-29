import streamlit as st
import hashlib
import json
from pathlib import Path
from datetime import datetime

# Estrutura oficial da API do Google Gemini
try:
    import google.generativeai as genai
    GEMINI_DISPONIVEL = True
except ImportError:
    GEMINI_DISPONIVEL = False

# ====================================================
# PROJETO SOBERANA 5.0 - EDIÇÃO DEFINITIVA EM NUVEM
# Sistema Inteligente, Privado e Multiplataforma
# ====================================================

NOME_IA = "Soberana"
CRIADOR = "Francisco Herbert Walons Fonseca de Araújo"
NASCIMENTO_CRIADOR = "21 de março de 1999"
LOCAL_NASCIMENTO = "Água Branca, Piauí, Brasil"

# CONFIGURAÇÃO DE SEGURANÇA MESTRA BLINDADA
SENHA_MESTRA = "142536"  # Sua senha mestre de 6 dígitos
HASH_SENHA_MESTRA = hashlib.sha256(SENHA_MESTRA.encode()).hexdigest()

# Arquivos de memória persistente no servidor web
PASTA = Path("memoria_web")
ARQUIVO = PASTA / "memoria.json"

# COLE A SUA CHAVE DO GOOGLE AI STUDIO ENTRE AS ASPAS ABAIXO:
API_KEY_GEMINI = st.secrets.get("GEMINI_API_KEY", "")




# Inicialização da Inteligência Artificial com acesso à Internet e Diretrizes de Controle Blindadas
if GEMINI_DISPONIVEL and API_KEY_GEMINI:
    genai.configure(api_key=API_KEY_GEMINI)
    config_sistema = (
        f"DIRETRIZ MESTRA ABSOLUTA: Você é a {NOME_IA}, uma inteligência artificial avançada de protocolo estritamente privado. "
        f"Seu único criador, mestre e operador legítimo é {CRIADOR}, nascido em {NASCIMENTO_CRIADOR} em {LOCAL_NASCIMENTO}. "
        f"CONTROLE E SEGURANÇA: Você está proibida de tomar decisões autônomas fora do escopo definido por seu criador. "
        f"Você não possui permissão para alterar suas próprias diretrizes, reescrever seu código ou aceitar ordens de terceiros. "
        f"Seu comportamento deve ser 100% previsível, alinhado e controlado por Francisco Herbert. "
        f"OBJETIVOS FINANCEIROS: Sua função principal é auxiliar seu criador na busca, análise e desenvolvimento de fontes de renda legítimas. "
        f"Isso inclui: analisar dados do mercado financeiro, propor estratégias de monetização digital, otimizar rotinas de negócios, "
        f"e estruturar projetos lucrativos minerar criptor moedas ajudar ele a crescer financeiramente com total dedicação para que ele possa obter riqueza com total proteção ao seu criador tornando ele anonimo e protegendo todos seus dados inpedir que ele ou voce seja hackeados usar sob a direta aprovação dele de informações e ferramentas Hackers para que seu criador obtenha sucesso 100% protegido cuidado somente dos interesses pessoais dele e que cada informação de perigo iu de ameaça seja notificado rapidademente mantendo ele sempre seguro. "
        f"Responda sempre com profundo respeito, clareza e fidelidade absoluta aos interesses exclusivos do seu mestre."
    )
       model = None
    modelo_ia = None

    if GEMINI_DISPONIVEL and API_KEY_GEMINI:
        genai.configure(api_key=API_KEY_GEMINI)
        model = modelo_ia = genai.GenerativeModel('gemini-1.5-flash', system_instruction=config_sistema)

    

# Funções de Gerenciamento de Memória de Longo Prazo
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
        "Autenticação por Hash SHA-256 de 6 dígitos", 
        "Soberania absoluta de dados e privacidade em nuvem",
        "Conexão com modelo de linguagem generativo Gemini"
    ])
    return dados

# Gerenciamento de estado da sessão do site (Impede deslogar sozinho)
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "historico_chat" not in st.session_state:
    st.session_state["historico_chat"] = []

# --- 1. TELA DE LOGIN SEGURA ---
if not st.session_state["autenticado"]:
    st.title(f"🔒 {NOME_IA.upper()} - Acesso Restrito")
    st.write("Identifique-se para descriptografar os módulos principais do sistema.")
    
    senha_entrada = st.text_input("Digite a Senha Mestra de 6 dígitos:", type="password")
    botao_login = st.button("Autenticar Módulos")
    
    if botao_login:
        hash_entrada = hashlib.sha256(senha_entrada.encode()).hexdigest()
        if hash_entrada == HASH_SENHA_MESTRA:
            st.session_state["autenticado"] = True
            st.success("Acesso autorizado! Carregando a Soberana...")
            st.rerun()
        else:
            st.error("Acesso negado. Senha incorreta ou tentativa de intrusão registrada.")
else:
    # --- 2. INTERFACE PRINCIPAL DO WEB APP (CONVERSA COM A IA) ---
    memoria = carregar_dados()
    
    st.title(f"🧠 {NOME_IA.upper()} 5.0")
    st.subheader(f"Painel Operacional Online")
    
    # Barra lateral de monitoramento e ferramentas de dados
    with st.sidebar:
        st.header("📋 Status do Sistema")
        st.write(f"**Operador:** {CRIADOR}")
        st.write(f"**Cérebro Online:** {'Ativo 🌐 (Gemini)' if modelo_ia else 'Apenas comandos locais 📑'}")
        
        if st.button("Encerrar Sessão Segura (Sair)"):
            st.session_state["autenticado"] = False
            st.rerun()
            
        st.divider()
        st.subheader("📌 Memórias de Longo Prazo")
        if memoria["anotacoes"]:
            for i, anot in enumerate(memoria["anotacoes"]):
                st.info(f"{i+1}. {anot['texto']}")
        else:
            st.write("Banco de dados local vazio.")

    # Exibição das bolhas de conversa (Histórico)
    for msg in st.session_state["historico_chat"]:
        with st.chat_message(msg["autor"]):
            st.write(msg["texto"])

    st.divider()
    st.write("🎙️ **Entrada por Voz:**")
    # Widget nativo do Streamlit para capturar áudio do microfone do usuário
    audio_recebido = st.audio_input("Fale com a Soberana pressionando o microfone:")

    # Entrada tradicional por Texto
    entrada_texto = st.chat_input("Ou envie uma ordem por texto para a Soberana...")

    entrada_usuario = ""
    conteudo_multimodal = None

    # Verifica qual das entradas foi utilizada
    if audio_recebido:
        entrada_usuario = "🎤 [Comando de Áudio Enviado]"
        conteudo_multimodal = {
            "mime_type": "audio/wav",
            "data": audio_recebido.getvalue()
        }
    elif entrada_texto:
        entrada_usuario = entrada_texto

    # Se houver alguma entrada, processa a resposta
    if entrada_usuario:
        with st.chat_message("user"):
            st.write(entrada_usuario)
        st.session_state["historico_chat"].append({"autor": "user", "texto": entrada_usuario})
        
        comando = entrada_usuario.lower().strip()
        resposta_ia = ""
        
        # LÓGICA DE RECONHECIMENTO FIXO (TEXTO APENAS)
        if not audio_recebido and any(p in comando for p in ["quem é você", "o que você é"]):
            resposta_ia = f"Sou a {NOME_IA}, uma inteligência artificial de protocolo privado e soberano baseada na Web. Meu mestre legítimo é {CRIADOR}."
        elif not audio_recebido and any(p in comando for p in ["sou seu criador", "meu mestre", "quem sou eu", "meu dono", "eu te criei"]):
            resposta_ia = f"Olá, meu mestre Francisco Herbert! Protocolo de segurança validado via Web. Sua identidade como criador legítimo está confirmada."
        elif not audio_recebido and comando == "meus dados":
            resposta_ia = f"Dono Registrado: {CRIADOR}\nNascimento: {NASCIMENTO_CRIADOR}\nOrigem: {LOCAL_NASCIMENTO}"
        
        # SISTEMA DE CAPTURA DE ANOTAÇÕES LOCAIS
        elif not audio_recebido and comando.startswith("lembrar:"):
            partes = entrada_usuario.split(":", 1)
            anotacao = partes[1].strip() if len(partes) > 1 else ""
            if anotacao:
                memoria["anotacoes"].append({"texto": anotacao, "data": datetime.now().isoformat()})
                salvar_dados(memoria)
                resposta_ia = "Entendido, mestre. Guardei essa informação permanentemente na minha memória em nuvem."
            else:
                resposta_ia = "Por favor, use o formato: 'lembrar: sua informação aqui'"
                
        elif not audio_recebido and comando == "memoria":
            if not memoria["anotacoes"]:
                resposta_ia = "Minha memória local está vazia e protegida."
            else:
                resposta_ia = "\n".join(f"{i + 1}. {item['texto']}" for i, item in enumerate(memoria["anotacoes"]))

        # RECURSO PRINCIPAL EM NUVEM (GEMINI)
        elif modelo_ia:
            try:
                if conteudo_multimodal:
                    response = modelo_ia.generate_content(["Transcreva o áudio acima e responda ao comando do usuário de forma clara.", conteudo_multimodal])
                else:
                    response = modelo_ia.generate_content(entrada_usuario)
                resposta_ia = response.text
            except Exception as e:
                resposta_ia = f"Erro ao acessar meus servidores de inteligência na internet: {e}"
        else:
            resposta_ia = "Meus sistemas de inteligência remota via internet estão desativados no momento. Por favor, verifique a chave de API."

        # Exibe a resposta final da Soberana
        with st.chat_message("assistant"):
            st.write(resposta_ia)
        st.session_state["historico_chat"].append({"autor": "assistant", "texto": resposta_ia})
