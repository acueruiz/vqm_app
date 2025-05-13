import streamlit as st
import requests
import pandas as pd
from sidebar import mostrar_sidebar
from verificar_autenticacion import verificar_autenticacion
from styles import estilos_css
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from utils.email_sender import enviar_email

API_URL = "http://127.0.0.1:5000/vqm"

st.markdown("""
    <div class='app-header'>
      <h1>VQM MDM – Introducción de Datos</h1>
      <p>Formulario de registro para Verificación de Calidad Másica y Báscula</p>
    </div>
    <hr class='app-divider'/>
""", unsafe_allow_html=True)

# llamo a la función para autenticación de usuarios
verificar_autenticacion()

# llamo a la función para mostrar barra lateral
mostrar_sidebar()

# estilos de la página
estilos_css()

# convertir valores ingresados a float
def convertir_a_float(valor):
    """Convierte un valor a float, devolviendo None si no es válido."""
    try:
        return float(valor)
    except ValueError:
        return None

# cargar datos de la API Flask
@st.cache_data
def get_mdm_data():
    response = requests.get(f"{API_URL}/datos_mdms")
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        st.error("❌ Error al obtener detalles de MDMs.")
        return pd.DataFrame()

df_mdm = get_mdm_data()

st.subheader("Datos del MDM")

# selección del MDM
if not df_mdm.empty:
    mdm_selected = st.selectbox("Módulo MDM:", df_mdm["masico"].unique())
    mdm_details = df_mdm[df_mdm["masico"] == mdm_selected].iloc[0] if not df_mdm.empty else {}
else:
    mdm_selected = None
    mdm_details = {}

st.markdown("---")

st.subheader("Parámetros de referencia")

# formulario de introducción de datos
col1, col2, col3 = st.columns(3)
with col1:
    circuito = st.text_input("Circuito", mdm_details.get("circuito", ""), disabled=True)
    operador = st.text_input("Operador", value=st.session_state["usuario"]["nombre"], disabled=True)

with col2:
    bascula = st.text_input("Báscula", mdm_details.get("bascula", ""), disabled=True)

with col3:
    fecha = st.date_input("Fecha")

# obtener tolerancias desde la tabla mdm_details
tolerancia_cero = mdm_details.get("tolerancia_cero", 0.1)  # Valor por defecto 0.1 si no está definido
tolerancia_vr = mdm_details.get("tolerancia_vr", 0.2)  # Valor por defecto 0.2 si no está definido

# asegurar que peso_patron es float
peso_patron = convertir_a_float(mdm_details.get("vr_masas_patron", 0.0))

# cálculo de conformidad de la báscula usando tolerancias
def verificar_conformidad_bascula(valor_bascula, valor_cero, tolerancia_cero, tolerancia_vr, peso_patron):
    """
    Verifica si la báscula está conforme.
    - valor_cero_bascula debe estar dentro de ±tolerancia_cero.
    - valor_vqm_bascula debe estar dentro de ±tolerancia_vr.
    """

    # convertir valores a float si aún no lo están
    valor_bascula = convertir_a_float(valor_bascula)
    valor_cero = convertir_a_float(valor_cero)
    peso_patron = convertir_a_float(peso_patron)

    if valor_bascula is None or valor_cero is None or peso_patron is None:
        return "Datos incompletos"
    
    if abs(valor_cero) > tolerancia_cero or abs(valor_bascula - peso_patron) > tolerancia_vr:
        return "NO CONFORME"
    
    return "CONFORME"

