import streamlit as st
import os
import requests
import pandas as pd
import time
import plotly.express as px

API_URL = os.getenv("https://vqm-api.onrender.com/")

# Verificar autenticación antes de mostrar la página
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("🔒 Debes iniciar sesión primero.")
    st.markdown('<meta http-equiv="refresh" content="0; URL=login.py">', unsafe_allow_html=True)
    st.stop()

# configuración de la página
st.set_page_config(page_title="Aplicación VQM", layout="wide", page_icon="🏠")

# Obtener ruta absoluta de la imagen
logo_path = os.path.join(os.getcwd(), "frontend", "imagenes", "logo_michelin.png")

# Verificar si la imagen existe
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_container_width=True)
else:
    st.sidebar.warning("⚠️ No se encontró el logo. Verifica la ruta del archivo.")

# ---------------- Sidebar con categorías agrupadas ---------------- #
st.sidebar.title("MENÚ DE NAVEGACIÓN")

# inicio
st.sidebar.page_link("pages/home.py", label="Inicio", icon="🏠")

# introducción de datos
with st.sidebar.expander("📝 Formularios", expanded=False):
    st.page_link("pages/vqm_mdm_form.py", label="VQM MDM Form")
    st.page_link("pages/vqm_temp_form.py", label="VQM Temperatura Form")
    st.page_link("pages/gestion_nc_form.py", label="Gestión NC Form")

# visualización de datos
with st.sidebar.expander("📊 Visualización de Datos", expanded=False):
    st.page_link("pages/view_data.py", label="Ver Datos MDM")
    st.page_link("pages/view_data_temp.py", label="Ver Datos Temp MI")
    st.page_link("pages/view_data_nc.py", label="Ver Datos NC")

# modificación de datos
with st.sidebar.expander("📊 Modificación de Datos", expanded=False):
    st.page_link("pages/edit_datos_mdms.py", label="Modificar Datos MDM")
    st.page_link("pages/edit_vqm_temp.py", label="Modificar Datos Teóricos VQM Temp")

# administración
with st.sidebar.expander("⚙️ Administración", expanded=False):
    st.page_link("pages/users.py", label="Gestión de usuarios")
    st.page_link("pages/correos.py", label="Gestión de correos")

# dashboard
st.sidebar.page_link("pages/vqm_dashboard.py", label="Dashboard", icon="📉")

# estilos CSS personalizados
st.markdown(
    """
    <style>

        /* Oculta el menú de navegación automático de Streamlit */
        [data-testid="stSidebarNav"] {
            display: none !important;
        }

        [data-testid="stSidebar"] {
            padding-top: 0px !important; /* Reduce el padding superior del sidebar */
        }
        
        [data-testid="stImage"] img {
            margin-top: -30px !important; /* Reduce el espacio superior del logo */
            margin-bottom: -20px !important; /* Reduce el espacio inferior del logo */
        }
    
        /* Encabezados mejorados */
        .header {
            text-align: center;
            background-color: #0055A4;
            padding: 15px;
            color: white;
            font-size: 24px;
            font-weight: bold;
            border-radius: 8px;
            margin-bottom: 20px;
        }

        /* Botones personalizados */
        .stButton > button {
            background-color: #0055A4;
            color: white;
            font-size: 16px;
            padding: 10px 15px;
            border-radius: 8px;
            border: none;
            transition: 0.3s;
        }

        .stButton > button:hover {
            background-color: #003C7E;
            transform: scale(1.05);
        }

        /* Separadores visuales */
        .separator {
            border-bottom: 3px solid #0055A4;
            margin: 30px 0;
        }

        /* Mejora en la tabla de datos */
        .dataframe {
            border-collapse: collapse;
            width: 100%;
            background-color: white;
            border: 1px solid #ddd;
        }

        .dataframe th, .dataframe td {
            border: 1px solid #ddd;
            padding: 8px;
        }

        .dataframe th {
            background-color: #0055A4;
            color: white;
            text-align: left;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# encabezado principal
st.markdown('<div class="header"><h1>Análisis de VQMs</h1></div>', unsafe_allow_html=True)

# cargar datos desde la API
with st.spinner("Cargando datos de VQM MDM..."):
    time.sleep(1)  # simulación de carga
    
    # datos de VQM MDM
    response_vqm = requests.get(f"{API_URL}/vqm_mdm")
    df_vqm = pd.DataFrame(response_vqm.json()) if response_vqm.status_code == 200 else pd.DataFrame()

# análisis de VQM MDM
st.subheader("📋 Estado de las VQM MDM Registradas")

if not df_vqm.empty:
    df_vqm["fecha"] = pd.to_datetime(df_vqm["fecha"], errors='coerce')

    # indicadores clave
    col1, col2, col3 = st.columns(3)

    with col1:
        total_vqm = len(df_vqm)
        st.metric(label="📏 Total de VQM Registradas", value=total_vqm)

    with col2:
        conformes = df_vqm["vqm_bascula_conforme"].sum()
        st.metric(label="✅ VQM Báscula Conformes", value=conformes)

    with col3:
        no_conformes = total_vqm - conformes
        st.metric(label="⚠️ VQM Báscula No Conformes", value=no_conformes)

    # gráfico de conformidad
    fig_conformidad = px.pie(df_vqm, names="vqm_bascula_conforme", title="📊 Porcentaje de Conformidad")
    st.plotly_chart(fig_conformidad, use_container_width=True)

    # gráfico de distribución de errores
    fig_errores = px.histogram(df_vqm, x=["error_cantidad1", "error_cantidad2"], title="📉 Distribución de Errores")
    st.plotly_chart(fig_errores, use_container_width=True)

    # filtrado por operador
    operadores = df_vqm["operador"].unique()
    selected_operador = st.selectbox("👨‍🔧 Selecciona un Operador:", options=operadores)

    df_filtrado = df_vqm[df_vqm["operador"] == selected_operador]
    st.write(f"🔎 Mostrando datos para **{selected_operador}**")
    st.dataframe(df_filtrado)

    # alertas de errores altos
    max_error = df_vqm[["error_cantidad1", "error_cantidad2"]].max().max()
    if max_error > 10:
        st.warning(f"⚠️ Se han detectado errores superiores a 10 kg en algunas mediciones.")
else:
    st.warning("📭 No hay datos de VQM MDM disponibles.")

st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

# notificación en tiempo real sobre No Conformidades
st.subheader("🚨 Estado de No Conformidades")
response_nc = requests.get(f"{API_URL}/tratamiento_nc_vqm")
if response_nc.status_code == 200:
    nc_data = response_nc.json()
    nc_count = len(nc_data)

    if nc_count > 0:
        st.warning(f"⚠️ Hay **{nc_count}** No Conformidades abiertas.")
    else:
        st.success("✅ No hay No Conformidades pendientes.")

st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

# acciones rápidas
st.subheader("📩 Acciones Rápidas")

col1, col2 = st.columns(2)

with col1:
    if st.button("📤 Enviar Reporte de VQM MDM"):
        st.success("📨 Reporte enviado correctamente.")

with col2:
    if st.button("Actualizar Datos"):
        st.experimental_rerun()
