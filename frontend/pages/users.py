import streamlit as st
import requests
import os
import time
import time
from sidebar import mostrar_sidebar
from verificar_autenticacion import verificar_autenticacion
from styles import estilos_css

API_URL = "http://127.0.0.1:5000"

st.set_page_config(page_title="Gestión de usuarios", page_icon="👥", layout="wide")

# llamo a la función para autenticación de usuarios
verificar_autenticacion()

# llamo a la función para mostrar barra lateral
mostrar_sidebar()

# estilos de la página
estilos_css()

# encabezado visual
st.markdown("""
    <div class='app-header'>
        <h1>Gestión de usuarios</h1>
        <p>Pantalla para creación, modificación y borrado de usuarios que acceden a la aplicación</p>
    </div>
    <hr class='app-divider'/>
""", unsafe_allow_html=True)

# Obtener lista de usuarios
response = requests.get(f"{API_URL}/vqm/usuarios")
usuarios = response.json() if response.status_code == 200 else []

# añadir usuario
st.markdown("<h3 style='color: #0055A4;'>Añadir usuario</h3>", unsafe_allow_html=True)
with st.expander("Expande para añadir un nuevo usuario", expanded=True):
    email = st.text_input("Correo electrónico")
    nombre = st.text_input("Nombre completo")
    password = st.text_input("Contraseña", type="password")

    if st.button("Crear usuario"):
        if email and nombre and password:
            data_to_send = {
                "email": email,
                "nombre": nombre,
                "password": password
            }

            response = requests.post(f"{API_URL}/register", json=data_to_send)

            if response.status_code == 201:
                st.success("Usuario creado exitosamente.")
                time.sleep(1.5)
                st.rerun()
            elif response.status_code == 400:
                st.error("El usuario ya existe.")
            else:
                st.error("Error al registrar el usuario.")
        else:
            st.warning("Completa todos los campos.")

# modificar usuario
st.markdown("<h3 style='color: #0055A4;'>Modificar usuario o hacerle administrador</h3>", unsafe_allow_html=True)
with st.expander("Expande para modificar un usuario existente", expanded=False):
    if usuarios:
        selected_user = st.selectbox("Selecciona un usuario para modificar", [u["email"] for u in usuarios])

        nuevo_nombre = st.text_input("Nuevo nombre completo", value="")
        nueva_password = st.text_input("Nueva contraseña (opcional)", type="password")
        nuevo_admin = st.checkbox("Convertir en Administrador", value=False)

        if st.button("Guardar cambios"):
            data = {"nombre": nuevo_nombre, "admin": nuevo_admin}
            if nueva_password:
                data["password"] = nueva_password  # solo cambia la contraseña si se mete una nueva, es opcional

            response = requests.put(f"{API_URL}/vqm/usuarios/{selected_user}", json=data)

            if response.status_code == 200:
                st.success("Usuario modificado correctamente.")
                time.sleep(1.5)
                st.rerun()
            else:
                st.error("Error al modificar el usuario.")
    else:
        st.warning("No hay usuarios registrados.")

# borrar usuario
st.markdown("<h3 style='color: #C70039;'>Borrar usuario</h3>", unsafe_allow_html=True)
with st.expander("Expande para elegir el usuario a borrar", expanded=False):
    if usuarios:
        # crear un diccionario para mapear email con ID
        email_to_id = {u["email"]: u["id"] for u in usuarios}
        
        # mostrar emails en el desplegable
        selected_email = st.selectbox("Selecciona un usuario para eliminar", list(email_to_id.keys()))
        
        # obtener el ID correspondiente
        selected_user_id = email_to_id[selected_email]

        if st.button("Eliminar Usuario"):
            response = requests.delete(f"{API_URL}/vqm/usuarios/{selected_user_id}")

            if response.status_code == 200:
                st.success("Usuario eliminado correctamente.")
                time.sleep(1.5)
                st.rerun()
            else:
                st.error("Error al eliminar el usuario.")
    else:
        st.warning("No hay usuarios registrados.")

