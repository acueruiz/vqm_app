import streamlit as st
import requests
import pandas as pd
from sidebar import mostrar_sidebar
from verificar_autenticacion import verificar_autenticacion
from styles import estilos_css

API_URL = "http://127.0.0.1:5000/vqm"

# Configuración de la página
st.set_page_config(page_title="Gestión de NC - Datos", layout="wide", page_icon="📋")

# encabezado
st.markdown("""
    <div class='app-header'>
        <h1>Visualización de la Gestión de NCs</h1>
        <p>Datos registrados de las validaciones de No Conformes</p>
    </div>
    <hr class='app-divider'/>
""", unsafe_allow_html=True)

# llamo a la función para autenticación de usuarios
verificar_autenticacion()

# llamo a la función para mostrar barra lateral
mostrar_sidebar()

# estilos de la página
estilos_css()

# ---------------- Cargar datos desde la API ---------------- #
@st.cache_data
def get_nc_data():
    response = requests.get(f"{API_URL}/tratamiento_nc_vqm")
    if response.status_code == 200:
        df = pd.DataFrame(response.json())

        # Convertir la columna 'fecha' a datetime si existe
        if "fecha" in df.columns:
            df["fecha"] = pd.to_datetime(df["fecha"], errors='coerce')

        return df
    else:
        st.error("Error al obtener datos de No Conformidades.")
        return pd.DataFrame()

df_nc = get_nc_data()

# Verificar si hay datos disponibles
if df_nc.empty:
    st.warning("No hay datos disponibles.")
    st.stop()

# Seleccionar columnas relevantes
df_nc = df_nc[["titulo", "fecha", "operario", "nc_validada", "vqm_conforme", "descripcion_intervencion", "resultado_intervencion"]]

# ---------------- Filtros de búsqueda ---------------- #
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    nc_selected = st.selectbox("Título NC", ["Todos"] + list(df_nc["titulo"].unique()))

with col2:
    fecha_inicio = st.date_input("Desde fecha:")

with col3:
    fecha_fin = st.date_input("Hasta fecha:")

with col4:
    buscar = st.button("Buscar", use_container_width=True)

if buscar:
    st.session_state.filtrar = True

# Filtrar datos según selección
if "filtrar" in st.session_state and st.session_state.filtrar:
    if nc_selected != "Todos":
        df_nc = df_nc[df_nc["titulo"] == nc_selected]

    if "fecha" in df_nc.columns:
        df_nc = df_nc[(df_nc["fecha"] >= pd.to_datetime(fecha_inicio)) & 
                      (df_nc["fecha"] <= pd.to_datetime(fecha_fin))]

# función de estilo
def colorear_conformidad(val):
    if val == "CONFORME":
        return 'background-color: #4CAF50; color: white; font-weight: bold;'
    elif val == "NO CONFORME":
        return 'background-color: #FF4B4B; color: white; font-weight: bold;'
    return ''

# transformar booleanos a texto
df_nc["nc_validada"] = df_nc["nc_validada"].map({True: "CONFORME", False: "NO CONFORME"})
df_nc["vqm_conforme"] = df_nc["vqm_conforme"].map({True: "CONFORME", False: "NO CONFORME"})

# renombrar columnas
df_nc = df_nc.rename(columns={
    "titulo": "Título",
    "fecha": "Fecha",
    "operario": "Operario",
    "descripcion_intervencion": "Causa",
    "resultado_intervencion": "Resultado",
    "vqm_conforme": "VQM Conforme",
    "nc_validada": "NC Validada"
})

# reordenar columnas
df_nc = df_nc[["Título", "Fecha", "Operario", "NC Validada", "VQM Conforme", "Causa", "Resultado"]]

st.dataframe(
    df_nc.style
        .applymap(colorear_conformidad, subset=["NC Validada"])
        .applymap(colorear_conformidad, subset=["VQM Conforme"]),
    use_container_width=True
)