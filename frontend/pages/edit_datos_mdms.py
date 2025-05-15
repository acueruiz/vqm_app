import streamlit as st
import requests
import pandas as pd
from sidebar import mostrar_sidebar
from verificar_autenticacion import verificar_autenticacion
from styles import estilos_css

API_URL = "http://127.0.0.1:5000/vqm"

# configuración inicial
st.set_page_config(page_title="Modificar Datos MDM", layout="wide", page_icon="🛠")
estilos_css()
verificar_autenticacion()
mostrar_sidebar()

# encabezado visual
st.markdown("""
    <div class='app-header'>
        <h1>Modificar Datos de MDM</h1>
        <p>Edición de parámetros técnicos de cada módulo dosificador y su báscula asociada</p>
    </div>
    <hr class='app-divider'/>
""", unsafe_allow_html=True)

# carga de datos
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

# selección de MDM
st.subheader("Selección de MDM")
selected_masico = st.selectbox("Selecciona el MDM a modificar:", df["masico"].unique())

df_filtered = df[df["masico"] == selected_masico]

st.markdown("---")

if not df_filtered.empty:
    row = df_filtered.iloc[0]

    st.markdown("<div class='section-header'>Datos generales del MDM</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        id_dosificador = st.text_input("ID Dosificador", row["id_dosificador"])
        circuito = st.text_input("Circuito", row["circuito"])
        kw = st.number_input("KW", value=row["kw"], step=0.1)

    with col2:
        bascula = st.text_input("Báscula", row["bascula"])
        id_bascula = st.text_input("ID Báscula", row["id_bascula"])
        id_masas_patron = st.text_input("ID Masas Patrón", row["id_masas_patron"])

    with col3:
        vr_masas_patron = st.number_input("VR Masas Patrón", value=row["vr_masas_patron"], step=0.1)
        tolerancia_vr = st.number_input("Tolerancia VR", value=row["tolerancia_vr"], step=0.1)
        tolerancia_cero = st.number_input("Tolerancia Cero", value=row["tolerancia_cero"], step=0.1)

    st.markdown("---")

    st.markdown("<div class='section-header'>Parámetros de verificación</div>", unsafe_allow_html=True)
    col4, col5 = st.columns(2)
    with col4:
        valor_test1 = st.number_input("Valor Test 1", value=row["valor_test1"], step=0.1)
        tolerancia1 = st.number_input("Tolerancia 1", value=row["tolerancia1"], step=0.1)
    with col5:
        valor_test2 = st.number_input("Valor Test 2", value=row["valor_test2"], step=0.1)
        tolerancia2 = st.number_input("Tolerancia 2", value=row["tolerancia2"], step=0.1)

    st.markdown("---")

    if st.button("Guardar cambios en el MDM"):
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
            st.success("Datos actualizados correctamente.")
        else:
            st.error("Error al actualizar los datos.")
else:
    st.warning("No se encontraron datos para el MDM seleccionado.")