import streamlit as st
import requests
import pandas as pd
import os

# Configuración de la API Flask
API_URL = "http://127.0.0.1:5000/vqm"

# Configuración de la página
st.set_page_config(page_title="VQM Temperatura MI10 - Datos", layout="wide")

# Encabezado
st.markdown('<div class="header">VQM Temperatura MI10 - VISUALIZACIÓN DE DATOS</div>', unsafe_allow_html=True)

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
st.sidebar.page_link("home.py", label="Inicio", icon="🏠")

# formularios
with st.sidebar.expander("📝 Formularios", expanded=False):
    st.page_link("pages/vqm_mdm_form.py", label="VQM MDM Form", icon="📝")
    st.page_link("pages/vqm_temp_form.py", label="VQM Temperatura Form", icon="🌡️")
    st.page_link("pages/gestion_nc_form.py", label="Gestión NC Form", icon="⚠️")

# visualización de Datos
with st.sidebar.expander("📊 Visualización de Datos", expanded=False):
    st.page_link("pages/view_data.py", label="Ver Datos MDM", icon="📋")
    st.page_link("pages/view_data_temp.py", label="Ver Datos Temp MI", icon="🌡️")
    st.page_link("pages/view_data_nc.py", label="Ver Datos NC", icon="⚠️")

# administración
with st.sidebar.expander("⚙️ Administración", expanded=False):
    st.page_link("pages/users.py", label="Usuarios", icon="👥")

# dashboard
st.sidebar.page_link("pages/vqm_dashboard.py", label="Dashboard", icon="📊")

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

# Cargar datos de la API Flask
@st.cache_data
def get_temp_mi10_data():
    response = requests.get(f"{API_URL}/vqm_temperatura_mi10")
    if response.status_code == 200:
        df = pd.DataFrame(response.json())

        # Convertir fecha a datetime
        if "fecha" in df.columns:
            df["fecha"] = pd.to_datetime(df["fecha"], errors='coerce')

        return df
    else:
        st.error("❌ Error al obtener datos de VQM Temperatura MI10.")
        return pd.DataFrame()

df_temp_mi10 = get_temp_mi10_data()

# Verificar que el DataFrame no esté vacío antes de continuar
if df_temp_mi10.empty:
    st.warning("No hay datos disponibles.")
    st.stop()

# Filtros de búsqueda
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    maquina_selected = st.selectbox("Máquina", ["Todas"] + list(df_temp_mi10["titulo"].unique()))

with col2:
    trimestre_selected = st.selectbox("Trimestre", ["Todos"] + list(df_temp_mi10["trimestre_anio"].unique()))

with col3:
    if st.button("🔍 Filtrar"):
        st.session_state.filtrar = True

# Filtrar datos según selección
if "filtrar" in st.session_state and st.session_state.filtrar:
    if maquina_selected != "Todas":
        df_temp_mi10 = df_temp_mi10[df_temp_mi10["titulo"] == maquina_selected]

    if trimestre_selected != "Todos":
        df_temp_mi10 = df_temp_mi10[df_temp_mi10["trimestre_anio"] == trimestre_selected]

# Mostrar tabla con funcionalidades adicionales
if not df_temp_mi10.empty:
    df_temp_mi10 = df_temp_mi10.sort_values(by="fecha", ascending=False)
    df_temp_mi10 = df_temp_mi10.reset_index(drop=True)
    
    def highlight_non_conform(val):
        if val is False:  # Resalta los NO CONFORMES en rojo
            return 'background-color: #FF4B4B; color: white; font-weight: bold;'
        return ''

    # Mostrar en Streamlit con resaltado de NO CONFORMIDADES
    st.dataframe(df_temp_mi10.style.applymap(highlight_non_conform, subset=["vqm_conforme"]))

else:
    st.warning("No se encontraron datos para los filtros seleccionados.")

# Botones adicionales
col1, col2 = st.columns([1, 1])

with col1:
    if st.button("📥 Exportar a CSV"):
        df_temp_mi10.to_csv("datos_vqm_temperatura_mi10.csv", index=False)
        st.success("Archivo CSV generado correctamente.")

with col2:
    if st.button("📥 Exportar a Excel"):
        df_temp_mi10.to_excel("datos_vqm_temperatura_mi10.xlsx", index=False)
        st.success("Archivo Excel generado correctamente.")