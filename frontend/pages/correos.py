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
    st.markdown(f"### {dept}")
    response = requests.get(f"{API_URL}/correos/departamento/{dept}")
    correos = response.json() if response.status_code == 200 else []

    st.write(f"Total correos: {len(correos)}")

    correos_activos = [c for c in correos if c["activo"]]

    col1, col2 = st.columns(2)
    with col1:
        with st.form(f"add_email_form_{dept}"):
            email = st.text_input("Nuevo correo", key=f"email_{dept}")
            nombre = st.text_input("Nombre del destinatario", key=f"nombre_{dept}")
            submitted = st.form_submit_button("Añadir")

            def obtener_tipo_notificacion(departamento):
                # lógica centralizada, extensible
                if departamento == "MANTENIMIENTO":
                    return "VQM_MDM"
                elif departamento == "MEDIDA":
                    return "VQM_Bascula"
                elif departamento == "OBTENCIÓN":
                    return "VQM_MDM"
                else:
                    return "DESCONOCIDO"

            if submitted and email:
                tipo_notificacion = obtener_tipo_notificacion(dept)
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
            if st.button(f"Eliminar '{selected_email}'", key=f"btn_delete_{dept}"):
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

# Obtener todos los tipos de notificación
resp_tipos = requests.get(f"{API_URL}/tipos_notificacion")
tipos_disponibles = resp_tipos.json() if resp_tipos.status_code == 200 else []

# Reunir todos los correos activos de todos los departamentos
correos_activos = []
departamentos = ["MANTENIMIENTO", "OBTENCIÓN", "MEDIDA"]
for dept in departamentos:
    response = requests.get(f"{API_URL}/correos/departamento/{dept}")
    if response.status_code == 200:
        correos = response.json()
        correos_activos.extend([c for c in correos if c["activo"]])

# Mostrar sección de configuración de notificaciones
st.markdown("### Tipos de notificación por correo")
for correo in correos_activos:
    correo_id = correo["id"]
    email = correo["email"]
    
    # Obtener tipos ya asignados a este correo
    tipos_actuales = [tipo["nombre"] for tipo in correo.get("tipos", [])]

    # Multiselect con todos los disponibles
    opciones_nombres = [tipo["nombre"] for tipo in tipos_disponibles]
    seleccionados = st.multiselect(
        f"Notificaciones para {email}",
        opciones_nombres,
        default=tipos_actuales,
        key=f"notif_{correo_id}"
    )

    # Botón para guardar cambios
    if st.button(f"💾 Guardar notificaciones para {email}", key=f"btn_save_notif_{correo_id}"):
        resp = requests.put(f"{API_URL}/correos/{correo_id}/notificaciones", json={
            "tipos": seleccionados
        })
        if resp.status_code == 200:
            st.success("Notificaciones actualizadas correctamente.")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Error al actualizar notificaciones.")

import pandas as pd

# Obtener todos los correos de todos los departamentos
response = requests.get(f"{API_URL}/vqm/correos_usuarios")
correos_todos = response.json() if response.status_code == 200 else []

# Obtener tipos de notificación disponibles (ya se hizo arriba, pero aseguramos)
if not tipos_disponibles:
    resp_tipos = requests.get(f"{API_URL}/tipos_notificacion")
    
    tipos_disponibles = resp_tipos.json() if resp_tipos.status_code == 200 else []

# Construir la tabla
tabla = []
for correo in correos_todos:
    tipos = correo.get("tipos", [])
    nombres_tipos = ", ".join([t["nombre"] for t in tipos]) if tipos else "Sin asignar"
    tabla.append({
        "Correo": correo["email"],
        "Nombre": correo.get("nombre", ""),
        "Departamento": correo.get("departamento", ""),
        "Tipos de notificación": nombres_tipos
    })

# Mostrar en Streamlit
st.markdown("## Resumen de notificaciones por correo")
df = pd.DataFrame(tabla)
st.dataframe(df, use_container_width=True)