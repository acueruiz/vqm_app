import streamlit as st
import requests
import pandas as pd
import numpy as np
from sidebar import mostrar_sidebar
from verificar_autenticacion import verificar_autenticacion
from styles import estilos_css
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from utils.email_sender import enviar_email

API_URL = "http://127.0.0.1:5000/vqm"

# Configuración de la página
st.set_page_config(page_title="VQM Temperatura - Introducción de Datos", layout="wide", page_icon="📝")

# Estilos y cabecera
estilos_css()
st.markdown("""
    <div class='app-header'>
      <h1>VQM Temperatura – Introducción de Datos</h1>
      <p>Formulario para registrar mediciones y comprobar conformidad en TMI</p>
    </div>
    <hr class='app-divider'/>
""", unsafe_allow_html=True)

# Verificación de autenticación y sidebar
verificar_autenticacion()
mostrar_sidebar()

# Cargar datos
@st.cache_data
def get_vqm_temperatura():
    response = requests.get(f"{API_URL}/vqm_temperatura")
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        st.error("❌ Error al obtener datos de temperatura desde la API.")
        return pd.DataFrame()

df_vqm_temp = get_vqm_temperatura()

# Formulario cabecera
st.subheader("Datos generales")
col1, col2 = st.columns(2)

with col1:
    trimestre = st.selectbox("Trimestre", ["Primer Trimestre 2025", "Segundo Trimestre 2025", "Tercer Trimestre 2025", "Cuarto Trimestre 2025"], key="trimestre_main")
    maquina = st.selectbox("Máquina", df_vqm_temp["maquina"].unique(), key="maquina_main")
    operador = st.text_input("Operador", value=st.session_state["usuario"]["nombre"], disabled=True)

with col2:
    filtro_maquina = df_vqm_temp[df_vqm_temp["maquina"] == maquina].iloc[0]
    st.text_input("Apelación", filtro_maquina["apelacion"], disabled=True)
    st.text_input("Receta", filtro_maquina["receta"], disabled=True)
    st.number_input("Tª caída", value=filtro_maquina["temperatura_caida"], disabled=True)
    st.number_input("Media de calificación", value=filtro_maquina["media_calificacion"], disabled=True)
    st.date_input("Fecha de Calificación", value=pd.to_datetime(filtro_maquina["fecha_calificacion"]), disabled=True)

st.markdown("---")

# Inicializar tabla
if "cargas" not in st.session_state:
    st.session_state.cargas = pd.DataFrame(columns=["fecha", "temperatura_mi", "temperatura_pistola", "diferencia_temperaturas", "trimestre_anio", "operario", "num_ml_dia"])

# Añadir nueva carga
with st.expander("➕ Añadir nueva carga de temperatura"):
    fecha = st.date_input("Fecha de carga", key="fecha_carga")
    tmi = st.text_input("Temperatura MI (TMI)", key="tmi_carga")
    tr = st.text_input("Temperatura Pistola (TR)", key="tr_carga")
    num_ml_dia = st.text_input("N.º ML del día", key="num_ml_dia_carga")

    if st.button("Agregar carga"):
        if len(st.session_state.cargas) >= 10:
            st.error("⚠️ No puedes agregar más de 10 registros a la vez.")
        else:
            try:
                tmi_float = float(tmi.strip()) if tmi.strip() else 0.0
                tr_float = float(tr.strip()) if tr.strip() else 0.0
                num_ml_float = float(num_ml_dia.strip()) if num_ml_dia.strip() else 0.0
                diferencia = tmi_float - tr_float

                nueva = pd.DataFrame({
                    "fecha": [fecha.strftime('%d-%m-%Y')],
                    "temperatura_mi": [tmi_float],
                    "temperatura_pistola": [tr_float],
                    "diferencia_temperaturas": [diferencia],
                    "trimestre_anio": [trimestre],
                    "operario": [operador],
                    "num_ml_dia": [num_ml_float]
                })

                st.session_state.cargas = pd.concat([st.session_state.cargas, nueva], ignore_index=True).drop_duplicates()
            except ValueError:
                st.error("❌ Ingrese valores numéricos válidos para TMI y TR.")

# Cálculo de estadísticas
if not st.session_state.cargas.empty:
    if len(st.session_state.cargas) > 1:
        std_tmi = st.session_state.cargas["temperatura_mi"].std(ddof=0)
        std_diff = st.session_state.cargas["diferencia_temperaturas"].std(ddof=0)
        mean_diff = st.session_state.cargas["diferencia_temperaturas"].mean()
    else:
        std_tmi = std_diff = 0.0
        mean_diff = st.session_state.cargas["diferencia_temperaturas"].mean()

    std_tmi = 0.0 if np.isnan(std_tmi) else std_tmi
    std_diff = 0.0 if np.isnan(std_diff) else std_diff
    mean_diff = 0.0 if np.isnan(mean_diff) else mean_diff

    lsx = mean_diff + std_diff
    lix = mean_diff - std_diff

    st.session_state.cargas["vqm_conforme"] = st.session_state.cargas["diferencia_temperaturas"].apply(lambda x: lix <= x <= lsx)
    st.session_state.cargas[["desviacion_tmi", "desviacion_tmi_tr", "media_tmi_tr", "lsx", "lix"]] = [std_tmi, std_diff, mean_diff, lsx, lix]

# Mostrar tabla
st.subheader("Cargas registradas")
st.dataframe(st.session_state.cargas)

st.markdown("---")

# Guardar
def enviar_datos():
    if st.session_state.cargas.empty:
        st.error("❌ No hay datos para guardar.")
        return

    data_to_send = (
        st.session_state.cargas
        .fillna(0.0)
        .replace([np.inf, -np.inf], 0.0)
        .applymap(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, pd.Timestamp) else x)
        .to_dict(orient="records")
    )

    for registro in data_to_send:
        try:
            response = requests.post(f"{API_URL}/vqm_temperatura_mi10", json=registro)
            if response.status_code == 201:
                st.success(f"✅ Registro guardado: {registro['fecha']}")
            else:
                st.error(f"❌ Error guardando {registro['fecha']}: {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Error en la conexión: {str(e)}")

    if not all(st.session_state.cargas["vqm_conforme"]):
        tipo_notificacion = "VQM Temperaturas MI NC"
        try:
            r = requests.get(f"{API_URL}/correos_usuarios")
            if r.status_code == 200:
                correos = [c["email"] for c in r.json() if c["activo"] and tipo_notificacion in [t["nombre"] for t in c.get("tipos", [])]]
                if correos:
                    cuerpo = f"""
                    Hola,
                    Se han registrado cargas con No Conformidad en Temperatura MI.
                    Revisa los detalles en la aplicación VQM.
                    Saludos,
                    Sistema VQM
                    """
                    for c in correos:
                        enviar_email(c, "⚠️ Nueva No Conformidad VQM Temperatura MI", cuerpo)
                    st.success("Correos enviados correctamente.")
                else:
                    st.warning("No hay correos activos configurados.")
            else:
                st.error("Error consultando destinatarios.")
        except Exception as e:
            st.error(f"❌ Error al enviar correos: {e}")

# Botón guardar
if len(st.session_state.cargas) < 5:
    st.warning("⚠️ Debes agregar al menos 5 registros antes de guardar.")

if st.button("📥 Guardar datos en la BBDD"):
    enviar_datos()
