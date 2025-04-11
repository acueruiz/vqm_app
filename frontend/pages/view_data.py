import streamlit as st
import requests
import pandas as pd
import os

API_URL = os.getenv("API_URL", "https://vqm-app.onrender.com")

# Configuración de la página
st.set_page_config(page_title="VQM MDM - Datos", layout="wide", page_icon="📋")

# Encabezado
st.markdown('<div class="header">VQM MDM - VISUALIZACIÓN DE DATOS</div>', unsafe_allow_html=True)

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

# modificación de datos
with st.sidebar.expander("📊 Modificación de Datos", expanded=False):
    st.page_link("pages/edit_datos_mdms.py", label="Modificar Datos MDM", icon="⚙️")
    st.page_link("pages/edit_vqm_temp.py", label="Modificar Datos Teóricos VQM Temp", icon="🌡️")
    
# administración
with st.sidebar.expander("⚙️ Administración", expanded=False):
    st.page_link("pages/users.py", label="Gestión de usuarios", icon="👥")
    st.page_link("pages/correos.py", label="Gestión de correos", icon="📨")

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

# Cargar datos de la API Flask
@st.cache_data
def get_mdm_data():
    response = requests.get(f"{API_URL}/vqm_mdm")
    if response.status_code == 200:
        df = pd.DataFrame(response.json())

        # Verificar que la columna 'fecha' existe y convertirla a datetime
        if "fecha" in df.columns:
            df["fecha"] = pd.to_datetime(df["fecha"], errors='coerce')

        return df
    else:
        st.error("❌ Error al obtener detalles de MDMs.")
        return pd.DataFrame()

df_mdm = get_mdm_data()

# Verifica que el DataFrame no esté vacío antes de continuar
if df_mdm.empty:
    st.warning("No hay datos disponibles.")
    st.stop()

# Filtrar solo las columnas necesarias y en el orden específico
df_mdm = df_mdm[["titulo", "fecha", "operador", "vqm_bascula_conforme", "vqm_masico_conforme"]]

# Filtros de búsqueda
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    mdm_selected = st.selectbox("MDM", ["Todos"] + list(df_mdm["titulo"].unique()))

with col2:
    fecha_inicio = st.date_input("Desde fecha:")

with col3:
    fecha_fin = st.date_input("Hasta fecha:")

with col4:
    buscar = st.button("🔍 Buscar", use_container_width=True)

if buscar:
    st.session_state.filtrar = True

# Filtrar datos según selección
if "filtrar" in st.session_state and st.session_state.filtrar:
    if mdm_selected != "Todos":
        df_mdm = df_mdm[df_mdm["titulo"] == mdm_selected]

    if "fecha" in df_mdm.columns:
        df_mdm = df_mdm[(df_mdm["fecha"] >= pd.to_datetime(fecha_inicio)) & 
                        (df_mdm["fecha"] <= pd.to_datetime(fecha_fin))]

# Mostrar tabla con estilos personalizados
if not df_mdm.empty:
    df_mdm = df_mdm.sort_values(by="fecha", ascending=False).reset_index(drop=True)

    def highlight_non_conform(val):
        if val is False:  # Resaltar valores no conformes
            return 'background-color: #FF4B4B; color: white; font-weight: bold;'
        return ''
    
    # Definir alias para las columnas
    column_aliases = {
        "titulo": "MDM",
        "fecha": "Fecha",
        "operador": "Operador",
        "vqm_bascula_conforme": "Bascula Conforme",
        "vqm_masico_conforme": "Másico Conforme"
    }

    # Renombrar las columnas en el DataFrame
    df_mdm = df_mdm.rename(columns=column_aliases)

    # Mostrar la tabla en Streamlit con formato y alias en los encabezados
    st.dataframe(
        df_mdm.style.applymap(highlight_non_conform, 
                            subset=["Bascula Conforme", "Másico Conforme"]),
        use_container_width=True
    )

else:
    st.warning("No se encontraron datos para los filtros seleccionados.")

# Botones de exportación
col1, col2 = st.columns([1, 1])

with col1:
    if st.button("📥 Exportar a CSV"):
        df_mdm.to_csv("datos_vqm.csv", index=False)
        st.success("Archivo CSV generado correctamente.")

with col2:
    if st.button("📥 Exportar a Excel"):
        df_mdm.to_excel("datos_vqm.xlsx", index=False)
        st.success("Archivo Excel generado correctamente.")
