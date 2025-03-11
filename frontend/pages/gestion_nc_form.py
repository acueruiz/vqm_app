import streamlit as st
import requests
import datetime
import os

# Configuración de la API Flask
API_URL = "http://127.0.0.1:5000/vqm"

# Configuración de la página
st.set_page_config(page_title="Gestión de No Conformidades", layout="wide")

# Encabezado
st.markdown('<div class="header">TRATAMIENTO DE LAS NC DE LAS VQM</div>', unsafe_allow_html=True)

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

# ---------------- Formulario de No Conformidades ---------------- #

col1, col2, col3 = st.columns(3)
with col1:
    titulo = st.text_input("Título")
    maquina = st.text_input("Máquina")
    descripcion = st.text_area("Descripción de la intervención")
    efectos_producto = st.text_input("Posibles efectos sobre PRODUCTO")
    efectos_proceso = st.text_input("Posibles efectos sobre PROCESO")

with col2:
    fecha = st.date_input("Fecha", value=datetime.date.today())
    operador = st.text_input("Operario")
    causa = st.text_input("Causa")
    acciones_producto = st.text_input("Si producto NC, acciones")
    nc_validada = st.selectbox("NC validada", ["Pendiente", "Sí", "No"])

with col3:
    instrumento = st.text_input("Instrumento de medida")
    resultado = st.text_input("Resultado tras intervención")
    fecha_acciones = st.date_input("Fecha acciones producto", value=datetime.date.today())
    traza = st.text_input("Traza disponible", "NO HAY TRAZA GUARDADA", disabled=True)

st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

# ---------------- Botones de acción ---------------- #
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🧹 Limpiar formulario"):
        st.experimental_rerun()

with col2:
    if st.button("📧 Gestión de correos"):
        st.warning("Funcionalidad pendiente de integración.")

with col3:
    if st.button("📥 Guardar"):
        if not titulo or not fecha or not causa or not resultado:
            st.error("❌ Faltan campos obligatorios: Título, Fecha, Causa, Resultado tras intervención.")
        else:
            nuevo_registro = {
                "titulo": titulo,
                "fecha": str(fecha),
                "instrumento": instrumento,
                "maquina": maquina,
                "operador": operador,
                "causa": causa,
                "descripcion": descripcion,
                "resultado": resultado,
                "efectos_producto": efectos_producto,
                "efectos_proceso": efectos_proceso,
                "acciones_producto": acciones_producto,
                "fecha_acciones": str(fecha_acciones),
                "nc_validada": nc_validada,
                "traza": traza
            }

            try:
                response = requests.post(f"{API_URL}/nc_vqm", json=nuevo_registro)
                if response.status_code == 201:
                    st.success("✅ No Conformidad guardada correctamente.")
                else:
                    st.error(f"❌ Error al guardar la No Conformidad: {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Error en la conexión con la API: {str(e)}")
