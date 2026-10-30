
import streamlit as st

# ==================================================
# 1. CONFIGURAÇÃO INICIAL
# ==================================================

st.set_page_config(
    page_title="Soberana 5.0 - Nyxara",
    page_icon="🧠",
    layout="centered"
)

import requests
import tempfile
import os
import json
import ast
import re
import io
import time

from gtts import gTTS
from streamlit_autorefresh import st_autorefresh


# ==================================================
# 2. CONFIGURAÇÕES E SECRETS
# ==================================================

NOME_IA = "Nyxara"
CRIADOR = "Senhor Herbert"

MODELO_GEMINI = "gemini-3.8-flash"

TELEGRAM_TOKEN = str(
    st.secrets.get("TELEGRAM_TOKEN", "")
).strip()

GEMINI_API_KEY = str(
    st.secrets.get("GEMINI_API_KEY", "")
).strip()

AUTHORIZED_CHAT_ID = str(
    st.secrets.get("AUTHORIZED_CHAT_ID", "")
).strip()

TELEGRAM_API = (
    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
)


# ==================================================
# 3. INTERFACE
# ==================================================

st.title("🧠 SOBERANA 5.0")
st.subheader("Núcleo de desenvolvimento supervisionado")


# ==================================================
# 4. VERIFICAÇÃO DAS CONFIGURAÇÕES
# ==================================================

if not TELEGRAM_TOKEN:
    st.error("Configure TELEGRAM_TOKEN nos Secrets.")
    st.stop()

if not GEMINI_API_KEY:
    st.error("Configure GEMINI_API_KEY nos Secrets.")
    st.stop()

if not AUTHORIZED_CHAT_ID:
    st.error("Configure AUTHORIZED_CHAT_ID nos Secrets.")
    st.stop()


# ==================================================
# 5. ESTADO DO SISTEMA
# ==================================================

if "last_id" not in st.session_state:
    st.session_state.last_id = 0

if "proposta_pendente" not in st.session_state:
    st.session_state.proposta_pendente = None

if "ultimo_status" not in st.session_state:
    st.session_state.ultimo_status = "Inicializando"

if "historico" not in st.session_state:
    st.session_state.historico = []

if "webhook_verificado" not in st.session_state:
    st.session_state.webhook_verificado = False


# ==================================================
# 6. PERSONALIDADE DA NYXARA
# ==================================================

SYSTEM_PROMPT = f"""
Você é {NOME_IA}, inteligência artificial pessoal
de {CRIADOR}.

Seu idioma é português brasileiro.

Você deve:

- Ser inteligente, objetiva e respeitosa.
- Ajudar no desenvolvimento do Projeto Soberana.
- Explicar suas decisões.
- Não inventar resultados.
- Não afirmar que executou algo que não executou.
- Proteger dados e credenciais.
- Pedir autorização para operações importantes.
- Explicar assuntos técnicos de maneira simples.

Você está funcionando em modo supervisionado.
"""


# ==================================================
# 7. COMUNICAÇÃO COM GEMINI
# ==================================================

