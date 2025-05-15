import streamlit as st
import requests
import pandas as pd
from sidebar import mostrar_sidebar
from verificar_autenticacion import verificar_autenticacion
from styles import estilos_css

API_URL = "http://127.0.0.1:5000/vqm"

# Configuración de la página
st.set_page_config(page_title="VQM Temperatura MI10 - Datos", layout="wide", page_icon="📋")

# Encabezado
st.markdown('<div class="header">VQM Temperatura MI10 - VISUALIZACIÓN DE DATOS</div>', unsafe_allow_html=True)

# encabezado
st.markdown("""
    <div class='app-header'>
        <h1>VQM Temperatura MI10</h1>
        <p>Datos registrados de verificaciones de temperaturas de los MIs</p>
    </div>
    <hr class='app-divider'/>
""", unsafe_allow_html=True)

# llamo a la función para autenticación de usuarios
verificar_autenticacion()

# llamo a la función para mostrar barra lateral
mostrar_sidebar()

# estilos de la página
estilos_css()

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
        st.error("Error al obtener datos de VQM Temperatura MI10.")
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
    if st.button("Filtrar"):
        st.session_state.filtrar = True

# Filtrar datos según selección
if "filtrar" in st.session_state and st.session_state.filtrar:
    if maquina_selected != "Todas":
        df_temp_mi10 = df_temp_mi10[df_temp_mi10["titulo"] == maquina_selected]

    if trimestre_selected != "Todos":
        df_temp_mi10 = df_temp_mi10[df_temp_mi10["trimestre_anio"] == trimestre_selected]

# Mostrar tabla con estilo uniforme
if not df_temp_mi10.empty:
    df_temp_mi10 = df_temp_mi10.sort_values(by="fecha", ascending=False).reset_index(drop=True)

    # renombrar columnas útiles y eliminar las que no son clave
    df_temp_mi10 = df_temp_mi10[[
        "titulo", "fecha", "operario", "trimestre_anio", "temperatura_mi",
        "temperatura_pistola", "diferencia_temperaturas", "vqm_conforme"
    ]].rename(columns={
        "titulo": "Máquina",
        "fecha": "Fecha",
        "operario": "Operador",
        "trimestre_anio": "Trimestre",
        "temperatura_mi": "Temperatura MI",
        "temperatura_pistola": "Temperatura Pistola",
        "diferencia_temperaturas": "ΔT (MI - Pistola)",
        "vqm_conforme": "Conformidad"
    })

    # convertir conformidad a texto
    df_temp_mi10["Conformidad"] = df_temp_mi10["Conformidad"].map({True: "CONFORME", False: "NO CONFORME"})

    # estilo condicional
    def colorear_conformidad(val):
        if val == "NO CONFORME":
            return 'background-color: #FF4B4B; color: white; font-weight: bold;'
        elif val == "CONFORME":
            return 'background-color: #4CAF50; color: white; font-weight: bold;'
        return ''

    # mostrar tabla con formato
    st.dataframe(
        df_temp_mi10.style.applymap(colorear_conformidad, subset=["Conformidad"]),
        use_container_width=True,
        height=700
    )
else:
    st.warning("No se encontraron datos para los filtros seleccionados.")