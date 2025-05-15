import streamlit as st
import requests
import datetime
import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import time
from sidebar import mostrar_sidebar
from verificar_autenticacion import verificar_autenticacion
from styles import estilos_css
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from utils.email_sender import enviar_email

API_URL = "http://127.0.0.1:5000/vqm"

# Configuración de la página
st.set_page_config(page_title="Gestión de No Conformidades", layout="wide", page_icon="⚠️")

verificar_autenticacion()
mostrar_sidebar()
estilos_css()

# encabezado
st.markdown("""
    <div class='app-header'>
      <h1>Gestión de NCs de las VQMs</h1>
      <p>Tratamiento y validación de NC detectadas en VQM de MDM y Temperatura</p>
    </div>
    <hr class='app-divider'/>
""", unsafe_allow_html=True)

st.markdown("---")

# cogemos los datos de la bbdd con las rutas correspondientes
@st.cache_data
def get_vqm_mdm_no_conformes():
    r = requests.get(f"{API_URL}/vqm_mdm")
    return [item for item in r.json() if not item.get("vqm_masico_conforme")] if r.status_code == 200 else []

@st.cache_data
def get_maquinas():
    r = requests.get(f"{API_URL}/vqm_temperatura")
    return list(set([i["maquina"] for i in r.json() if i.get("maquina")])) if r.status_code == 200 else []

@st.cache_data
def get_instrumentos():
    r = requests.get(f"{API_URL}/datos_mdms")
    return list(set([i["id_dosificador"] for i in r.json() if i.get("id_dosificador")])) if r.status_code == 200 else []

@st.cache_data
def get_vqm_temp_no_validadas():
    r = requests.get(f"{API_URL}/vqm_temperatura_resumen")
    if r.status_code != 200:
        return []
    return [i for i in r.json() if i["estado"] == "NO CONFORME" and i["origen"] == "medicion"]

# ─────────────────────────────────────────────────────────────────────────────
st.subheader("Selección del tipo de NC")
tipo_nc = st.radio("Selecciona el tipo de NC a tratar:", ["NC en MDM", "NC en Temperatura MI"], horizontal=True, index=None)
if tipo_nc is None:
    st.info("Selecciona primero el tipo de No Conformidad.")
    st.stop()

vqm_seleccionada = None
instrumento = maquina = None

if tipo_nc == "NC en MDM":
    opciones = [f"{i['titulo']}  -  {i['operador']}  -  {i['fecha']}" for i in get_vqm_mdm_no_conformes()]
    seleccion = st.selectbox("Selecciona una VQM MDM no conforme:", opciones)
    vqm_seleccionada = get_vqm_mdm_no_conformes()[opciones.index(seleccion)]
    instrumento = vqm_seleccionada["titulo"]

if tipo_nc == "NC en Temperatura MI":
    opciones = [f"{i['maquina']} - {i['grupo_fecha']}" for i in get_vqm_temp_no_validadas()]
    seleccion = st.selectbox("Selecciona una VQM Temperatura no conforme:", opciones)
    vqm_seleccionada = get_vqm_temp_no_validadas()[opciones.index(seleccion)]
    maquina = vqm_seleccionada["maquina"]
    grupo_fecha = vqm_seleccionada["grupo_fecha"]

# ─────────────────────────────────────────────────────────────────────────────
if vqm_seleccionada:
    st.subheader("1. Datos generales")
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        titulo = st.text_input("Título", f"VQM NC del {instrumento}" if tipo_nc == "NC en MDM" else f"VQM NC de Temperatura MI - {maquina}")
    with col2:
        fecha = st.date_input("Fecha", value=datetime.date.today())
        operador = st.text_input("Operador", value=st.session_state["usuario"]["nombre"], disabled=True)
    with col3:
        trimestre = st.selectbox("Trimestre", ["1 Trimestre", "2 Trimestre", "3 Trimestre", "4 Trimestre"])

# ─────────────────────────────────────────────────────────────────────────────
st.subheader("2. Intervención")
st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

descripcion = st.text_area("Descripción de la intervención", height=150, placeholder="Explica en detalle qué intervención se ha realizado")
resultado = st.text_input("Resultado tras la intervención", placeholder="¿Qué resultado se obtuvo después de intervenir?")
causa     = st.text_input("Causa primera del fallo", placeholder="¿Cuál fue la causa raíz detectada?")

# ─────────────────────────────────────────────────────────────────────────────
st.subheader("3. Posible efecto sobre el producto")
st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

afecta_producto = st.radio("¿Posible efecto sobre el producto?", ["No", "Sí"], horizontal=True)
acciones_producto = traza_producto = None

if afecta_producto == "Sí":
    with st.expander("Detalles sobre la afectación al producto"):
        resuelto_producto = st.radio("¿Anomalía resuelta por mantenimiento?", ["Sí", "No"], horizontal=True, key="resuelto_producto")
        if resuelto_producto == "No":
            acciones_producto = st.text_area("Acciones para evitar producto NC futuro", placeholder="Describe qué acciones se han tomado o se tomarán")
        traza_producto = st.file_uploader("Subir traza del producto afectado", type=["pdf", "jpg", "png", "csv", "xlsx"])

