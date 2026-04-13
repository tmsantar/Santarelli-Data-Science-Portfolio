import streamlit as st
import pandas as pd
from pandas.api.types import is_numeric_dtype
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import accuracy_score, mean_squared_error, root_mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


st.set_page_config(page_title="Predictions", page_icon="📈", layout="wide")

st.title("Predictions")

if "dataframe" in st.session_state:
    df = st.session_state["dataframe"]

    with st.sidebar:
        st.subheader("Model Options")
        scale_data = st.toggle("Scale numeric features")

    st.markdown("""
    What are you trying to predict? Select a target variable
    to discover which models you can use.
    """)
    st.caption("Optional preprocessing: you can scale numeric features using the sidebar before training your model.")

    target = st.selectbox("Select a target variable", df.columns)

    target_series = df[target].dropna()
    num_unique = target_series.nunique()

    if not is_numeric_dtype(target_series):
        detected_problem_type = "classification"
    elif num_unique <= 10:
        detected_problem_type = "classification"
    else:
        detected_problem_type = "regression"

    st.write(
        f"Based on the target variable you selected, the app detected this as a "
        f"**{detected_problem_type.title()}** problem."
    )

    problem_type = st.radio(
        "Would you like to keep that detected problem type, or switch it?",
        ["Classification", "Regression"],
        index=0 if detected_problem_type == "classification" else 1
    )

    if problem_type == "Regression":
        model = st.selectbox(
            "Choose a regression model",
            ["Linear Regression", "Decision Tree Regressor"]
        )
    else:
        model = st.selectbox(
            "Choose a classification model",
            ["Logistic Regression", "Decision Tree Classifier", "XGBoost"]
        )

    if model == "Linear Regression":
        feature_candidates = [col for col in df.columns if col != target]
        usable_features = df[feature_candidates].select_dtypes(include=["number"]).columns.tolist()

        if not usable_features:
            st.warning("There are no numeric input variables available for Linear Regression.")
        else:
            selected_features = st.multiselect(
                "Select your input variables",
                usable_features,
                key="linear_features"
            )

            if selected_features:
                X = df[selected_features]
                y = df[target]

                modeling_df = pd.concat([X, y], axis=1)
                missing_rows = int(modeling_df.isnull().any(axis=1).sum())

                if missing_rows > 0:
                    st.warning(
                        f"The selected data still contains missing values in {missing_rows} rows. "
                        "Linear Regression cannot run until those missing values are handled."
                    )
                    st.write(
                        "You can go back to the Data Cleaning page to clean the data further, "
                        "or drop the rows with missing values below for this model."
                    )

                    missing_data_choice = st.radio(
                        "How would you like to handle the remaining missing values?",
                        ["Go back and clean the data", "Drop rows with missing values for this model"],
                        key="linear_missing_choice"
                    )

                    if missing_data_choice == "Drop rows with missing values for this model":
                        modeling_df = modeling_df.dropna()
                        X = modeling_df[selected_features]
                        y = modeling_df[target]
                        st.info(f"{missing_rows} rows with missing values were removed for this model run.")
                    else:
                        st.stop()

                test_size = st.slider(
                    "Select a test size",
                    min_value=0.10,
                    max_value=0.50,
                    value=0.20,
                    step=0.05,
                    key="linear_test_size"
                )

                X_train, X_test, y_train, y_test = train_test_split(
                    X,
                    y,
                    test_size=test_size,
                    random_state=42
                )

                if scale_data:
                    scaler = StandardScaler()
                    X_train = scaler.fit_transform(X_train)
                    X_test = scaler.transform(X_test)
                    st.info("Numeric input features were scaled for this model run.")

                lin_reg = LinearRegression()
                lin_reg.fit(X_train, y_train)
                y_pred = lin_reg.predict(X_test)

                mse = mean_squared_error(y_test, y_pred)
                rmse = root_mean_squared_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)

                st.write("### Here are your results!")
                st.write(f"Mean Squared Error: {mse:.2f}")
                st.write(f"Root Mean Squared Error: {rmse:.2f}")
                st.write(f"R-squared Score: {r2:.2f}")

                coefficients_df = pd.DataFrame({
                    "Feature": selected_features,
                    "Coefficient": lin_reg.coef_
                })
                coefficients_df["Absolute Impact"] = coefficients_df["Coefficient"].abs()
                coefficients_df = coefficients_df.sort_values("Absolute Impact", ascending=False)

                st.subheader("Feature Coefficients")
                st.caption("Larger absolute coefficients generally indicate a stronger contribution to the prediction.")
                st.dataframe(
                    coefficients_df[["Feature", "Coefficient"]].round(4),
                    height=250
                )

                results_df = pd.DataFrame({
                    "Actual": y_test.reset_index(drop=True),
                    "Predicted": pd.Series(y_pred).round(2)
                })

                st.subheader("Actual vs Predicted Values")
                st.dataframe(results_df.head(10), height=250)

    if model == "Logistic Regression":
        feature_candidates = [col for col in df.columns if col != target]
        usable_features = df[feature_candidates].select_dtypes(include=["number"]).columns.tolist()

        if not usable_features:
            st.warning("There are no numeric input variables available for Logistic Regression.")
        else:
            selected_features = st.multiselect(
                "Select your input variables",
                usable_features,
                key="logistic_features"
            )

            if selected_features:
                X = df[selected_features]
                y = df[target]

                modeling_df = pd.concat([X, y], axis=1)
                missing_rows = int(modeling_df.isnull().any(axis=1).sum())

                if missing_rows > 0:
                    st.warning(
                        f"The selected data still contains missing values in {missing_rows} rows. "
                        "Logistic Regression cannot run until those missing values are handled."
                    )
                    st.write(
                        "You can go back to the Data Cleaning page to clean the data further, "
                        "or drop the rows with missing values below for this model."
                    )

                    missing_data_choice = st.radio(
                        "How would you like to handle the remaining missing values?",
                        ["Go back and clean the data", "Drop rows with missing values for this model"],
                        key="logistic_missing_choice"
                    )

                    if missing_data_choice == "Drop rows with missing values for this model":
                        modeling_df = modeling_df.dropna()
                        X = modeling_df[selected_features]
                        y = modeling_df[target]
                        st.info(f"{missing_rows} rows with missing values were removed for this model run.")
                    else:
                        st.stop()

                if y.nunique() < 2:
                    st.warning("Logistic Regression needs at least two target classes to run.")
                    st.stop()

                test_size = st.slider(
                    "Select a test size",
                    min_value=0.10,
                    max_value=0.50,
                    value=0.20,
                    step=0.05,
                    key="logistic_test_size"
                )

                X_train, X_test, y_train, y_test = train_test_split(
                    X,
                    y,
                    test_size=test_size,
                    random_state=42,
                    stratify=y
                )

                if scale_data:
                    scaler = StandardScaler()
                    X_train = scaler.fit_transform(X_train)
                    X_test = scaler.transform(X_test)
                    st.info("Numeric input features were scaled for this model run.")

                log_reg = LogisticRegression()
                log_reg.fit(X_train, y_train)
                y_pred = log_reg.predict(X_test)

                accuracy = accuracy_score(y_test, y_pred)

                st.write("### Here are your results!")
                st.write(f"Accuracy Score: {accuracy:.2f}")

                if len(log_reg.coef_) == 1:
                    coefficients_df = pd.DataFrame({
                        "Feature": selected_features,
                        "Coefficient": log_reg.coef_[0]
                    })
                    coefficients_df["Absolute Impact"] = coefficients_df["Coefficient"].abs()
                    coefficients_df = coefficients_df.sort_values("Absolute Impact", ascending=False)

                    st.subheader("Feature Coefficients")
                    st.caption("Larger absolute coefficients generally indicate a stronger contribution to the prediction.")
                    st.dataframe(
                        coefficients_df[["Feature", "Coefficient"]].round(4),
                        height=250
                    )

                results_df = pd.DataFrame({
                    "Actual": y_test.reset_index(drop=True),
                    "Predicted": pd.Series(y_pred)
                })

                st.subheader("Actual vs Predicted Values")
                st.dataframe(results_df.head(10), height=250)

else:
    st.info("No dataset is loaded yet. Go to the Data Cleaning page first if you want to work from a CSV.")