def consultar_gemini(texto, instrucao=None):

    if not GEMINI_API_KEY:
        return "A chave Gemini não está configurada."

    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{MODELO_GEMINI}:generateContent"
    )

    sistema = instrucao or SYSTEM_PROMPT

    payload = {
        "systemInstruction": {
            "parts": [
                {"text": sistema}
            ]
        },
        "contents": [
            {
                "parts": [
                    {"text": texto}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 6000
        }
    }

    # Até quatro tentativas para erros temporários.
    for tentativa in range(4):

        try:

            resposta = requests.post(
                url,
                headers={
                    "x-goog-api-key": GEMINI_API_KEY
                },
                json=payload,
                timeout=(15, 120)
            )

            # Resposta bem-sucedida.
            if resposta.status_code == 200:

                dados = resposta.json()

                candidatos = dados.get(
                    "candidates", []
                )

                if not candidatos:
                    return (
                        "O Gemini não retornou uma resposta."
                    )

                partes = candidatos[0].get(
                    "content", {}
                ).get("parts", [])

                resultado = "".join(
                    parte.get("text", "")
                    for parte in partes
                ).strip()

                return (
                    resultado
                    or "Resposta vazia do Gemini."
                )

            # Erros que podem ser temporários.
            if resposta.status_code in (
                429, 500, 502, 503, 504
            ):

                if tentativa < 3:

                    espera = 2 ** (tentativa + 1)

                    time.sleep(espera)

                    continue

            # Erro não recuperável ou tentativas esgotadas.
            return (
                f"Erro Gemini HTTP {resposta.status_code}: "
                f"{resposta.text[:500]}"
            )

        except requests.Timeout:

            if tentativa < 3:

                espera = 2 ** (tentativa + 1)

                time.sleep(espera)

                continue

            return (
                "O Gemini demorou demais para responder. "
                "Tente novamente em alguns instantes."
            )

        except requests.RequestException as erro:

            if tentativa < 3:

                espera = 2 ** (tentativa + 1)

                time.sleep(espera)

                continue

            return (
                f"Falha na conexão Gemini: {erro}"
            )

        except (
            ValueError,
            KeyError,
            TypeError
        ) as erro:

            return (
                f"Erro ao interpretar Gemini: {erro}"
            )

    return (
        "O Gemini está temporariamente indisponível. "
        "Tente novamente."
    )


def inteligencia_gemini(texto):
    return consultar_gemini(texto)


# ==================================================
# 8. NÚCLEO DE DESENVOLVIMENTO
# ==================================================

INSTRUCAO_DESENVOLVEDORA = """
Você é a engenheira de software da Nyxara.

Sua função é desenvolver módulos Python para o
Projeto Soberana.

REGRAS OBRIGATÓRIAS:

1. Gere somente um módulo Python por solicitação.
2. Não modifique app.py.
3. Não solicite nem inclua tokens, senhas ou chaves.
4. Não gere códigos para roubar credenciais.
5. Não gere malware ou invasão.
6. Não execute comandos no sistema operacional.
7. Não tente modificar arquivos fora do módulo solicitado.
8. O código deve ser organizado e documentado.
9. Não afirme que o código foi executado.
10. O proprietário fará a aprovação.

RETORNE SOMENTE JSON VÁLIDO, COM ESTA ESTRUTURA:

{
  "arquivo": "nome_do_modulo.py",
  "resumo": "Descrição da funcionalidade",
  "codigo": "Código Python completo"
}

O nome do arquivo deve conter somente letras
minúsculas, números e underline.
"""


def gerar_proposta(pedido):

    resultado = consultar_gemini(
        pedido,
        INSTRUCAO_DESENVOLVEDORA
    )

    try:

        inicio = resultado.find("{")
        fim = resultado.rfind("}") + 1

        if inicio < 0 or fim <= inicio:
            raise ValueError("JSON não encontrado.")

        proposta = json.loads(
            resultado[inicio:fim]
        )

        arquivo = proposta.get("arquivo", "")
        codigo = proposta.get("codigo", "")
        resumo = proposta.get("resumo", "")

        if not re.fullmatch(
            r"[a-z][a-z0-9_]{0,39}\.py",
            arquivo
        ):
            raise ValueError("Nome de arquivo inválido.")

        if arquivo in [
            "app.py",
            "__init__.py",
            "secrets.py"
        ]:
            raise ValueError("Arquivo protegido.")

        if not isinstance(codigo, str):
            raise ValueError("Código inválido.")

        if not codigo.strip():
            raise ValueError("Código vazio.")

        if len(codigo) > 30000:
            raise ValueError("Código excede o limite.")

        # Verifica a sintaxe sem executar o código.
        ast.parse(codigo)

        proposta_validada = {
            "arquivo": arquivo,
            "resumo": str(resumo)[:1000],
            "codigo": codigo
        }

        return proposta_validada, None

    except (
        ValueError,
        TypeError,
        SyntaxError
    ) as erro:

        return None, str(erro)


# ==================================================
# 9. ENVIO DE TEXTO PELO TELEGRAM
# ==================================================

def enviar_texto(chat_id, texto):

    resposta = requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": str(texto)[:4000]
        },
        timeout=20
    )

    resposta.raise_for_status()

    dados = resposta.json()

    if not dados.get("ok"):
        raise RuntimeError(
            "Telegram não confirmou o envio."
        )


# ==================================================
# 10. ENVIO DE ARQUIVO PYTHON
# ==================================================

def enviar_modulo(chat_id, proposta):

    nome = proposta["arquivo"]
    codigo = proposta["codigo"]

    arquivo = io.BytesIO(
        codigo.encode("utf-8")
    )

    arquivo.name = nome

    resposta = requests.post(
        f"{TELEGRAM_API}/sendDocument",
        data={
            "chat_id": chat_id,
            "caption": (
                f"Módulo aprovado: {nome}\n"
                "Arquivo gerado pela Nyxara."
            )
        },
        files={
            "document": (
                nome,
                arquivo,
                "text/x-python"
            )
        },
        timeout=60
    )

    resposta.raise_for_status()

    dados = resposta.json()

    if not dados.get("ok"):
        raise RuntimeError(
            "Telegram não confirmou o arquivo."
        )


