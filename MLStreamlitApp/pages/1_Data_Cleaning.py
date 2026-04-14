import pandas as pd
import streamlit as st


# Configure the Data Cleaning page.
st.set_page_config(page_title="Data Cleaning", page_icon="🧹", layout="wide")


# Page title and short instructions.
st.title("Data Cleaning")
st.markdown("Upload a dataset or choose one of the sample CSV files from the sidebar.")

with st.sidebar:
    # Let the user decide whether to upload their own CSV
    # or work from one of the sample datasets.
    st.subheader("Data Source")
    source = st.radio(
        "Choose a dataset source",
        ["Upload CSV", "Use sample dataset"]
    )

    # These stay empty until a dataset is loaded.
    dataframe = None
    dataset_name = None

    if source == "Upload CSV":
        # Read in a CSV file uploaded by the user.
        uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
        if uploaded_file is not None:
            dataframe = pd.read_csv(uploaded_file)
            dataset_name = uploaded_file.name
    else:
        # Sample datasets let the user explore the app quickly.
        sample_choice = st.selectbox(
            "Choose a sample dataset",
            ["Student Performance", "Soccer Injury Predictor",
            "Titanic Survival", "Baseball Success", "Teen Mental Health"]
        )

        # Load the sample dataset the user selected.
        if sample_choice == "Student Performance":
            dataframe = pd.read_csv("MLStreamlitApp/data/Student_Performance.csv")
            dataset_name = "Student Performance"
        elif sample_choice == "Soccer Injury Predictor":
            dataframe = pd.read_csv("MLStreamlitApp/data/Soccer_injuries.csv")
            dataset_name = "Soccer Injury Predictor"
        elif sample_choice == "Titanic Survival":
            dataframe = pd.read_csv("MLStreamlitApp/data/titanic-1.csv")
            dataset_name = "Titanic Survival"
        elif sample_choice == "Baseball Success":
            dataframe = pd.read_csv("MLStreamlitApp/data/baseball.csv")
            dataset_name = "Baseball Success"
        elif sample_choice == "Teen Mental Health":
            dataframe = pd.read_csv("MLStreamlitApp/data/Teen_Mental_Health_Dataset.csv")
            dataset_name = "Teen Mental Health"

# If the upload widget resets after switching pages,
# fall back to the saved working dataframe.
if dataframe is None and "working_df" in st.session_state:
    dataframe = st.session_state["working_df"].copy()
    dataset_name = st.session_state.get("dataset_name")

