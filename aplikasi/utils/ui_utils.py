import streamlit as st
import os

def render_centered_title(title: str):
    st.markdown(
        f"""
        <style>
        .centered-title {{
            text-align: center;
            font-size: 36px;
            font-weight: bold;
            margin-top: auto;
        }}
        </style>
        <div class="centered-title">{title}</div>
        """,
        unsafe_allow_html=True
    )

def render_centered_image(image_path: str):
    st.markdown(
        """
        <style>
        .centered-image {
            display:flex;
            margin-top: 5px;
            margin-bottom: 5px;s
            margin-left: 20px;
            margin-right: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.image(image_path, width=1400, use_container_width=True)
