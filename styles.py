# styles.py

COMMON_CSS = """
<style>
.stSelectbox div[data-baseweb="select"] {
    margin-top: -35px;
}
.stTextInput div[data-baseweb="input"] {
    margin-top: -35px;
}
.stTextArea div[data-baseweb="textarea"] {
    margin-top: -35px;
}
.stFileUploader div[data-baseweb="input"] {
    margin-top: -100px;
}
.stSelectbox {
    max-width: 300px;
}
.stTextInput, .stTextArea {
    max-width: 1400px;
}
.stSelectbox div, .stTextInput input, .stTextArea textarea {
    font-size: 14px;
}
.stButton > button {
    font-size: 6px; 
    padding: 2px 8px;
    border-radius: 10px; 
    background-color: #1560BD; 
    color: white; 
}
.stButton > button:hover {
    background-color: #1560BD;
    border: none;
    outline: none; 
}
.stRadio div[data-baseweb="radio"] {
    font-size: 14px; /* Ensure font size for the entire radio button group */
    margin-top: -100px; /* Reduce margin between label and radio button */
}
</style>
"""