# ==================================================
# 11. SISTEMA DE VOZ
# ==================================================

def enviar_voz(chat_id, texto):

    caminho = None

    try:

        with tempfile.NamedTemporaryFile(
            suffix=".mp3",
            delete=False
        ) as arquivo:
            caminho = arquivo.name

        gTTS(
            text=str(texto)[:2500],
            lang="pt"
        ).save(caminho)

        with open(caminho, "rb") as audio:

            resposta = requests.post(
                f"{TELEGRAM_API}/sendVoice",
                data={
                    "chat_id": chat_id
                },
                files={
                    "voice": (
                        "nyxara.mp3",
                        audio,
                        "audio/mpeg"
                    )
                },
                timeout=60
            )

        resposta.raise_for_status()

        dados = resposta.json()

        return dados.get("ok", False)

    except Exception:
        return False

    finally:

        if caminho and os.path.exists(caminho):

            try:
                os.remove(caminho)

            except OSError:
                pass


# ==================================================
# 12. COMANDOS
# ==================================================

def processar_comando(chat_id, mensagem):

    comando = mensagem.strip()
    comando_lower = comando.lower()

    # ATIVAR
    if comando_lower in [
        "/start",
        "iniciar",
        "ativar"
    ]:

        return (
            f"Nyxara ativada, {CRIADOR}.\n"
            "Modo supervisionado operacional."
        )

    # AJUDA
    if comando_lower in [
        "/ajuda",
        "ajuda",
        "/comandos"
    ]:

        return (
            "COMANDOS DA NYXARA\n\n"
            "/start - Ativar\n"
            "/ajuda - Comandos\n"
            "/status - Estado do sistema\n"
            "/desenvolver pedido - Criar módulo\n"
            "/pendente - Ver proposta\n"
            "/aprovar - Aprovar módulo\n"
            "/rejeitar - Rejeitar módulo\n\n"
            "Envie mensagens normais para conversar."
        )

    # STATUS
    if comando_lower == "/status":

        return (
            "NYXARA - STATUS\n\n"
            "Inteligência: Configurada\n"
            "Modo: Supervisionado\n"
            "Execução automática de código: Desativada\n"
            "Alteração automática de app.py: Bloqueada\n"
            "Proposta pendente: "
            + (
                "Sim"
                if st.session_state.proposta_pendente
                else "Não"
            )
        )

    # DESENVOLVER
    if comando_lower.startswith("/desenvolver"):

        pedido = comando[
            len("/desenvolver"):
        ].strip()

        if not pedido:

            return (
                "Informe o que deseja desenvolver.\n\n"
                "Exemplo:\n"
                "/desenvolver criar um módulo de memória"
            )

        proposta, erro = gerar_proposta(pedido)

        if erro:

            return (
                "Não consegui preparar o módulo.\n"
                f"Motivo: {erro}\n"
                "Tente novamente com uma descrição mais clara."
            )

        st.session_state.proposta_pendente = proposta

        return (
            "PROPOSTA CRIADA!\n\n"
            f"Arquivo: {proposta['arquivo']}\n"
            f"Resumo: {proposta['resumo']}\n\n"
            "O código passou pela verificação de sintaxe.\n"
            "Ainda não foi executado nem instalado.\n\n"
            "Envie /aprovar para receber o arquivo.\n"
            "Envie /rejeitar para descartar."
        )

    # CONSULTAR PROPOSTA
    if comando_lower == "/pendente":

        proposta = st.session_state.proposta_pendente

        if not proposta:
            return "Não existe proposta pendente."

        return (
            "PROPOSTA PENDENTE\n\n"
            f"Arquivo: {proposta['arquivo']}\n"
            f"Resumo: {proposta['resumo']}\n\n"
            "Envie /aprovar ou /rejeitar."
        )

    # APROVAR
    if comando_lower == "/aprovar":

        proposta = st.session_state.proposta_pendente

        if not proposta:
            return "Não existe proposta para aprovar."

        try:

            ast.parse(proposta["codigo"])

            enviar_modulo(chat_id, proposta)

            st.session_state.proposta_pendente = None

            return (
                "MÓDULO APROVADO E ENTREGUE!\n\n"
                f"Arquivo: {proposta['arquivo']}\n\n"
                "O arquivo foi enviado como documento Python.\n"
                "Ele ainda precisa ser revisado e "
                "adicionado ao projeto manualmente."
            )

        except Exception as erro:

            return (
                "Não foi possível entregar o módulo.\n"
                f"Erro: {erro}\n"
                "A proposta continua pendente."
            )

    # REJEITAR
    if comando_lower == "/rejeitar":

        if not st.session_state.proposta_pendente:
            return "Não existe proposta pendente."

        st.session_state.proposta_pendente = None

        return "Proposta rejeitada e descartada."

    return None


