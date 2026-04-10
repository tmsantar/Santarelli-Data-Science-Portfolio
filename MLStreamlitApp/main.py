import streamlit as st

st.set_page_config(page_title="Machine Learning App", page_icon="🤖", layout="wide")

st.title("Machine Learning App 🧠")

st.markdown("### Welcome 👋")
st.write("Use the sidebar to navigate between pages for data cleaning and predictions.")

st.markdown("### 📂 Available Pages")

st.markdown("""
- **🧹 Data Cleaning**  
  Upload a CSV or choose a sample dataset and review missing values.

- **📈 Predictions**  
  Utilize different machine learning algorithms to make predictions using your data.
""")


st.info("💡 Tip: Start with Data Cleaning to prepare your dataset before making predictions.")

with st.sidebar:   

    # About me portion of the sidebar with links to LinkedIn and GitHub
    st.markdown("Built by **Tommy Santarelli**")
    st.caption("Business Analytics Major at Notre Dame")
    st.markdown("🔗 [LinkedIn](https://www.linkedin.com/in/tommy-santarelli-792651329/)")
    st.markdown("🐙 [GitHub](https://github.com/tmsantar)")
    st.markdown("---")