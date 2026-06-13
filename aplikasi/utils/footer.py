import streamlit as st

def render_footer():
    st.markdown(
        """
        <hr>
        <div style="text-align: center; font-weight: bold; color: blue;">
            Developed by Dzaya @2025
        </div>
        """,
        unsafe_allow_html=True
    )
