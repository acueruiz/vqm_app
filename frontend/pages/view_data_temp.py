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