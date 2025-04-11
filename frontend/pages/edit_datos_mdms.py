import streamlit as st
import requests
import pandas as pd
import os

API_URL = "https://vqm-app.onrender.com/vqm"

st.set_page_config(page_title="Modificar Datos MDM", layout="wide", page_icon="🛠")

# obtener ruta absoluta de la imagen
logo_path = os.path.join(os.getcwd(), "frontend", "imagenes", "logo_michelin.png")

# verificar si la imagen existe
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
with st.sidebar.expander("🛠 Modificación de Datos", expanded=False):
    st.page_link("pages/edit_datos_mdms.py", label="Modificar Datos MDM")
    st.page_link("pages/edit_vqm_temp.py", label="Modificar VQM Temp")

# administración
with st.sidebar.expander("⚙️ Administración", expanded=False):
    st.page_link("pages/users.py", label="Gestión de usuarios")
    st.page_link("pages/correos.py", label="Gestión de correos")

# dashboard
st.sidebar.page_link("pages/vqm_dashboard.py", label="Dashboard", icon="📊")

# estilos CSS personalizados
st.markdown(
    """
    <style>
        /* Oculta el menú de navegación automático de Streamlit */
        [data-testid="stSidebarNav"] { display: none !important; }
        [data-testid="stSidebar"] { padding-top: 0px !important; }
        
        [data-testid="stImage"] img {
            margin-top: -30px !important;
            margin-bottom: -20px !important;
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
        .separator { border-bottom: 3px solid #0055A4; margin: 30px 0; }

        /* Tabla de datos */
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

st.title("🔧 Modificar Datos MDM")

@st.cache_data
def get_mdms_data():
    response = requests.get(f"{API_URL}/datos_mdms")
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        st.error("Error al cargar los datos de MDM.")
        return pd.DataFrame()

df = get_mdms_data()

if df.empty:
    st.warning("No hay datos de MDM disponibles.")
    st.stop()

# Selección del masico para editar
masicos = df["masico"].unique()
selected_masico = st.selectbox("Selecciona el MDM:", masicos)

# Filtrar datos del masico seleccionado
df_filtered = df[df["masico"] == selected_masico]

if not df_filtered.empty:
    row = df_filtered.iloc[0]
    
    kw = st.number_input("KW", value=row["kw"], step=0.1)
    id_dosificador = st.text_input("ID Dosificador", row["id_dosificador"])
    valor_test1 = st.number_input("Valor Test 1", value=row["valor_test1"], step=0.1)
    tolerancia1 = st.number_input("Tolerancia 1", value=row["tolerancia1"], step=0.1)
    valor_test2 = st.number_input("Valor Test 2", value=row["valor_test2"], step=0.1)
    tolerancia2 = st.number_input("Tolerancia 2", value=row["tolerancia2"], step=0.1)
    circuito = st.text_input("Circuito", row["circuito"])
    bascula = st.text_input("Báscula", row["bascula"])
    id_bascula = st.text_input("ID Báscula", row["id_bascula"])
    id_masas_patron = st.text_input("ID Masas Patrón", row["id_masas_patron"])
    vr_masas_patron = st.number_input("VR Masas Patrón", value=row["vr_masas_patron"], step=0.1)
    tolerancia_vr = st.number_input("Tolerancia VR", value=row["tolerancia_vr"], step=0.1)
    tolerancia_cero = st.number_input("Tolerancia Cero", value=row["tolerancia_cero"], step=0.1)

    if st.button("💾 Guardar Cambios"):
        updated_data = {
            "masico": selected_masico,
            "kw": kw,
            "id_dosificador": id_dosificador,
            "valor_test1": valor_test1,
            "tolerancia1": tolerancia1,
            "valor_test2": valor_test2,
            "tolerancia2": tolerancia2,
            "circuito": circuito,
            "bascula": bascula,
            "id_bascula": id_bascula,
            "id_masas_patron": id_masas_patron,
            "vr_masas_patron": vr_masas_patron,
            "tolerancia_vr": tolerancia_vr,
            "tolerancia_cero": tolerancia_cero
        }
        response = requests.put(f"{API_URL}/datos_mdms/{selected_masico}", json=updated_data)
        if response.status_code == 200:
            st.success("✅ Datos actualizados correctamente.")
        else:
            st.error("❌ Error al actualizar los datos.")
else:
    st.warning("No se encontraron datos para el MDM seleccionado.")