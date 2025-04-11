import streamlit as st
import requests
import os
import time

API_URL = os.getenv("API_URL", "http://127.0.0.1:5000/")

st.set_page_config(page_title="Gestión de correos", page_icon="📧", layout="wide")

logo_path = os.path.join(os.getcwd(), "frontend", "imagenes", "logo_michelin.png")
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_container_width=True)
else:
    st.sidebar.warning("⚠️ No se encontró el logo. Verifica la ruta del archivo.")

st.sidebar.title("MENÚ DE NAVEGACIÓN")
st.sidebar.page_link("pages/home.py", label="Inicio", icon="🏠")

with st.sidebar.expander("📝 Formularios", expanded=False):
    st.page_link("pages/vqm_mdm_form.py", label="VQM MDM Form", icon="📝")
    st.page_link("pages/vqm_temp_form.py", label="VQM Temperatura Form", icon="🌡️")
    st.page_link("pages/gestion_nc_form.py", label="Gestión NC Form", icon="⚠️")

with st.sidebar.expander("📊 Visualización de Datos", expanded=False):
    st.page_link("pages/view_data.py", label="Ver Datos MDM", icon="📋")
    st.page_link("pages/view_data_temp.py", label="Ver Datos Temp MI", icon="🌡️")
    st.page_link("pages/view_data_nc.py", label="Ver Datos NC", icon="⚠️")

with st.sidebar.expander("📊 Modificación de Datos", expanded=False):
    st.page_link("pages/edit_datos_mdms.py", label="Modificar Datos MDM", icon="⚙️")
    st.page_link("pages/edit_vqm_temp.py", label="Modificar Datos Teóricos VQM Temp", icon="🌡️")

with st.sidebar.expander("⚙️ Administración", expanded=False):
    st.page_link("pages/users.py", label="Gestión de usuarios", icon="👥")
    st.page_link("pages/correos.py", label="Gestión de correos", icon="📨")

st.sidebar.page_link("pages/vqm_dashboard.py", label="Dashboard", icon="📊")

st.markdown("""
<style>
    [data-testid="stSidebarNav"] { display: none !important; }
    [data-testid="stSidebar"] { padding-top: 0px !important; }
    [data-testid="stImage"] img {
        margin-top: -30px !important;
        margin-bottom: -20px !important;
    }
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
    .separator {
        border-bottom: 3px solid #0055A4;
        margin: 30px 0;
    }
</style>
""", unsafe_allow_html=True)

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
