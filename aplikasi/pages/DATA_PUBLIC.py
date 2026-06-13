import streamlit as st
from utils.ui_utils import render_centered_title
from utils.footer import render_footer

# if "logged_in" not in st.session_state or not st.session_state.logged_in:
#     st.warning("Silakan login terlebih dahulu melalui halaman Login.")
#     st.stop()
            
# Judul aplikasi
render_centered_title("PUBLIC DATA SOURCES")

# Penjelasan tentang sumber data publik
st.markdown("""
<div style="text-align: center;">
Public data refers to data that is freely and openly available for access, use, and sharing by anyone. This data is typically collected and managed by governments, international organizations, research institutions, or other entities aimed at research, transparency, and community empowerment.
</div>
""",unsafe_allow_html=True)
st.divider()
# DATA PUBLIC Link
st.subheader("list of public data sources")
st.markdown("""
- [Kaggle](https://www.kaggle.com/datasets)
- [MIT Open Data](https://openlearning.mit.edu/resources-educators/open-data)
- [UCI Machine Learning Repository](https://archive.ics.uci.edu/)
- [European Data Portal (Uni Eropa)](https://data.europa.eu/euodp/en/data/)
- [Indonesian Government Data](https://data.go.id/)
- [Data.gov (United States)](https://www.data.gov)
- [World Bank Open Data](https://data.worldbank.org/)
- [United Nations Data](https://data.un.org/)

""")
render_footer()
