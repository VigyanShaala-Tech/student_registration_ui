# modules/page_config.py

import streamlit as st

def setup_she_for_stem_page():
    # Set page config at the very beginning
    st.set_page_config(
        page_title="She for STEM Program ",
        page_icon="👩‍🔬",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Display the PNG image in the top left corner of the Streamlit sidebar with custom dimensions
    image_path = "https://raw.githubusercontent.com/VigyanShaala-Tech/student_registration_ui/final_registration_ui/image/vslogo.png"
    st.markdown(
        f'<div style="text-align:center"><img src="{image_path}" width="200"></div>',
        unsafe_allow_html=True
    )

    # Title display
    st.markdown(
        "<div style='text-align: center;margin-bottom: 30px;'>"
        "<span style='font-size: 34px; font-weight: bold;'>Registration Records Access</span><br>"
        "</div>", 
        unsafe_allow_html=True
    )

