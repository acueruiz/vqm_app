import streamlit as st
import requests
import pandas as pd
from sidebar import mostrar_sidebar
from verificar_autenticacion import verificar_autenticacion
from styles import estilos_css

API_URL = "http://127.0.0.1:5000/vqm"

# Configuración de la página
st.set_page_config(page_title="Gestión de NC - Datos", layout="wide", page_icon="📋")

# Encabezado
st.markdown('<div class="header">GESTIÓN DE NC - VISUALIZACIÓN DE DATOS</div>', unsafe_allow_html=True)

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
        st.error("❌ Error al obtener datos de No Conformidades.")
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
    buscar = st.button("🔍 Buscar", use_container_width=True)

if buscar:
    st.session_state.filtrar = True

# Filtrar datos según selección
if "filtrar" in st.session_state and st.session_state.filtrar:
    if nc_selected != "Todos":
        df_nc = df_nc[df_nc["titulo"] == nc_selected]

    if "fecha" in df_nc.columns:
        df_nc = df_nc[(df_nc["fecha"] >= pd.to_datetime(fecha_inicio)) & 
                      (df_nc["fecha"] <= pd.to_datetime(fecha_fin))]

# ---------------- Mostrar tabla con estilos ---------------- #
if not df_nc.empty:
    df_nc = df_nc.sort_values(by="fecha", ascending=False).reset_index(drop=True)

    def highlight_non_conform(val):
        if val is False:  # Resaltar valores no conformes
            return 'background-color: #FF4B4B; color: white; font-weight: bold;'
        return ''
    
    # Definir alias para las columnas
    column_aliases = {
        "titulo": "Título",
        "fecha": "Fecha",
        "operario": "Operario",
        "nc_validada": "NC Validada",
        "vqm_conforme": "VQM Conforme",
        "descripcion_intervencion": "Causa",
        "resultado_intervencion": "Resultado"
    }

    # Renombrar las columnas en el DataFrame
    df_nc = df_nc.rename(columns=column_aliases)

    # Mostrar la tabla en Streamlit con formato
    st.dataframe(
        df_nc.style.applymap(highlight_non_conform, 
                            subset=["NC Validada", "VQM Conforme"]),
        use_container_width=True
    )

else:
    st.warning("No se encontraron datos para los filtros seleccionados.")

# ---------------- Botones de exportación ---------------- #
col1, col2 = st.columns([1, 1])

with col1:
    if st.button("📥 Exportar a CSV"):
        df_nc.to_csv("datos_nc.csv", index=False)
        st.success("Archivo CSV generado correctamente.")

with col2:
    if st.button("📥 Exportar a Excel"):
        df_nc.to_excel("datos_nc.xlsx", index=False)
        st.success("Archivo Excel generado correctamente.")
