import streamlit as st

# -----------------------------------------------------------------------------
# Archivo de estilos CSS global para toda la aplicación
# -----------------------------------------------------------------------------
def estilos_css():
    st.markdown(
        """
        <style>
            /* Espaciado global */
            .block-container {
                padding-top: 1rem !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }

            /* Cabecera personalizada */
            .app-header {
                padding-top: 2rem !important;
            }
            .app-header h1 {
                margin: 0;
                font-size: 3rem;
            }
            .app-header p {
                margin: 0.3rem 0 1rem;
                font-size: 1.3rem;
                font-weight: 300;
            }

            /* Section headers sin border-radius inferior y sin separación */
            .section-header {
                padding: 6px !important;
                font-weight: bold !important;
                border-radius: 0 !important;
                margin: 1rem 0 0 !important;
                color: white !important;
            }
            .section-header--mensual { background-color: #5cb3ff !important; }
            .section-header--trimestral-dosi,
            .section-header--trimestral-cero { background-color: #ffb3e6 !important; }
            .section-header--trimestral-temp { background-color: #d6c944 !important; }

            /* Nuevo para formularios */
            .section-header--form {
                background-color: transparent !important;
                color: black !important;
                font-size: 1.25rem !important;
                padding-bottom: 0.25rem !important;
                border-bottom: 1px solid #ddd !important;
                margin-top: 2rem !important;
            }

            /* DataFrame: quitar border-radius superior */
            .stDataFrame > div > div:first-child {
                border-top-left-radius: 0 !important;
                border-top-right-radius: 0 !important;
            }

            /* Elimina separadores <hr> generados manualmente */
            hr.app-divider {
                display: none !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

