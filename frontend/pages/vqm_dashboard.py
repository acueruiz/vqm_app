import streamlit as st
import os
import base64
import time
import requests
from sidebar import mostrar_sidebar
from verificar_autenticacion import verificar_autenticacion
from styles import estilos_css

API_URL = "http://127.0.0.1:5000/vqm"

st.set_page_config(page_title="Dashboards", page_icon="📉", layout="wide")

# llamo a la función para autenticación de usuarios
verificar_autenticacion()

# llamo a la función para mostrar barra lateral
mostrar_sidebar()

# estilos de la página
estilos_css()

# encabezado visual
st.markdown("""
    <div class='app-header'>
        <h1>Informes de tratamiento de NCs</h1>
        <p>Visualización de informes generado a partir del formulario de tratamiento de NCs generado</p>
    </div>
    <hr class='app-divider'/>
""", unsafe_allow_html=True)

st.markdown("---")

carpeta_informes = "C:\\Users\\acuer\\OneDrive\\Escritorio\\informes"

if os.path.exists(carpeta_informes):
    informes = [f for f in os.listdir(carpeta_informes) if f.endswith((".html", ".pdf"))]

    if informes:
        informe_seleccionado = st.selectbox("Selecciona un informe:", sorted(informes, reverse=True))

        ruta_informe = os.path.join(carpeta_informes, informe_seleccionado)

        if informe_seleccionado.endswith(".html"):
            with open(ruta_informe, "r", encoding="utf-8") as f:
                contenido_html = f.read()

            st.components.v1.html(
                f"""
                <div style='display: flex; justify-content: center; padding: 20px;'>
                    <div style='width: 794px; padding: 40px; box-shadow: 0 0 10px rgba(0,0,0,0.2);'>
                        {contenido_html}
                    </div>
                </div>
                """,
                height=1200,
                scrolling=True
            )

        elif informe_seleccionado.endswith(".pdf"):
            ruta_pdf = os.path.join(carpeta_informes, informe_seleccionado)

            with open(ruta_pdf, "rb") as f:
                pdf_data = f.read()
                pdf_base64 = base64.b64encode(pdf_data).decode("utf-8")

            # Botón de descarga opcional
            st.download_button("Descargar PDF", data=pdf_data, file_name=informe_seleccionado, mime="application/pdf")

            st.markdown("### Vista previa del PDF")
            st.markdown(
                f"""
                <iframe 
                    src="data:application/pdf;base64,{pdf_base64}" 
                    width="794px" 
                    height="1123px" 
                    style="border:none; display: block; margin-left: auto; margin-right: auto;"
                    type="application/pdf">
                </iframe>
                """,
                unsafe_allow_html=True
            )

    else:
        st.info("No hay informes generados todavía.")
else:
    st.warning("La carpeta de informes no existe.")