if dataframe is not None:
    # If the user loaded a different dataset, reset the saved copies.
    if st.session_state.get("dataset_name") != dataset_name:
        st.session_state["dataset_name"] = dataset_name
        st.session_state["original_df"] = dataframe.copy()
        st.session_state["working_df"] = dataframe.copy()

    # original_df stays untouched so the user can reset back to it.
    # working_df is the version that changes as cleaning steps are applied.
    original_df = st.session_state["original_df"]
    working_df = st.session_state["working_df"]

    # Save the current cleaned dataframe so the Predictions page can use it.
    st.session_state["dataframe"] = working_df

    # Show the current version of the dataset.
    st.subheader("📊 Current Working Data")
    st.dataframe(working_df)

    # This overview helps the user understand data types and missingness by column.
    st.subheader("Data Types Overview")
    dtype_df = pd.DataFrame({
        "Column": working_df.columns,
        "Data Type": working_df.dtypes.astype(str).values,
        "Non-Null Values": working_df.notnull().sum().values,
        "Missing Values": working_df.isnull().sum().values
    })
    st.dataframe(dtype_df, height=250)

    # Missing-data summary for the current cleaned version of the dataset.
    st.subheader("⚠️ Missing Data Overview")
    st.write("These numbers reflect the current cleaned version of your dataset.")

    missing_counts = working_df.isnull().sum()
    missing_percent = (missing_counts / len(working_df)) * 100

    # Build a table of columns that still have missing values.
    missing_df = pd.DataFrame({
        "Missing Values": missing_counts,
        "Percent Missing (%)": missing_percent.round(3).astype(str) + "%"
    })

    # Only show columns where missing values still exist.
    missing_df = missing_df[missing_df["Missing Values"] > 0]

    if missing_df.empty:
        st.success("✅ No missing values detected in the current working dataset.")
    else:
        # Show the remaining missing-value problem columns.
        st.write("The following columns still have missing data:")
        st.dataframe(missing_df)

        # Preview rows that contain at least one missing value.
        st.subheader("🔍 Preview Rows with Missing Data")
        st.dataframe(working_df[working_df.isnull().any(axis=1)], height=200)

    # These metrics show how much the cleaned dataframe changed from the original.
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    with metric_col1:
        st.metric("Rows", working_df.shape[0], working_df.shape[0] - original_df.shape[0])
    with metric_col2:
        st.metric("Columns", working_df.shape[1], working_df.shape[1] - original_df.shape[1])
    with metric_col3:
        st.metric("Missing Before", int(original_df.isnull().sum().sum()))
    with metric_col4:
        st.metric("Missing Now", int(working_df.isnull().sum().sum()))

    # This section lets the user apply one cleaning action at a time.
    st.subheader("🛠️ Apply a Cleaning Step")
    st.write("Each time you click the button below, the change will be applied to the current working dataset.")

    # These lists are used for the fill operations later in the page.
    numeric_columns = working_df.select_dtypes(include=["number"]).columns
    numeric_missing_columns = [col for col in numeric_columns if working_df[col].isnull().sum() > 0]

    # Main cleaning-method selector.
    method = st.selectbox(
        "Choose how to handle missing values:",
        ["Keep Current DataFrame", "Drop Rows", "Drop Rows for Specific Missing Variables",
         "Drop Columns (>50% Missing)", "Drop Selected Columns", "Fill with Mean",
         "Fill with Median", "Fill with Zero"]
    )

    if method == "Drop Rows for Specific Missing Variables":
        # Let the user choose which missing-value columns should trigger row removal.
        selected_missing_columns = st.multiselect(
            "Choose columns whose missing values should trigger row removal",
            missing_df.index.tolist() if not missing_df.empty else []
        )
    else:
        selected_missing_columns = []

    if method == "Drop Selected Columns":
        # Let the user manually choose columns to remove.
        selected_columns = st.multiselect(
            "Choose columns to drop",
            working_df.columns.tolist()
        )
    else:
        selected_columns = []

    if method in ["Fill with Mean", "Fill with Median", "Fill with Zero"]:
        # Only allow fill operations on numeric columns that still have missing values.
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
            # Work on a copy first, then save the updated version.
            updated_df = working_df.copy()

            if method == "Drop Rows":
                # Remove every row that has at least one missing value.
                updated_df = updated_df.dropna()
            elif method == "Drop Rows for Specific Missing Variables" and selected_missing_columns:
                # Only drop rows when the selected columns are missing.
                updated_df = updated_df.dropna(subset=selected_missing_columns)
            elif method == "Drop Columns (>50% Missing)":
                # Automatically remove columns where more than half the rows are missing.
                updated_df = updated_df.drop(columns=updated_df.columns
                                             [updated_df.isnull().mean() > 0.5])
            elif method == "Drop Selected Columns" and selected_columns:
                # Remove only the columns the user selected.
                updated_df = updated_df.drop(columns=selected_columns)
            elif method == "Fill with Mean" and column is not None:
                # Fill missing values with that column's mean.
                updated_df[column] = updated_df[column].fillna(updated_df[column].mean())
            elif method == "Fill with Median" and column is not None:
                # Fill missing values with that column's median.
                updated_df[column] = updated_df[column].fillna(updated_df[column].median())
            elif method == "Fill with Zero" and column is not None:
                # Fill missing values with 0.
                updated_df[column] = updated_df[column].fillna(0)

            # Save the cleaned dataframe so the changes persist across reruns/pages.
            st.session_state["working_df"] = updated_df
            st.session_state["dataframe"] = updated_df
            st.rerun()

    with button_col2:
        if st.button("Reset to Original Data"):
            # Restore the untouched original dataframe.
            st.session_state["working_df"] = original_df.copy()
            st.session_state["dataframe"] = original_df.copy()
            st.rerun()

    # Final preview of the current cleaned dataframe.
    st.subheader("Current Cleaned Data")
    st.dataframe(working_df.head(10), height=250)
    st.success("Your data is clean and ready for modeling! Select the predictions tab from the sidebar 👈")
else:
    # Message shown before any dataset is loaded.
    st.info("Upload a CSV file or choose a sample dataset from the sidebar to begin.")
