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

API_URL = "http://127.0.0.1:5000/vqm"

# Configuración de la página
st.set_page_config(page_title="Gestión de No Conformidades", layout="wide", page_icon="⚠️")

# Encabezado
st.markdown('<div class="header">TRATAMIENTO DE LAS NC DE LAS VQM</div>', unsafe_allow_html=True)

# llamo a la función para autenticación de usuarios
verificar_autenticacion()

# llamo a la función para mostrar barra lateral
mostrar_sidebar()

# estilos de la página
estilos_css()

# ... (importaciones y configuración igual que antes)

@st.cache_data
def get_vqm_mdm_no_conformes():
    response = requests.get(f"{API_URL}/vqm_mdm")
    if response.status_code == 200:
        return [item for item in response.json() if not item.get("vqm_masico_conforme")]
    return []

@st.cache_data
def get_vqm_temp_no_conformes():
    response = requests.get(f"{API_URL}/vqm_temperatura")
    if response.status_code == 200:
        return [item for item in response.json() if not item.get("vqm_conforme")]
    return []

# ---------------- Selección de tipo de NC ---------------- #
st.markdown("### Selección del tipo de NC")
tipo_nc = st.radio("Selecciona el tipo de NC a tratar:", ["", "NC en MDM", "NC en Temperatura MI"], horizontal=True)

if tipo_nc == "":
    st.info("Selecciona primero el tipo de No Conformidad.")
    st.stop()

vqm_seleccionada = None
maquina = None
instrumento = None

if tipo_nc == "NC en MDM":
    vqms_mdm = get_vqm_mdm_no_conformes()
    opciones = [f"{item['titulo']} - Operador: {item['operador']}" for item in vqms_mdm]
    seleccion = st.selectbox("Selecciona una VQM MDM no conforme:", opciones)
    vqm_seleccionada = vqms_mdm[opciones.index(seleccion)]
    instrumento = vqm_seleccionada["titulo"]

elif tipo_nc == "NC en Temperatura MI":
    vqms_temp = get_vqm_temp_no_conformes()
    opciones = [f"{item['maquina']} - {item['trimestre_anio']}" for item in vqms_temp]
    seleccion = st.selectbox("Selecciona una VQM Temperatura no conforme:", opciones)
    vqm_seleccionada = vqms_temp[opciones.index(seleccion)]
    maquina = vqm_seleccionada["maquina"]

# Si ya se seleccionó una VQM, mostrar el formulario completo
if vqm_seleccionada:
    # ---------------- Sección 1: Datos generales ---------------- #
    st.markdown("### 1. Datos generales")
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        titulo = st.text_input("Título")

    with col2:
        fecha = st.date_input("Fecha", value=datetime.date.today())
        operador = st.text_input("Operario", value=st.session_state.get("user_name", ""), disabled=True)

    with col3:
        trimestre = st.selectbox("Trimestre", ["1 Trimestre", "2 Trimestre", "3 Trimestre", "4 Trimestre"])

    # Luego todo tu código actual del formulario...
    # Secciones 2 a 5 + enviar_datos() + boton "Guardar"
    # (puedes copiarlo tal cual debajo de este bloque condicional)

# Fin del bloque


@st.cache_data
def get_maquinas():
    response = requests.get(f"{API_URL}/vqm_temperatura")
    if response.status_code == 200:
        return list(set([item["maquina"] for item in response.json() if item["maquina"]]))
    return []

@st.cache_data
def get_instrumentos():
    response = requests.get(f"{API_URL}/datos_mdms")
    if response.status_code == 200:
        return list(set([item["id_dosificador"] for item in response.json() if item["id_dosificador"]]))
    return []

# ---------------- Sección 1: Datos generales ---------------- #
st.markdown("### 1. Datos generales")
st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

lista_maquinas = get_maquinas()
lista_instrumentos = get_instrumentos()

col1, col2, col3 = st.columns(3)

with col1:
    titulo = st.text_input("Título")
    maquina = st.selectbox("Máquina", lista_maquinas) if lista_maquinas else st.text_input("Máquina (manual)")

with col2:
    fecha = st.date_input("Fecha", value=datetime.date.today())
    operador = st.text_input("Operario", value=st.session_state.get("user_name", ""), disabled=True)

