import streamlit as st
import requests
import pandas as pd
from sidebar import mostrar_sidebar
from verificar_autenticacion import verificar_autenticacion
from styles import estilos_css

API_URL = "http://127.0.0.1:5000/vqm"

# configuración inicial
st.set_page_config(page_title="Modificar VQM Temperatura", layout="wide", page_icon="🛠")
estilos_css()
verificar_autenticacion()
mostrar_sidebar()

# encabezado visual
st.markdown("""
    <div class='app-header'>
        <h1>Modificar Datos de VQM Temperatura</h1>
        <p>Edición de los parámetros registrados en máquinas de mezcla – apelación, receta, temperatura, etc.</p>
    </div>
    <hr class='app-divider'/>
""", unsafe_allow_html=True)

# cargar datos
@st.cache_data
def get_temperatura_data():
    response = requests.get(f"{API_URL}/vqm_temperatura")
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        st.error("Error al cargar los datos de temperatura.")
        return pd.DataFrame()

df = get_temperatura_data()

if df.empty:
    st.warning("No hay datos de temperatura disponibles.")
    st.stop()

# selección de máquina
st.subheader("Selección de máquina")
selected_maquina = st.selectbox("Selecciona la máquina:", df["maquina"].unique())

df_filtered = df[df["maquina"] == selected_maquina]

st.markdown("---")

# formulario de modificación
if not df_filtered.empty:
    row = df_filtered.iloc[0]

    st.markdown("<div class='section-header'>Datos técnicos y operario</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        apelacion = st.text_input("Apelación", row["apelacion"])
        receta = st.text_input("Receta", row["receta"])

    with col2:
        temperatura_caida = st.number_input("Temperatura caída", value=row["temperatura_caida"], step=0.1)
        media_calificacion = st.number_input("Media calificación", value=row["media_calificacion"], step=0.1)

    with col3:
        fecha_calificacion = st.date_input("Fecha de calificación", pd.to_datetime(row["fecha_calificacion"]))
        operario = st.text_input("Operario", row["operario"])

    st.markdown("---")

    if st.button("Guardar cambios en la máquina seleccionada"):
        updated_data = {
            "maquina": selected_maquina,
            "apelacion": apelacion,
            "receta": receta,
            "temperatura_caida": temperatura_caida,
            "media_calificacion": media_calificacion,
            "fecha_calificacion": str(fecha_calificacion),
            "operario": operario,
        }

        response = requests.put(f"{API_URL}/vqm_temperatura/{selected_maquina}", json=updated_data)

        if response.status_code == 200:
            st.success("Datos actualizados correctamente.")
        else:
            st.error("Error al actualizar los datos.")
else:
    st.warning("No se encontraron datos para la máquina seleccionada.")
