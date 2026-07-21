import requests
import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime, timezone

import streamlit as st

st.set_page_config(page_title="Gestão de Banca", layout="wide")

# ==========================================
# DESIGN VIBECODE SYSTEM (CSS CUSTOMIZADO)
# ==========================================
st.markdown("""
<style>
    /* Importação de fonte moderna e clean */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    /* Reset global de tipografia e fundo da aplicação */
    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
        background-color: #07090E !important; /* Preto puro/profundo */
        color: #E2E8F0 !important;
    }

    /* Estilização da Barra Lateral (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: #0B0E14 !important;
        border-right: 1px solid #1E293B !important;
    }

    /* Cards e Containers com estética Dark/Glassmorphism */
    div[data-testid="stMetric"], .stCard {
        background: linear-gradient(135deg, #0F172A 0%, #0B0F17 100%) !important;
        border: 1px solid #1E293B !important;
        border-radius: 12px !important;
        padding: 16px 20px !important;
        box-shadow: 0 8px 16px -4px rgba(0, 0, 0, 0.5) !important;
        transition: transform 0.2s ease, border-color 0.2s ease !important;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        border-color: #2563EB !important;
    }

    /* Estilização das métricas/KPIs */
    div[data-testid="stMetricLabel"] p {
        color: #94A3B8 !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }

    div[data-testid="stMetricValue"] {
        color: #F8FAFC !important;
        font-weight: 800 !important;
    }

    /* Botões Dinâmicos (Efeito Glow Vibecode) */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #1E3A8A 0%, #1E293B 100%) !important;
        color: #F8FAFC !important;
        border: 1px solid #2563EB !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-weight: 700 !important;
        letter-spacing: 0.3px !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15) !important;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        border-color: #60A5FA !important;
        color: #FFFFFF !important;
        transform: translateY(-2px) scale(1.01) !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.45) !important;
    }

    .stButton > button:active {
        transform: translateY(0px) scale(0.98) !important;
    }

    /* Input Fields (Caixas de texto e números) */
    .stTextInput input, .stNumberInput input, .stSelectbox > div > div {
        background-color: #0F172A !important;
        color: #F8FAFC !important;
        border: 1px solid #1E293B !important;
        border-radius: 8px !important;
        transition: border-color 0.2s ease !important;
    }

    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #3B82F6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
    }

    /* Tabelas e Dataframes */
    [data-testid="stDataFrame"] {
        background-color: #0F172A !important;
        border: 1px solid #1E293B !important;
        border-radius: 10px !important;
    }

    /* Limpeza de rodapés e menus padrões */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# CONEXÃO COM O SUPABASE
SUPABASE_URL = "https://nsrcevzonxssbtwtmuro.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5zcmNldnpvbnhzc2J0d3RtdXJvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODQ2MTA5NzgsImV4cCI6MjEwMDE4Njk3OH0.PFJuxdg8rIKxwn5glfCeypdeuLfL0zhmPKYliesVA98"

@st.cache_resource
def init_supabase():
    return create_client(
        supabase_url=SUPABASE_URL.strip(),
        supabase_key=SUPABASE_KEY.strip()
    )

supabase = init_supabase()

# --- SESSÃO E LOGIN ---
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
if "access_token" not in st.session_state:
    st.session_state.access_token = None

if st.session_state.usuario_logado is None:
    st.title("🔒 Login")
    email = st.text_input("E-mail").strip()
    senha = st.text_input("Senha", type="password")
    c1, c2 = st.columns(2)
    
    if c1.button("Entrar"):
        if not email or not senha:
            st.warning("Preencha e-mail e senha.")
        else:
            login_url = f"{SUPABASE_URL.rstrip('/')}/auth/v1/token?grant_type=password"
            headers = {
                "apikey": SUPABASE_KEY.strip(),
                "Content-Type": "application/json"
            }
            payload = {"email": email, "password": senha}
            
            res = requests.post(login_url, json=payload, headers=headers)
            if res.status_code == 200:
                dados = res.json()
                st.session_state.usuario_logado = dados["user"]
                st.session_state.access_token = dados["access_token"]
                st.success("Login efetuado com sucesso!")
                st.rerun()
            else:
                erro_info = res.json()
                erro_msg = erro_info.get("error_description") or erro_info.get("msg") or "E-mail ou senha incorretos."
                st.error(f"Erro no login: {erro_msg}")

    if c2.button("Criar Conta"):
        if not email or not senha:
            st.warning("Preencha e-mail e senha para criar a conta.")
        elif len(senha) < 6:
            st.warning("A senha precisa ter pelo menos 6 caracteres.")
        else:
            signup_url = f"{SUPABASE_URL.rstrip('/')}/auth/v1/signup"
            headers = {
                "apikey": SUPABASE_KEY.strip(),
                "Content-Type": "application/json"
            }
            payload = {"email": email, "password": senha}
            
            res = requests.post(signup_url, json=payload, headers=headers)
            if res.status_code in [200, 201]:
                st.success("Conta criada com sucesso! Clique em 'Entrar' para acessar.")
            else:
                erro_info = res.json()
                erro_msg = erro_info.get("msg") or erro_info.get("error_description") or res.text
                st.error(f"Erro ao criar conta: {erro_msg}")
    st.stop()

# Helper para requisições na API REST do Supabase com Token
def get_headers():
    return {
        "apikey": SUPABASE_KEY.strip(),
        "Authorization": f"Bearer {st.session_state.access_token}",
        "Content-Type": "application/json"
    }

# --- BUSCA DE DADOS GERAIS ---
@st.cache_data(ttl=60)
def carregar_dados(user_id, token):
    try:
        url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/apostas?user_id=eq.{user_id}&select=*"
        headers = {
            "apikey": SUPABASE_KEY.strip(),
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            df = pd.DataFrame(res.json())
            if not df.empty:
                df['created_at'] = pd.to_datetime(df['created_at'])
                df['lucro'] = df['retorno_bruto'] - df['valor_investido']
            return df
        else:
            st.error(f"Erro ao carregar dados: {res.text}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

df = carregar_dados(st.session_state.usuario_logado["id"], st.session_state.access_token)

# --- BARRA LATERAL (MENU) ---
st.sidebar.write(f"👤 **{st.session_state.usuario_logado['email']}**")
menu = st.sidebar.radio(
    "Navegação", 
    ["1. Dashboard & KPIs", "2. Nova Entrada", "3. Entradas Pendentes", "4. Histórico e Filtros"]
)

if st.sidebar.button("Sair"):
    st.session_state.usuario_logado = None
    st.session_state.access_token = None
    st.rerun()

# ==========================================
# SEÇÃO 1: DASHBOARD E KPIs
# ==========================================
if menu == "1. Dashboard & KPIs":
    st.title("📊 Indicadores de Desempenho")
    
    if df.empty:
        st.info("Sem dados cadastrados. Clique na opção '2. Nova Entrada' no menu da esquerda para registrar!")
    else:
        agora = datetime.now(timezone.utc)
        
        df_mensal = df[df['created_at'].dt.month == agora.month] if 'created_at' in df.columns else df
        uma_semana_atras = agora - pd.Timedelta(days=7)
        df_semanal = df[df['created_at'] >= uma_semana_atras] if 'created_at' in df.columns else df
        
        lucro_sem = df_semanal['lucro'].sum() if 'lucro' in df_semanal.columns else 0.0
        investido_sem = df_semanal['valor_investido'].sum() if 'valor_investido' in df_semanal.columns else 0.0
        roi_sem = (lucro_sem / investido_sem * 100) if investido_sem > 0 else 0
        
        lucro_mes = df_mensal['lucro'].sum() if 'lucro' in df_mensal.columns else 0.0
        investido_mes = df_mensal['valor_investido'].sum() if 'valor_investido' in df_mensal.columns else 0.0
        roi_mes = (lucro_mes / investido_mes * 100) if investido_mes > 0 else 0
        
        lucro_total = df['lucro'].sum() if 'lucro' in df.columns else 0.0
        abertas = df[df['resultado'] == 'Pendente'] if 'resultado' in df.columns else pd.DataFrame()
        valor_aberto = abertas['valor_investido'].sum() if not abertas.empty else 0.0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("ROI Semanal", f"{roi_sem:.2f}%", f"R$ {lucro_sem:.2f}")
        c2.metric("ROI Mensal", f"{roi_mes:.2f}%", f"R$ {lucro_mes:.2f}")
        c3.metric("Lucro Total Acumulado", f"R$ {lucro_total:.2f}")
        c4.metric("Em Aberto (Pendentes)", f"{len(abertas)} Entradas", f"R$ {valor_aberto:.2f}", delta_color="off")

# ==========================================
# SEÇÃO 2: NOVA ENTRADA
# ==========================================
elif menu == "2. Nova Entrada":
    st.title("➕ Registrar Entrada")
    
    tipo_entrada = st.radio("Selecione a Modalidade", ["Sports Betting", "Cassino"], horizontal=True)
    
    with st.form("form_entrada"):
        casa_de_aposta = st.text_input("Qual Casa de Aposta?")
        dono_da_conta = st.text_input("Dono da Conta")
        valor_investido = st.number_input("Valor Investido (R$)", min_value=0.01, step=1.0)
        
        estrategia = ""
        resultado = "Pendente"
        retorno_bruto = 0.0
        data_hora_manual = ""
        
        if tipo_entrada == "Sports Betting":
            estrategia = st.selectbox("Estratégia", ["Cashout", "Punter", "Delay", "Duplo Green", "Surebet", "Bug", "Outros"])
            
            st.markdown("**Data e Hora do Jogo (Digitado Manualmente):**")
            c_data, c_hora = st.columns(2)
            data_str = c_data.text_input("Data (ex: 21/07/2026)", placeholder="ex: 21/07/2026")
            hora_str = c_hora.text_input("Hora (ex: 16:00)", placeholder="ex: 16:00")
            data_hora_manual = f"{data_str} {hora_str}".strip()
            
            resultado = st.selectbox("Resultado Inicial", ["Pendente", "Green", "Red", "Cashout Parcial"])
            
            if resultado == "Green":
                retorno_bruto = st.number_input("Retorno Total (Green) R$", min_value=0.0)
            elif resultado == "Red":
                retorno_bruto = 0.0
                st.info("Retorno será R$ 0.00")
            elif resultado == "Cashout Parcial":
                retorno_bruto = st.number_input("Valor Exato do Cashout (R$)", min_value=0.0, step=0.1)
                
            if estrategia in ["Duplo Green", "Surebet"]:
                st.warning("⚠️ Entrada marcada como estratégia múltipla.")
                
        elif tipo_entrada == "Cassino":
            estrategia = st.selectbox("Estratégia", ["Deposite e ganhe", "Deposite e jogue", "Bug", "Missão", "Outros"])
            resultado = st.selectbox("Resultado Inicial", ["Pendente", "Concluído (Green)", "Red"])
            
            if resultado == "Concluído (Green)":
                retorno_bruto = st.number_input("Retorno Total R$", min_value=0.0)
            elif resultado == "Red":
                retorno_bruto = 0.0

        if st.form_submit_button("Salvar Entrada"):
            dados = {
                "user_id": st.session_state.usuario_logado["id"],
                "tipo": tipo_entrada,
                "casa_de_aposta": casa_de_aposta,
                "dono_da_conta": dono_da_conta,
                "estrategia": estrategia,
                "valor_investido": valor_investido,
                "resultado": resultado,
                "retorno_bruto": retorno_bruto,
                "data_hora_jogo": data_hora_manual if tipo_entrada == "Sports Betting" else None
            }
            url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/apostas"
            res = requests.post(url, json=dados, headers=get_headers())
            
            if res.status_code in [200, 201]:
                st.success("Entrada salva com sucesso!")
                carregar_dados.clear()
                st.rerun()
            else:
                st.error(f"Erro ao salvar: {res.text}")

# ==========================================
# SEÇÃO 3: ENTRADAS PENDENTES
# ==========================================
elif menu == "3. Entradas Pendentes":
    st.title("⏳ Entradas Pendentes / A Classificar")
    
    if df.empty or 'resultado' not in df.columns:
        st.info("Nenhuma entrada cadastrada.")
    else:
        df_pendentes = df[df['resultado'] == 'Pendente']
        
        if df_pendentes.empty:
            st.success("🎉 Nenhuma aposta pendente no momento! Todas estão classificadas.")
        else:
            st.warning(f"Existem **{len(df_pendentes)}** apostas aguardando resultado.")
            
            colunas_exibicao = [col for col in ['data_hora_jogo', 'tipo', 'casa_de_aposta', 'estrategia', 'valor_investido', 'dono_da_conta'] if col in df_pendentes.columns]
            st.dataframe(df_pendentes[colunas_exibicao], use_container_width=True)

            st.markdown("---")
            st.subheader("📝 Classificar Entrada Selecionada")
            
            apostas_opcoes = df_pendentes.apply(
                lambda r: f"ID: {r['id'][:4]}... | {r['tipo']} | {r['casa_de_aposta']} | {r['estrategia']} | R$ {r['valor_investido']:.2f}", axis=1
            )
            
            id_selecionado = st.selectbox(
                "Escolha a entrada para atualizar:", 
                options=df_pendentes['id'].tolist(),
                format_func=lambda x: apostas_opcoes[df_pendentes['id'] == x].values[0]
            )
            
            aposta_atual = df_pendentes[df_pendentes['id'] == id_selecionado].iloc[0]
            
            with st.form("form_classificacao"):
                st.write(f"**Atualizando:** {aposta_atual['casa_de_aposta']} ({aposta_atual['estrategia']}) - Investido: R$ {aposta_atual['valor_investido']:.2f}")
                
                novo_resultado = st.selectbox("Novo Resultado", ["Green", "Red", "Cashout Parcial"])
                
                novo_retorno = 0.0
                if novo_resultado == "Green":
                    novo_retorno = st.number_input("Valor Total do Retorno (R$)", min_value=0.01, step=0.1)
                elif novo_resultado == "Cashout Parcial":
                    novo_retorno = st.number_input("Valor Digitado do Cashout (R$)", min_value=0.01, step=0.01)
                elif novo_resultado == "Red":
                    st.info("Retorno definido como R$ 0.00")
                
                if st.form_submit_button("Confirmar Classificação"):
                    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/apostas?id=eq.{id_selecionado}"
                    patch_data = {
                        "resultado": novo_resultado,
                        "retorno_bruto": novo_retorno
                    }
                    res = requests.patch(url, json=patch_data, headers=get_headers())
                    
                    if res.status_code in [200, 204]:
                        st.success("Entrada classificada com sucesso!")
                        carregar_dados.clear()
                        st.rerun()
                    else:
                        st.error(f"Erro ao atualizar: {res.text}")

# ==========================================
# SEÇÃO 4: HISTÓRICO E FILTROS
# ==========================================
elif menu == "4. Histórico e Filtros":
    st.title("📋 Histórico Geral e Filtros")
    
    if df.empty:
        st.info("Nenhuma entrada cadastrada.")
    else:
        st.subheader("🔍 Filtros Avançados (Multisseleção)")
        c1, c2, c3 = st.columns(3)
        
        filtro_tipo = c1.multiselect("Modalidade/Tipo", df['tipo'].unique(), default=df['tipo'].unique())
        filtro_status = c2.multiselect("Resultado/Status", df['resultado'].unique(), default=df['resultado'].unique())
        filtro_estrategia = c3.multiselect("Estratégia", df['estrategia'].unique(), default=df['estrategia'].unique())
        
        c4, c5 = st.columns(2)
        filtro_casa = c4.multiselect("Casa de Aposta", df['casa_de_aposta'].unique(), default=df['casa_de_aposta'].unique())
        filtro_dono = c5.multiselect("Dono da Conta", df['dono_da_conta'].unique(), default=df['dono_da_conta'].unique())
        
        df_filtrado = df[
            (df['tipo'].isin(filtro_tipo)) &
            (df['resultado'].isin(filtro_status)) &
            (df['estrategia'].isin(filtro_estrategia)) &
            (df['casa_de_aposta'].isin(filtro_casa)) &
            (df['dono_da_conta'].isin(filtro_dono))
        ]
        
        st.write(f"Exibindo **{len(df_filtrado)}** registros encontrados:")
        
        cols_para_exibir = ['data_hora_jogo', 'tipo', 'casa_de_aposta', 'dono_da_conta', 'estrategia', 'resultado', 'valor_investido', 'retorno_bruto', 'lucro']
        cols_existentes = [c for c in cols_para_exibir if c in df_filtrado.columns]
        
        st.dataframe(df_filtrado[cols_existentes], use_container_width=True)
