import streamlit as st

# Set the page title, icon, and layout for the app's home page.
st.set_page_config(page_title="Machine Learning App", page_icon="ðŸ¤–", layout="wide")

# Main title shown at the top of the landing page.
st.title("Machine Learning App ðŸ§ ")

# Quick welcome text so users know how to begin.
st.markdown("### Welcome ðŸ‘‹")
st.write("Use the sidebar to navigate between pages for data cleaning and predictions.")

# Short overview of the pages inside the app.
st.markdown("### ðŸ“‚ Available Pages")

st.markdown("""
- **ðŸ§¹ Data Cleaning**  
  Upload a CSV or choose a sample dataset and review missing values.

- **ðŸ“ˆ Predictions**  
  Utilize different machine learning algorithms to make predictions using your data.
""")

# Friendly reminder about the recommended workflow.
st.info("ðŸ’¡ Tip: Start with Data Cleaning to prepare your dataset before making predictions.")

with st.sidebar:

    # Sidebar section with author information and portfolio links.
    st.markdown("Built by **Tommy Santarelli**")
    st.caption("Business Analytics Major at Notre Dame")
    st.markdown("ðŸ”— [LinkedIn](https://www.linkedin.com/in/tommy-santarelli-792651329/)")
    st.markdown("ðŸ™ [GitHub](https://github.com/tmsantar)")
    st.markdown("---")
