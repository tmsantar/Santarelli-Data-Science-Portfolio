import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from scipy.cluster.hierarchy import dendrogram, linkage


st.set_page_config(page_title="Unsupervised Learning Lab", page_icon="📈", layout="wide")


if "dataframe" not in st.session_state:
    # Stop here if the user has not loaded or cleaned a dataset yet.
    st.info("No dataset loaded yet. Go to the **Data Cleaning** page first.")
    st.stop()

# Pull the cleaned dataframe from session state.
df = st.session_state["dataframe"]
numeric_columns = df.select_dtypes(include="number").columns.tolist()

if len(numeric_columns) < 2:
    st.warning("This page needs at least 2 numeric columns for unsupervised learning.")
    st.stop()

# Sidebar contains settings that depend on the selected model.
with st.sidebar:
    st.subheader("Model Settings")

    method = st.radio(
        "Choose an unsupervised learning method",
        ["K-Means Clustering", "Hierarchical Clustering", "PCA"])

    st.subheader("Model Options")

    scale_data = st.toggle("Scale numeric features", value=True)
    st.caption("Helpful for distance-based methods and PCA.")

    if method == "K-Means Clustering":
        st.subheader("K-Means Clustering")
        st.info(
            "K-Means finds groups of similar rows in your dataset. "
            "Use it when you want to split observations into a set number of clusters.")

    elif method == "Hierarchical Clustering":
        st.subheader("Hierarchical Clustering")
        st.info(
            "Hierarchical clustering builds groups step by step. "
            "Use it to see how observations connect as smaller groups combine into larger clusters.")

    elif method == "PCA":
        st.subheader("Principal Component Analysis")
        st.info(
            "PCA reduces many numeric features into fewer principal components. "
            "Use it to simplify your dataset while keeping as much information as possible.")

# Main title and page instructions.
st.title(f"📈 Unsupervised Learning Lab: {method}")
st.markdown("Use your cleaned dataset to view patterns in your data using an unsupervised model.")

st.info("❓ Hover over the small question mark icons next to controls for extra help while exploring the app.")

if method == "K-Means Clustering":
    st.subheader("Step 1: Select Features")

    selected_features = st.multiselect(
        "Select features for K-Means",
        numeric_columns,
        default=numeric_columns,
        help="Choose the numeric columns K-Means should use to group similar rows.")

    st.subheader("Step 2: Choose Model Settings")

    n_clusters = st.slider(
    "Select the number of clusters",
        min_value=2,
        max_value=10,
        value=3,
        help="This is the number of distinct groups you want to categorize your data into.")

    if len(selected_features) >= 2:
        X = df[selected_features].dropna()

        if len(X) <= n_clusters:
            st.warning("Please choose fewer clusters or select features with fewer missing values.")
            st.stop()

        if scale_data:
            scaler = StandardScaler()
            X_std = scaler.fit_transform(X)
            st.info("Numeric features were scaled using StandardScaler.")
        else:
            X_std = X

        X_array = np.asarray(X_std)

        st.subheader("Step 3: Compare Cluster Options")

        max_k = min(10, len(X) - 1)
        k_values = list(range(2, max_k + 1))
        inertia_values = []
        silhouette_values = []

        for k in k_values:
            test_kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            test_clusters = test_kmeans.fit_predict(X_array)
            inertia_values.append(test_kmeans.inertia_)
            silhouette_values.append(silhouette_score(X_array, test_clusters))

        elbow_col, silhouette_col = st.columns(2)

        with elbow_col:
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.plot(k_values, inertia_values, marker="o", linewidth=2)
            ax.axvline(n_clusters, color="#ff4b4b", linestyle="--", label="Selected k")
            ax.set_title("Elbow Plot")
            ax.set_xlabel("Number of Clusters")
            ax.set_ylabel("Inertia")
            ax.grid(True, alpha=0.3)
            ax.legend()
            st.pyplot(fig)
            st.caption(
                "This elbow plot tests several K values for K-Means. Look for the bend in the line; "
                "that point is where adding more clusters starts giving smaller improvements.")

        with silhouette_col:
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.plot(k_values, silhouette_values, marker="o", color="#1C8510", linewidth=2)
            ax.axvline(n_clusters, color="#ff4b4b", linestyle="--", label="Selected k")
            ax.set_title("Silhouette Plot")
            ax.set_xlabel("Number of Clusters")
            ax.set_ylabel("Silhouette Score")
            ax.grid(True, alpha=0.3)
            ax.legend()
            st.pyplot(fig)
            st.caption(
                "This silhouette plot compares how well rows fit inside their assigned K-Means cluster. "
                "Higher values usually mean rows fit better inside their own cluster than in other clusters.")

        st.subheader("Step 4: View Model Results")

        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_array)

        results_df = X.copy()
        results_df["Cluster"] = clusters

        st.write("Number of rows in each cluster:")
        st.dataframe(results_df["Cluster"].value_counts().sort_index())

        st.write("Cluster labels for each row:")
        st.dataframe(results_df)

        st.download_button(
            "Download K-Means Clustered Dataset",
            data=results_df.to_csv(index=False).encode("utf-8"),
            file_name="kmeans_clustered_dataset.csv",
            mime="text/csv"
        )

        st.subheader("Cluster Scatter Plot")
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_array)

        scatter_df = pd.DataFrame({
            "PC1": X_pca[:, 0],
            "PC2": X_pca[:, 1],
            "Cluster": clusters.astype(str)})

        fig, ax = plt.subplots(figsize=(8, 5))
        for cluster in sorted(scatter_df["Cluster"].unique()):
            cluster_data = scatter_df[scatter_df["Cluster"] == cluster]
            ax.scatter(
                cluster_data["PC1"],
                cluster_data["PC2"],
                label=f"Cluster {cluster}",
                alpha=0.75,
                edgecolors="white",
                linewidths=0.5)

        ax.set_xlabel("Principal Component 1")
        ax.set_ylabel("Principal Component 2")
        ax.set_title("K-Means Clustering Results")
        ax.grid(True, alpha=0.3)
        ax.legend(title="Cluster")
        st.pyplot(fig)
        st.caption(
            "This scatter plot uses PCA to compress the selected features into two axes. "
            "Points close together have similar feature values, and the colors show the K-Means cluster assignments."
        )
    else:
        st.warning("Please select at least 2 numeric features for K-Means.")


