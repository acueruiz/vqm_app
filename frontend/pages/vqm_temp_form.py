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
import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from utils.email_sender import enviar_email

API_URL = "http://127.0.0.1:5000/vqm"

# Configuración de la página
st.set_page_config(page_title="VQM Temperatura - Introducción de Datos", layout="wide", page_icon="📝")

# Estilos y cabecera
st.markdown("""
    <div class='app-header'>
      <h1>VQM Temperatura – Introducción de Datos</h1>
      <p>Formulario para registrar mediciones y comprobar conformidad en TMI</p>
    </div>
    <hr class='app-divider'/>
""", unsafe_allow_html=True)

# Verificación de autenticación y sidebar
verificar_autenticacion()
estilos_css()
mostrar_sidebar()

# Cargar datos
@st.cache_data
def get_vqm_temperatura():
    response = requests.get(f"{API_URL}/vqm_temperatura")
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        st.error("Error al obtener datos de temperatura desde la API.")
        return pd.DataFrame()

df_vqm_temp = get_vqm_temperatura()

# Formulario cabecera
st.subheader("Datos generales")
col1, col2 = st.columns(2)

with col1:
    trimestre = st.selectbox("Trimestre", ["Primer Trimestre", "Segundo Trimestre", "Tercer Trimestre", "Cuarto Trimestre"], key="trimestre_main")
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
with st.expander("Añadir nueva carga de temperatura"):
    fecha = st.date_input("Fecha de carga", key="fecha_carga")
    tmi = st.text_input("Temperatura MI (TMI)", key="tmi_carga")
    tr = st.text_input("Temperatura Pistola (TR)", key="tr_carga")
    num_ml_dia = st.text_input("N.º ML del día", key="num_ml_dia_carga")

    if st.button("Agregar carga"):
        if len(st.session_state.cargas) >= 15:
            st.error("No puedes agregar más de 15 registros.")
        else:
            try:
                tmi_float = float(tmi.strip()) if tmi.strip() else 0.0
                tr_float = float(tr.strip()) if tr.strip() else 0.0
                num_ml = num_ml_dia.strip()
                diferencia = tmi_float - tr_float

                nueva = pd.DataFrame({
                    "titulo": [maquina],
                    "fecha": [fecha.strftime('%d-%m-%Y')],
                    "temperatura_mi": [tmi_float],
                    "temperatura_pistola": [tr_float],
                    "diferencia_temperaturas": [diferencia],
                    "trimestre_anio": [trimestre],
                    "operario": [operador],
                    "num_ml_dia": [num_ml]
                })

                st.session_state.cargas = pd.concat([st.session_state.cargas, nueva], ignore_index=True).drop_duplicates()
            except ValueError:
                st.error("Ingrese valores numéricos válidos para TMI y TR.")

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

    # usa mean_diff como base para lsx/lix
    lsx = mean_diff + std_diff
    lix = mean_diff - std_diff

    st.session_state.cargas["vqm_conforme"] = st.session_state.cargas["diferencia_temperaturas"].apply(lambda x: lix <= x <= lsx)
    st.session_state.cargas["desviacion_tmi"] = std_tmi
    st.session_state.cargas["desviacion_tmi_tr"] = std_diff
    st.session_state.cargas["media_tmi_tr"] = mean_diff
    st.session_state.cargas["lsx"] = lsx
    st.session_state.cargas["lix"] = lix

    st.session_state.cargas["titulo"] = maquina

# Mostrar tabla
st.subheader("Cargas registradas")
st.dataframe(st.session_state.cargas)

# Botón para limpiar manualmente
if st.button("Limpiar cargas actuales"):
    st.session_state.cargas = pd.DataFrame(columns=[
        "fecha", "temperatura_mi", "temperatura_pistola",
        "diferencia_temperaturas", "trimestre_anio",
        "operario", "num_ml_dia"
    ])
    st.success("Cargas eliminadas.")
    st.rerun()

st.markdown("---")

def enviar_datos():
    if st.session_state.cargas.empty:
        st.error("No hay datos para guardar.")
        return

    # Convertir a formato JSON serializable
    data_to_send = (
        st.session_state.cargas
        .fillna(0.0)
        .replace([np.inf, -np.inf], 0.0)
        .applymap(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, pd.Timestamp) else x)
        .to_dict(orient="records")
    )

    # Enviar cada carga individual a la API
    for registro in data_to_send:
        try:
            response = requests.post(f"{API_URL}/vqm_temperatura_mi10", json=registro)
            if response.status_code == 201:
                st.success(f"Registro guardado: {registro['fecha']}")
            else:
                st.error(f"Error guardando {registro['fecha']}: {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Error en la conexión: {str(e)}")

    # Crear resumen automático si hay 15 registros
    if len(st.session_state.cargas) == 15:
        # otener valores para el cálculo
        mean_diff = st.session_state.cargas["diferencia_temperaturas"].mean()
        std_diff = st.session_state.cargas["diferencia_temperaturas"].std(ddof=0)
        media_calificacion = filtro_maquina["media_calificacion"]

        # calcular los límites
        lsx = media_calificacion + std_diff
        lix = media_calificacion - std_diff

        # evaluar conformidad global
        estado_global = (
            "CONFORME"
            if lix <= mean_diff <= lsx
            else "NO CONFORME"
        )

        # guardar resumen
        grupo_fecha = pd.to_datetime(st.session_state.cargas["fecha"].iloc[0], dayfirst=True).strftime('%Y-%m-%d')

        resumen_data = {
            "maquina": maquina.strip().upper(),
            "grupo_fecha": grupo_fecha,
            "estado": estado_global,
            "origen": "medicion",
            "fecha_evento": datetime.date.today().strftime("%Y-%m-%d")
        }

        try:
            r = requests.post(f"{API_URL}/vqm_temperatura_resumen", json=resumen_data)
            if r.status_code == 201:
                st.success("Resumen de grupo de 15 cargas creado correctamente.")
            else:
                st.warning(f"No se pudo guardar el resumen: {r.text}")
        except Exception as e:
            st.error(f"Error al crear resumen: {e}")

    # enviar correos si alguna carga es NO CONFORME
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
                        enviar_email(c, "Nueva No Conformidad VQM Temperatura MI", cuerpo)
                    st.success("Correos enviados correctamente.")
                else:
                    st.warning("No hay correos activos configurados.")
            else:
                st.error("Error consultando destinatarios.")
        except Exception as e:
            st.error(f"Error al enviar correos: {e}")

# Botón guardar
if len(st.session_state.cargas) < 5:
    st.warning("Debes agregar al menos 5 registros antes de guardar.")

if st.button("Guardar datos en la BBDD"):
    enviar_datos()
