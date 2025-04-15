import streamlit as st
import requests
import pandas as pd
import os
from sidebar import mostrar_sidebar
from verificar_autenticacion import verificar_autenticacion
from styles import estilos_css

API_URL = "http://127.0.0.1:5000/vqm"

st.set_page_config(page_title="Modificar VQM Temperatura", layout="wide", page_icon="🛠")

# Obtener ruta absoluta de la imagen
logo_path = os.path.join(os.getcwd(), "frontend", "imagenes", "logo_michelin.png")

# llamo a la función para autenticación de usuarios
verificar_autenticacion()

# llamo a la función para mostrar barra lateral
mostrar_sidebar()

# estilos de la página
estilos_css()

st.title("🔧 Modificar Datos de VQM Temperatura")

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

# Selección de la máquina para editar
maquinas = df["maquina"].unique()
selected_maquina = st.selectbox("Selecciona la máquina:", maquinas)

# Filtrar datos de la máquina seleccionada
df_filtered = df[df["maquina"] == selected_maquina]

if not df_filtered.empty:
    row = df_filtered.iloc[0]
    apelacion = st.text_input("Apelación", row["apelacion"])
    receta = st.text_input("Receta", row["receta"])
    temperatura_caida = st.number_input("Temperatura caída", value=row["temperatura_caida"], step=0.1)
    media_calificacion = st.number_input("Media calificación", value=row["media_calificacion"], step=0.1)
    fecha_calificacion = st.date_input("Fecha de calificación", pd.to_datetime(row["fecha_calificacion"]))
    operario = st.text_input("Operario", row["operario"])

    if st.button("💾 Guardar Cambios"):
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
            st.success("✅ Datos actualizados correctamente.")
        else:
            st.error("❌ Error al actualizar los datos.")
else:
    st.warning("No se encontraron datos para la máquina seleccionada.")
