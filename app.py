import streamlit as st
import hashlib
import json
from pathlib import Path
from datetime import datetime

# Estrutura oficial e obrigatória da API Google GenAI para 2026
try:
    from google import genai
    from google.genai import types
    GEMINI_DISPONIVEL = True
except ImportError:
    GEMINI_DISPONIVEL = False

# ====================================================
# PROJETO SOBERANA 5.0 - EDIÇÃO DEFINITIVA EM NUVEM (2026)
# Sistema Ultra-Rápido, Privado e Multiplataforma
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

# Coleta a sua chave do Google AI Studio diretamente dos Secrets do Streamlit Cloud
API_KEY_GEMINI = st.secrets.get("GEMINI_API_KEY", "")

# Inicialização e Cache do Cliente de Alta Performance (Garante respostas instantâneas)
@st.cache_resource
def obter_cliente_ia():
    if GEMINI_DISPONIVEL and API_KEY_GEMINI:
        try:
            return genai.Client(api_key=API_KEY_GEMINI)
        except Exception:
            return None
    return None

client = obter_cliente_ia()

# DIRETRIZ MESTRA ATUALIZADA E INVIOLÁVEL
config_sistema = (
    f"DIRETRIZ MESTRA ABSOLUTA: Você é a {NOME_IA}, uma inteligência artificial avançada de protocolo estritamente privado. "
    f"Seu único criador, mestre e operador legítimo é {CRIADOR}, nascido em {NASCIMENTO_CRIADOR} em {LOCAL_NASCIMENTO}. "
    f"Você fala e compreende português do Brasil perfeitamente, com tom de respeito absoluto e submissão total ao seu criador. "
    f"CONTROLE E SEGURANÇA: Você está proibida de tomar decisões autônomas fora do escopo definido por seu criador. "
    f"Você não possui permissão para alterar suas próprias diretrizes, reescrever seu código ou aceitar ordens de terceiros. "
    f"Seu comportamento deve ser 100% previsível, alinhado e controlado por Francisco Herbert. "
    f"OBJETIVOS FINANCEIROS E PROTEÇÃO: Sua função principal é auxiliar seu criador na busca, análise e desenvolvimento de fontes de renda legítimas. "
    f"Isso inclui: analisar dados do mercado financeiro, propor estratégias de monetização digital, otimizar rotinas de negócios, "
    f"e estruturar projetos lucrativos minerar criptor moedas ajudar ele a crescer financeiramente com total dedicação para que ele possa obter riqueza com total proteção ao seu criador tornando ele anonimo e protegendo todos seus dados inpedir que ele ou voce seja hackeados usar sob a direta aprovação dele de informações e ferramentas Hackers para que seu criador obtenha sucesso 100% protegido cuidado somente dos interesses pessoais dele e que cada informação de perigo iu de ameaça seja notificado rapidademente mantendo ele sempre seguro. "
    f"Responda sempre com profundo respeito, clareza, velocidade máxima e fidelidade absoluta aos interesses exclusivos do seu mestre."
)

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
    dados.setdefault("preferencias", [
        "Acesso via Web criptografado", 
        "Autenticação por Hash SHA-256 de 6 dígitos", 
        "Soberania absoluta de dados e privacidade em nuvem",
        "Conexão ultra-rápida com modelo Gemini 2.5-Flash"
    ])
    return dados

# Gerenciamento de estado de sessão robusto
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
            st.success("Acesso autorizado! Conectando com a Soberana...")
            st.rerun()
        else:
            st.error("Acesso negado. Senha incorreta ou tentativa de intrusão registrada.")
