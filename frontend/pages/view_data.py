import streamlit as st
import pandas as pd
import requests
from sidebar import mostrar_sidebar
from verificar_autenticacion import verificar_autenticacion
from styles import estilos_css

# configuración de la página
st.set_page_config(page_title="VQM MDM - Datos", layout="wide", page_icon="📋")
estilos_css()
verificar_autenticacion()
mostrar_sidebar()

# define la URL de la API
API_URL = "http://127.0.0.1:5000/vqm"

# encabezado
st.markdown("""
    <div class='app-header'>
        <h1>Visualización de VQM MDM</h1>
        <p>Datos registrados de verificaciones másicas y báscula</p>
    </div>
    <hr class='app-divider'/>
""", unsafe_allow_html=True)

# cargar datos desde la API
@st.cache_data
def get_mdm_data():
    response = requests.get(f"{API_URL}/vqm_mdm")
    if response.status_code == 200:
        df = pd.DataFrame(response.json())
        if "fecha" in df.columns:
            df["fecha"] = pd.to_datetime(df["fecha"], errors='coerce')
        return df
    else:
        st.error("❌ Error al obtener datos de MDM.")
        return pd.DataFrame()

df_mdm = get_mdm_data()

# si no hay datos, detener
if df_mdm.empty:
    st.warning("No hay datos disponibles.")
    st.stop()

# seleccionar solo las columnas clave
df_mdm = df_mdm[["titulo", "fecha", "operador", "vqm_bascula_conforme", "vqm_masico_conforme"]]

# subencabezado de filtros
st.subheader("Filtros de búsqueda")

# filtros
col1, col2, col3, col4 = st.columns(4)
with col1:
    mdm_selected = st.selectbox("MDM", ["Todos"] + sorted(df_mdm["titulo"].unique()))
with col2:
    fecha_inicio = st.date_input("Desde fecha:")
with col3:
    fecha_fin = st.date_input("Hasta fecha:")
with col4:
    buscar = st.button("🔍 Buscar", use_container_width=True)

if buscar:
    st.session_state.filtrar = True

# aplicar filtros si corresponde
if "filtrar" in st.session_state and st.session_state.filtrar:
    if mdm_selected != "Todos":
        df_mdm = df_mdm[df_mdm["titulo"] == mdm_selected]
    df_mdm = df_mdm[(df_mdm["fecha"] >= pd.to_datetime(fecha_inicio)) & 
                    (df_mdm["fecha"] <= pd.to_datetime(fecha_fin))]

# mostrar resultados
st.markdown("<div class='section-header section-header--mensual'>Resultados de búsqueda</div>", unsafe_allow_html=True)

if not df_mdm.empty:
    df_mdm = df_mdm.sort_values(by="fecha", ascending=False).reset_index(drop=True)

    # renombrar columnas
    df_mdm = df_mdm.rename(columns={
        "titulo": "MDM",
        "fecha": "Fecha",
        "operador": "Operador",
        "vqm_bascula_conforme": "Báscula Conforme",
        "vqm_masico_conforme": "Másico Conforme"
    })

    # convertir booleanos a texto "CONFORME"/"NO CONFORME"
    df_mdm["Báscula Conforme"] = df_mdm["Báscula Conforme"].map({True: "CONFORME", False: "NO CONFORME"})
    df_mdm["Másico Conforme"] = df_mdm["Másico Conforme"].map({True: "CONFORME", False: "NO CONFORME"})

    # aplicar colores según conformidad
    def color_conformidad(val):
        if val == "NO CONFORME":
            return 'background-color: #FF4B4B; color: white; font-weight: bold;'
        elif val == "CONFORME":
            return 'background-color: #4CAF50; color: white; font-weight: bold;'
        return ''

    st.dataframe(
        df_mdm.style.applymap(color_conformidad, subset=["Báscula Conforme", "Másico Conforme"]),
        use_container_width=True
    )
else:
    st.warning("No se encontraron datos para los filtros seleccionados.")