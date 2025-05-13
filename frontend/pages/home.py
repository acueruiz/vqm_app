import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from sidebar import mostrar_sidebar
from verificar_autenticacion import verificar_autenticacion
from styles import estilos_css

# ─────────────────────────────────────────────────────────────────────────────
# configuración y sidebar
st.set_page_config(page_title="Panel de Control VQM", page_icon="🏭", layout="wide")
estilos_css()
verificar_autenticacion()
mostrar_sidebar()

# definimos aquí la URL de la API antes de cargar los datos
API_URL = "http://127.0.0.1:5000/vqm"

# ─────────────────────────────────────────────────────────────────────────────
# encabezado
st.markdown("""
    <div class='app-header'>
        <h1>Panel de control VQM</h1>
        <p>Monitorización de Verificaciones de Calidad de la Medida – Michelin</p>
    </div>
    <hr class='app-divider'/>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
# carga de datos
@st.cache_data(show_spinner=False)
def cargar_datos():
    df_vqm  = pd.DataFrame(requests.get(f"{API_URL}/vqm_mdm").json())
    df_temp = pd.DataFrame(requests.get(f"{API_URL}/vqm_temperatura_mi10").json())
    df_nc   = pd.DataFrame(requests.get(f"{API_URL}/tratamiento_nc_vqm").json())

    meses_es = {
        1:"enero",2:"febrero",3:"marzo",4:"abril",5:"mayo",6:"junio",
        7:"julio",8:"agosto",9:"septiembre",10:"octubre",11:"noviembre",12:"diciembre"
    }

    for df in (df_vqm, df_temp, df_nc):
        if "fecha" in df.columns:
            df["fecha"]     = pd.to_datetime(df["fecha"], errors="coerce")
            df["anio"]      = df["fecha"].dt.year
            df["mes_num"]   = df["fecha"].dt.month
            df["mes"]       = df["mes_num"].map(meses_es)
            df["trimestre"] = df["fecha"].dt.quarter

    return df_vqm, df_temp, df_nc

with st.spinner("Cargando datos..."):
    df_vqm, df_temp, df_nc = cargar_datos()

if df_vqm.empty and df_temp.empty:
    st.error("No hay datos disponibles. Comprueba la API.")
    st.stop()

# selector de año
years = sorted(set(df_vqm["anio"].dropna().unique()) | set(df_temp["anio"].dropna().unique()))
year_sel = st.selectbox("Selecciona año:", years, index=len(years)-1)

# aplicar filtros
df_vqm = df_vqm[df_vqm["anio"] == year_sel]
df_temp = df_temp[df_temp["anio"] == year_sel]
df_nc = df_nc[df_nc["anio"] == year_sel]

# ─────────────────────────────────────────────────────────────────────────────
# VQM por tipo
total_dosi = df_vqm["vqm_masico_conforme"].notna().sum()
total_basc = df_vqm["vqm_bascula_conforme"].notna().sum()
total_temp = df_temp["vqm_conforme"].notna().sum()

# No conformidades por tipo
nc_dosi  = (df_vqm["vqm_masico_conforme"] == False).sum()
nc_basc  = (df_vqm["vqm_bascula_conforme"] == False).sum()
nc_temp  = (df_temp["vqm_conforme"] == False).sum()

# Gestión NC
tratadas   = len(df_nc)
pendientes = (df_nc["nc_validada"] == False).sum()

# ─────────────────────────────────────────────────────────────────────────────
# pestañas de navegación interna
tab_res, tab_men, tab_tri = st.tabs([
    "Resumen",
    "Mensual",
    "Trimestral",
])

# ─────────────────────────────────────────────────────────────────────────────
with tab_res:
    st.subheader("KPIs")

    # Sección 1 – Verificaciones VQM
    vqm_cols = st.columns(3)
    vqm_cols[0].metric("VQM Dosificadores", total_dosi)
    vqm_cols[1].metric("VQM Básculas", total_basc)
    vqm_cols[2].metric("VQM Temperatura", total_temp)

    # Sección 2 – No conformidades
    nc_cols = st.columns(3)
    nc_cols[0].metric("NC Dosificadores", nc_dosi)
    nc_cols[1].metric("NC Básculas", nc_basc)
    nc_cols[2].metric("NC Temperatura", nc_temp)

    # Sección 3 – Gestión de NC
    ncg_cols = st.columns(2)
    ncg_cols[0].metric("NC registradas", tratadas)
    ncg_cols[1].metric("NC pendientes validación", pendientes)

    st.markdown("---")

    g1, g2 = st.columns(2, gap="large")

    with g1:
        st.subheader("Evolución mensual VQM Báscula")

        # gráfico de barras
        df_mes = df_vqm.groupby(["mes_num", "vqm_bascula_conforme"])\
                    .size().reset_index(name="count")
        fig_mes = px.bar(
            df_mes, x="mes_num", y="count", color="vqm_bascula_conforme",
            labels={"mes_num": "Mes", "count": "Cantidad", "vqm_bascula_conforme": "Conforme"},
            barmode="stack"
        )
        g1.plotly_chart(fig_mes, use_container_width=True)

    # título + gráfico de pastel (todo dentro de g2)
    with g2:
        st.subheader("Reparto conformidad anual")
        total_conf = (df_vqm["vqm_bascula_conforme"] == True).sum() + (df_temp["vqm_conforme"] == True).sum()
        total_nc2  = (df_vqm["vqm_bascula_conforme"] == False).sum() + (df_temp["vqm_conforme"] == False).sum()
        fig_pie = px.pie(
            names=["Conforme", "No Conforme"],
            values=[total_conf, total_nc2]
        )
        st.plotly_chart(fig_pie, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
with tab_men:
    st.markdown(
        "<div class='section-header section-header--mensual'>"
        "VQM Dosificadores (Revisión Mensual)"
        "</div>",
        unsafe_allow_html=True
    )
    if not df_vqm.empty:
        df_dosi = df_vqm.assign(
            estado=df_vqm["vqm_masico_conforme"].map({True:"CONFORME",False:"NO CONFORME"})
        ).pivot_table(
            index="titulo", columns="mes", values="estado", aggfunc="first"
        ).reindex(
            columns=["enero","febrero","marzo","abril","mayo","junio",
                     "julio","agosto","septiembre","octubre","noviembre","diciembre"]
        ).fillna("")
        st.dataframe(df_dosi, use_container_width=True)
    else:
        st.info("No hay registros de Dosificadores.")

    st.markdown(
        "<div class='section-header section-header--mensual'>"
        "VQM Cero Básculas (Revisión Mensual)"
        "</div>",
        unsafe_allow_html=True
    )
    if not df_vqm.empty:
        df_cero = df_vqm.assign(
            estado=df_vqm["vqm_bascula_conforme"].map({True:"CONFORME",False:"NO CONFORME"})
        ).pivot_table(
            index="titulo", columns="mes", values="estado", aggfunc="first"
        ).reindex(
            columns=["enero","febrero","marzo","abril","mayo","junio",
                     "julio","agosto","septiembre","octubre","noviembre","diciembre"]
        ).fillna("")
        st.dataframe(df_cero, use_container_width=True)
    else:
        st.info("No hay registros de Cero Básculas.")

# ─────────────────────────────────────────────────────────────────────────────
with tab_tri:
    t1, t2, t3 = st.columns(3)
    with t1:
        st.markdown(
            "<div class='section-header section-header--trimestral-dosi'>"
            "VQM Dosificadores (Revisión Trimestral)"
            "</div>",
            unsafe_allow_html=True
        )
        if not df_vqm.empty:
            df_dt = df_vqm.assign(
                estado=df_vqm["vqm_masico_conforme"].map({True:"CONFORME",False:"NO CONFORME"})
            ).pivot_table(
                index="titulo", columns="trimestre", values="estado", aggfunc="first"
            ).reindex(columns=[1,2,3,4]).rename(
                columns={1:"Qtr 1",2:"Qtr 2",3:"Qtr 3",4:"Qtr 4"}
            ).fillna("")
            st.dataframe(df_dt, use_container_width=True)
        else:
            st.info("Sin datos trimestrales de Dosificadores.")

    with t2:
        st.markdown(
            "<div class='section-header section-header--trimestral-cero'>"
            "VQM Cero Básculas (Revisión Trimestral)"
            "</div>",
            unsafe_allow_html=True
        )
        if not df_vqm.empty:
            df_ct = df_vqm.assign(
                estado=df_vqm["vqm_bascula_conforme"].map({True:"CONFORME",False:"NO CONFORME"})
            ).pivot_table(
                index="titulo", columns="trimestre", values="estado", aggfunc="first"
            ).reindex(columns=[1,2,3,4]).rename(
                columns={1:"Qtr 1",2:"Qtr 2",3:"Qtr 3",4:"Qtr 4"}
            ).fillna("")
            st.dataframe(df_ct, use_container_width=True)
        else:
            st.info("Sin datos trimestrales de Cero Básculas.")

    with t3:
        st.markdown(
            "<div class='section-header section-header--trimestral-temp'>"
            "Temperatura MI (Revisión Trimestral)"
            "</div>",
            unsafe_allow_html=True
        )
        if not df_temp.empty:
            df_tt = df_temp.assign(
                estado=df_temp["vqm_conforme"].map({True:"CONFORME",False:"NO CONFORME"})
            ).pivot_table(
                index="titulo", columns="trimestre", values="estado", aggfunc="first"
            ).reindex(columns=[1,2,3,4]).rename(
                columns={1:"Qtr 1",2:"Qtr 2",3:"Qtr 3",4:"Qtr 4"}
            ).fillna("")
            st.dataframe(df_tt, use_container_width=True)
        else:
            st.info("Sin datos trimestrales de Temperatura MI.")

# ─────────────────────────────────────────────────────────────────────────────
st.caption("© Michelin - Sistema VQM | Última sincronización automática")
