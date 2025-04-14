import streamlit as st
import requests
import os
import time

API_URL = "http://127.0.0.1:5000/"

st.set_page_config(page_title="Gestión de permisos", page_icon="🔐", layout="wide")

logo_path = os.path.join(os.getcwd(), "frontend", "imagenes", "logo_michelin.png")
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_container_width=True)
else:
    st.sidebar.warning("⚠️ No se encontró el logo. Verifica la ruta del archivo.")

st.sidebar.title("MENÚ DE NAVEGACIÓN")
st.sidebar.page_link("pages/home.py", label="Inicio", icon="🏠")

with st.sidebar.expander("📝 Formularios", expanded=False):
    st.page_link("pages/vqm_mdm_form.py", label="VQM MDM Form")
    st.page_link("pages/vqm_temp_form.py", label="VQM Temperatura Form")
    st.page_link("pages/gestion_nc_form.py", label="Gestión NC Form")

with st.sidebar.expander("📊 Visualización de Datos", expanded=False):
    st.page_link("pages/view_data.py", label="Ver Datos MDM")
    st.page_link("pages/view_data_temp.py", label="Ver Datos Temp MI")
    st.page_link("pages/view_data_nc.py", label="Ver Datos NC")

with st.sidebar.expander("🔧 Modificación de Datos", expanded=False):
    st.page_link("pages/edit_datos_mdms.py", label="Modificar Datos MDM")
    st.page_link("pages/edit_vqm_temp.py", label="Modificar Datos Teóricos VQM Temp")

with st.sidebar.expander("⚙️ Administración", expanded=False):
    st.page_link("pages/users.py", label="Gestión de usuarios")
    st.page_link("pages/correos.py", label="Gestión de correos")
    st.page_link("pages/permisos.py", label="Gestión de permisos")

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

st.markdown('<div class="header">Gestión de permisos por departamento</div>', unsafe_allow_html=True)

# Lista de departamentos
departamentos = ["OBTENCIÓN", "MEDIDA", "GARANTÍA"]

# Obtener usuarios
response_users = requests.get(f"{API_URL}/vqm/usuarios")
usuarios = response_users.json() if response_users.status_code == 200 else []

# Obtener permisos
response_permisos = requests.get(f"{API_URL}/vqm/permisos_usuarios")
permisos = response_permisos.json() if response_permisos.status_code == 200 else []

# Mostrar formulario por departamento
for dept in departamentos:
    st.markdown(f"### 🧩 {dept}")
    permisos_dept = [p for p in permisos if p["departamento"] == dept]
    usuarios_dept_ids = [p["usuario_id"] for p in permisos_dept]
    usuarios_dept = [u for u in usuarios if u["id"] in usuarios_dept_ids]

    col1, col2 = st.columns(2)

    # Añadir usuario al departamento
    with col1:
        with st.form(f"add_permiso_form_{dept}"):
            usuario_nuevo = st.selectbox(f"Selecciona usuario para añadir a {dept}", [u["email"] for u in usuarios if u["id"] not in usuarios_dept_ids], key=f"sel_add_{dept}")
            submitted = st.form_submit_button("➕ Añadir permiso")
            if submitted and usuario_nuevo:
                usuario_id = next((u["id"] for u in usuarios if u["email"] == usuario_nuevo), None)
                if usuario_id:
                    requests.post(f"{API_URL}/vqm/permisos_usuarios", json={
                        "usuario_id": usuario_id,
                        "departamento": dept
                    })
                    st.success("Permiso añadido correctamente")
                    time.sleep(1.5)
                    st.rerun()

    # Eliminar usuario del departamento
    with col2:
        if usuarios_dept:
            usuario_actual = st.selectbox(f"Selecciona usuario para eliminar de {dept}", [u["email"] for u in usuarios_dept], key=f"sel_del_{dept}")
            if st.button(f"❌ Eliminar '{usuario_actual}'", key=f"btn_del_{dept}"):
                permiso_id = next((p["id"] for p in permisos if p["departamento"] == dept and p["usuario_id"] == next((u["id"] for u in usuarios if u["email"] == usuario_actual), None)), None)
                if permiso_id:
                    requests.delete(f"{API_URL}/vqm/permisos_usuarios/{permiso_id}")
                    st.success("Permiso eliminado correctamente")
                    time.sleep(1.5)
                    st.rerun()
        else:
            st.info("No hay usuarios con acceso a este departamento.")

# Gestión de administradores
st.markdown("---")
st.markdown("### 👑 Administradores")
usuarios_admin = [u for u in usuarios if u.get("admin")]

col1, col2 = st.columns(2)

with col1:
    with st.form("add_admin_form"):
        usuario_admin = st.selectbox("Selecciona usuario para hacerlo administrador", [u["email"] for u in usuarios if not u.get("admin")], key="admin_add")
        submitted = st.form_submit_button("⭐ Añadir admin")
        if submitted:
            requests.put(f"{API_URL}/vqm/usuarios/{usuario_admin}", json={"admin": True})
            st.success("Administrador añadido")
            time.sleep(1.5)
            st.rerun()

with col2:
    if usuarios_admin:
        admin_actual = st.selectbox("Selecciona administrador para quitarle el rol", [u["email"] for u in usuarios_admin], key="admin_del")
        if st.button(f"❌ Quitar admin a '{admin_actual}'"):
            requests.put(f"{API_URL}/vqm/usuarios/{admin_actual}", json={"admin": False})
            st.success("Administrador eliminado")
            time.sleep(1.5)
            st.rerun()