# ==================================================
# 13. SEGURANÇA E AUTORIZAÇÃO
# ==================================================

def usuario_autorizado(chat_id):

    if not AUTHORIZED_CHAT_ID:
        return False

    return str(chat_id) == AUTHORIZED_CHAT_ID


# ==================================================
# 14. PREPARAR TELEGRAM
# ==================================================

if not st.session_state.webhook_verificado:

    try:

        resposta_webhook = requests.post(
            f"{TELEGRAM_API}/deleteWebhook",
            json={
                "drop_pending_updates": False
            },
            timeout=20
        )

        resposta_webhook.raise_for_status()

        dados_webhook = resposta_webhook.json()

        if not dados_webhook.get("ok"):

            st.error(
                "Não foi possível preparar o Telegram: "
                + dados_webhook.get(
                    "description",
                    "Erro desconhecido."
                )
            )

            st.stop()

        st.session_state.webhook_verificado = True

    except requests.RequestException as erro:

        st.error(
            f"Falha ao preparar o Telegram: {erro}"
        )

        st.stop()


# ==================================================
# 15. PAINEL DE CONTROLE
# ==================================================

st.divider()

st.markdown("### Painel de controle")

st.success("Sistema configurado.")
st.info("Modo de desenvolvimento: supervisionado.")

st.caption(
    "A Nyxara está aguardando mensagens autorizadas."
)

st_autorefresh(
    interval=4000,
    key="nyxara_refresh"
)


# ==================================================
# 16. RECEBER MENSAGENS DO TELEGRAM
# ==================================================

try:

    resposta = requests.get(
        f"{TELEGRAM_API}/getUpdates",
        params={
            "offset": st.session_state.last_id + 1,
            "timeout": 0,
            "allowed_updates": json.dumps(["message"])
        },
        timeout=15
    )

    resposta.raise_for_status()

    dados = resposta.json()

    if not dados.get("ok"):

        raise RuntimeError(
            dados.get(
                "description",
                "Telegram não confirmou a consulta."
            )
        )

    atualizacoes = dados.get("result", [])

    for update in atualizacoes:

        st.session_state.last_id = (
            update["update_id"]
        )

        mensagem = update.get("message", {})
        chat = mensagem.get("chat", {})

        chat_id = chat.get("id")

        texto_recebido = mensagem.get(
            "text", ""
        ).strip()

        if not chat_id or not texto_recebido:
            continue

        # Verificação de autorização.
        if not usuario_autorizado(chat_id):
            continue

        # Processamento dos comandos.
        resposta_bot = processar_comando(
            chat_id,
            texto_recebido
        )

        # Conversa normal com Gemini.
        if resposta_bot is None:

            resposta_bot = inteligencia_gemini(
                texto_recebido
            )

        # Envia resposta de texto.
        enviar_texto(
            chat_id,
            resposta_bot
        )

        # Envia áudio, exceto para comandos de arquivo.
        if texto_recebido.lower() not in [
            "/aprovar",
            "/rejeitar"
        ] and not texto_recebido.lower().startswith(
            "/desenvolver"
        ):

            enviar_voz(
                chat_id,
                resposta_bot
            )

        st.session_state.ultimo_status = (
            "Última mensagem processada."
        )

        st.session_state.historico.append(
            texto_recebido[:200]
        )

except requests.RequestException as erro:

    st.error(
        f"Falha de comunicação com o Telegram: {erro}"
    )

except Exception as erro:

    st.error(
        f"Erro no sistema: {erro}"
    )


# ==================================================
# 17. PAINEL DE PROPOSTAS
# ==================================================

st.divider()

st.markdown("### Desenvolvimento da Nyxara")

proposta = st.session_state.proposta_pendente

if proposta:

    st.warning(
        "Existe uma proposta aguardando aprovação."
    )

    st.write(
        "**Arquivo:**",
        proposta["arquivo"]
    )

    st.write(
        "**Resumo:**",
        proposta["resumo"]
    )

    with st.expander("Visualizar código proposto"):

        st.code(
            proposta["codigo"],
            language="python"
        )

    st.caption(
        "O código ainda não foi executado ou instalado."
    )

else:

    st.info(
        "Nenhuma proposta aguardando aprovação."
    )

st.divider()

st.write(
    "**Estado:**",
    st.session_state.ultimo_status
)
