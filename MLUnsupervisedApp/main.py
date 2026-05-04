import streamlit as st
from pathlib import Path


APP_DIR = Path(__file__).resolve().parent
HOME_IMAGE = APP_DIR / "images" / "unsupervised.png"

# Set the page title, icon, and layout for the app's home page.
st.set_page_config(page_title="Unsupervised Machine Learning App", page_icon="🤖", layout="wide")

# Main title shown at the top of the landing page.
st.title("Unsupervised Machine Learning App 🧠")


# Quick welcome text so users know how to begin.
st.markdown("### Welcome 👋")
st.write("Use the sidebar to clean a dataset, then explore clusters and PCA patterns in the unsupervised learning lab.")

st.write(
    "This app helps users find hidden groups and patterns in a dataset. "
    "Instead of predicting one answer, it looks for rows that are similar to each other and shows those patterns with charts."
)

st.write(
    "You can start with one of the sample datasets or upload your own CSV file. "
    "After cleaning the data, the app lets you explore how different rows group together and which features help explain those patterns."
)

# Short overview of the pages inside the app.
st.markdown("### What You Can Do 📂")

st.markdown("""
- **Data Cleaning**  
  Upload a CSV or choose one of the curated sample datasets, then review and handle missing values.

- **Unsupervised Learning Lab**  
  Use K-Means clustering, hierarchical clustering, and PCA to discover hidden patterns, structures, and relationships.
""")

# Friendly reminder about the recommended workflow.
st.info("💡 Tip: Start with Data Cleaning so the modeling page has a prepared dataset to use.")

image_col, spacer_col = st.columns([2, 1])
with image_col:
    st.image(HOME_IMAGE)

with st.sidebar:

    # Sidebar section with author information and portfolio links.
    st.markdown("Built by **Tommy Santarelli**")
    st.caption("Business Analytics Major and Data Science Minor at Notre Dame")
    st.markdown("🔗 [LinkedIn](https://www.linkedin.com/in/tommy-santarelli-792651329/)")
    st.markdown("🐙 [GitHub](https://github.com/tmsantar)")
    st.markdown("---")