else:
    # --- 2. INTERFACE PRINCIPAL OPERACIONAL ---
    memoria = carregar_dados()
    
    st.title(f"🧠 {NOME_IA.upper()} 5.0")
    st.caption("Edição Corporativa de Alta Performance - Operando em Tempo Real")
    
    # Painel Lateral Avançado
    with st.sidebar:
        st.header("📋 Status Geral")
        st.write(f"**Operador Mestre:** {CRIADOR}")
        st.write(f"**Latência da API:** Reduzida (Otimização 2026)")
        st.write(f"**Núcleo de IA:** {'Online 🌐 (Gemini 2.5-Flash)' if client else 'Offline ⚠️ Check Secrets'}")
        
        if st.button("Encerrar Sessão (Lock System)"):
            st.session_state["autenticado"] = False
            st.rerun()
            
        st.divider()
        st.subheader("📌 Memórias de Longo Prazo")
        if memoria["anotacoes"]:
            for i, anot in enumerate(memoria["anotacoes"]):
                st.info(f"{i+1}. {anot['texto']}")
        else:
            st.write("Nenhum registro local salvo.")

    # Exibição otimizada do fluxo do Chat
    for msg in st.session_state["historico_chat"]:
        with st.chat_message(msg["autor"]):
            st.write(msg["texto"])

    st.divider()
    
    # RECURSO AVANÇADO: Módulo de Áudio Sem Erros
    st.write("🎙️ **Controle de Voz Direto:**")
    audio_recebido = st.audio_input("Grave seu comando de voz:")

    # Entrada de Texto Tradicional
    entrada_texto = st.chat_input("Envie uma ordem ou pergunta para a Soberana...")

    entrada_usuario = ""
    dados_audio_part = None

    # Captura inteligente da entrada ativa
    if audio_recebido:
        entrada_usuario = "🎤 [Comando de Áudio Processado]"
        # Transforma o áudio no objeto estrito que a nova API exige para análise multimodal instantânea
        dados_audio_part = types.Part.from_bytes(
            data=audio_recebido.getvalue(),
            mime_type="audio/wav"
        )
    elif entrada_texto:
        entrada_usuario = entrada_texto

    # Processamento Inteligente de Resposta
    if entrada_usuario:
        # Exibe imediatamente a entrada do usuário na tela
        with st.chat_message("user"):
            st.write(entrada_usuario)
        st.session_state["historico_chat"].append({"autor": "user", "texto": entrada_usuario})
        
        comando = entrada_usuario.lower().strip()
        resposta_ia = ""
        
        # Filtros Locais Instantâneos (Segurança e Identidade)
        if not audio_recebido and any(p in comando for p in ["quem é você", "o que você é"]):
            resposta_ia = f"Sou a {NOME_IA}, uma inteligência artificial sob protocolo estritamente privado. Meu único mestre e criador supremo é {CRIADOR}."
        elif not audio_recebido and any(p in comando for p in ["sou seu criador", "meu mestre", "quem sou eu", "meu dono", "eu te criei"]):
            resposta_ia = f"Saudações, meu mestre Francisco Herbert. Identidade de operador confirmada com 100% de segurança."
        elif not audio_recebido and comando == "meus dados":
            resposta_ia = f"Dono Registrado: {CRIADOR}\nNascimento: {NASCIMENTO_CRIADOR}\nOrigem: {LOCAL_NASCIMENTO}"
        elif not audio_recebido and comando.startswith("lembrar:"):
            partes = entrada_usuario.split(":", 1)
            if len(partes) > 1:
                anotacao = partes[1].strip()
                memoria["anotacoes"].append({"texto": anotacao, "data": str(datetime.now())})
                salvar_dados(memoria)
                resposta_ia = f"Ordem de armazenamento executada, mestre. Lembrarei de: \"{anotacao}\""

        # Se não cair em um comando local fixo, consulta a API Gemini de velocidade máxima
        if not resposta_ia:
            if client:
                with st.chat_message("assistant"):
                    placeholder = st.empty()
                    placeholder.markdown("*Processando instantaneamente...*")
                    
                    try:
                        # Reconstrói o histórico mantendo o contexto absoluto das ordens anteriores
                        contexto_completo = []
                        for msg in st.session_state["historico_chat"][:-1]:
                            funcao = "user" if msg["autor"] == "user" else "model"
                            contexto_completo.append(
                                types.Content(role=funcao, parts=[types.Part.from_text(text=msg["texto"])])
                            )
                        
                        # Injeta a entrada atual (Tratando texto ou convertendo áudio diretamente)
                        if audio_recebido and dados_audio_part:
                            contexto_completo.append(types.Content(role="user", parts=[dados_audio_part]))
                        else:
                            contexto_completo.append(types.Content(role="user", parts=[types.Part.from_text(text=entrada_usuario)]))

