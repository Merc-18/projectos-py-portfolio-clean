"""Interfaz Streamlit opcional para una solicitud PDF completamente ficticia."""
from __future__ import annotations
from pathlib import Path
import tempfile

try:
    from .generate_pdf import create_demo_pdf
except ImportError:  # invoked via streamlit run app.py
    from generate_pdf import create_demo_pdf


def main():
    import streamlit as st
    st.set_page_config(page_title='Generador PDF de demostración', page_icon='📄')
    st.title('Generador de solicitudes ficticias')
    st.info('Solo para demostración de programación. No introduzca datos personales reales.')
    with st.form('solicitud_ficticia'):
        descripcion = st.text_input('Descripción de ejemplo', value='Registro de prueba')
        monto = st.text_input('Monto ficticio', value='35.00')
        crear = st.form_submit_button('Crear PDF DEMO')
    if crear:
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'demo.pdf'
            try:
                create_demo_pdf(descripcion, monto, output)
            except (ValueError, FileExistsError) as exc:
                st.error(str(exc))
            else:
                st.download_button('Descargar PDF ficticio', output.read_bytes(), 'demo.pdf', mime='application/pdf')


if __name__ == '__main__':
    main()