with col3:
    instrumento = st.selectbox("Instrumento de medida", lista_instrumentos) if lista_instrumentos else st.text_input("Instrumento (manual)")
    trimestre = st.selectbox("Trimestre", ["1 Trimestre", "2 Trimestre", "3 Trimestre", "4 Trimestre"])

# ---------------- Sección 2: Intervención ---------------- #
st.markdown("### 2. Intervención")
st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

# Descripción → Resultado → Causa
descripcion = st.text_area(
    "Descripción de la intervención",
    height=150,
    placeholder="Explica en detalle qué intervención se ha realizado"
)

resultado = st.text_input(
    "Resultado tras la intervención",
    placeholder="¿Qué resultado se obtuvo después de intervenir?"
)

causa = st.text_input(
    "Causa primera del fallo",
    placeholder="¿Cuál fue la causa raíz detectada?"
)

# ---------------- Sección 3: Posible efecto sobre el producto ---------------- #
st.markdown("### 3. Posible efecto sobre el producto")
st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

afecta_producto = st.radio("¿Posible efecto sobre el producto?", ["No", "Sí"], horizontal=True)

if afecta_producto == "Sí":
    with st.expander("Detalles sobre la afectación al producto"):
        resuelto_producto = st.radio("¿Anomalía resuelta por mantenimiento?", ["Sí", "No"], horizontal=True, key="resuelto_producto")

        if resuelto_producto == "No":
            acciones_producto = st.text_area(
                "Acciones para evitar producto NC futuro",
                placeholder="Describe qué acciones se han tomado o se tomarán"
            )

        traza_producto = st.file_uploader(
            "📎 Subir traza del producto afectado",
            type=["pdf", "jpg", "png", "csv", "xlsx"],
            help="Adjunta documentación o evidencias"
        )
else:
    acciones_producto = None
    traza_producto = None

# ---------------- Sección 4: Posible impacto sobre el proceso ---------------- #
st.markdown("### 4. Posible impacto sobre el proceso")
st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

afecta_proceso = st.radio("¿Posible impacto sobre el proceso?", ["No", "Sí"], horizontal=True)

if afecta_proceso == "Sí":
    with st.expander("Detalles sobre el impacto en el proceso"):
        resuelto_proceso = st.radio("¿Anomalía resuelta por mantenimiento?", ["Sí", "No"], horizontal=True, key="resuelto_proceso")

        if resuelto_proceso == "No":
            acciones_proceso = st.text_area(
                "Acciones para compensar deficiencia del proceso",
                placeholder="Describe qué acciones correctoras o preventivas se aplican"
            )
else:
    acciones_proceso = None

# ---------------- Sección 5: Validación final de la NC ---------------- #
st.markdown("### 5. Validación final de la NC")
st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

nc_validada = st.selectbox("¿NC validada?", ["Sí", "Sí con acciones", "No"])

comentarios_validacion = None
producto_nc = None
acciones_producto_nc = None
fecha_acciones = None

if nc_validada == "Sí con acciones":
    comentarios_validacion_si = st.text_area(
        "Comentarios del responsable o validador",
        placeholder="Explica por qué se toman acciones o por qué queda sin validar aún"
    )

if nc_validada == "No":
    comentarios_validacion_no = st.text_area(
        "Comentarios del responsable o validador",
        placeholder="Explica por qué no está validada, con opción a modificar a futuro"
    )

if nc_validada == "Sí con acciones":
    fecha_acciones = st.date_input("Fecha de implementación de acciones", value=datetime.date.today())

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
            st.success("✅ No Conformidad guardada correctamente.")
            # 📄 Generar informe PDF tras guardar la NC usando Jinja2
            env = Environment(loader=FileSystemLoader("templates"))
            template = env.get_template("informe_nc.html")

            # Preparar el contexto: filtrar los campos vacíos para no mostrarlos en el informe
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

            st.success(f"📄 PDF generado: {nombre_base}.pdf")
            time.sleep(1.5)
            st.rerun()

        else:
            st.error(f"❌ Error al guardar la NC: {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error en la conexión con la API: {str(e)}")

# botón para guardar
if st.button("Guardar datos en la BBDD"):
    enviar_datos()