if method == "Hierarchical Clustering":
    st.subheader("Step 1: Select Features")

    selected_features = st.multiselect(
        "Select features for Hierarchical Clustering",
        numeric_columns,
        default=numeric_columns,
        help="Choose the numeric columns hierarchical clustering should use to group similar rows.")

    st.subheader("Step 2: Choose Model Settings")

    n_clusters = st.slider(
    "Select the number of clusters (k)",
        min_value=2,
        max_value=10,
        value=3,
        help="This is the number of distinct groups you want to categorize your data into.")

    linkage_method = st.selectbox(
        "Linkage method", ["ward", "complete", "average", "single"],
        help=(
        "Linkage controls how distances between clusters are measured when groups are merged. "
        "'ward' tries to create compact, balanced clusters, 'complete' uses the farthest points, "
        "'average' uses average distance, and 'single' uses the closest points."))

    if len(selected_features) >= 2:
        X = df[selected_features].dropna()

        if len(X) <= n_clusters:
            st.warning("Please choose fewer clusters or select features with fewer missing values.")
            st.stop()

        if scale_data:
            scaler = StandardScaler()
            X_std = scaler.fit_transform(X)
            st.info("Numeric features were scaled using StandardScaler.")
        else:
            X_std = X

        X_array = np.asarray(X_std)

        st.subheader("Step 3: Compare Cluster Options")

        max_k = min(10, len(X) - 1)
        k_values = list(range(2, max_k + 1))
        elbow_values = []
        silhouette_values = []

        for k in k_values:
            test_hierarchical = AgglomerativeClustering(
                n_clusters=k,
                linkage=linkage_method)
            test_clusters = test_hierarchical.fit_predict(X_array)

            cluster_total = 0
            for cluster in np.unique(test_clusters):
                cluster_rows = X_array[test_clusters == cluster]
                cluster_center = cluster_rows.mean(axis=0)
                cluster_total += ((cluster_rows - cluster_center) ** 2).sum()

            elbow_values.append(cluster_total)
            silhouette_values.append(silhouette_score(X_array, test_clusters))

        elbow_col, silhouette_col = st.columns(2)

        with elbow_col:
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.plot(k_values, elbow_values, marker="o", linewidth=2)
            ax.axvline(n_clusters, color="#ff4b4b", linestyle="--", label="Selected k")
            ax.set_title("Elbow Plot")
            ax.set_xlabel("Number of Clusters")
            ax.set_ylabel("Within-Cluster Variation")
            ax.grid(True, alpha=0.3)
            ax.legend()
            st.pyplot(fig)
            st.caption(
                "This elbow plot tests several cluster counts for hierarchical clustering. "
                "Look for the bend in the line, where the groups improve less after that point.")

        with silhouette_col:
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.plot(k_values, silhouette_values, marker="o", color="#1C8510", linewidth=2)
            ax.axvline(n_clusters, color="#ff4b4b", linestyle="--", label="Selected k")
            ax.set_title("Silhouette Plot")
            ax.set_xlabel("Number of Clusters")
            ax.set_ylabel("Silhouette Score")
            ax.grid(True, alpha=0.3)
            ax.legend()
            st.pyplot(fig)
            st.caption(
                "This silhouette plot compares how clearly the hierarchical clusters separate from each other. "
                "Higher values usually mean the clusters are more distinct.")

        st.subheader("Step 4: View Model Results")

        hierarchical = AgglomerativeClustering(
            n_clusters=n_clusters,
            linkage=linkage_method)

        clusters = hierarchical.fit_predict(X_array)

        results_df = X.copy()
        results_df["Cluster"] = clusters

        st.write("Number of rows in each cluster:")
        st.dataframe(results_df["Cluster"].value_counts().sort_index())

        st.write("Cluster labels for each row:")
        st.dataframe(results_df)

        st.download_button(
            "Download Hierarchical Clustered Dataset",
            data=results_df.to_csv(index=False).encode("utf-8"),
            file_name="hierarchical_clustered_dataset.csv",
            mime="text/csv"
        )

        st.subheader("Cluster Scatter Plot")
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_array)

        scatter_df = pd.DataFrame({
            "PC1": X_pca[:, 0],
            "PC2": X_pca[:, 1],
            "Cluster": clusters.astype(str)})

        fig, ax = plt.subplots(figsize=(8, 5))
        for cluster in sorted(scatter_df["Cluster"].unique()):
            cluster_data = scatter_df[scatter_df["Cluster"] == cluster]
            ax.scatter(
                cluster_data["PC1"],
                cluster_data["PC2"],
                label=f"Cluster {cluster}",
                alpha=0.75,
                edgecolors="white",
                linewidths=0.5)

        ax.set_xlabel("Principal Component 1")
        ax.set_ylabel("Principal Component 2")
        ax.set_title("Hierarchical Clustering Results")
        ax.grid(True, alpha=0.3)
        ax.legend(title="Cluster")
        st.pyplot(fig)
        st.caption(
            "This scatter plot uses PCA to show the hierarchical clustering results in two dimensions. "
            "Nearby points are more similar based on the selected features, and each color represents a cluster."
        )

        st.divider()

        label_options = ["Row Number"] + df.select_dtypes(exclude="number").columns.tolist()
        label_options += [col for col in df.columns.tolist() if col not in label_options]
        default_label_index = label_options.index("country_name") if "country_name" in label_options else 0

        label_column = st.selectbox(
            "Choose dendrogram labels",
            label_options,
            index=default_label_index,
            help=(
                "Choose what text appears under each dendrogram leaf. Pick a name, ID, "
                "category, or other identifying column when your dataset has one."))

        if label_column == "Row Number":
            st.caption("The dendrogram will label each row by its row number.")
        else:
            sample_values = df[label_column].dropna().astype(str).head(3).tolist()
            sample_text = ", ".join(sample_values) if sample_values else "no examples available"
            unique_count = df[label_column].nunique(dropna=True)
            st.caption(
                f"The dendrogram will label each row using `{label_column}`. "
                f"This column has {unique_count} unique values. Examples: {sample_text}."
            )


        st.subheader("Dendrogram")
        dendrogram_size = min(50, len(X))
        rng = np.random.default_rng(42)
        dendrogram_positions = np.sort(rng.choice(len(X), size=dendrogram_size, replace=False))
        dendrogram_data = X_array[dendrogram_positions]

        if label_column == "Row Number":
            dendrogram_labels = X.index[dendrogram_positions].astype(str)
        else:
            dendrogram_labels = (
                df.loc[X.index[dendrogram_positions], label_column]
                .astype(str)
                .str.slice(0, 25))

        fig, ax = plt.subplots(figsize=(10, 6))
        linked = linkage(dendrogram_data, method=linkage_method)
        dendrogram(linked, ax=ax, labels=dendrogram_labels.tolist(), leaf_rotation=90)
        ax.set_title("Hierarchical Clustering Dendrogram")
        ax.set_xlabel(label_column)
        ax.set_ylabel("Distance")
        plt.tight_layout()
        st.pyplot(fig)
        st.caption(
            "The dendrogram shows how rows merge together from most similar to less similar. "
            "Shorter branches mean observations joined earlier, while taller merges show larger differences between groups."
        )

        if len(X) > dendrogram_size:
            st.caption("Showing a random sample of 50 rows in the dendrogram so the chart stays readable.")
    else:
        st.warning("Please select at least 2 numeric features for Hierarchical Clustering.")


