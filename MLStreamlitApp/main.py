import pandas as pd
import streamlit as st


st.set_page_config(page_title = "Machine Learning App", page_icon = "🤖", layout = "wide", )

st.title("Machine Learning App")
st.write("This application is used to make predictions using different machine learning algorithms." \
" Upload your CSV file, tidy up the data, and make your predictions!")

uploaded_file = st.file_uploader("Choose a CSV file")

if uploaded_file is not None:
    dataframe = pd.read_csv(uploaded_file)
    st.write(dataframe)

st.write(f"There are {dataframe.isnull().sum()} null values")

