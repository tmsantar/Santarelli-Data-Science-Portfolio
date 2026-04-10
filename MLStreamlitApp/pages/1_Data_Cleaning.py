import pandas as pd
import streamlit as st


st.set_page_config(page_title="Data Cleaning", page_icon="🧹", layout="wide")


st.title("Data Cleaning")
st.markdown("Upload a dataset or choose one of your sample CSV files from the sidebar.")

with st.sidebar:
    st.subheader("Data Source")
    source = st.radio(
        "Choose a dataset source",
        ["Upload CSV", "Use sample dataset"]
    )

    dataframe = None

    if source == "Upload CSV":
        uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
        if uploaded_file is not None:
            dataframe = pd.read_csv(uploaded_file)
    else:
        sample_choice = st.selectbox(
            "Choose a sample dataset",
            ["Sample Dataset 1", "Sample Dataset 2"]
        )

        if sample_choice == "Sample Dataset 1: NFL Wide Receiver Stats":
            dataframe = pd.read_csv("MLStreamlitApp/data/nextgen_receiving_stats.csv")
        elif sample_choice == "Sample Dataset 2: Titanic Survival":
            dataframe = pd.read_csv("MLStreamlitApp/data/titanic-1.csv")

if dataframe is not None:
    st.session_state["dataframe"] = dataframe

    st.subheader("📊 Raw Data")
    st.dataframe(dataframe)

    st.subheader("⚠️ Missing Data Overview")
    st.write("Before building a model, it's important to handle missing values properly.")

    missing_counts = dataframe.isnull().sum()
    missing_percent = (missing_counts / len(dataframe)) * 100

    missing_df = pd.DataFrame({
        "Missing Values": missing_counts,
        "Percent Missing (%)": missing_percent.round(3).astype(str) + "%"
    })

    missing_df = missing_df[missing_df["Missing Values"] > 0]

    if missing_df.empty:
        st.success("✅ No missing values detected. Your dataset is clean!")
    else:
        st.write("The following columns have missing data:")
        st.dataframe(missing_df)

        st.write(
            "You should handle missing values before training a model.\n"
            "Options include:\n"
            "- Keep Original DataFrame\n"
            "- Dropping rows or columns\n"
            "- Filling with mean/median/mode\n"
        )

        st.subheader("🔍 Preview Rows with Missing Data")
        st.dataframe(dataframe[dataframe.isnull().any(axis=1)])

        st.subheader("🛠️ Next Step: Handle Missing Values")
        numeric_columns = dataframe.select_dtypes(include=["number"]).columns

        if len(numeric_columns) > 0:
            column = st.selectbox("Choose a column to fill", numeric_columns)

            method = st.selectbox(
                "Choose how to handle missing values:",
                [
                    "Keep Original DataFrame",
                    "Drop Rows",
                    "Drop Columns (>50% Missing)",
                    "Fill with Mean",
                    "Fill with Median",
                    "Fill with Zero"
                ]
            )

            df_clean = dataframe.copy()

            if method == "Keep Original DataFrame":
                pass
            elif method == "Drop Rows":
                df_clean = df_clean.dropna()
            elif method == "Drop Columns (>50% Missing)":
                df_clean = df_clean.drop(columns=df_clean.columns[df_clean.isnull().mean() > 0.5])
            elif method == "Fill with Mean":
                df_clean[column] = df_clean[column].fillna(dataframe[column].mean())
            elif method == "Fill with Median":
                df_clean[column] = df_clean[column].fillna(dataframe[column].median())
            elif method == "Fill with Zero":
                df_clean[column] = df_clean[column].fillna(0)
        else:
            st.info("This dataset has no numeric columns available for the current fill options.")
else:
    st.info("Upload a CSV file or choose a sample dataset from the sidebar to begin.")
