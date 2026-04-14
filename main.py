
import streamlit as st

from ui.components import apply_custom_css, render_header
from ui.sidebar import render_sidebar
from ui.views import render_main_view

st.set_page_config(
    page_title="Prescripto | Asistent Medical",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    """Punctul de intrare principal al aplicației."""
    # 1. Aplicăm CSS-ul
    apply_custom_css()

    # 2. Afișăm elementele de meniu
    render_sidebar()
    render_header()

    # 3. Executăm logica principală (Upload, Analiză, Calendar)
    render_main_view()


if __name__ == "__main__":
    main()