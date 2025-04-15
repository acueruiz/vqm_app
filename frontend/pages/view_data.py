import streamlit as st
import requests
import pandas as pd
from sidebar import mostrar_sidebar
from verificar_autenticacion import verificar_autenticacion
from styles import estilos_css

API_URL = "http://127.0.0.1:5000/vqm"

# Configuración de la página
st.set_page_config(page_title="VQM MDM - Datos", layout="wide", page_icon="📋")

# Encabezado
st.markdown('<div class="header">VQM MDM - VISUALIZACIÓN DE DATOS</div>', unsafe_allow_html=True)

# llamo a la función para autenticación de usuarios
verificar_autenticacion()

# llamo a la función para mostrar barra lateral
mostrar_sidebar()

# estilos de la página
estilos_css()

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
