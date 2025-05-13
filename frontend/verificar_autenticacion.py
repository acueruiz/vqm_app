# auth.py
import streamlit as st

def verificar_autenticacion():
    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        st.warning("🔒 Debes iniciar sesión primero.")
        st.markdown('<meta http-equiv="refresh" content="0; URL=login.py">', unsafe_allow_html=True)
        st.stop()

    # asegurar que siempre haya valores válidos en el usuario
    st.session_state.setdefault("usuario", {
        "email": "sin_email",
        "nombre": "Usuario no identificado",
        "admin": False,
        "permisos": []
    })