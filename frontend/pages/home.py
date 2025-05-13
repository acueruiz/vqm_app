import streamlit as st
import pandas as pd
import requests
from sidebar import mostrar_sidebar
from verificar_autenticacion import verificar_autenticacion
from styles import estilos_css

# configuración de la página principal
st.set_page_config(page_title="Panel de Control VQM", page_icon="🏭", layout="wide")

# aplica los estilos css definidos
estilos_css()

# define la url de la API y verifica si el usuario está autenticado
API_URL = "http://127.0.0.1:5000/vqm"
verificar_autenticacion()

# muestra la barra lateral personalizada
mostrar_sidebar()

# encabezado de la página con título y descripción
st.markdown(
    """
    <div class='app-header'>
      <h1>Panel de Control VQM</h1>
      <p>Monitorización de Verificaciones de Calidad de la Medida – Michelin</p>
    </div>
    <hr class='app-divider'/>
    """,
    unsafe_allow_html=True
)

# carga de datos desde la API y transformación de fechas
@st.cache_data(show_spinner=False)
def cargar_datos():
    r_vqm = requests.get(f"{API_URL}/vqm_mdm")
    r_temp = requests.get(f"{API_URL}/vqm_temperatura_mi10")
    df_vqm = pd.DataFrame(r_vqm.json()) if r_vqm.status_code == 200 else pd.DataFrame()
    df_temp = pd.DataFrame(r_temp.json()) if r_temp.status_code == 200 else pd.DataFrame()

    meses_es = {1:"enero",2:"febrero",3:"marzo",4:"abril",5:"mayo",6:"junio",
               7:"julio",8:"agosto",9:"septiembre",10:"octubre",11:"noviembre",12:"diciembre"}
    for df in (df_vqm, df_temp):
        if "fecha" in df.columns:
            df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
            df["anio"] = df["fecha"].dt.year
            df["mes"] = df["fecha"].dt.month.map(meses_es)
            df["trimestre"] = df["fecha"].dt.quarter
    return df_vqm, df_temp

# muestra spinner mientras se cargan los datos
with st.spinner("Cargando datos..."):
    df_vqm, df_temp = cargar_datos()

# si no hay datos, se muestra un mensaje de error y se detiene la ejecución
if df_vqm.empty and df_temp.empty:
    st.error("No hay datos disponibles. Comprueba la conexión con la API.")
    st.stop()

# selector de año para filtrar los datos
years = sorted(set(df_vqm.get("anio", [])) | set(df_temp.get("anio", [])))
year_sel = st.selectbox("Selecciona año:", years, index=len(years)-1)
if "anio" in df_vqm.columns: df_vqm = df_vqm[df_vqm["anio"] == year_sel]
if "anio" in df_temp.columns: df_temp = df_temp[df_temp["anio"] == year_sel]

# bloque mensual de dosificadores
st.markdown(
    """
    <div class='section-header section-header--mensual'>
      VQM Dosificadores (Revisión Mensual)
    </div>
    """,
    unsafe_allow_html=True
)
if not df_vqm.empty:
    df_dosi = (
        df_vqm.assign(estado=df_vqm["vqm_masico_conforme"].map({True:"CONFORME",False:"NO CONFORME"}))
        .pivot_table(index="titulo", columns="mes", values="estado", aggfunc="first")
        .reindex(columns=["enero","febrero","marzo","abril","mayo","junio",
                          "julio","agosto","septiembre","octubre","noviembre","diciembre"]).fillna("")
    )
    st.dataframe(df_dosi, use_container_width=True)
else:
    st.info("No hay registros de Dosificadores para este año.")

# bloque mensual de cero básculas
st.markdown(
    """
    <div class='section-header section-header--mensual'>
      VQM Cero Básculas (Revisión Mensual)
    </div>
    """,
    unsafe_allow_html=True
)
if not df_vqm.empty:
    df_cero = (
        df_vqm.assign(estado=df_vqm["vqm_bascula_conforme"].map({True:"CONFORME",False:"NO CONFORME"}))
        .pivot_table(index="titulo", columns="mes", values="estado", aggfunc="first")
        .reindex(columns=["enero","febrero","marzo","abril","mayo","junio",
                          "julio","agosto","septiembre","octubre","noviembre","diciembre"]).fillna("")
    )
    st.dataframe(df_cero, use_container_width=True)
else:
    st.info("No hay registros de Cero Básculas para este año.")

# bloques trimestrales para tres tipos de VQM
col1, col2, col3 = st.columns(3)

# revisión trimestral dosificadores
with col1:
    st.markdown(
        """
        <div class='section-header section-header--trimestral-dosi'>
          VQM Dosificadores (Revisión Trimestral)
        </div>
        """,
        unsafe_allow_html=True
    )
    if not df_vqm.empty:
        df_dt = (
            df_vqm.assign(estado=df_vqm["vqm_masico_conforme"].map({True:"CONFORME",False:"NO CONFORME"}))
            .pivot_table(index="titulo", columns="trimestre", values="estado", aggfunc="first")
            .reindex(columns=[1,2,3,4]).rename(columns={1:"Qtr 1",2:"Qtr 2",3:"Qtr 3",4:"Qtr 4"}).fillna("")
        )
        st.dataframe(df_dt, use_container_width=True)
    else:
        st.info("Sin datos trimestrales de Dosificadores.")

# revisión trimestral cero básculas
with col2:
    st.markdown(
        """
        <div class='section-header section-header--trimestral-cero'>
          VQM Cero Básculas (Revisión Trimestral)
        </div>
        """,
        unsafe_allow_html=True
    )
    if not df_vqm.empty:
        df_ct = (
            df_vqm.assign(estado=df_vqm["vqm_bascula_conforme"].map({True:"CONFORME",False:"NO CONFORME"}))
            .pivot_table(index="titulo", columns="trimestre", values="estado", aggfunc="first")
            .reindex(columns=[1,2,3,4]).rename(columns={1:"Qtr 1",2:"Qtr 2",3:"Qtr 3",4:"Qtr 4"}).fillna("")
        )
        st.dataframe(df_ct, use_container_width=True)
    else:
        st.info("Sin datos trimestrales de Cero Básculas.")

# revisión trimestral temperatura mi
with col3:
    st.markdown(
        """
        <div class='section-header section-header--trimestral-temp'>
          Temperatura MI (Revisión Trimestral)
        </div>
        """,
        unsafe_allow_html=True
    )
    if not df_temp.empty:
        df_tt = (
            df_temp.assign(estado=df_temp["vqm_conforme"].map({True:"CONFORME",False:"NO CONFORME"}))
            .pivot_table(index="titulo", columns="trimestre", values="estado", aggfunc="first")
            .reindex(columns=[1,2,3,4]).rename(columns={1:"Qtr 1",2:"Qtr 2",3:"Qtr 3",4:"Qtr 4"}).fillna("")
        )
        st.dataframe(df_tt, use_container_width=True)
    else:
        st.info("Sin datos trimestrales de Temperatura MI.")

# pie de página con nota informativa
st.caption("© Michelin - Sistema VQM | Última sincronización automática")

