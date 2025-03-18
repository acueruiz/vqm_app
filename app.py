from backend import create_app
import streamlit as st

# Iniciar la aplicación Flask en segundo plano si es necesario
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)