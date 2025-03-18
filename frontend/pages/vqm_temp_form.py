import streamlit as st
import requests
import pandas as pd
import numpy as np
import os

# configuración de la API Flask
API_URL = "http://127.0.0.1:5000/vqm"

# configuración de la página
st.set_page_config(page_title="VQM Temperatura - Introducción de Datos", layout="wide")

# encabezado
st.markdown('<div class="header">VQM TEMPERATURA - INTRODUCCIÓN DE DATOS</div>', unsafe_allow_html=True)

# Obtener ruta absoluta de la imagen
logo_path = os.path.join(os.getcwd(), "frontend", "imagenes", "logo_michelin.png")

# Verificar si la imagen existe
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_container_width=True)
else:
    st.sidebar.warning("⚠️ No se encontró el logo. Verifica la ruta del archivo.")

# ---------------- Sidebar con categorías agrupadas ---------------- #
st.sidebar.title("MENÚ DE NAVEGACIÓN")

# inicio
st.sidebar.page_link("home.py", label="Inicio", icon="🏠")

# formularios
with st.sidebar.expander("📝 Formularios", expanded=False):
    st.page_link("pages/vqm_mdm_form.py", label="VQM MDM Form", icon="📝")
    st.page_link("pages/vqm_temp_form.py", label="VQM Temperatura Form", icon="🌡️")
    st.page_link("pages/gestion_nc_form.py", label="Gestión NC Form", icon="⚠️")

# visualización de Datos
with st.sidebar.expander("📊 Visualización de Datos", expanded=False):
    st.page_link("pages/view_data.py", label="Ver Datos MDM", icon="📋")
    st.page_link("pages/view_data_temp.py", label="Ver Datos Temp MI", icon="🌡️")
    st.page_link("pages/view_data_nc.py", label="Ver Datos NC", icon="⚠️")

# administración
with st.sidebar.expander("⚙️ Administración", expanded=False):
    st.page_link("pages/users.py", label="Usuarios", icon="👥")

# dashboard
st.sidebar.page_link("pages/vqm_dashboard.py", label="Dashboard", icon="📊")

