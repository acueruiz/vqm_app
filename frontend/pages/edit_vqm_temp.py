import streamlit as st
import requests
import pandas as pd
import os

API_URL = "https://vqm-app.onrender.com"

st.set_page_config(page_title="Modificar VQM Temperatura", layout="wide", page_icon="🛠")

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
    st.page_link("pages/vqm_mdm_form.py", label="VQM MDM Form", icon="📝")
    st.page_link("pages/vqm_temp_form.py", label="VQM Temperatura Form", icon="🌡️")
    st.page_link("pages/gestion_nc_form.py", label="Gestión NC Form", icon="⚠️")

# visualización de datos
with st.sidebar.expander("📊 Visualización de Datos", expanded=False):
    st.page_link("pages/view_data.py", label="Histórico VQMs MDM", icon="📋")
    st.page_link("pages/view_data_temp.py", label="Histórico VQMs temperaturas MI", icon="🌡️")
    st.page_link("pages/view_data_nc.py", label="Histórico VQMs no conformes", icon="⚠️")

# modificación de datos
with st.sidebar.expander("🛠 Modificación de Datos", expanded=False):
    st.page_link("pages/edit_datos_mdms.py", label="Modificar Datos MDM", icon="⚙️")
    st.page_link("pages/edit_vqm_temp.py", label="Modificar Datos Teóricos VQM Temp", icon="🌡️")

# administración
with st.sidebar.expander("⚙️ Administración", expanded=False):
    st.page_link("pages/users.py", label="Gestión de usuarios", icon="👥")
    st.page_link("pages/correos.py", label="Gestión de correos", icon="📨")

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

st.title("🔧 Modificar Datos de VQM Temperatura")

@st.cache_data
def get_temperatura_data():
    response = requests.get(f"{API_URL}/vqm_temperatura")
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        st.error("Error al cargar los datos de temperatura.")
        return pd.DataFrame()

df = get_temperatura_data()

if df.empty:
    st.warning("No hay datos de temperatura disponibles.")
    st.stop()

# Selección de la máquina para editar
maquinas = df["maquina"].unique()
selected_maquina = st.selectbox("Selecciona la máquina:", maquinas)

# Filtrar datos de la máquina seleccionada
df_filtered = df[df["maquina"] == selected_maquina]

if not df_filtered.empty:
    row = df_filtered.iloc[0]
    apelacion = st.text_input("Apelación", row["apelacion"])
    receta = st.text_input("Receta", row["receta"])
    temperatura_caida = st.number_input("Temperatura caída", value=row["temperatura_caida"], step=0.1)
    media_calificacion = st.number_input("Media calificación", value=row["media_calificacion"], step=0.1)
    fecha_calificacion = st.date_input("Fecha de calificación", pd.to_datetime(row["fecha_calificacion"]))
    operario = st.text_input("Operario", row["operario"])

    if st.button("💾 Guardar Cambios"):
        updated_data = {
            "maquina": selected_maquina,
            "apelacion": apelacion,
            "receta": receta,
            "temperatura_caida": temperatura_caida,
            "media_calificacion": media_calificacion,
            "fecha_calificacion": str(fecha_calificacion),
            "operario": operario,
        }
        response = requests.put(f"{API_URL}/vqm_temperatura/{selected_maquina}", json=updated_data)
        if response.status_code == 200:
            st.success("✅ Datos actualizados correctamente.")
        else:
            st.error("❌ Error al actualizar los datos.")
else:
    st.warning("No se encontraron datos para la máquina seleccionada.")
