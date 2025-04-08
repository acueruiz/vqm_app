import streamlit as st
import requests

# configurar API URL
API_URL = "http://127.0.0.1:5000"

st.set_page_config(page_title="VQM - Iniciar Sesión", page_icon="🔐", layout="centered", initial_sidebar_state="collapsed")

st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            display: none !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Iniciar sesión")

# estado de autenticación en la sesión de Streamlit
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# formulario de Login
email = st.text_input("Correo electrónico", value="")
password = st.text_input("Contraseña", type="password", value="")

if st.button("Iniciar sesión"):
    response = requests.post(f"{API_URL}/login", json={"email": email, "password": password})

    if response.status_code == 200:
        data = response.json()
        st.session_state["authenticated"] = True
        st.session_state["user_email"] = data["email"]
        st.session_state["user_name"] = data["nombre"]
        st.success("✅ Inicio de sesión exitoso. Redirigiendo...")
        st.rerun()  # recarga la página
    else:
        st.error("❌ Credenciales incorrectas. Inténtalo de nuevo.")

if st.session_state["authenticated"]:
    st.switch_page("pages/home.py")