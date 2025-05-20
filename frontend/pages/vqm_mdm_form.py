import streamlit as st
import requests
import pandas as pd
from sidebar import mostrar_sidebar
from verificar_autenticacion import verificar_autenticacion
from styles import estilos_css
import sys
import os
import time

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
        st.error("Error al obtener detalles de MDMs.")
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

st.markdown("---")

st.subheader("Verificación de la báscula")

# obtener tolerancias desde la tabla mdm_details
tolerancia_cero = mdm_details.get("tolerancia_cero", 0.1)  # valor por defecto 0.1 si no está definido
tolerancia_vr = mdm_details.get("tolerancia_vr", 0.2)  # valor por defecto 0.2 si no está definido

# asegurar que peso_patron es float
peso_patron = convertir_a_float(mdm_details.get("vr_masas_patron", 0.0))

# cálculo de conformidad de la báscula usando tolerancias
def verificar_conformidad_bascula(valor_bascula, valor_cero, tolerancia_cero, tolerancia_vr, peso_patron):
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
    color = "#BDBDBD"  # gris por defecto (Datos incompletos)

    if mensaje == "CONFORME":
        color = "#4CAF50"  # verde
    elif mensaje == "NO CONFORME":
        color = "#FF4B4B"  # rojo

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

col1, col2, col3 = st.columns(3, gap="medium")

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

# convertir todos los valores
peso_patron = convertir_a_float(mdm_details.get("vr_masas_patron", 0.0))
valor_vqm_bascula = convertir_a_float(valor_vqm_bascula)
valor_cero_bascula = convertir_a_float(valor_cero_bascula)

st.markdown("---")

st.subheader("Verificación del MDM")

# --- Tolerancias ---
tolerancia1 = mdm_details.get("tolerancia1", 30)
tolerancia2 = mdm_details.get("tolerancia2", 110)

st.markdown("#### Parámetros de referencia")
col_tol1, col_tol2 = st.columns(2)
with col_tol1:
    st.text_input("Tolerancia 1ª cantidad (g)", value=tolerancia1, disabled=True)
with col_tol2:
    st.text_input("Tolerancia 2ª cantidad (g)", value=tolerancia2, disabled=True)

st.markdown("#### Introducción de valores medidos")
col1, col2 = st.columns(2)

# ---------- INPUTS CANTIDAD 1 ----------
with col1:
    c1_masico_v1 = st.text_input("Cantidad 1 - Másico 1ª verificación (kg)")
    c1_bascula_v1 = st.text_input("Cantidad 1 - Báscula 1ª verificación (kg)")

with col2:
    c2_masico_v1 = st.text_input("Cantidad 2 - Másico 1ª verificación (kg)")
    c2_bascula_v1 = st.text_input("Cantidad 2 - Báscula 1ª verificación (kg)")

# Convertimos las 1ª verificaciones
c1_m1 = convertir_a_float(c1_masico_v1)
c1_b1 = convertir_a_float(c1_bascula_v1)
c2_m1 = convertir_a_float(c2_masico_v1)
c2_b1 = convertir_a_float(c2_bascula_v1)

# Función de error
def calcular_error(b1, m1, b2=None, m2=None):
    if b1 is None or m1 is None:
        return None
    if b2 is not None and m2 is not None:
        return round((b2 - m2) * 1000, 0)
    return round((b1 - m1) * 1000, 0)

# Detectar necesidad de 2ª verif
def necesita_segunda(error, tol):
    return error is not None and abs(error) > tol

error_c1 = calcular_error(c1_b1, c1_m1)
error_c2 = calcular_error(c2_b1, c2_m1)

activar_c1_v2 = necesita_segunda(error_c1, tolerancia1)
activar_c2_v2 = necesita_segunda(error_c2, tolerancia2)

# ---------- INPUTS 2ª VERIFICACIÓN (si necesarias) ----------
col3, col4 = st.columns(2)

with col3:
    c1_masico_v2 = st.text_input("Cantidad 1 - Másico 2ª verificación (kg)", disabled=not activar_c1_v2)
    c1_bascula_v2 = st.text_input("Cantidad 1 - Báscula 2ª verificación (kg)", disabled=not activar_c1_v2)

with col4:
    c2_masico_v2 = st.text_input("Cantidad 2 - Másico 2ª verificación (kg)", disabled=not activar_c2_v2)
    c2_bascula_v2 = st.text_input("Cantidad 2 - Báscula 2ª verificación (kg)", disabled=not activar_c2_v2)

# Convertir segunda verif (solo si necesarias)
c1_m2 = convertir_a_float(c1_masico_v2) if activar_c1_v2 else None
c1_b2 = convertir_a_float(c1_bascula_v2) if activar_c1_v2 else None
c2_m2 = convertir_a_float(c2_masico_v2) if activar_c2_v2 else None
c2_b2 = convertir_a_float(c2_bascula_v2) if activar_c2_v2 else None

