import pandas as pd
import streamlit as st
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA


st.set_page_config(page_title="Unsupervised Learning Lab", page_icon="📈", layout="wide")


# Main title and page instructions.
st.title("📈 Unsupervised Learning Lab")
st.markdown("Use your cleaned dataset to view patterns in your data using an unsupervised model.")

if "dataframe" not in st.session_state:
    # Stop here if the user has not loaded or cleaned a dataset yet.
    st.info("No dataset loaded yet. Go to the **Data Cleaning** page first.")
    st.stop()

# Pull the cleaned dataframe from session state.
df = st.session_state["dataframe"]
numeric_columns = df.select_dtypes(include="number").columns.tolist()

# Sidebar contains settings that depend on the selected model.
with st.sidebar:
    st.subheader("Model Settings")

    method = st.radio(
        "Choose an unsupervised learning method",
        ["K-Means Clustering", "Hierarchical Clustering", "PCA"]
    )

    st.subheader("Model Options")

    scale_data = st.toggle("Scale numeric features", value=True)
    st.caption("Helpful for distance-based methods and PCA.")

    if method == "K-Means Clustering":
        st.subheader("K-Means Clustering")
        st.write("Run K-Means to")

    elif method == "Hierarchical Clustering":
        st.subheader("Hierarchical Clustering")
        st.write("Run hierarchical clustering to")

    elif method == "PCA":
        st.subheader("Principal Component Analysis")
        st.write("Run PCA to reduce your selected numeric features into principal components.")

if method == "K-means Clustering":
    n_clusters = st.slider(
    "Select the number of clusters",
        min_value=2,
        max_value=10,
        value=3,
        help = "This is the number of distinct groups you want to categorize your data into" )


if method == "Hierarchical Clustering":
    n_clusters = st.slider(
    "Select the number of clusters",
        min_value=2,
        max_value=10,
        value=3,
        help = "This is the number of distinct groups you want to categorize your data into")

    linkage_method = st.selectbox(
        "Linkage method", ["ward", "complete", "average", "single"])


if method == "PCA":
    st.subheader("Principal Component Analysis")

    if len(numeric_columns) < 2:
        st.warning("PCA needs at least 2 numeric columns.")
        st.stop()

    selected_features = st.multiselect(
        "Select features for PCA",
        numeric_columns,
        default=numeric_columns,
        help=(
            "Choose the numeric columns PCA should use. PCA looks for patterns across "
            "these features and combines them into new columns called principal components."))

    if len(selected_features) >= 2:
        max_components = min(10, len(selected_features))
        n_components = st.slider(
            "Number of PCA components",
            min_value=2,
            max_value=max_components,
            value=2,
            help=(
                "This controls how many new PCA columns are created. Fewer components "
                "make the data easier to visualize, while more components keep more of "
                "the original dataset's information."))

        X = df[selected_features].dropna()

        if scale_data:
            scaler = StandardScaler()
            X_for_pca = scaler.fit_transform(X)
            st.info("Numeric features were scaled using StandardScaler.")
        else:
            X_for_pca = X

        pca = PCA(n_components=n_components)
        X_pca = pca.fit_transform(X_for_pca)

        pca_columns = [f"PC{i + 1}" for i in range(n_components)]
        pca_df = pd.DataFrame(X_pca, columns=pca_columns, index=X.index)

        explained_variance = pca.explained_variance_ratio_
        variance_df = pd.DataFrame({
            "Principal Component": pca_columns,
            "Explained Variance Ratio": explained_variance,
            "Cumulative Explained Variance": np.cumsum(explained_variance)})

        st.write("Run PCA using", n_components, "components.")
        st.dataframe(variance_df)
        st.bar_chart(variance_df.set_index("Principal Component")["Explained Variance Ratio"])
        st.dataframe(pca_df)
    else:
        st.warning("Please select at least 2 numeric features for PCA.")
