import streamlit as st


# Print all available secrets to check if GOOGLE_APPLICATION_CREDENTIALS_JSON is there
st.write(st.secrets.keys())

# Set page configuration
st.set_page_config(page_title="Hoax Detection Dashboard", layout="wide")
st.title("Dashboard Deteksi Berita Hoax")

from home import show_home
from deteksicontent_gcs import show_deteksi_kontengcs
from deteksiupload_gcs import show_deteksi_uploadgcs

# Create tabs
tab1, tab2, tab3 = st.tabs(["Home", "Deteksi Konten", "Deteksi File"])

with tab1:
    show_home()

with tab2:
    show_deteksi_kontengcs()

with tab3:
    show_deteksi_uploadgcs()