# Recalcular errores (usando 2ª si procede)
error_c1 = calcular_error(c1_b1, c1_m1, c1_b2, c1_m2)
error_c2 = calcular_error(c2_b1, c2_m1, c2_b2, c2_m2)

# Evaluar conformidad
def evaluar(error1, m2, b2, tol):
    if error1 is None:
        return "Datos incompletos"
    if abs(error1) > tol:
        if m2 is None or b2 is None:
            return "Datos segunda verificación"
        elif abs((b2 - m2) * 1000) > tol:
            return "NO CONFORME"
        else:
            return "CONFORME"
    return "CONFORME"

c1_conforme = evaluar(error_c1, c1_m2, c1_b2, tolerancia1)
c2_conforme = evaluar(error_c2, c2_m2, c2_b2, tolerancia2)

# Resultado global
if "NO CONFORME" in (c1_conforme, c2_conforme):
    vqm_masico_conforme = "NO CONFORME"
elif "Datos incompletos" in (c1_conforme, c2_conforme):
    vqm_masico_conforme = "Datos incompletos"
elif "Datos segunda verificación" in (c1_conforme, c2_conforme):
    vqm_masico_conforme = "Datos segunda verificación"
else:
    vqm_masico_conforme = "CONFORME"

# ---------- Mostrar resultados ----------
st.markdown("#### Cálculo de errores automático")
col1, col2 = st.columns(2)
with col1:
    st.number_input("Error cantidad 1 (g)", value=error_c1 or 0, disabled=True)
    st.number_input("Error cantidad 2 (g)", value=error_c2 or 0, disabled=True)

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
        "error_cantidad1": error_c1,
        "error_cantidad2": error_c2,
        "vqm_masico_conforme": vqm_masico_conforme == "CONFORME",
        "vqm_bascula_conforme": vqm_bascula_conforme == "CONFORME",
        "cant1_verif1_valor_masico": c1_m1,
        "cant1_verif1_valor_bascula": c1_b1,
        "cant1_verif2_valor_masico": c1_m2,
        "cant1_verif2_valor_bascula": c1_b2,
        "cant2_verif1_valor_masico": c2_m1,
        "cant2_verif1_valor_bascula": c2_b1,
        "cant2_verif2_valor_masico": c2_m2,
        "cant2_verif2_valor_bascula": c2_b2
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
        tipo_notificacion = "VQM MDM NC"

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

                                Tipo de NC detectada:
                                {"- NC MÁSICO" if vqm_masico_conforme == "NO CONFORME" else ""}
                                {"- NC BÁSCULA" if vqm_bascula_conforme == "NO CONFORME" else ""}

                                Detalles generales:
                                - Fecha: {fecha}
                                - Operador: {operador}
                                - MDM: {mdm_selected}

                                Verificación BÁSCULA:
                                - Valor patrón: {peso_patron} kg
                                - Valor leído báscula: {valor_vqm_bascula} kg
                                - Valor cero: {valor_cero_bascula} kg
                                - Tolerancia VR: {tolerancia_vr} kg
                                - Tolerancia Cero: {tolerancia_cero} kg
                                - Resultado: {"NO CONFORME" if vqm_bascula_conforme == "NO CONFORME" else "CONFORME"}

                                Verificación MÁSICO:

                                Cantidad 1:
                                - 1ª Verif: {c1_m1} kg (másico) vs {c1_b1} kg (báscula)
                                - 2ª Verif: {c1_m2 or '-'} kg (másico) vs {c1_b2 or '-'} kg (báscula)
                                - Error resultante: {error_c1 or '-'} g

                                Cantidad 2:
                                - 1ª Verif: {c2_m1} kg (másico) vs {c2_b1} kg (báscula)
                                - 2ª Verif: {c2_m2 or '-'} kg (másico) vs {c2_b2 or '-'} kg (báscula)
                                - Error resultante: {error_c2 or '-'} g

                                - Tolerancia cantidad 1: {tolerancia1} g
                                - Tolerancia cantidad 2: {tolerancia2} g
                                - Resultado: {"NO CONFORME" if vqm_masico_conforme == "NO CONFORME" else "CONFORME"}

                                Puedes revisar más detalles desde la aplicación VQM.

                                Saludos,
                                Sistema VQM
                                """

                    for correo in correos_destino:
                        enviar_email(correo, "⚠️ Nueva No Conformidad VQM MDM", cuerpo)

                    st.success("Enviados correos automáticos.")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.warning("No hay correos activos asignados al tipo VQM_MDM.")
            else:
                st.error("Error al consultar destinatarios de correo.")
        except Exception as e:
            st.error(f"Error al enviar correos automáticos: {e}")