# estilos CSS personalizados
st.markdown(
    """
    <style>

        /* Oculta el menú de navegación automático de Streamlit */
        [data-testid="stSidebarNav"] {
            display: none !important;
        }

        [data-testid="stSidebar"] {
            padding-top: 0px !important; /* Reduce el padding superior del sidebar */
        }
        
        [data-testid="stImage"] img {
            margin-top: -30px !important; /* Reduce el espacio superior del logo */
            margin-bottom: -20px !important; /* Reduce el espacio inferior del logo */
        }
    
        /* Encabezados mejorados */
        .header {
            text-align: center;
            background-color: #0055A4;
            padding: 15px;
            color: white;
            font-size: 24px;
            font-weight: bold;
            border-radius: 8px;
            margin-bottom: 20px;
        }

        /* Botones personalizados */
        .stButton > button {
            background-color: #0055A4;
            color: white;
            font-size: 16px;
            padding: 10px 15px;
            border-radius: 8px;
            border: none;
            transition: 0.3s;
        }

        .stButton > button:hover {
            background-color: #003C7E;
            transform: scale(1.05);
        }

        /* Separadores visuales */
        .separator {
            border-bottom: 3px solid #0055A4;
            margin: 30px 0;
        }

        /* Mejora en la tabla de datos */
        .dataframe {
            border-collapse: collapse;
            width: 100%;
            background-color: white;
            border: 1px solid #ddd;
        }

        .dataframe th, .dataframe td {
            border: 1px solid #ddd;
            padding: 8px;
        }

        .dataframe th {
            background-color: #0055A4;
            color: white;
            text-align: left;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# cargar datos de la API Flask
@st.cache_data
def get_vqm_temperatura():
    response = requests.get(f"{API_URL}/vqm_temperatura")
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        st.error("❌ Error al obtener datos de temperatura desde la API.")
        return pd.DataFrame()

df_vqm_temp = get_vqm_temperatura()

# formulario de Introducción de Datos
col1, col2 = st.columns(2)

with col1:
    trimestre = st.selectbox("Trimestre", ["Primer Trimestre 2025", "Segundo Trimestre 2025", "Tercer Trimestre 2025", "Cuarto Trimestre 2025"], key="trimestre_main")
    maquina = st.selectbox("Máquina", df_vqm_temp["maquina"].unique(), key="maquina_main")
    operador = st.text_input("Operador", key="operador_main")

with col2:
    filtro_maquina = df_vqm_temp[df_vqm_temp["maquina"] == maquina].iloc[0]

    apelacion = filtro_maquina["apelacion"]
    receta = filtro_maquina["receta"]
    temperatura_caida = filtro_maquina["temperatura_caida"]
    media_calificacion = filtro_maquina["media_calificacion"]
    fecha_calificacion = filtro_maquina["fecha_calificacion"]

    st.text_input("Apelación", apelacion, disabled=True)
    st.text_input("Receta", receta, disabled=True)
    st.number_input("Tª caída", value=temperatura_caida, disabled=True)
    st.number_input("Media de calificación", value=media_calificacion, disabled=True)
    st.date_input("Fecha de Calificación", value=pd.to_datetime(fecha_calificacion), disabled=True)

st.markdown("<div class='separator'></div>", unsafe_allow_html=True)

# inicializar tabla de cargas en la sesión si no existe
if "cargas" not in st.session_state:
    st.session_state.cargas = pd.DataFrame(columns=[
        "fecha", "temperatura_mi", "temperatura_pistola", "diferencia_temperaturas",
        "trimestre_anio", "operario", "num_ml_dia"
    ])

# añadir nueva carga de temperatura
with st.expander("Añadir nueva carga de temperatura"):
    fecha = st.date_input("Fecha de carga", key="fecha_carga")
    tmi = st.text_input("Temperatura MI (TMI)", key="tmi_carga")
    tr = st.text_input("Temperatura Pistola (TR)", key="tr_carga")
    num_ml_dia = st.text_input("Número de ML (apelación) del día", key="num_ml_dia_carga")

    if st.button("Agregar carga"):
        if len(st.session_state.cargas) >= 10:
            st.error("⚠️ No puedes agregar más de 10 registros a la vez.")
        else:
            try:
                # Convertir valores a float de manera segura
                tmi_float = float(tmi) if tmi.strip() else 0.0
                tr_float = float(tr) if tr.strip() else 0.0
                diferencia_temperaturas = tmi_float - tr_float
                num_ml_float = float(num_ml_dia) if num_ml_dia.strip() else 0.0

                nueva_carga = pd.DataFrame({
                    "fecha": [fecha.strftime('%d-%m-%Y')],
                    "temperatura_mi": [tmi_float],
                    "temperatura_pistola": [tr_float],
                    "diferencia_temperaturas": [diferencia_temperaturas],
                    "trimestre_anio": [trimestre],
                    "operario": [operador],
                    "num_ml_dia": [num_ml_float]
                })

                # Concatenar los nuevos datos con los existentes y eliminar duplicados
                st.session_state.cargas = pd.concat([st.session_state.cargas, nueva_carga], ignore_index=True)
                st.session_state.cargas.drop_duplicates(inplace=True)

            except ValueError:
                st.error("❌ Error: Ingrese valores numéricos válidos para TMI y TR.")

if not st.session_state.cargas.empty:
    # verificar que haya suficientes datos antes de calcular estadísticas
    if len(st.session_state.cargas) > 1:
        desviacion_tmi = st.session_state.cargas["temperatura_mi"].std(ddof=0)
        desviacion_tmi_tr = st.session_state.cargas["diferencia_temperaturas"].std(ddof=0)
        media_tmi_tr = st.session_state.cargas["diferencia_temperaturas"].mean()
    else:
        desviacion_tmi = 0.0
        desviacion_tmi_tr = 0.0
        media_tmi_tr = st.session_state.cargas["diferencia_temperaturas"].mean()

    # evitar problemas con NaN
    desviacion_tmi = 0.0 if np.isnan(desviacion_tmi) else desviacion_tmi
    desviacion_tmi_tr = 0.0 if np.isnan(desviacion_tmi_tr) else desviacion_tmi_tr
    media_tmi_tr = 0.0 if np.isnan(media_tmi_tr) else media_tmi_tr

    lsx = media_tmi_tr + desviacion_tmi_tr
    lix = media_tmi_tr - desviacion_tmi_tr

    # verificar conformidad (VQM CONFORME)
    st.session_state.cargas["vqm_conforme"] = st.session_state.cargas["diferencia_temperaturas"].apply(
        lambda x: True if lix <= x <= lsx else False
    )

    # agregar cálculos a la tabla de cargas
    st.session_state.cargas["desviacion_tmi"] = desviacion_tmi
    st.session_state.cargas["desviacion_tmi_tr"] = desviacion_tmi_tr
    st.session_state.cargas["media_tmi_tr"] = media_tmi_tr
    st.session_state.cargas["lsx"] = lsx
    st.session_state.cargas["lix"] = lix


# mostrar cargas ingresadas
st.dataframe(st.session_state.cargas)

st.markdown("<div class='separator'></div>", unsafe_allow_html=True)

# enviar los datos a la BBDD a través de la API Flask
def enviar_datos():
    if st.session_state.cargas.empty:
        st.error("❌ No hay datos para guardar.")
        return
    
    # reemplazar valores problemáticos antes de enviar a la API
    data_to_send = (
        st.session_state.cargas
        .fillna(0.0)  # Sustituir NaN por 0.0
        .replace([np.inf, -np.inf], 0.0)  # Sustituir Inf y -Inf por 0.0
        .applymap(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, pd.Timestamp) else x)  # Convertir fechas a string
        .to_dict(orient="records")
    )

    # enviar cada registro por separado
    for registro in data_to_send:
        nuevo_registro = {
            "titulo": maquina,
            "fecha": registro["fecha"],
            "num_ml_dia": registro["num_ml_dia"],
            "temperatura_mi": registro["temperatura_mi"],
            "temperatura_pistola": registro["temperatura_pistola"],
            "diferencia_temperaturas": registro["diferencia_temperaturas"],
            "trimestre_anio": registro["trimestre_anio"],
            "operario": registro["operario"],
            "desviacion_tmi": registro["desviacion_tmi"],
            "desviacion_tmi_tr": registro["desviacion_tmi_tr"],
            "media_tmi_tr": registro["media_tmi_tr"],
            "lsx": registro["lsx"],
            "lix": registro["lix"],
            "vqm_conforme": bool(registro["vqm_conforme"])
        }

        try:
            response = requests.post(f"{API_URL}/vqm_temperatura_mi10", json=nuevo_registro)
            if response.status_code == 201:
                st.success(f"✅ Registro guardado correctamente: {registro['fecha']}")
            else:
                st.error(f"❌ Error al guardar el registro {registro['fecha']}. {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Error en la conexión con la API: {str(e)}")

# deshabilitar el botón si no hay suficientes registros
boton_guardar_desactivado = len(st.session_state.cargas) < 5

# mostrar advertencia si hay menos de 5 registros
if boton_guardar_desactivado:
    st.warning("⚠️ Debes agregar al menos 5 registros antes de guardar en la base de datos.")

# botón para guardar datos en la BBDD
if st.button("📥 Guardar datos en la BBDD", disabled=boton_guardar_desactivado):
    enviar_datos()