import pandas as pd
import streamlit as st


st.set_page_config(page_title="Data Cleaning", page_icon="🧹", layout="wide")


st.title("Data Cleaning")
st.markdown("Upload a dataset or choose one of the sample CSV files from the sidebar.")

with st.sidebar:
    st.subheader("Data Source")
    source = st.radio(
        "Choose a dataset source",
        ["Upload CSV", "Use sample dataset"]
    )

    dataframe = None
    dataset_name = None

    if source == "Upload CSV":
        uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
        if uploaded_file is not None:
            dataframe = pd.read_csv(uploaded_file)
            dataset_name = uploaded_file.name
    else:
        sample_choice = st.selectbox(
            "Choose a sample dataset",
            ["NFL Wide Receiver Stats", "Titanic Survival"]
        )

        if sample_choice == "NFL Wide Receiver Stats":
            dataframe = pd.read_csv("data/nextgen_receiving_stats.csv")
            dataset_name = "NFL Wide Receiver Stats"
        elif sample_choice == "Titanic Survival":
            dataframe = pd.read_csv("data/titanic-1.csv")
            dataset_name = "Titanic Survival"

if dataframe is None and "working_df" in st.session_state:
    dataframe = st.session_state["working_df"].copy()
    dataset_name = st.session_state.get("dataset_name")

if dataframe is not None:
    if st.session_state.get("dataset_name") != dataset_name:
        st.session_state["dataset_name"] = dataset_name
        st.session_state["original_df"] = dataframe.copy()
        st.session_state["working_df"] = dataframe.copy()

    original_df = st.session_state["original_df"]
    working_df = st.session_state["working_df"]
    st.session_state["dataframe"] = working_df

    st.subheader("📊 Current Working Data")
    st.dataframe(working_df)

    st.subheader("Data Types Overview")
    dtype_df = pd.DataFrame({
        "Column": working_df.columns,
        "Data Type": working_df.dtypes.astype(str).values,
        "Non-Null Values": working_df.notnull().sum().values,
        "Missing Values": working_df.isnull().sum().values
    })
    st.dataframe(dtype_df, height=250)

    st.subheader("⚠️ Missing Data Overview")
    st.write("These numbers reflect the current cleaned version of your dataset.")

    missing_counts = working_df.isnull().sum()
    missing_percent = (missing_counts / len(working_df)) * 100

    missing_df = pd.DataFrame({
        "Missing Values": missing_counts,
        "Percent Missing (%)": missing_percent.round(3).astype(str) + "%"
    })

    missing_df = missing_df[missing_df["Missing Values"] > 0]

    if missing_df.empty:
        st.success("✅ No missing values detected in the current working dataset.")
    else:
        st.write("The following columns still have missing data:")
        st.dataframe(missing_df)
        st.subheader("🔍 Preview Rows with Missing Data")
        st.dataframe(working_df[working_df.isnull().any(axis=1)], height=200)

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    with metric_col1:
        st.metric("Rows", working_df.shape[0], working_df.shape[0] - original_df.shape[0])
    with metric_col2:
        st.metric("Columns", working_df.shape[1], working_df.shape[1] - original_df.shape[1])
    with metric_col3:
        st.metric("Missing Before", int(original_df.isnull().sum().sum()))
    with metric_col4:
        st.metric("Missing Now", int(working_df.isnull().sum().sum()))

    st.subheader("🛠️ Apply a Cleaning Step")
    st.write("Each time you click the button below, the change will be applied to the current working dataset.")

    numeric_columns = working_df.select_dtypes(include=["number"]).columns
    numeric_missing_columns = [col for col in numeric_columns if working_df[col].isnull().sum() > 0]

    method = st.selectbox(
        "Choose how to handle missing values:",
        ["Keep Current DataFrame", "Drop Rows", "Drop Columns (>50% Missing)",
         "Drop Selected Columns", "Fill with Mean", "Fill with Median",
         "Fill with Zero"]
    )

    if method == "Drop Selected Columns":
        selected_columns = st.multiselect(
            "Choose columns to drop",
            working_df.columns.tolist()
        )
    else:
        selected_columns = []

    if method in ["Fill with Mean", "Fill with Median", "Fill with Zero"]:
        if len(numeric_missing_columns) > 0:
            column = st.selectbox("Choose a numeric column to fill", numeric_missing_columns)
        else:
            column = None
            st.info("There are no numeric columns with missing values to fill right now.")
    else:
        column = None

    button_col1, button_col2 = st.columns(2)

    with button_col1:
        if st.button("Apply Cleaning Step", type="primary"):
            updated_df = working_df.copy()

            if method == "Drop Rows":
                updated_df = updated_df.dropna()
            elif method == "Drop Columns (>50% Missing)":
                updated_df = updated_df.drop(columns=updated_df.columns
                                             [updated_df.isnull().mean() > 0.5])
            elif method == "Drop Selected Columns" and selected_columns:
                updated_df = updated_df.drop(columns=selected_columns)
            elif method == "Fill with Mean" and column is not None:
                updated_df[column] = updated_df[column].fillna(updated_df[column].mean())
            elif method == "Fill with Median" and column is not None:
                updated_df[column] = updated_df[column].fillna(updated_df[column].median())
            elif method == "Fill with Zero" and column is not None:
                updated_df[column] = updated_df[column].fillna(0)

            st.session_state["working_df"] = updated_df
            st.session_state["dataframe"] = updated_df
            st.rerun()

    with button_col2:
        if st.button("Reset to Original Data"):
            st.session_state["working_df"] = original_df.copy()
            st.session_state["dataframe"] = original_df.copy()
            st.rerun()

    st.subheader("Current Cleaned Data")
    st.dataframe(working_df.head(10), height=250)
    st.success("Your data is clean and ready for modeling! Select the predictions tab from the sidebar 👈")
else:
    st.info("Upload a CSV file or choose a sample dataset from the sidebar to begin.")
