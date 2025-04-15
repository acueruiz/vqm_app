import streamlit as st

def estilos_css():
    st.markdown(
        """
        <style>
            /* Encabezado principal de la página */
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

            /* Separadores visuales solo si usas en el contenido */
            .separator {
                border-bottom: 3px solid #0055A4;
                margin: 30px 0;
            }
        </style>
        """,
        unsafe_allow_html=True
    )