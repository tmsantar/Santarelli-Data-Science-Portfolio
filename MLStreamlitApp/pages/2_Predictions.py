import streamlit as st


st.set_page_config(page_title="Predictions", page_icon="📈", layout="wide")


st.title("Predictions")
st.write("This page is intentionally blank for now.")

if "dataframe" in st.session_state:
    st.info("A dataset is already loaded from the Data Cleaning page and is available for your next steps.")
else:
    st.info("No dataset is loaded yet. Go to the Data Cleaning page first if you want to work from a CSV.")
