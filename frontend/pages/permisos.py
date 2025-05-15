import streamlit as st
import requests
import os
import time
from sidebar import mostrar_sidebar
from verificar_autenticacion import verificar_autenticacion
from styles import estilos_css

API_URL = "http://127.0.0.1:5000/"

st.set_page_config(page_title="Gestión de permisos", page_icon="🔐", layout="wide")

# llamo a la función para autenticación de usuarios
verificar_autenticacion()

# llamo a la función para mostrar barra lateral
mostrar_sidebar()

# estilos de la página
estilos_css()

# encabezado visual
st.markdown("""
    <div class='app-header'>
        <h1>Gestión de permisos</h1>
        <p>Gestión de permisos por departamento</p>
    </div>
    <hr class='app-divider'/>
""", unsafe_allow_html=True)

# lista de departamentos
departamentos = ["OBTENCIÓN", "MEDIDA", "GARANTÍA"]

# obtener usuarios
response_users = requests.get(f"{API_URL}/vqm/usuarios")
usuarios = response_users.json() if response_users.status_code == 200 else []

# obtener permisos
response_permisos = requests.get(f"{API_URL}/vqm/permisos_usuarios")
permisos = response_permisos.json() if response_permisos.status_code == 200 else []

# mostrar formulario por departamento
for dept in departamentos:
    st.markdown(f"### {dept}")
    permisos_dept = [p for p in permisos if p["departamento"] == dept]
    usuarios_dept_ids = [p["usuario_id"] for p in permisos_dept]
    usuarios_dept = [u for u in usuarios if u["id"] in usuarios_dept_ids]

    col1, col2 = st.columns(2)

    # añadir usuario al departamento
    with col1:
        with st.form(f"add_permiso_form_{dept}"):
            usuario_nuevo = st.selectbox(f"Selecciona usuario para añadir a {dept}", [u["email"] for u in usuarios if u["id"] not in usuarios_dept_ids], key=f"sel_add_{dept}")
            submitted = st.form_submit_button("Añadir permiso")
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

    # eliminar usuario del departamento
    with col2:
        if usuarios_dept:
            usuario_actual = st.selectbox(f"Selecciona usuario para eliminar de {dept}", [u["email"] for u in usuarios_dept], key=f"sel_del_{dept}")
            if st.button(f"Eliminar '{usuario_actual}'", key=f"btn_del_{dept}"):
                permiso_id = next((p["id"] for p in permisos if p["departamento"] == dept and p["usuario_id"] == next((u["id"] for u in usuarios if u["email"] == usuario_actual), None)), None)
                if permiso_id:
                    requests.delete(f"{API_URL}/vqm/permisos_usuarios/{permiso_id}")
                    st.success("Permiso eliminado correctamente")
                    time.sleep(1.5)
                    st.rerun()
        else:
            st.info("No hay usuarios con acceso a este departamento.")

# gestión de administradores
st.markdown("---")
st.markdown("### Administradores")
usuarios_admin = [u for u in usuarios if u.get("admin")]

col1, col2 = st.columns(2)

with col1:
    with st.form("add_admin_form"):
        usuario_admin = st.selectbox("Selecciona usuario para hacerlo administrador", [u["email"] for u in usuarios if not u.get("admin")], key="admin_add")
        submitted = st.form_submit_button("Añadir admin")
        if submitted:
            requests.put(f"{API_URL}/vqm/usuarios/{usuario_admin}", json={"admin": True})
            st.success("Administrador añadido")
            time.sleep(1.5)
            st.rerun()

with col2:
    if usuarios_admin:
        admin_actual = st.selectbox("Selecciona administrador para quitarle el rol", [u["email"] for u in usuarios_admin], key="admin_del")
        if st.button(f"Quitar admin a '{admin_actual}'"):
            requests.put(f"{API_URL}/vqm/usuarios/{admin_actual}", json={"admin": False})
            st.success("Administrador eliminado")
            time.sleep(1.5)
            st.rerun()
