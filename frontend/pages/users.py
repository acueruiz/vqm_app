import streamlit as st
import requests
import os
import time

# Configurar API URL
API_URL = "http://127.0.0.1:5000"

st.set_page_config(page_title="Gestión de Usuarios", page_icon="👥", layout="wide")

# Obtener ruta absoluta de la imagen
logo_path = os.path.join(os.getcwd(), "frontend", "imagenes", "logo_michelin.png")

# Verificar si la imagen existe
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_container_width=True)
else:
    st.sidebar.warning("⚠️ No se encontró el logo. Verifica la ruta del archivo.")

# ---------------- Sidebar con categorías agrupadas ---------------- #
st.sidebar.title("MENÚ DE NAVEGACIÓN")

# inicio
st.sidebar.page_link("pages/home.py", label="Inicio", icon="🏠")

# introducción de datos
with st.sidebar.expander("📝 Formularios", expanded=False):
    st.page_link("pages/vqm_mdm_form.py", label="VQM MDM Form", icon="📝")
    st.page_link("pages/vqm_temp_form.py", label="VQM Temperatura Form", icon="🌡️")
    st.page_link("pages/gestion_nc_form.py", label="Gestión NC Form", icon="⚠️")

# visualización de datos
with st.sidebar.expander("📊 Visualización de Datos", expanded=False):
    st.page_link("pages/view_data.py", label="Ver Datos MDM", icon="📋")
    st.page_link("pages/view_data_temp.py", label="Ver Datos Temp MI", icon="🌡️")
    st.page_link("pages/view_data_nc.py", label="Ver Datos NC", icon="⚠️")

# modificación de datos
with st.sidebar.expander("📊 Modificación de Datos", expanded=False):
    st.page_link("pages/edit_datos_mdms.py", label="Modificar Datos MDM", icon="⚙️")
    st.page_link("pages/edit_vqm_temp.py", label="Modificar Datos Teóricos VQM Temp", icon="🌡️")

# administración
with st.sidebar.expander("⚙️ Administración", expanded=False):
    st.page_link("pages/users.py", label="Usuarios", icon="👥")

# dashboard
st.sidebar.page_link("pages/vqm_dashboard.py", label="Dashboard", icon="📊")

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

st.title("Gestión de Usuarios")

# Obtener lista de usuarios
response = requests.get(f"{API_URL}/vqm/usuarios")
usuarios = response.json() if response.status_code == 200 else []

# añadir usuario
st.markdown("<h3 style='color: #0055A4;'>➕ Añadir Usuario</h3>", unsafe_allow_html=True)
with st.expander("Expande para añadir un nuevo usuario", expanded=False):
    email = st.text_input("📧 Correo electrónico")
    nombre = st.text_input("👤 Nombre completo")
    password = st.text_input("🔑 Contraseña", type="password")

    if st.button("📝 Crear Usuario"):
        if email and nombre and password:
            data_to_send = {
                "email": email,
                "nombre": nombre,
                "password": password
            }

            response = requests.post(f"{API_URL}/register", json=data_to_send)

            if response.status_code == 201:
                st.success("✅ Usuario creado exitosamente.")
                time.sleep(1.5)
                st.rerun()
            elif response.status_code == 400:
                st.error("❌ El usuario ya existe.")
            else:
                st.error("⚠️ Error al registrar el usuario.")
        else:
            st.warning("⚠️ Completa todos los campos.")

# modificar usuario
st.markdown("<h3 style='color: #0055A4;'>✏️ Modificar usuario o hacerle administrador</h3>", unsafe_allow_html=True)
with st.expander("Expande para modificar un usuario existente", expanded=False):
    if usuarios:
        selected_user = st.selectbox("🔄 Selecciona un usuario para modificar", [u["email"] for u in usuarios])

        nuevo_nombre = st.text_input("👤 Nuevo nombre completo", value="")
        nueva_password = st.text_input("🔑 Nueva contraseña (opcional)", type="password")
        nuevo_admin = st.checkbox("Convertir en Administrador", value=False)

        if st.button("💾 Guardar Cambios"):
            data = {"nombre": nuevo_nombre, "admin": nuevo_admin}
            if nueva_password:
                data["password"] = nueva_password  # Solo cambia la contraseña si se proporciona

            response = requests.put(f"{API_URL}/vqm/usuarios/{selected_user}", json=data)

            if response.status_code == 200:
                st.success("✅ Usuario modificado correctamente.")
                time.sleep(1.5)
                st.rerun()
            else:
                st.error("⚠️ Error al modificar el usuario.")
    else:
        st.warning("⚠️ No hay usuarios registrados.")

# borrar usuario
st.markdown("<h3 style='color: #C70039;'>🗑️ Borrar Usuario</h3>", unsafe_allow_html=True)
with st.expander("Expande para elegir el usuario a borrar", expanded=False):
    if usuarios:
        # crear un diccionario para mapear email con ID
        email_to_id = {u["email"]: u["id"] for u in usuarios}
        
        # mostrar emails en el desplegable
        selected_email = st.selectbox("Selecciona un usuario para eliminar", list(email_to_id.keys()))
        
        # obtener el ID correspondiente
        selected_user_id = email_to_id[selected_email]

        if st.button("❌ Eliminar Usuario"):
            response = requests.delete(f"{API_URL}/vqm/usuarios/{selected_user_id}")

            if response.status_code == 200:
                st.success("✅ Usuario eliminado correctamente.")
                time.sleep(1.5)
                st.rerun()
            else:
                st.error("⚠️ Error al eliminar el usuario.")
    else:
        st.warning("⚠️ No hay usuarios registrados.")

