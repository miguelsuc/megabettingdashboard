import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime, timezone

st.set_page_config(page_title="Gestão de Banca", layout="wide")

# CONEXÃO COM O SUPABASE
SUPABASE_URL = "SUA_API_URL_AQUI"
SUPABASE_KEY = "SUA_CHAVE_ANON_AQUI"

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# --- SESSÃO E LOGIN ---
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

if st.session_state.usuario_logado is None:
    st.title("🔒 Login")
    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")
    c1, c2 = st.columns(2)
    if c1.button("Entrar"):
        try:
            resposta = supabase.auth.sign_in_with_password({"email": email, "password": senha})
            st.session_state.usuario_logado = resposta.user
            st.rerun()
        except Exception:
            st.error("E-mail/Senha inválidos.")
    if c2.button("Criar Conta"):
        try:
            supabase.auth.sign_up({"email": email, "password": senha})
            st.success("Conta criada! Tente logar.")
        except Exception as e:
            st.error(f"Erro: {e}")
    st.stop()

# --- BUSCA DE DADOS GERAIS ---
@st.cache_data(ttl=60)
def carregar_dados():
    res = supabase.table("apostas").select("*").execute()
    df = pd.DataFrame(res.data)
    if not df.empty:
        # Converter a data de lançamento interna para datetime para poder filtrar semana/mês
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['lucro'] = df['retorno_bruto'] - df['valor_investido']
    return df

df = carregar_dados()

# --- BARRA LATERAL (MENU) ---
st.sidebar.write(f"👤 **{st.session_state.usuario_logado.email}**")
menu = st.sidebar.radio(
    "Navegação", 
    ["1. Dashboard & KPIs", "2. Nova Entrada", "3. Entradas Pendentes", "4. Histórico e Filtros"]
)

if st.sidebar.button("Sair"):
    st.session_state.usuario_logado = None
    st.rerun()

# ==========================================
# SEÇÃO 1: DASHBOARD E KPIs
# ==========================================
if menu == "1. Dashboard & KPIs":
    st.title("📊 Indicadores de Desempenho")
    
    if df.empty:
        st.info("Sem dados. Vá para 'Nova Entrada' para começar.")
    else:
        # Usando a data interna automatizada para filtrar semana e mês
        agora = datetime.now(timezone.utc)
        
        df_mensal = df[df['created_at'].dt.month == agora.month]
        uma_semana_atras = agora - pd.Timedelta(days=7)
        df_semanal = df[df['created_at'] >= uma_semana_atras]
        
        # Cálculos de ROI
        lucro_sem = df_semanal['lucro'].sum()
        investido_sem = df_semanal['valor_investido'].sum()
        roi_sem = (lucro_sem / investido_sem * 100) if investido_sem > 0 else 0
        
        lucro_mes = df_mensal['lucro'].sum()
        investido_mes = df_mensal['valor_investido'].sum()
        roi_mes = (lucro_mes / investido_mes * 100) if investido_mes > 0 else 0
        
        lucro_total = df['lucro'].sum()
        abertas = df[df['resultado'] == 'Pendente']
        valor_aberto = abertas['valor_investido'].sum()

        # Layout dos KPIs
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("ROI Semanal", f"{roi_sem:.2f}%", f"R$ {lucro_sem:.2f}")
        c2.metric("ROI Mensal", f"{roi_mes:.2f}%", f"R$ {lucro_mes:.2f}")
        c3.metric("Lucro Total Acumulado", f"R$ {lucro_total:.2f}")
        c4.metric("Em Aberto (Pendentes)", f"{len(abertas)} Entradas", f"R$ {valor_aberto:.2f}", delta_color="off")

# ==========================================
# SEÇÃO 2: NOVA ENTRADA (FORMULÁRIOS CONDICIONAIS)
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
        
        # --- LÓGICA: SPORTS BETTING ---
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
                
        # --- LÓGICA: CASSINO ---
        elif tipo_entrada == "Cassino":
            estrategia = st.selectbox("Estratégia", ["Deposite e ganhe", "Deposite e jogue", "Bug", "Missão", "Outros"])
            resultado = st.selectbox("Resultado Inicial", ["Pendente", "Concluído (Green)", "Red"])
            
            if resultado == "Concluído (Green)":
                retorno_bruto = st.number_input("Retorno Total R$", min_value=0.0)
            elif resultado == "Red":
                retorno_bruto = 0.0

        if st.form_submit_button("Salvar Entrada"):
            dados = {
                "tipo": tipo_entrada,
                "casa_de_aposta": casa_de_aposta,
                "dono_da_conta": dono_da_conta,
                "estrategia": estrategia,
                "valor_investido": valor_investido,
                "resultado": resultado,
                "retorno_bruto": retorno_bruto,
                "data_hora_jogo": data_hora_manual if tipo_entrada == "Sports Betting" else None
            }
            supabase.table("apostas").insert(dados).execute()
            st.success("Entrada salva com sucesso!")
            carregar_dados.clear()
            st.rerun()

# ==========================================
# SEÇÃO 3: ENTRADAS PENDENTES E CLASSIFICAÇÃO
# ==========================================
elif menu == "3. Entradas Pendentes":
    st.title("⏳ Entradas Pendentes / A Classificar")
    
    if df.empty:
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
                    supabase.table("apostas").update({
                        "resultado": novo_resultado,
                        "retorno_bruto": novo_retorno
                    }).eq("id", id_selecionado).execute()
                    
                    st.success("Entrada classificada com sucesso!")
                    carregar_dados.clear()
                    st.rerun()

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
        
        # Aplicação dos Filtros
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