# ─────────────────────────────────────────────────────────────────────────────
st.subheader("4. Posible impacto sobre el proceso")
st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

afecta_proceso = st.radio("¿Posible impacto sobre el proceso?", ["No", "Sí"], horizontal=True)
acciones_proceso = None

if afecta_proceso == "Sí":
    with st.expander("Detalles sobre el impacto en el proceso"):
        resuelto_proceso = st.radio("¿Anomalía resuelta por mantenimiento?", ["Sí", "No"], horizontal=True, key="resuelto_proceso")
        if resuelto_proceso == "No":
            acciones_proceso = st.text_area("Acciones para compensar deficiencia del proceso", placeholder="Describe acciones correctoras o preventivas")

# ─────────────────────────────────────────────────────────────────────────────
st.subheader("5. Validación final de la NC")
st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

nc_validada = st.selectbox("¿NC validada?", ["Sí", "Sí con acciones", "No"])
comentarios_validacion_si = comentarios_validacion_no = fecha_acciones = None

if nc_validada == "Sí con acciones":
    comentarios_validacion_si = st.text_area("Comentarios del responsable o validador")
    fecha_acciones = st.date_input("Fecha de implementación de acciones", value=datetime.date.today())

if nc_validada == "No":
    producto_nc = st.radio("¿El producto final queda como No Conforme?", ["No", "Sí"], key="producto_nc_radio")
    if producto_nc == "Sí":
        acciones_producto_nc = st.text_area("Acciones adicionales sobre el producto No Conforme")



# ---------------- Guardado de datos en la BBDD ---------------- #

from weasyprint import HTML  # Asegúrate de haber instalado weasyprint y las dependencias del sistema

