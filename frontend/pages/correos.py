import streamlit as st
import requests
import os
import time
from permisos_usuarios import tiene_departamento

API_URL = "http://127.0.0.1:5000/"

st.set_page_config(page_title="Gestión de correos", page_icon="📧", layout="wide")

# Verificar autenticación antes de mostrar la página
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("🔒 Debes iniciar sesión primero.")
    st.markdown('<meta http-equiv="refresh" content="0; URL=login.py">', unsafe_allow_html=True)
    st.stop()

# Inicializar claves necesarias ANTES DE USARLAS
st.session_state.setdefault("usuario", {
    "email": "sin_email",
    "nombre": "Usuario no identificado",
    "admin": False,
    "permisos": []
})

st.sidebar.markdown(
    f"""
    <div style='margin-top: -20px; padding-bottom: 5px; font-size: 11px; text-align: center; color: #bbb;'>
        Usuario: <span>{st.session_state['usuario']['email']}</span>
    </div>
    """,
    unsafe_allow_html=True
)

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
st.sidebar.page_link("pages/home.py", label="Inicio", icon="🏠")

# introducción de datos
with st.sidebar.expander("📝 Formularios", expanded=False):
    if tiene_departamento("MEDIDA") or tiene_departamento("OBTENCIÓN"):
        st.page_link("pages/vqm_mdm_form.py", label="VQM MDM Form")

    if tiene_departamento("OBTENCIÓN"):
        st.page_link("pages/vqm_temp_form.py", label="VQM Temperatura Form")

    if tiene_departamento("GARANTÍA"):
        st.page_link("pages/gestion_nc_form.py", label="Gestión NC Form")

# visualización de datos
with st.sidebar.expander("📊 Visualización de Datos", expanded=False):
    st.page_link("pages/view_data.py", label="Ver Datos MDM")
    st.page_link("pages/view_data_temp.py", label="Ver Datos Temp MI")
    st.page_link("pages/view_data_nc.py", label="Ver Datos NC")

# modificación de datos
with st.sidebar.expander("📊 Modificación de Datos", expanded=False):
    st.page_link("pages/edit_datos_mdms.py", label="Modificar Datos MDM")
    st.page_link("pages/edit_vqm_temp.py", label="Modificar Datos Teóricos VQM Temp")

# administración
if st.session_state["usuario"]["admin"]:
    with st.sidebar.expander("⚙️ Administración", expanded=False):
        st.page_link("pages/users.py", label="Gestión de usuarios")
        st.page_link("pages/correos.py", label="Gestión de correos")
        st.page_link("pages/permisos.py", label="Gestión de permisos")

# dashboard
st.sidebar.page_link("pages/vqm_dashboard.py", label="Dashboard", icon="📉")

st.sidebar.markdown('<hr style="margin-top: 30px; margin-bottom: 15px; border: none; border-top: 2px solid #666;">', unsafe_allow_html=True)

# botón de logout
if st.sidebar.button("Cerrar sesión", key="logout"):
    try:
        requests.post("http://127.0.0.1:5000/logout")
    except Exception as e:
        print("Error al cerrar sesión:", e)

    for key in list(st.session_state.keys()):
        del st.session_state[key]

    st.success("🔒 Sesión cerrada. Redirigiendo...")
    time.sleep(1.5)
    st.switch_page("login.py")

# estilos CSS personalizados
st.markdown(
    """
    <style>

        /* Estilo más pequeño y elegante para el usuario */
        .st-emotion-cache-1c7y2kd {
            font-size: 13px !important;
            margin-bottom: 0 !important;
        }

        /* Estilo del botón de cerrar sesión */
        .stButton > button[kind="secondary"] {
            background-color: #333 !important;
            color: white !important;
            width: 100%;
            text-align: center;
            border-radius: 8px;
        }

        .stButton > button[kind="secondary"]:hover {
            background-color: #555 !important;
        }

        /* Oculta el menú de navegación automático de Streamlit */
        [data-testid="stSidebarNav"] {
            display: none !important;
        }

        [data-testid="stSidebar"] {
            padding-top: -30px !important;
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

st.title("Gestión de correos por departamento")

# Lista de departamentos
departamentos = ["MANTENIMIENTO", "OBTENCIÓN", "MEDIDA"]

for dept in departamentos:
    st.markdown(f"### ✉️ {dept}")
    response = requests.get(f"{API_URL}/correos/departamento/{dept}")
    correos = response.json() if response.status_code == 200 else []

    st.write(f"Total correos: {len(correos)}")

    correos_activos = [c for c in correos if c["activo"]]

    col1, col2 = st.columns(2)
    with col1:
        with st.form(f"add_email_form_{dept}"):
            email = st.text_input("Nuevo correo", key=f"email_{dept}")
            nombre = st.text_input("Nombre del destinatario", key=f"nombre_{dept}")
            submitted = st.form_submit_button("➕ Añadir")
            if submitted and email:
                response = requests.post(f"{API_URL}/correos", json={
                    "email": email,
                    "nombre": nombre,
                    "departamento": dept
                })
                if response.status_code == 201:
                    st.success("Correo añadido correctamente")
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error("Error al añadir el correo")

    with col2:
        if correos:
            selected_email = st.selectbox(f"Selecciona correo para eliminar - {dept}", [c["email"] for c in correos], key=f"delete_{dept}")
            if st.button(f"❌ Eliminar '{selected_email}'", key=f"btn_delete_{dept}"):
                correo_id = next((c["id"] for c in correos if c["email"] == selected_email), None)
                if correo_id:
                    response = requests.delete(f"{API_URL}/correos/{correo_id}")
                    if response.status_code == 200:
                        st.success("Correo eliminado correctamente")
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.error("Error al eliminar el correo")
        else:
            st.info("No hay correos registrados para este departamento.")
