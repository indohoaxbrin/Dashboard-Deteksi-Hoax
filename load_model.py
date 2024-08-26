from transformers import BertTokenizer, BertForSequenceClassification
import streamlit as st

# Dictionary to map model names to their paths
model_paths = {
    "cahya/bert-base-indonesian-522M": "nlp-brin-id/cahyabert",
    "indobenchmark/indobert-base-p2": "nlp-brin-id/indobenchmark",
    "indolem/indobert-base-uncased": "nlp-brin-id/indolem",
    "mdhugol/indonesia-bert-sentiment-classification": "nlp-brin-id/mdhugol"
}

# Function to load the selected model
@st.cache_resource
def load_model(model_name):
    path = model_paths[model_name]
    tokenizer = BertTokenizer.from_pretrained(path)
    model = BertForSequenceClassification.from_pretrained(path)
    model.eval()
    return tokenizer, model