def enviar_datos():
    # Guardar archivo subido (traza del producto) localmente con nombre único basado en fecha y contador
    nombre_archivo = None
    fecha_str = datetime.date.today().strftime("%Y%m%d")

    if traza_producto:
        carpeta_destino = "C:\\Users\\acuer\\OneDrive\\Escritorio\\trazas_vqm"
        os.makedirs(carpeta_destino, exist_ok=True)

        # Obtener extensión y crear nombre base con fecha
        extension = os.path.splitext(traza_producto.name)[-1]
        base_nombre = f"Traza_Producto_{fecha_str}"
        nombre_archivo = base_nombre + extension
        ruta_archivo = os.path.join(carpeta_destino, nombre_archivo)

        # Si ya existe un archivo con ese nombre, añadir contador
        contador = 1
        while os.path.exists(ruta_archivo):
            nombre_archivo = f"{base_nombre}_{contador}{extension}"
            ruta_archivo = os.path.join(carpeta_destino, nombre_archivo)
            contador += 1

        # Guardar archivo
        with open(ruta_archivo, "wb") as f:
            f.write(traza_producto.getbuffer())

    nuevo_registro = {
        "titulo": titulo,
        "fecha": str(fecha),
        "instrumento_medida": instrumento,
        "maquina": maquina,
        "operario": operador,
        "descripcion_intervencion": descripcion,
        "resultado_intervencion": resultado,
        "causa_fallo": causa,
        "trimestre_anio": trimestre,
        "afecta_producto": afecta_producto == "Sí",
        "afecta_proceso": afecta_proceso == "Sí",
        "resuelto_producto": resuelto_producto == "Sí" if afecta_producto == "Sí" else None,
        "acciones_producto": acciones_producto if afecta_producto == "Sí" and resuelto_producto == "No" else None,
        "traza_producto_nombre": nombre_archivo if traza_producto else None,
        "resuelto_proceso": resuelto_proceso == "Sí" if afecta_proceso == "Sí" else None,
        "acciones_proceso": acciones_proceso if afecta_proceso == "Sí" and resuelto_proceso == "No" else None,
        "nc_validada": True if nc_validada == "Sí" or nc_validada == "Sí con acciones" else False,
        "comentarios_validacion": comentarios_validacion_si if nc_validada == "Sí con acciones" else comentarios_validacion_no if nc_validada == "No" else None,
        "fecha_acciones": str(fecha_acciones) if fecha_acciones else None,
        "producto_nc": True if nc_validada == "No" and "producto_nc" in st.session_state and st.session_state["producto_nc_radio"] == "Sí" else False if nc_validada == "No" else None,
        "acciones_producto_nc": acciones_producto_nc if nc_validada == "No" and "producto_nc" in st.session_state and st.session_state["producto_nc_radio"] == "Sí" else None,
        "vqm_conforme": None  # --> esto se ajustará en un futuro
    }

    # Filtrar campos vacíos antes de enviar
    nuevo_registro = {k: v for k, v in nuevo_registro.items() if v is not None}

    try:
        response = requests.post(f"{API_URL}/tratamiento_nc_vqm", json=nuevo_registro)
        if response.status_code == 201:
            # Si es NC de temperatura validada, registrar nuevo resumen
            if tipo_nc == "NC en Temperatura MI" and nc_validada in ["Sí", "Sí con acciones"]:
                resumen_validado = {
                    "maquina": maquina.strip().upper(),
                    "grupo_fecha": grupo_fecha,  # debe estar definida en el selector
                    "estado": "CONFORME",
                    "origen": "validacion",
                    "fecha_evento": str(datetime.date.today())
                }

                r_resumen = requests.post(f"{API_URL}/vqm_temperatura_resumen", json=resumen_validado)
                if r_resumen.status_code == 201:
                    st.success("Resumen de validación añadido correctamente.")
                else:
                    st.warning(f"No se pudo guardar el resumen validado: {r_resumen.text}")

            st.success("Tratamiento de No Conformidad guardada correctamente.")
            # generar informe PDF tras guardar la NC usando Jinja2
            env = Environment(loader=FileSystemLoader("templates"))
            template = env.get_template("informe_nc.html")

            # preparar el contexto: filtrar los campos vacíos para no mostrarlos en el informe
            contexto_nc = {
                "titulo": titulo,
                "fecha": str(fecha),
                "instrumento_medida": instrumento,
                "maquina": maquina,
                "operario": operador,
                "descripcion_intervencion": descripcion,
                "resultado_intervencion": resultado,
                "causa_fallo": causa,
                "trimestre_anio": trimestre,
                "afecta_producto": afecta_producto,
                "resuelto_producto": resuelto_producto if afecta_producto == "Sí" else None,
                "acciones_producto": acciones_producto if afecta_producto == "Sí" and resuelto_producto == "No" else None,
                "traza_producto_nombre": nombre_archivo if traza_producto else None,
                "afecta_proceso": afecta_proceso,
                "resuelto_proceso": resuelto_proceso if afecta_proceso == "Sí" else None,
                "acciones_proceso": acciones_proceso if afecta_proceso == "Sí" and resuelto_proceso == "No" else None,
                "nc_validada": nc_validada,
                "comentarios_validacion": comentarios_validacion_si if nc_validada == "Sí con acciones" else comentarios_validacion_no if nc_validada == "No" else None,
                "fecha_acciones": fecha_acciones if nc_validada == "Sí con acciones" else None,
                "producto_nc": st.session_state.get("producto_nc_radio") if nc_validada == "No" else None,
                "acciones_producto_nc": acciones_producto_nc if nc_validada == "No" and st.session_state.get("producto_nc_radio") == "Sí" else None
            }
            # Remover claves con valores vacíos
            contexto_nc = {k: v for k, v in contexto_nc.items() if v not in [None, "", []]}

            # Renderizar el HTML del informe
            html_content = template.render(nc=contexto_nc)

            carpeta_informes = "C:\\Users\\acuer\\OneDrive\\Escritorio\\informes"
            os.makedirs(carpeta_informes, exist_ok=True)
            nombre_base = f"Informe_{titulo}_{fecha_str}"
            ruta_pdf = os.path.join(carpeta_informes, nombre_base + ".pdf")

            # Convertir el HTML a PDF y guardarlo
            HTML(string=html_content).write_pdf(ruta_pdf)

            # Convertir el HTML a PDF y guardarlo
            HTML(string=html_content).write_pdf(ruta_pdf)
            st.success(f"PDF generado: {nombre_base}.pdf")

            tipo_notificacion = "Tratamiento NCs No Resuelta" if tipo_nc == "VQM MDM NC" else "VQM Temperaturas MI NC"

            try:
                resp = requests.get(f"{API_URL}/correos_usuarios")  # ruta completa
                if resp.status_code == 200:
                    correos_todos = resp.json()
                    correos_destino = []

                    for correo in correos_todos:
                        if correo["activo"]:
                            tipos = [t["nombre"] for t in correo.get("tipos", [])]
                            if tipo_notificacion in tipos:
                                correos_destino.append(correo["email"])

                    if correos_destino:
                        cuerpo = f"""
                        Hola,

                        Se ha registrado una nueva NO CONFORMIDAD validada en el sistema VQM.

                        Tipo: {tipo_nc}
                        Fecha: {fecha}
                        Operario: {operador}
                        Instrumento/Máquina: {instrumento or maquina}

                        Puedes consultar más detalles en la aplicación VQM o revisar el informe generado.

                        Saludos,
                        Sistema VQM
                        """
                        for correo in correos_destino:
                            enviar_email(correo, f"⚠️ Nueva NC registrada en VQM - {tipo_nc}", cuerpo)

                        st.success("Correos de notificación enviados correctamente.")
                    else:
                        st.warning(f"No hay correos activos asignados al tipo '{tipo_notificacion}'.")
                else:
                    st.error("Error al consultar destinatarios para el envío automático de correos.")
            except Exception as e:
                st.error(f"Error al enviar correos automáticos: {e}")

        else:
            st.error(f"Error al guardar la NC: {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error en la conexión con la API: {str(e)}")

    time.sleep(5)
    st.rerun()

# ---------------- Botón para guardar la NC ---------------- #
if st.button("Guardar datos en la BBDD"):
    enviar_datos()