if method == "PCA":
    st.subheader("Step 1: Select Features")

    selected_features = st.multiselect(
        "Select features for PCA",
        numeric_columns,
        default=numeric_columns,
        help=(
            "Choose the numeric columns PCA should use. PCA looks for patterns across "
            "these features and combines them into new columns called principal components."))

    st.subheader("Step 2: Choose Model Settings")

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

        X_array = np.asarray(X_for_pca)

        st.subheader("Step 3: View PCA Results")

        pca = PCA(n_components=n_components)
        X_pca = pca.fit_transform(X_array)

        pca_columns = [f"PC{i + 1}" for i in range(n_components)]
        pca_df = pd.DataFrame(X_pca, columns=pca_columns, index=X.index)

        explained_variance = pca.explained_variance_ratio_
        variance_df = pd.DataFrame({
            "Principal Component": pca_columns,
            "Explained Variance Ratio": explained_variance,
            "Cumulative Explained Variance": np.cumsum(explained_variance)})

        st.write("Explained variance tells you how much information each component keeps.")
        st.dataframe(variance_df)
        st.bar_chart(variance_df.set_index("Principal Component")["Explained Variance Ratio"])
        st.caption(
            "This bar chart shows how much of the dataset's variation each principal component captures. "
            "Taller bars mean that component keeps more information from the original features."
        )

        st.subheader("PCA Scatter Plot")

        label_column = st.selectbox(
            "Optional color column for PCA scatter plot",
            ["None"] + df.columns.tolist(),
            help="Choose a column to color the PCA scatter plot. This is only for visualization.")

        fig, ax = plt.subplots(figsize=(8, 5))

        if label_column == "None":
            ax.scatter(pca_df["PC1"], pca_df["PC2"], alpha=0.75, edgecolors="white", linewidths=0.5)
        else:
            plot_df = pca_df.copy()
            plot_df["Label"] = df.loc[pca_df.index, label_column]

            if pd.api.types.is_numeric_dtype(plot_df["Label"]):
                unique_values = sorted(plot_df["Label"].dropna().unique())

                if len(unique_values) <= 10:
                    for label in unique_values:
                        label_data = plot_df[plot_df["Label"] == label]
                        ax.scatter(
                            label_data["PC1"],
                            label_data["PC2"],
                            label=str(label),
                            alpha=0.75,
                            edgecolors="white",
                            linewidths=0.5)

                    ax.legend(title=label_column)
                    st.caption(
                        f"The selected color column has {len(unique_values)} numeric groups, "
                        "so the plot uses a regular legend instead of a continuous scale."
                    )
                else:
                    scatter = ax.scatter(
                        plot_df["PC1"],
                        plot_df["PC2"],
                        c=plot_df["Label"],
                        cmap="YlOrRd",
                        alpha=0.80,
                        edgecolors="white",
                        linewidths=0.5)
                    fig.colorbar(scatter, ax=ax, label=label_column)
                    st.caption(
                        f"The selected color column has many numeric values, so the plot uses a light-to-dark scale. "
                        f"Darker points have higher `{label_column}` values."
                    )
            else:
                plot_df["Label"] = plot_df["Label"].astype(str)

                if plot_df["Label"].nunique() <= 10:
                    for label in sorted(plot_df["Label"].dropna().unique()):
                        label_data = plot_df[plot_df["Label"] == label]
                        ax.scatter(
                            label_data["PC1"],
                            label_data["PC2"],
                            label=label,
                            alpha=0.75,
                            edgecolors="white",
                            linewidths=0.5)

                    ax.legend(title=label_column)
                else:
                    label_codes, label_names = pd.factorize(plot_df["Label"])
                    scatter = ax.scatter(
                        plot_df["PC1"],
                        plot_df["PC2"],
                        c=label_codes,
                        cmap="tab20",
                        alpha=0.75,
                        edgecolors="white",
                        linewidths=0.5)
                    fig.colorbar(scatter, ax=ax, label=f"{label_column} code")
                    st.caption(
                        "The selected color column is categorical and has more than 10 unique values, "
                        "so the plot uses color codes instead of a long legend.")

        ax.set_xlabel("Principal Component 1")
        ax.set_ylabel("Principal Component 2")
        ax.set_title("PCA Scatter Plot")
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
        st.caption(
            "This scatter plot places each row using the first two principal components. "
            "Rows that appear close together have similar patterns across the selected numeric features."
        )

    else:
        st.warning("Please select at least 2 numeric features for PCA.")
