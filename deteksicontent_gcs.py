import streamlit as st
from datetime import datetime
import pandas as pd
from lime.lime_text import LimeTextExplainer
from test import predict_hoax, predict_proba_for_lime
import streamlit.components.v1 as components
from load_model import load_model
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from styles import COMMON_CSS
from google.cloud import storage
import os
from io import StringIO
import pytz

# # Ambil kredensial JSON dari secrets Streamlit
# credentials_json = st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"]

# # Simpan kredensial JSON ke file sementara
# with open("/tmp/credentials.json", "w") as f:
#     f.write(credentials_json)

# # Set environment variable for Google Cloud credentials
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/credentials.json"

def download_json_from_gcs(bucket_name, source_blob_name, destination_file_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)
    print(f"Downloaded storage object {source_blob_name} from bucket {bucket_name} to local file {destination_file_name}.")

# Konfigurasi
bucket_name = 'dashboardhoax-bucket'
source_blob_name = 'dashboardhoax-bucket/inbound-source-431806-g7-e49e388ce0be.json'
destination_file_name = '/tmp/json-file.json'

# Unduh file JSON dari GCS
download_json_from_gcs(bucket_name, source_blob_name, destination_file_name)

# Gunakan file JSON yang diunduh
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = destination_file_name

def save_corrections_to_gcs(bucket_name, file_name, correction_data):
    client = storage.Client()  # Uses the credentials set by the environment variable
    bucket = client.bucket("dashboardhoax-bucket")
    blob = bucket.blob("koreksi_pengguna_content.csv")
    
    # Check if the blob (file) exists
    if blob.exists():
        # Download existing CSV from GCS
        existing_data = blob.download_as_string().decode('utf-8')
        existing_df = pd.read_csv(StringIO(existing_data))
    else:
        # Create a new DataFrame if the file does not exist
        existing_df = pd.DataFrame(columns=['Timestamp', 'Title', 'Content', 'Prediction', 'Correction'])

    # Append the new data to the existing data
    new_data_df = pd.DataFrame(correction_data)
    updated_df = pd.concat([existing_df, new_data_df], ignore_index=True)

    # Convert the DataFrame back to CSV and upload
    updated_csv_data = updated_df.to_csv(index=False)
    blob.upload_from_string(updated_csv_data, content_type='text/csv')

def show_deteksi_kontengcs():
    st.markdown(COMMON_CSS, unsafe_allow_html=True)

    if 'correction' not in st.session_state:
        st.session_state.correction = None
    if 'detection_result' not in st.session_state:
        st.session_state.detection_result = None
    if 'lime_explanation' not in st.session_state:
        st.session_state.lime_explanation = None
    if 'headline' not in st.session_state:
        st.session_state.headline = ""
    if 'content' not in st.session_state:
        st.session_state.content = ""
    if 'is_correct' not in st.session_state:
        st.session_state.is_correct = None

    # Dropdown for selecting a model
    st.markdown("<h6 style='font-size: 14px; margin-bottom: 0;'>Pilih Model</h6>", unsafe_allow_html=True)
    selected_model = st.selectbox(
        "",
        [
            "cahya/bert-base-indonesian-522M",
            "indobenchmark/indobert-base-p2",
            "indolem/indobert-base-uncased",
            "mdhugol/indonesia-bert-sentiment-classification"
        ],
        key="model_selector_content"
    )

    # Load the selected model
    tokenizer, model = load_model(selected_model)

    st.markdown("<h6 style='font-size: 14px; margin-bottom: 0;'>Masukkan Judul Berita :</h6>", unsafe_allow_html=True)
    st.session_state.headline = st.text_input("", value=st.session_state.headline)

    st.markdown("<h6 style='font-size: 14px; margin-bottom: 0;'>Masukkan Konten Berita :</h6>", unsafe_allow_html=True)
    st.session_state.content = st.text_area("", value=st.session_state.content)

    # Detection button
    if st.button("Deteksi", key="detect_content"):
        st.session_state.detection_result = predict_hoax(st.session_state.headline, st.session_state.content)
        st.success(f"Prediksi: {st.session_state.detection_result}")

        # Prepare the text for LIME
        lime_texts = [f"{st.session_state.headline} [SEP] {st.session_state.content}"]

        # Add a spinner and progress bar to indicate processing
        with st.spinner("Sedang memproses LIME, harap tunggu..."):
            # Explain the prediction
            explainer = LimeTextExplainer(class_names=['NON-HOAX', 'HOAX'])
            explanation = explainer.explain_instance(lime_texts[0], predict_proba_for_lime, num_features=5, num_samples=1000)

            # Save the LIME explanation in session state
            st.session_state.lime_explanation = explanation.as_html()

    # Display the detection result and LIME explanation if available
    if st.session_state.lime_explanation:
        lime_html = st.session_state.lime_explanation

        # Inject CSS for font size adjustment
        lime_html = f"""
        <style>
        .lime-text-explanation, .lime-highlight, .lime-classification, 
        .lime-text-explanation * {{
            font-size: 14px !important;
        }}
        </style>
        <div class="lime-text-explanation">
            {lime_html}
        </div>
        """
        components.html(lime_html, height=200, scrolling=True)

    # Display a radio button asking if the detection result is correct
    if st.session_state.detection_result is not None:
        st.markdown("<h6 style='font-size: 16px; margin-bottom: -150px;'>Apakah hasil deteksi sudah benar?</h6>", unsafe_allow_html=True)
        st.session_state.is_correct = st.radio("", ("Ya", "Tidak"))

        if st.session_state.is_correct == "Ya":
            st.success("Deteksi sudah benar.")
        else:
            # Determine the correction based on the prediction
            st.session_state.correction = "HOAX" if st.session_state.detection_result == "NON-HOAX" else "NON-HOAX"

            # Display the correction DataFrame
            wib = pytz.timezone('Asia/Jakarta')
            correction_data = [{
                'Title': st.session_state.headline,
                'Content': st.session_state.content,
                'Prediction': st.session_state.detection_result,
                'Correction': st.session_state.correction,
                'Timestamp': datetime.now(wib).strftime('%Y-%m-%d %H:%M:%S')
            }]

            # Save button
            if st.button("Simpan"):
                # Save the correction data to GCS
                save_corrections_to_gcs("your-bucket-name", "koreksi_pengguna.csv", correction_data)
                
                # Create a formatted string with CSS for alignment and multi-line content handling
                formatted_text = f"""
                <div style='font-size: 14px;'>
                    <p style='margin: 0;'><span style='display: inline-block; width: 120px; font-weight: bold;'>Title</span> : <span style='white-space: pre-wrap;'>{st.session_state.headline}</span></p>
                    <p style='margin: 0;'><span style='display: inline-block; width: 120px; font-weight: bold;'>Content</span> : <span style='white-space: pre-wrap;'>{st.session_state.content}</span></p>
                    <p style='margin: 0;'><span style='display: inline-block; width: 120px; font-weight: bold;'>Prediction</span> : {st.session_state.detection_result}</p>
                    <p style='margin: 0;'><span style='display: inline-block; width: 120px; font-weight: bold;'>Correction</span> : {st.session_state.correction}</p>
                </div>
                """
                
                # Display the correction as text
                st.markdown(formatted_text, unsafe_allow_html=True)
                st.success("Koreksi telah disimpan.")
