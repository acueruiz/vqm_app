import streamlit as st
import os
import base64

API_URL = "https://vqm-api.onrender.com/vqm"

st.set_page_config(page_title="Dashboards", page_icon="📉", layout="wide")

# Obtener ruta absoluta de la imagen
logo_path = os.path.join(os.getcwd(), "frontend", "imagenes", "logo_michelin.png")

# Verificar si la imagen existe
t_logo = os.path.exists(logo_path)
if t_logo:
    st.sidebar.image(logo_path, use_container_width=True)
else:
    st.sidebar.warning("⚠️ No se encontró el logo. Verifica la ruta del archivo.")

# ---------------- Sidebar ---------------- #
st.sidebar.title("MENÚ DE NAVEGACIÓN")
st.sidebar.page_link("pages/home.py", label="Inicio", icon="🏠")

with st.sidebar.expander("📝 Formularios", expanded=False):
    st.page_link("pages/vqm_mdm_form.py", label="VQM MDM Form")
    st.page_link("pages/vqm_temp_form.py", label="VQM Temperatura Form")
    st.page_link("pages/gestion_nc_form.py", label="Gestión NC Form")

with st.sidebar.expander("📊 Visualización de Datos", expanded=False):
    st.page_link("pages/view_data.py", label="Ver Datos MDM")
    st.page_link("pages/view_data_temp.py", label="Ver Datos Temp MI")
    st.page_link("pages/view_data_nc.py", label="Ver Datos NC")

with st.sidebar.expander("📊 Modificación de Datos", expanded=False):
    st.page_link("pages/edit_datos_mdms.py", label="Modificar Datos MDM")
    st.page_link("pages/edit_vqm_temp.py", label="Modificar Datos Teóricos VQM Temp")

with st.sidebar.expander("⚙️ Administración", expanded=False):
    st.page_link("pages/users.py", label="Gestión de usuarios")
    st.page_link("pages/correos.py", label="Gestión de correos")

st.sidebar.page_link("pages/vqm_dashboard.py", label="Dashboard", icon="📉")

# estilos CSS personalizados
st.markdown(
    """
    <style>

        /* Oculta el menú de navegación automático de Streamlit */
        [data-testid="stSidebarNav"] {
            display: none !important;
        }

        [data-testid="stSidebar"] {
            padding-top: 0px !important; /* Reduce el padding superior del sidebar */
        }
        
        [data-testid="stImage"] img {
            margin-top: -30px !important; /* Reduce el espacio superior del logo */
            margin-bottom: -20px !important; /* Reduce el espacio inferior del logo */
        }
    
        /* Encabezados mejorados */
        .header {
            text-align: center;
            background-color: #0055A4;
            padding: 15px;
            color: white;
            font-size: 24px;
            font-weight: bold;
            border-radius: 8px;
            margin-bottom: 20px;
        }

        /* Botones personalizados */
        .stButton > button {
            background-color: #0055A4;
            color: white;
            font-size: 16px;
            padding: 10px 15px;
            border-radius: 8px;
            border: none;
            transition: 0.3s;
        }

        .stButton > button:hover {
            background-color: #003C7E;
            transform: scale(1.05);
        }

        /* Separadores visuales */
        .separator {
            border-bottom: 3px solid #0055A4;
            margin: 30px 0;
        }

        /* Mejora en la tabla de datos */
        .dataframe {
            border-collapse: collapse;
            width: 100%;
            background-color: white;
            border: 1px solid #ddd;
        }

        .dataframe th, .dataframe td {
            border: 1px solid #ddd;
            padding: 8px;
        }

        .dataframe th {
            background-color: #0055A4;
            color: white;
            text-align: left;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --------- Mostrar informes generados --------- #
st.markdown("---")
st.subheader("📄 Informes de NC generados")

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
            st.download_button("📥 Descargar PDF", data=pdf_data, file_name=informe_seleccionado, mime="application/pdf")

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