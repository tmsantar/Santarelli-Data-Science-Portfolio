import streamlit as st


st.set_page_config(page_title="Machine Learning App", page_icon="🤖", layout="wide")


st.title("Machine Learning App")
st.markdown("### Welcome")
st.write(
    "Use the sidebar to move between pages for data cleaning and predictions."
)

st.markdown("**Available Pages**")
st.markdown("- **Data Cleaning:** Upload a CSV or choose a sample dataset and review missing values.")
st.markdown("- **Predictions:** Placeholder page for your future model-building work.")
