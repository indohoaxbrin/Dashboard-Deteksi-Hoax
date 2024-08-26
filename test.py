import torch
from torch.nn.functional import softmax
from load_model import load_model  # Import the load_model function
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import streamlit as st

@st.cache_resource
def get_model_and_tokenizer(model_name):
    return load_model(model_name)

# Initialize default model (could be anything, or even load dynamically)
default_model_name = "cahya/bert-base-indonesian-522M"
tokenizer, model = load_model(default_model_name)

# Prediction function
def predict_hoax(title, content):
    if tokenizer is None or model is None:
        raise ValueError("Model and tokenizer must be loaded before prediction.")
    
    print(f"Using model: {model}")
    print(f"Using tokenizer: {tokenizer}")

    text = f"{title} [SEP] {content}"
    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=256)
    with torch.no_grad():
        outputs = model(**inputs)
    probs = softmax(outputs.logits, dim=1)
    pred = torch.argmax(probs, dim=1).item()
    label = 'HOAX' if pred == 1 else 'NON-HOAX'
    return label

# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# model.to(device)


# LIME prediction function
def predict_proba_for_lime(texts):
    results = []
    for text in texts:
        inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=256)
        with torch.no_grad():
            outputs = model(**inputs)
        probs = softmax(outputs.logits, dim=1).detach().cpu().numpy()
        results.append(probs[0])
    return np.array(results)



def evaluate_model_performance(df, tokenizer, model):
    true_labels = []
    pred_labels = []

    for index, row in df.iterrows():
        true_label = row['Label']  # Menggunakan 'Title' sebagai label sebenarnya karena tidak ada 'Final_Result'
        pred_label = predict_hoax(row['Title'], row['Content'])
        
        true_labels.append(1 if true_label == 'HOAX' else 0)
        pred_labels.append(1 if pred_label == 'HOAX' else 0)

    accuracy = accuracy_score(true_labels, pred_labels)
    precision = precision_score(true_labels, pred_labels, average='binary')
    recall = recall_score(true_labels, pred_labels, average='binary')
    f1 = f1_score(true_labels, pred_labels, average='binary')

    return accuracy, precision, recall, f1