def mostrar_conformidad(mensaje):
    color = "#BDBDBD"  # Gris por defecto (Datos incompletos)

    if mensaje == "CONFORME":
        color = "#4CAF50"  # Verde
    elif mensaje == "NO CONFORME":
        color = "#FF4B4B"  # Rojo

    st.markdown(f"""
        <div style="
            padding: 10px;
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
            color: white;
            background-color: {color};
            font-size: 18px;
            margin-top: 10px;
        ">
            {mensaje}
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

st.subheader("Verificación de la báscula")

col1, col2, col3, col4 = st.columns(4, gap="medium")

with col1:
    peso_patron = st.text_input("Peso masas patrón (kg)", str(mdm_details.get("vr_masas_patron", 0.0)), disabled=True)
    primera_cantidad = st.text_input("Primera cantidad (kg)", str(mdm_details.get("valor_test1", 0.0)), disabled=True)
    segunda_cantidad = st.text_input("Segunda cantidad (kg)", str(mdm_details.get("valor_test2", 0.0)), disabled=True)

with col2:
    st.text_input("Tolerancia VR (kg)", value=tolerancia_vr, disabled=True)
    st.text_input("Tolerancia Cero (kg)", value=tolerancia_cero, disabled=True)

with col3:
    valor_vqm_bascula = st.text_input("Valor VQM báscula (kg)")
    valor_cero_bascula = st.text_input("Valor cero VQM báscula (kg)")

    # calcular y mostrar "VQM Báscula Conforme"
    vqm_bascula_conforme = verificar_conformidad_bascula(valor_vqm_bascula, valor_cero_bascula, tolerancia_cero, tolerancia_vr, peso_patron)

    st.text("VQM Báscula Conforme:")
    mostrar_conformidad(vqm_bascula_conforme)

with col4:
    verif1_valor_masico = st.text_input("Cantidad 1 - Valor másico (kg)")
    verif1_valor_bascula = st.text_input("Cantidad 1 - Valor báscula (kg)")
    verif2_valor_masico = st.text_input("Cantidad 2 - Valor másico (kg)")
    verif2_valor_bascula = st.text_input("Cantidad 2 - Valor báscula (kg)")

# convertir todos los valores
peso_patron = convertir_a_float(mdm_details.get("vr_masas_patron", 0.0))
valor_vqm_bascula = convertir_a_float(valor_vqm_bascula)
valor_cero_bascula = convertir_a_float(valor_cero_bascula)
verif1_valor_masico = convertir_a_float(verif1_valor_masico)
verif1_valor_bascula = convertir_a_float(verif1_valor_bascula)
verif2_valor_masico = convertir_a_float(verif2_valor_masico)
verif2_valor_bascula = convertir_a_float(verif2_valor_bascula)

# cálculo errores
def calcular_error(valor_bascula, valor_maxico):
    """Calcula el error en gramos, redondeando a 0 decimales y manejando valores vacíos."""
    if valor_bascula is None or valor_maxico is None:
        return None
    return round((valor_bascula - valor_maxico) * 1000, 0)

error_cantidad_1 = calcular_error(verif1_valor_bascula, verif1_valor_masico)
error_cantidad_2 = calcular_error(verif2_valor_bascula, verif2_valor_masico)

# verificación de conformidad
tolerancia1 = mdm_details.get("tolerancia1", 10)
tolerancia2 = mdm_details.get("tolerancia2", 10)

def verificar_conformidad(error1, error2, tolerancia1, tolerancia2, segunda_cantidad):
    if error1 is None or error2 is None:
        return "Datos incompletos"
    if abs(error1) > tolerancia1 or abs(error2) > tolerancia2:
        return "NO CONFORME"
    if segunda_cantidad in [None, 0]:
        return "Introducir datos cantidad 2"
    return "CONFORME"

vqm_masico_conforme = verificar_conformidad(error_cantidad_1, error_cantidad_2, tolerancia1, tolerancia2, convertir_a_float(segunda_cantidad))

st.markdown("---")

st.subheader("Verificación del MDM")

col1, col2 = st.columns(2)
with col1:
    st.number_input("Error cantidad 1 (g)", value=error_cantidad_1 or 0, disabled=True)
    st.number_input("Error cantidad 2 (g)", value=error_cantidad_2 or 0, disabled=True)

with col2:
    st.text("VQM Másico Conforme:")
    mostrar_conformidad(vqm_masico_conforme)

st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

# envío de datos a la API Flask
def enviar_datos():
    nuevo_registro = {
        "titulo": mdm_selected,
        "fecha": str(fecha),
        "operador": operador,
        "valor_bascula": valor_vqm_bascula,
        "valor_cero_bascula": valor_cero_bascula,
        "error_cantidad1": error_cantidad_1,
        "error_cantidad2": error_cantidad_2,
        "vqm_masico_conforme": vqm_masico_conforme == "CONFORME",
        "vqm_bascula_conforme": vqm_bascula_conforme == "CONFORME",
        "cant1_verif1_valor_masico": verif1_valor_masico if verif1_valor_masico is not None else None,
        "cant1_verif1_valor_bascula": verif1_valor_bascula if verif1_valor_bascula is not None else None,
        "cant1_verif2_valor_masico": verif2_valor_masico if verif2_valor_masico is not None else None,
        "cant1_verif2_valor_bascula": verif2_valor_bascula if verif2_valor_bascula is not None else None,
        "cant2_verif1_valor_masico": segunda_cantidad if segunda_cantidad is not None else None,
        "cant2_verif1_valor_bascula": verif1_valor_bascula if verif1_valor_bascula is not None else None,
        "cant2_verif2_valor_masico": segunda_cantidad if segunda_cantidad is not None else None,
        "cant2_verif2_valor_bascula": verif2_valor_bascula if verif2_valor_bascula is not None else None
    }

    nuevo_registro = {k: v for k, v in nuevo_registro.items() if v is not None}

    try:
        response = requests.post(f"{API_URL}/vqm_mdm", json=nuevo_registro)
        if response.status_code == 201:
            st.success("Datos enviados correctamente.")
        else:
            st.error(f"Error al enviar los datos. {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error en la conexión con la API: {str(e)}")

if st.button("Guardar datos en la BBDD"):
    enviar_datos()

    if vqm_masico_conforme == "NO CONFORME" or vqm_bascula_conforme == "NO CONFORME":
        # tipo común para todos los casos MDM
        tipo_notificacion = "VQM MDM NC"

        # Obtener correos con ese tipo de notificación
        try:
            response = requests.get(f"{API_URL}/correos_usuarios")
            if response.status_code == 200:
                correos_todos = response.json()
                correos_destino = []

                for correo in correos_todos:
                    if correo["activo"]:
                        tipos = [t["nombre"] for t in correo.get("tipos", [])]
                        if tipo_notificacion in tipos:
                            correos_destino.append(correo["email"])

                if correos_destino:
                    cuerpo = f"""
                                Hola,

                                Se ha registrado una nueva NO CONFORMIDAD en un formulario VQM MDM.

                                Tipo de NC:
                                {"- NC MÁSICO" if vqm_masico_conforme == "NO CONFORME" else ""}
                                {"- NC BÁSCULA" if vqm_bascula_conforme == "NO CONFORME" else ""}

                                Detalles:
                                - Fecha: {fecha}
                                - Operador: {operador}
                                - Valor báscula: {valor_vqm_bascula} kg
                                - Valor másico: {verif1_valor_masico} kg

                                Puedes revisar más detalles en la aplicación VQM.

                                Saludos,
                                Sistema VQM
                                """
                    for correo in correos_destino:
                        enviar_email(correo, "⚠️ Nueva No Conformidad VQM MDM", cuerpo)

                    st.success("Formulario enviado y correos automáticos enviados.")
                else:
                    st.warning("No hay correos activos asignados al tipo VQM_MDM.")
            else:
                st.error("Error al consultar destinatarios de correo.")
        except Exception as e:
            st.error(f"Error al enviar correos automáticos: {e}")
