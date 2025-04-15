import streamlit as st
import requests
import os
import time
from sidebar import mostrar_sidebar
from verificar_autenticacion import verificar_autenticacion
from styles import estilos_css

API_URL = "http://127.0.0.1:5000/"

st.set_page_config(page_title="Gestión de correos", page_icon="📧", layout="wide")

# llamo a la función para autenticación de usuarios
verificar_autenticacion()

# llamo a la función para mostrar barra lateral
mostrar_sidebar()

# estilos de la página
estilos_css()

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
