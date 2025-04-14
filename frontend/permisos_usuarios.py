import streamlit as st

def tiene_departamento(dep):
    return st.session_state.get("usuario", {}).get("admin") or dep in st.session_state.get("usuario", {}).get("permisos", [])
