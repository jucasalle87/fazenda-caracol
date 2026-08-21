import os
import io
import time
import base64
import json
from datetime import datetime, timedelta, timezone

import streamlit as st
import streamlit_authenticator as stauth
import yaml
import pandas as pd
from streamlit_autorefresh import st_autorefresh

import github_storage

# ─────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")
LOG_PATH = os.path.join(BASE_DIR, "data", "access_log.csv")
ASSETS = os.path.join(BASE_DIR, "assets")
GEOJSON_PATH = os.path.join(BASE_DIR, "data", "fazenda_caracol.geojson")
BRT = timezone(timedelta(hours=-3))

# Nomes dos arquivos DENTRO do repositório GitHub (caminho relativo, igual
# ao que aparece no repo — não usar caminho absoluto do disco local aqui).
GH_CONFIG_PATH = "config.yaml"
GH_LOG_PATH = "data/access_log.csv"
LOG_HEADER = ["timestamp_brt", "username", "nome", "email"]

st.set_page_config(
    page_title="Fazenda 400 ha — Caracol/MS | DarkPool",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# STYLE — mesma paleta DarkPool usada no dataroom do Resort em Porto Seguro
# ─────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    :root {
        --gold: #C9A96E; --gold-light: #E8D5B0; --gold-dark: #8B6A35;
        --forest: #1C2B1A; --forest-light: #4A7A47;
        --cream: #F5F0E8; --cream-dark: #EDE5D4;
        --ink: #1A1A18; --ink-mid: #3A3A36;
        --black: #000000;
    }
    .stApp { background: var(--cream); }
    /* Sidebar na mesma cor de fundo do logo da DarkPool (preto), pra ficar
       tudo integrado visualmente. */
    section[data-testid="stSidebar"] { background: var(--black); }
    /* Só forçamos a cor clara em texto "solto" da sidebar (títulos, legendas,
       labels, markdown) — nunca em inputs/textareas ou em popovers/tooltips,
       que têm fundo claro próprio e ficariam ilegíveis (texto claro em
       fundo claro). */
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"],
    section[data-testid="stSidebar"] small {
        color: var(--cream);
    }
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] textarea {
        color: var(--ink) !important;
        background: white !important;
        -webkit-text-fill-color: var(--ink) !important;
    }
    /* Botões "de verdade" da sidebar (Sair, Salvar) têm fundo claro por
       padrão — sem isso o texto ficava claro em fundo claro. Escopado só
       pros botões reais (stButton/stFormSubmitButton), NUNCA pro botãozinho
       de mostrar/ocultar senha (esse fica dentro de stTextInput, ver abaixo
       — ele deve continuar discreto, sem caixa dourada). */
    section[data-testid="stSidebar"] div[data-testid="stButton"] button,
    section[data-testid="stSidebar"] div[data-testid="stFormSubmitButton"] button {
        background: var(--gold) !important;
        border: 1px solid var(--gold) !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button p,
    section[data-testid="stSidebar"] div[data-testid="stButton"] button span,
    section[data-testid="stSidebar"] div[data-testid="stButton"] button div,
    section[data-testid="stSidebar"] div[data-testid="stFormSubmitButton"] button p,
    section[data-testid="stSidebar"] div[data-testid="stFormSubmitButton"] button span,
    section[data-testid="stSidebar"] div[data-testid="stFormSubmitButton"] button div {
        color: var(--forest) !important;
        font-weight: 600 !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button:hover,
    section[data-testid="stSidebar"] div[data-testid="stFormSubmitButton"] button:hover {
        background: var(--gold-light) !important;
        border-color: var(--gold-light) !important;
    }
    /* Botão de mostrar/ocultar senha (o "olhinho") — sem caixa colorida,
       só o ícone preto em cima do fundo branco do campo, como no padrão
       do Streamlit. */
    section[data-testid="stSidebar"] div[data-testid="stTextInput"] button {
        background: transparent !important;
        border: none !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stTextInput"] button svg {
        fill: var(--ink) !important;
    }
    /* Cabeçalho do expander ("Navegação" etc.) tem o mesmo problema. */
    section[data-testid="stSidebar"] details summary {
        background: var(--gold) !important;
        border-radius: 4px;
    }
    section[data-testid="stSidebar"] details summary span,
    section[data-testid="stSidebar"] details summary p {
        color: var(--forest) !important;
        font-weight: 600 !important;
    }
    /* Qualquer tooltip/popover do Streamlit (ex: dica de senha) — sempre
       texto escuro em fundo claro, onde quer que seja renderizado. */
    div[data-baseweb="tooltip"], div[data-baseweb="popover"] {
        color: var(--ink) !important;
    }
    h1, h2, h3 { color: var(--forest); font-family: Georgia, 'Times New Roman', serif; }
    .dp-badge {
        display:inline-block; border:1px solid var(--gold); color:var(--gold-dark);
        font-size:11px; font-weight:600; letter-spacing:.14em; text-transform:uppercase;
        padding:4px 12px; margin-bottom:14px; border-radius:2px;
    }
    .dp-cover {
        position:relative; border-radius:6px; overflow:hidden; margin-bottom:8px;
    }
    .dp-cover img { width:100%; max-height:380px; object-fit:cover; filter:brightness(0.55); }
    .dp-cover-text {
        position:absolute; bottom:0; left:0; right:0; padding:28px 32px;
        color:white;
    }
    .dp-cover-text .eyebrow { color:var(--gold-light); font-size:12px; letter-spacing:.16em; text-transform:uppercase; margin-bottom:6px;}
    .dp-cover-text h1 { color:white; font-size:2.6rem; margin:0 0 4px 0; line-height:1.05; }
    .dp-cover-text .sub { color:var(--gold-light); font-style:italic; font-size:1.1rem; }
    .dp-section-label { font-size:11px; font-weight:700; letter-spacing:.16em; text-transform:uppercase; color:var(--gold-dark); margin-bottom:6px; }
    .dp-feature {
        background: var(--cream-dark); border-top:3px solid var(--gold); border-bottom:3px solid var(--gold);
        padding: 28px 30px; border-radius:4px; margin: 18px 0;
    }
    .dp-badge-feature {
        display:inline-block; background:var(--gold); color:var(--forest); font-size:10px; font-weight:700;
        letter-spacing:.14em; text-transform:uppercase; padding:5px 14px; margin-bottom:14px; border-radius:2px;
    }
    .dp-quote { border-left:4px solid var(--gold); padding-left:18px; font-style:italic; color:var(--forest); font-size:1.08rem; }
    .dp-chip {
        display:inline-block; border:1px solid var(--gold-dark); color:var(--gold-dark); font-size:12px;
        font-weight:500; padding:4px 11px; margin:3px 6px 3px 0; border-radius:2px;
    }
    .dp-contact-box {
        background: var(--forest); color: var(--cream); padding: 26px 30px; border-radius: 6px;
    }
    .dp-contact-box a { color: var(--gold-light) !important; text-decoration:none; }
    div[data-testid="stMetric"] {
        background: white; border: 1px solid var(--cream-dark); padding: 12px 8px; border-radius: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────
# HELPERS — leitura/escrita sempre passam pelo github_storage, que
# sincroniza com o repositório (se configurado) e cai para arquivo local
# como fallback. Isso resolve o problema de perder usuários/log quando o
# Streamlit Cloud reinicia o container.
# ─────────────────────────────────────────────────────────────
def load_config():
    conteudo = github_storage.ler_arquivo(GH_CONFIG_PATH)
    if not conteudo:
        # primeira execução sem GitHub configurado: usa o que já está local
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            conteudo = f.read()
    return yaml.safe_load(conteudo)


def save_config(config):
    conteudo = yaml.safe_dump(config, default_flow_style=False, allow_unicode=True)
    n_usuarios = len(config.get("credentials", {}).get("usernames", {}))
    github_storage.salvar_arquivo(
        GH_CONFIG_PATH, conteudo, mensagem=f"Atualiza usuários do dataroom ({n_usuarios} cadastrados)"
    )


def _log_rows_to_df(csv_text):
    if not csv_text or not csv_text.strip():
        return pd.DataFrame(columns=LOG_HEADER)
    try:
        return pd.read_csv(io.StringIO(csv_text))
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=LOG_HEADER)


def log_access(username, name, email):
    conteudo = github_storage.ler_arquivo(GH_LOG_PATH)
    df = _log_rows_to_df(conteudo)
    nova_linha = pd.DataFrame(
        [[datetime.now(BRT).strftime("%Y-%m-%d %H:%M:%S"), username, name, email]],
        columns=LOG_HEADER,
    )
    df = pd.concat([df, nova_linha], ignore_index=True)
    github_storage.salvar_arquivo(
        GH_LOG_PATH, df.to_csv(index=False), mensagem=f"Registra acesso de '{username}'"
    )


def read_log():
    conteudo = github_storage.ler_arquivo(GH_LOG_PATH)
    return _log_rows_to_df(conteudo)


def asset(name):
    return os.path.join(ASSETS, name)


def img_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def sync_config_from_github_to_local():
    """No arranque do app, garante que o config.yaml local (usado pelo
    streamlit_authenticator, que só sabe ler/escrever no disco) esteja
    atualizado com a última versão do GitHub."""
    if not github_storage.github_configurado():
        return
    conteudo = github_storage.ler_arquivo(GH_CONFIG_PATH)
    if conteudo:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            f.write(conteudo)


def push_local_config_to_github(mensagem="Atualiza config.yaml"):
    """Empurra o config.yaml local (que o streamlit_authenticator acabou de
    escrever, ex: após reset_password) de volta pro GitHub."""
    if not github_storage.github_configurado():
        return
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        conteudo = f.read()
    github_storage.salvar_arquivo(GH_CONFIG_PATH, conteudo, mensagem=mensagem)


# ─────────────────────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────────────────────
sync_config_from_github_to_local()
config = load_config()


class SenhaLivreValidator(stauth.Validator):
    """Desliga a exigência de senha forte da biblioteca (maiúscula, número,
    caractere especial etc.) — aqui qualquer senha não vazia é aceita."""

    def validate_password(self, password: str) -> bool:
        return bool(password)


authenticator = stauth.Authenticate(
    credentials=CONFIG_PATH,
    cookie_name=config["cookie"]["name"],
    cookie_key=config["cookie"]["key"],
    cookie_expiry_days=config["cookie"]["expiry_days"],
    auto_hash=False,
    validator=SenhaLivreValidator(),
    # Sem exigência de senha forte — qualquer senha é aceita, e some a
    # dica de regras que aparecia embaixo do campo.
    password_instructions="",
)

if not st.session_state.get("authentication_status"):
    # Tela de login com fundo preto, na mesma cor do logo — pra ficar tudo
    # integrado (fundo + logo + sidebar, quando ela aparecer, depois do
    # login, também é preta).
    st.markdown(
        """
        <style>
        .stApp { background: var(--black) !important; }
        [data-testid="stMain"] h1,
        [data-testid="stMain"] h2,
        [data-testid="stMain"] h3,
        [data-testid="stMain"] p,
        [data-testid="stMain"] span,
        [data-testid="stMain"] label,
        [data-testid="stMain"] small {
            color: var(--cream) !important;
        }
        [data-testid="stMain"] input {
            color: var(--ink) !important;
            background: white !important;
            -webkit-text-fill-color: var(--ink) !important;
        }
        [data-testid="stMain"] div[data-testid="stTextInput"] button {
            background: transparent !important;
            border: none !important;
        }
        [data-testid="stMain"] div[data-testid="stTextInput"] button svg {
            fill: var(--ink) !important;
        }
        [data-testid="stMain"] div[data-testid="stButton"] button,
        [data-testid="stMain"] div[data-testid="stFormSubmitButton"] button {
            background: var(--gold) !important;
            border: 1px solid var(--gold) !important;
        }
        [data-testid="stMain"] div[data-testid="stButton"] button p,
        [data-testid="stMain"] div[data-testid="stButton"] button span,
        [data-testid="stMain"] div[data-testid="stFormSubmitButton"] button p,
        [data-testid="stMain"] div[data-testid="stFormSubmitButton"] button span {
            color: var(--forest) !important;
            font-weight: 600 !important;
        }
        /* Tudo centralizado: textos, rótulos, campos e botão — não só
           largura reduzida, mas também alinhamento central de verdade,
           via flexbox nos containers (mais confiável que só margin:auto). */
        [data-testid="stMain"] * {
            text-align: center;
        }
        [data-testid="stMain"] div[data-testid="stVerticalBlock"] {
            align-items: center;
        }
        [data-testid="stMain"] div[data-testid="stForm"] {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
        }
        [data-testid="stMain"] div[data-testid="stTextInput"],
        [data-testid="stMain"] div[data-testid="stFormSubmitButton"] {
            max-width: 280px;
            width: 100%;
            margin-left: auto;
            margin-right: auto;
        }
        [data-testid="stMain"] div[data-testid="stFormSubmitButton"] button {
            margin: 0 auto;
        }
        /* Menos espaço em branco no topo da página. */
        [data-testid="stMain"] div[data-testid="stMainBlockContainer"] {
            padding-top: 2rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        st.markdown(
            f"<div style='text-align:center; margin-bottom:4px;'>"
            f"<img src='data:image/png;base64,{img_b64(asset('darkpool_logo.png'))}' "
            f"style='width:260px; max-width:80%; height:auto;'></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div class='dp-badge'>Acesso Restrito · Estritamente Confidencial</div>",
            unsafe_allow_html=True,
        )
        st.markdown("### Dataroom — Fazenda 400 ha, Caracol/MS")
        mensagem_pos_logout = st.session_state.pop("_mensagem_pos_logout", None)
        if mensagem_pos_logout:
            st.info(mensagem_pos_logout)
        authenticator.login(
            location="main",
            fields={
                "Form name": "Entrar",
                "Username": "Usuário",
                "Password": "Senha",
                "Login": "Entrar",
            },
        )
        if st.session_state.get("authentication_status") is False:
            st.error("Usuário ou senha incorretos.")
        elif st.session_state.get("authentication_status") is None:
            st.info("Informe seu usuário e senha para acessar o dataroom.")
        st.caption("Acesso individual e monitorado. Em caso de dúvidas, contate a DarkPool Intermediação de Ativos.")
        st.markdown(
            "<div style='text-align:center; margin-top:6px;'>"
            "<a href='https://www.darkpool.com.br' target='_blank' "
            "style='color:var(--gold-light); text-decoration:none; font-size:0.85rem;'>"
            "www.darkpool.com.br</a><br>"
            "<a href='mailto:negocios@darkpool.com.br' "
            "style='color:var(--gold-light); text-decoration:none; font-size:0.85rem;'>"
            "negocios@darkpool.com.br</a></div>",
            unsafe_allow_html=True,
        )
    st.stop()

# ─────────────────────────────────────────────────────────────
# LOGOUT AUTOMÁTICO POR INATIVIDADE (20 minutos)
# ─────────────────────────────────────────────────────────────
LIMITE_INATIVIDADE_MIN = 20

if "last_activity" not in st.session_state:
    st.session_state["last_activity"] = time.time()

# Verifica a cada 60s mesmo sem nenhuma ação do usuário (sem isso, o script
# só roda de novo quando alguém clica em algo, e o timeout nunca seria
# percebido enquanto a pessoa só fica olhando a tela sem clicar em nada).
st_autorefresh(interval=60_000, key="verifica_inatividade")

minutos_inativo = (time.time() - st.session_state["last_activity"]) / 60
if minutos_inativo > LIMITE_INATIVIDADE_MIN:
    authenticator.logout(location="unrendered")
    st.session_state.pop("_access_logged", None)
    st.session_state.pop("last_activity", None)
    st.session_state["_mensagem_pos_logout"] = (
        f"Sessão encerrada automaticamente após {LIMITE_INATIVIDADE_MIN} "
        "minutos de inatividade. Faça login novamente."
    )
    st.rerun()


def _marcar_atividade():
    st.session_state["last_activity"] = time.time()


# ─────────────────────────────────────────────────────────────
# LOGGED IN
# ─────────────────────────────────────────────────────────────
username = st.session_state["username"]
name = st.session_state["name"]
user_entry = config["credentials"]["usernames"].get(username, {})
email = user_entry.get("email", "")
role = user_entry.get("role", "user")

if not st.session_state.get("_access_logged"):
    log_access(username, name, email)
    st.session_state["_access_logged"] = True

with st.sidebar:
    st.image(asset("darkpool_logo.png"), width=180)
    st.markdown(f"**Bem-vindo(a),**  \n{name}")
    st.caption(f"Usuário: {username}")
    authenticator.logout("Sair", "sidebar")
    st.divider()
    page = "Dataroom"
    if role == "master":
        page = st.radio(
            "Navegação", ["Dataroom", "Administração"],
            label_visibility="collapsed", on_change=_marcar_atividade,
        )
    try:
        if authenticator.reset_password(
            username,
            location="sidebar",
            clear_on_submit=True,
            fields={
                "Form name": "Alterar Senha",
                "Current password": "Senha atual",
                "New password": "Nova senha",
                "Repeat password": "Confirmar nova senha",
                "Reset": "Salvar",
            },
        ):
            push_local_config_to_github(f"Atualiza senha de '{username}'")
            st.success("Senha alterada com sucesso.")
    except Exception as e:
        st.error(str(e))

# ═════════════════════════════════════════════════════════════
# ADMIN PAGE
# ═════════════════════════════════════════════════════════════
if role == "master" and page == "Administração":
    st.title("Administração do Dataroom")

    tab_users, tab_log = st.tabs(["👤 Usuários", "📋 Log de Acessos"])

    with tab_users:
        st.subheader("Cadastrar novo usuário")
        with st.form("add_user_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            new_username = c1.text_input("Usuário (login)")
            new_name = c2.text_input("Nome completo")
            new_email = c1.text_input("E-mail")
            new_password = c2.text_input("Senha provisória", type="password")
            submitted = st.form_submit_button("Cadastrar")

            if submitted:
                cfg = load_config()
                usernames = cfg["credentials"]["usernames"]
                if not new_username or not new_name or not new_password:
                    st.error("Preencha usuário, nome e senha.")
                elif new_username in usernames:
                    st.error("Já existe um usuário com esse login.")
                else:
                    usernames[new_username] = {
                        "name": new_name,
                        "email": new_email,
                        "password": stauth.Hasher.hash(new_password),
                        "role": "user",
                        "failed_login_attempts": 0,
                        "logged_in": False,
                    }
                    save_config(cfg)
                    st.success(f"Usuário '{new_username}' cadastrado com sucesso.")

        st.divider()
        st.subheader("Usuários com acesso")
        cfg = load_config()
        usernames = cfg["credentials"]["usernames"]

        removable = [u for u in usernames if usernames[u].get("role") != "master"]
        if removable:
            col_a, col_b = st.columns([3, 1])
            to_remove = col_a.selectbox("Remover acesso de:", removable)
            if col_b.button("Remover", type="primary"):
                cfg = load_config()
                cfg["credentials"]["usernames"].pop(to_remove, None)
                save_config(cfg)
                st.success(f"Acesso de '{to_remove}' removido.")
                cfg = load_config()
                usernames = cfg["credentials"]["usernames"]

        rows = [
            {"usuário": u, "nome": v.get("name", ""), "e-mail": v.get("email", ""), "papel": v.get("role", "user")}
            for u, v in usernames.items()
        ]
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

    with tab_log:
        st.subheader("Histórico de acessos")
        df = read_log()
        if df.empty:
            st.info("Nenhum acesso registrado ainda.")
        else:
            st.dataframe(df.sort_values("timestamp_brt", ascending=False), width="stretch", hide_index=True)
            st.download_button(
                "Baixar log (CSV)",
                df.to_csv(index=False).encode("utf-8"),
                file_name="access_log_fazenda_caracol.csv",
                mime="text/csv",
            )
        st.caption(
            "⚠️ Este log fica salvo no armazenamento do próprio app. Se o Streamlit Cloud reiniciar o "
            "container (por inatividade prolongada ou novo deploy via GitHub), o histórico pode ser perdido. "
            "Baixe o CSV periodicamente para manter um registro permanente."
        )

    st.stop()

# ═════════════════════════════════════════════════════════════
# DATAROOM — CONTEÚDO DO IMÓVEL
# ═════════════════════════════════════════════════════════════
st.markdown(
    f"""
    <div class="dp-cover">
        <img src="data:image/jpeg;base64,{img_b64(asset('01.jpg'))}">
        <div class="dp-cover-text">
            <div class="eyebrow">Oportunidade de Investimento · Forte Vocação Agrícola</div>
            <h1>Fazenda 400 ha</h1>
            <div class="sub">Caracol — Mato Grosso do Sul</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Área Total", "400 ha")
c2.metric("Área Agricultável", "280 ha")
c3.metric("Potencial de Abertura", "+20 ha")
c4.metric("Valor", "R$ 22 mi")

st.markdown("<div class='dp-section-label'>Sumário Executivo</div>", unsafe_allow_html=True)
st.markdown("## Fazenda de 400 hectares em região de forte vocação agrícola no Planalto de Caracol/MS")
st.write(
    "Fazenda à venda com 400 hectares no município de Caracol, Mato Grosso do Sul, em topografia de "
    "planalto — relevo predominantemente plano a suavemente ondulado, favorável à mecanização agrícola. "
    "Do total, 280 hectares já são agricultáveis, com possibilidade de abertura de mais 20 hectares, "
    "elevando a área produtiva potencial para 300 hectares."
)
st.write(
    "A propriedade está localizada em uma região reconhecida pela forte vocação agrícola, a apenas 70 km "
    "de Bela Vista/MS e a 10 km da Rota Bioceânica — corredor logístico estratégico que liga o Brasil aos "
    "portos do Pacífico, na fronteira com o Paraguai e a Bolívia, agregando valor logístico ao ativo."
)

st.divider()

st.markdown("<div class='dp-section-label'>Galeria de Fotos</div>", unsafe_allow_html=True)
st.markdown("## Conheça a Propriedade")
gallery = [
    ("01.jpg", "Vista da lavoura de soja em pleno desenvolvimento — topografia de planalto"),
    ("02.jpg", "Lavoura de soja ao entardecer, relevo plano típico da região"),
    ("03.jpg", "Talhão em início de desenvolvimento — solo exposto entre as linhas de plantio"),
    ("04.jpg", "Acesso interno à lavoura, junto à divisa do talhão"),
    ("05.jpg", "Área preparada para plantio, com mata nativa preservada ao fundo"),
    ("06.jpg", "Colheita da soja — carregamento de caminhão ao entardecer"),
    ("07.jpg", "Veículo utilitário junto à lavoura de soja madura, estrada interna de acesso"),
    ("08.jpg", "Colheitadeira em operação na lavoura de soja madura"),
    ("09.jpg", "Colheita mecanizada, com vegetação nativa preservada na borda do talhão"),
    ("10.jpg", "Solo preparado para plantio — relevo de planalto e mata nativa ao fundo"),
    ("11.jpg", "Planta de soja com sistema radicular desenvolvido — indicador de boa fertilidade do solo"),
    ("12.jpg", "Detalhe do sistema radicular com nódulos de fixação biológica de nitrogênio"),
    ("13.jpg", "Detalhe da folha — qualidade e vigor do estande da lavoura"),
]
cols = st.columns(4)
for i, (fname, label) in enumerate(gallery):
    with cols[i % 4]:
        st.image(asset(fname), caption=label, width="stretch")

st.divider()

st.markdown("<div class='dp-section-label'>Mapa da Propriedade</div>", unsafe_allow_html=True)
st.markdown("## Localização")
if os.path.exists(GEOJSON_PATH):
    import folium
    from streamlit_folium import st_folium

    with open(GEOJSON_PATH, encoding="utf-8") as f:
        gj = json.load(f)

    all_lats, all_lons = [], []
    for feat in gj["features"]:
        geom = feat["geometry"]
        coords = geom["coordinates"]
        rings = coords if geom["type"] == "Polygon" else [r for poly in coords for r in poly]
        for ring in rings:
            for lon, lat in ring:
                all_lats.append(lat)
                all_lons.append(lon)
    center = [sum(all_lats) / len(all_lats), sum(all_lons) / len(all_lons)]

    m = folium.Map(location=center, zoom_start=13, tiles=None)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr=" ",
        name="Satélite",
    ).add_to(m)
    m.get_root().html.add_child(
        folium.Element("<style>.leaflet-control-attribution{display:none !important;}</style>")
    )

    def estilo(feature):
        nome = feature["properties"].get("name", "")
        if "Limites" in nome or "Perímetro" in nome:
            return {"color": "#FFD700", "weight": 4, "fillOpacity": 0}
        elif "(RL)" in nome or "Reserva" in nome:
            return {"color": "#2ecc71", "weight": 1.5, "fillColor": "#2ecc71", "fillOpacity": 0.35}
        return {"color": "#3388ff", "weight": 1.5, "fillColor": "#3388ff", "fillOpacity": 0.15}

    folium.GeoJson(
        gj,
        style_function=estilo,
        tooltip=folium.GeoJsonTooltip(fields=["name"], aliases=["Área:"]),
    ).add_to(m)

    st_folium(m, width=None, height=600)
    st.caption("🟡 Perímetro geral · 🔵 Área agricultável · 🟢 Reserva Legal")
else:
    import folium
    from streamlit_folium import st_folium

    # Ainda não recebemos o KML/KMZ com o perímetro exato da fazenda — assim
    # que o arquivo chegar, basta converter para GeoJSON e salvar em
    # "data/fazenda_caracol.geojson" que o mapa com o polígono real passa a
    # aparecer automaticamente aqui, sem precisar mexer no código.
    st.info(
        "O perímetro exato da propriedade (arquivo KML) ainda será enviado. "
        "O mapa abaixo mostra a localização aproximada do município de "
        "Caracol/MS — assim que o KML for recebido, o contorno real da "
        "fazenda passa a aparecer automaticamente nesta seção."
    )
    center = [-22.0139, -57.0239]
    m = folium.Map(location=center, zoom_start=11, tiles=None)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr=" ",
        name="Satélite",
    ).add_to(m)
    folium.Marker(
        center, tooltip="Caracol/MS (localização aproximada do município)",
        icon=folium.Icon(color="orange"),
    ).add_to(m)
    m.get_root().html.add_child(
        folium.Element("<style>.leaflet-control-attribution{display:none !important;}</style>")
    )
    st_folium(m, width=None, height=500)

st.divider()

st.markdown("<div class='dp-section-label'>Localização & Diferenciais Competitivos</div>", unsafe_allow_html=True)
st.markdown("## Caracol — Mato Grosso do Sul")
st.write(
    "Localização estratégica no Planalto de Caracol/MS, em região de forte vocação agrícola, com relevo "
    "favorável à mecanização e proximidade de rotas logísticas relevantes para o escoamento da produção "
    "e para o comércio regional com Paraguai e Bolívia."
)
chips = [
    "Caracol — MS", "400 ha (280 ha agricultáveis)", "70 km de Bela Vista/MS",
    "10 km da Rota Bioceânica", "Topografia de Planalto", "Forte Vocação Agrícola",
]
st.markdown("".join(f"<span class='dp-chip'>{c}</span>" for c in chips), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── DESTAQUE: POTENCIAL DE EXPANSÃO + PERFIL DO INVESTIMENTO ──
st.markdown('<div class="dp-feature">', unsafe_allow_html=True)
st.markdown('<div class="dp-badge-feature">Destaque do Investimento</div>', unsafe_allow_html=True)
st.markdown("<div class='dp-section-label'>Potencial de Expansão da Área Produtiva</div>", unsafe_allow_html=True)
st.markdown("### Margem para Ampliar a Área Agricultável")
st.write(
    "Além dos 280 hectares já agricultáveis, a propriedade tem potencial de abertura de mais 20 hectares, "
    "elevando a área produtiva para até 300 hectares — um ganho direto de capacidade produtiva sem "
    "necessidade de aquisição de área adicional."
)
e1, e2 = st.columns(2)
e1.metric("Área Agricultável Atual", "280 ha")
e2.metric("Área Agricultável Potencial", "300 ha")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='dp-section-label'>Perfil do Investimento</div>", unsafe_allow_html=True)
st.markdown("### Ativo Estratégico para Produtores, Fundos e Investidores do Agronegócio")
st.markdown(
    "<div class='dp-quote'>Oportunidade de aquisição de propriedade rural em região de forte vocação "
    "agrícola no Mato Grosso do Sul, com topografia de planalto favorável à mecanização, área "
    "agricultável consolidada e potencial de expansão imediato — um ativo estratégico para produtores, "
    "fundos e investidores do agronegócio, com proximidade a corredores logísticos relevantes como a "
    "Rota Bioceânica.</div>",
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── CONTATO ──
st.markdown(
    """
    <div class="dp-contact-box">
        <div class="dp-section-label" style="color:#E8D5B0;">Contato</div>
        <h3 style="color:white; margin-top:4px;">DarkPool Intermediação de Ativos</h3>
        <p style="color:#E8D5B0; font-style:italic;">Assessor Responsável</p>
        <p>📧 <a href="mailto:negocios@darkpool.com.br">negocios@darkpool.com.br</a></p>
        <p>💬 <a href="https://wa.me/554333369677" target="_blank">+55 43 3336-9677</a></p>
        <p>🌐 <a href="https://darkpool.com.br/" target="_blank">DarkPool.com.br</a></p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "Este documento é estritamente confidencial e foi preparado exclusivamente para fins informativos. "
    "As informações aqui contidas são baseadas em dados fornecidos pelo vendedor e não constituem "
    "auditoria ou due diligence. O destinatário não deverá reproduzir, distribuir ou utilizar este "
    "material sem autorização prévia por escrito da DarkPool Intermediação de Ativos."
)
