import streamlit as st
import os
import requests
from permisos_usuarios import tiene_departamento

def mostrar_sidebar():
    # mostrar usuario arriba del todo
    st.sidebar.markdown(
        f"""
        <div style='margin-top: -20px; padding-bottom: 5px; font-size: 11px; text-align: center; color: #bbb;'>
            Usuario: <span>{st.session_state['usuario']['nombre']}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # mostrar logo
    logo_path = os.path.join(os.getcwd(), "frontend", "imagenes", "logo_michelin.png")
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, use_container_width=True)
    else:
        st.sidebar.warning("No se encontró el logo. Verifica la ruta del archivo.")

    # menú de navegación
    st.sidebar.title("MENÚ DE NAVEGACIÓN")

    st.sidebar.page_link("pages/home.py", label="Inicio")

    with st.sidebar.expander("Formularios", expanded=False):
        if tiene_departamento("MEDIDA") or tiene_departamento("OBTENCIÓN"):
            st.page_link("pages/vqm_mdm_form.py", label="VQM MDM Form")
        if tiene_departamento("OBTENCIÓN"):
            st.page_link("pages/vqm_temp_form.py", label="VQM Temperatura Form")
        if tiene_departamento("GARANTÍA"):
            st.page_link("pages/gestion_nc_form.py", label="Gestión NC Form")

    with st.sidebar.expander("Visualización de Datos", expanded=False):
        st.page_link("pages/view_data.py", label="Ver Datos MDM")
        st.page_link("pages/view_data_temp.py", label="Ver Datos Temp MI")
        st.page_link("pages/view_data_nc.py", label="Ver Datos NC")

    with st.sidebar.expander("Modificación de Datos", expanded=False):
        st.page_link("pages/edit_datos_mdms.py", label="Modificar Datos MDM")
        st.page_link("pages/edit_vqm_temp.py", label="Modificar Datos Teóricos VQM Temp")

    if st.session_state["usuario"]["admin"]:
        with st.sidebar.expander("Administración", expanded=False):
            st.page_link("pages/users.py", label="Gestión de usuarios")
            st.page_link("pages/correos.py", label="Gestión de correos")
            st.page_link("pages/permisos.py", label="Gestión de permisos")

    st.sidebar.page_link("pages/vqm_dashboard.py", label="Dashboard")

    # separador y botón logout
    st.sidebar.markdown('<hr style="margin-top: 30px; margin-bottom: 15px; border: none; border-top: 2px solid #666;">', unsafe_allow_html=True)

    if st.sidebar.button("Cerrar sesión", key="logout"):
        try:
            requests.post("http://127.0.0.1:5000/logout")
        except Exception as e:
            print("Error al cerrar sesión:", e)
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("🔒 Sesión cerrada. Redirigiendo...")
        import time
        time.sleep(1.5)
        st.switch_page("login.py")

    # CSS personalizado
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] { display: none !important; }
            [data-testid="stSidebar"] { padding-top: 5px !important; }
            [data-testid="stImage"] img {
                margin-top: -30px !important;
                margin-bottom: -20px !important;
            }

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
        </style>
    """, unsafe_allow_html=True)
