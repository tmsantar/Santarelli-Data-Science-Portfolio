import streamlit as st

# Set the page title, icon, and layout for the app's home page.
st.set_page_config(page_title="Unsupervised Machine Learning App", page_icon="🤖", layout="wide")

# Main title shown at the top of the landing page.
st.title("Unsupervised Machine Learning App 🧠")

# Quick welcome text so users know how to begin.
st.markdown("### Welcome 👋")
st.write("Use the sidebar to navigate between pages for data cleaning and predictions.")

# Short overview of the pages inside the app.
st.markdown("### Available Pages 📂")

st.markdown("""
- **Data Cleaning**  
  Upload a CSV or choose a sample dataset and review missing values.

- **Unsupervised Learning Lab**  
  Utilize different unsupervised machine learning algorithms to discover 
    hidden patterns, underlying structures, and relationships.
""")

# Friendly reminder about the recommended workflow.
st.info("💡 Tip: Start with Data Cleaning to prepare your dataset.")

with st.sidebar:

    # Sidebar section with author information and portfolio links.
    st.markdown("Built by **Tommy Santarelli**")
    st.caption("Business Analytics Major and Data Science Minor at Notre Dame")
    st.markdown("🔗 [LinkedIn](https://www.linkedin.com/in/tommy-santarelli-792651329/)")
    st.markdown("🐙 [GitHub](https://github.com/tmsantar)")
    st.markdown("---")
