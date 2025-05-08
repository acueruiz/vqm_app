import streamlit as st
import os
import requests
import pandas as pd
import time
import plotly.express as px
from sidebar import mostrar_sidebar
from verificar_autenticacion import verificar_autenticacion
from styles import estilos_css

API_URL = "http://127.0.0.1:5000/vqm"

# configuración de la página
st.set_page_config(page_title="Aplicación VQM", layout="wide", page_icon="🏠")

# llamo a la función para autenticación de usuarios
verificar_autenticacion()

# llamo a la función para mostrar barra lateral
mostrar_sidebar()

# estilos de la página
estilos_css()

# encabezado principal
st.markdown('<div class="header"><h2>Análisis de VQMs</h1></div>', unsafe_allow_html=True)

# cargar datos desde la API
with st.spinner("Cargando datos de VQM MDM..."):
    time.sleep(1)
    
    # datos de VQM MDM
    response_vqm = requests.get(f"{API_URL}/vqm_mdm")
    df_vqm = pd.DataFrame(response_vqm.json()) if response_vqm.status_code == 200 else pd.DataFrame()

# análisis de VQM MDM
st.subheader("📋 Estado de las VQM MDM Registradas")

if not df_vqm.empty:
    df_vqm["fecha"] = pd.to_datetime(df_vqm["fecha"], errors='coerce')

    # indicadores clave
    col1, col2, col3 = st.columns(3)

    with col1:
        total_vqm = len(df_vqm)
        st.metric(label="📏 Total de VQM Registradas", value=total_vqm)

    with col2:
        conformes = df_vqm["vqm_bascula_conforme"].sum()
        st.metric(label="✅ VQM Báscula Conformes", value=conformes)

    with col3:
        no_conformes = total_vqm - conformes
        st.metric(label="⚠️ VQM Báscula No Conformes", value=no_conformes)

# VQM Temperatura MI
response_temp = requests.get(f"{API_URL}/vqm_temperatura_mi10")
df_temp = pd.DataFrame(response_temp.json()) if response_temp.status_code == 200 else pd.DataFrame()

if not df_temp.empty:
    conformes_temp = df_temp["vqm_conforme"].sum()
    total_temp = len(df_temp)

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="🌡️ VQM Temperatura Conformes", value=conformes_temp)
    with col2:
        st.metric(label="⚠️ VQM Temperatura No Conformes", value=total_temp - conformes_temp)

df_vqm["semana"] = df_vqm["fecha"].dt.strftime("%Y-%W")
df_agrupado = df_vqm.groupby(["semana", "vqm_bascula_conforme"]).size().reset_index(name="count")

fig_temporal = px.bar(df_agrupado, x="semana", y="count", color="vqm_bascula_conforme",
                      title="📆 Evolución semanal de VQM Báscula", barmode="stack")
st.plotly_chart(fig_temporal, use_container_width=True)

response_nc = requests.get(f"{API_URL}/tratamiento_nc_vqm")
df_nc = pd.DataFrame(response_nc.json()) if response_nc.status_code == 200 else pd.DataFrame()

if not df_nc.empty:
    top_op = df_nc["operario"].value_counts().reset_index()
    top_op.columns = ["Operario", "NCs"]

    fig_top = px.bar(top_op, x="Operario", y="NCs", title="👷 Operarios con más NC registradas")
    st.plotly_chart(fig_top, use_container_width=True)

if "titulo" in df_vqm.columns:
    heatmap_df = df_vqm.groupby("titulo")[["error_cantidad1", "error_cantidad2"]].mean().reset_index()
    heatmap_df["Media de errores"] = heatmap_df[["error_cantidad1", "error_cantidad2"]].mean(axis=1)

    fig_heatmap = px.density_heatmap(heatmap_df, x="titulo", y="Media de errores",
                                     title="🌡️ Promedio de errores por instrumento", nbinsx=20)
    st.plotly_chart(fig_heatmap, use_container_width=True)

nc_abiertas = df_nc[~df_nc["nc_validada"]].shape[0]
color = "🔴" if nc_abiertas > 3 else "🟡" if nc_abiertas else "🟢"
st.metric(label="Estado global de NC", value=f"{color} {nc_abiertas} pendientes")

st.markdown("### 🧭 Navegación rápida")
col1, col2, col3 = st.columns(3)
with col1:
    st.link_button("Nueva VQM MDM", "/VQM_MDM")
with col2:
    st.link_button("Nueva VQM Temperatura", "/VQM_Temperatura")
with col3:
    st.link_button("Tratamiento NC", "/Tratamiento_NC")

