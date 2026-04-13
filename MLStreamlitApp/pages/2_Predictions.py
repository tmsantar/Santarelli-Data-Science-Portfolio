import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from pandas.api.types import is_numeric_dtype
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import accuracy_score, mean_squared_error, root_mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier, plot_tree
from xgboost import XGBClassifier


st.set_page_config(page_title="Predictions", page_icon="📈", layout="wide")


def prepare_model_data(df, target, key_prefix):
    feature_candidates = [col for col in df.columns if col != target]
    numeric_features = df[feature_candidates].select_dtypes(include=["number"]).columns.tolist()

    encode_categorical = st.radio(
        "Would you like to dummy code categorical predictor columns?",
        ["No", "Yes"],
        key=f"{key_prefix}_dummy_code"
    )

    if encode_categorical == "Yes":
        usable_features = feature_candidates
        st.caption("Categorical predictor columns will be converted into dummy variables for the model.")
    else:
        usable_features = numeric_features
        st.caption("Only numeric predictor columns are shown unless dummy coding is turned on.")

    if not usable_features:
        st.warning("There are no usable input variables available for this model.")
        return None

    selected_features = st.multiselect(
        "Select your input variables",
        usable_features,
        key=f"{key_prefix}_features"
    )

    if not selected_features:
        return None

    X = df[selected_features].copy()
    y = df[target].copy()

    if encode_categorical == "Yes":
        X = pd.get_dummies(X, drop_first=True)

    modeling_df = pd.concat([X, y], axis=1)
    missing_rows = int(modeling_df.isnull().any(axis=1).sum())

    if missing_rows > 0:
        st.warning(
            f"The selected data still contains missing values in {missing_rows} rows. "
            "This model cannot run until those missing values are handled."
        )
        st.write(
            "You can go back to the Data Cleaning page to clean the data further, "
            "or drop the rows with missing values below for this model."
        )

        missing_data_choice = st.radio(
            "How would you like to handle the remaining missing values?",
            ["Go back and clean the data", "Drop rows with missing values for this model"],
            key=f"{key_prefix}_missing_choice"
        )

        if missing_data_choice == "Drop rows with missing values for this model":
            modeling_df = modeling_df.dropna()
            X = modeling_df.drop(columns=[target])
            y = modeling_df[target]
            st.info(f"{missing_rows} rows with missing values were removed for this model run.")
        else:
            st.stop()

    return X, y


def show_regression_results(y_test, y_pred):
    mse = mean_squared_error(y_test, y_pred)
    rmse = root_mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    st.write("### Here are your results!")
    st.write(f"Mean Squared Error: {mse:.2f}")
    st.write(f"Root Mean Squared Error: {rmse:.2f}")
    st.write(f"R-squared Score: {r2:.2f}")

    results_df = pd.DataFrame({
        "Actual": y_test.reset_index(drop=True),
        "Predicted": pd.Series(y_pred).round(2)
    })

    st.subheader("Actual vs Predicted Values")
    st.dataframe(results_df.head(10), height=250)


def show_classification_results(y_test, y_pred):
    accuracy = accuracy_score(y_test, y_pred)

    st.write("### Here are your results!")
    st.write(f"Accuracy Score: {accuracy:.2f}")

    results_df = pd.DataFrame({
        "Actual": y_test.reset_index(drop=True),
        "Predicted": pd.Series(y_pred)
    })

    st.subheader("Actual vs Predicted Values")
    st.dataframe(results_df.head(10), height=250)


def show_coefficients(feature_names, coefficients, intercept, title="Feature Coefficients"):
    coefficients_df = pd.DataFrame({
        "Feature": feature_names,
        "Coefficient": coefficients
    })
    intercept_df = pd.DataFrame({
        "Feature": ["Intercept"],
        "Coefficient": [intercept]
    })
    coefficients_df = pd.concat([intercept_df, coefficients_df], ignore_index=True)
    coefficients_df["Absolute Impact"] = coefficients_df["Coefficient"].abs()
    coefficients_df = coefficients_df.sort_values("Absolute Impact", ascending=False)

    st.subheader(title)
    st.caption("Larger absolute values generally indicate a stronger contribution to the prediction.")
    st.dataframe(coefficients_df[["Feature", "Coefficient"]].round(4), height=250)


def show_importances(feature_names, importances, title="Feature Importances"):
    importance_df = pd.DataFrame({
        "Feature": feature_names,
        "Importance": importances
    }).sort_values("Importance", ascending=False)

    st.subheader(title)
    st.caption("Higher values indicate features the model relied on more heavily.")
    st.dataframe(importance_df.round(4), height=250)


st.title("Predictions")

if "dataframe" in st.session_state:
    df = st.session_state["dataframe"]

    st.markdown("""
    What are you trying to predict? Select a target variable
    to discover which models you can use.
    """)

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
        model = "Linear Regression"
        st.write("Regression model: **Linear Regression**")
    else:
        classification_models = ["Logistic Regression", "Decision Tree Classifier", "XGBoost Classifier"]
        model = st.selectbox("Choose a classification model", classification_models)

    scaling_models = ["Linear Regression", "Logistic Regression"]
    with st.sidebar:
        st.subheader("Model Options")
        if model in scaling_models:
            scale_data = st.toggle("Scale numeric features")
        else:
            scale_data = False
            st.caption("Scaling is only used for Linear Regression and Logistic Regression.")

    if model in scaling_models:
        st.caption("Optional preprocessing: you can scale numeric features using StandardScaler before training your model.")

    if model == "Linear Regression":
        prepared = prepare_model_data(df, target, "linear")
        if prepared is not None:
            X, y = prepared

            test_size = st.slider(
                "Select a test size",
                min_value=0.10,
                max_value=0.50,
                value=0.20,
                step=0.05,
                key="linear_test_size"
            )

            if scale_data:
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
                X_scaled = pd.DataFrame(
                    X_scaled,
                    columns=X.columns,
                    index=X.index
                )
                X_train, X_test, y_train, y_test = train_test_split(
                    X_scaled, y, test_size=test_size, random_state=42
                )
                st.info("Numeric input features were scaled for this model run.")
            else:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=test_size, random_state=42
                )

            lin_reg = LinearRegression()
            lin_reg.fit(X_train, y_train)
            y_pred = lin_reg.predict(X_test)

            show_regression_results(y_test, y_pred)
            show_coefficients(X.columns, lin_reg.coef_, lin_reg.intercept_)

    if model == "Logistic Regression":
        prepared = prepare_model_data(df, target, "logistic")
        if prepared is not None:
            X, y = prepared

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

            if scale_data:
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
                X_scaled = pd.DataFrame(
                    X_scaled,
                    columns=X.columns,
                    index=X.index
                )
                X_train, X_test, y_train, y_test = train_test_split(
                    X_scaled, y, test_size=test_size, random_state=42, stratify=y
                )
                st.info("Numeric input features were scaled for this model run.")
            else:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=test_size, random_state=42, stratify=y
                )

            log_reg = LogisticRegression(max_iter=1000)
            log_reg.fit(X_train, y_train)
            y_pred = log_reg.predict(X_test)

            show_classification_results(y_test, y_pred)

            if len(log_reg.coef_) == 1:
                show_coefficients(X.columns, log_reg.coef_[0], log_reg.intercept_[0])
            else:
                avg_abs_coef = pd.DataFrame(log_reg.coef_, columns=X.columns).abs().mean(axis=0)
                intercept_value = pd.Series(log_reg.intercept_).abs().mean()
                show_coefficients(X.columns, avg_abs_coef.values, intercept_value, "Average Feature Coefficients")

    if model == "Decision Tree Classifier":
        prepared = prepare_model_data(df, target, "tree_clf")
        if prepared is not None:
            X, y = prepared

            if y.nunique() < 2:
                st.warning("Decision Tree Classifier needs at least two target classes to run.")
                st.stop()

            test_size = st.slider(
                "Select a test size",
                min_value=0.10,
                max_value=0.50,
                value=0.20,
                step=0.05,
                key="tree_clf_test_size"
            )

            max_depth = st.slider(
                "Select max depth",
                min_value=1,
                max_value=15,
                value=4,
                key="tree_clf_depth"
            )

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42, stratify=y
            )

            tree_clf = DecisionTreeClassifier(max_depth=max_depth, random_state=42)
            tree_clf.fit(X_train, y_train)
            y_pred = tree_clf.predict(X_test)

            show_classification_results(y_test, y_pred)
            show_importances(X.columns, tree_clf.feature_importances_)

            fig, ax = plt.subplots(figsize=(20, 10))
            plot_tree(
                tree_clf,
                feature_names=X.columns,
                class_names=[str(label) for label in sorted(y.unique())],
                filled=True,
                rounded=True,
                fontsize=8,
                ax=ax
            )
            st.subheader("Decision Tree Diagram")
            st.pyplot(fig)
            plt.close(fig)

    if model == "XGBoost Classifier":
        prepared = prepare_model_data(df, target, "xgb_clf")
        if prepared is not None:
            X, y = prepared

            if y.nunique() < 2:
                st.warning("XGBoost Classifier needs at least two target classes to run.")
                st.stop()

            label_encoder = LabelEncoder()
            y_encoded = label_encoder.fit_transform(y)

            test_size = st.slider(
                "Select a test size",
                min_value=0.10,
                max_value=0.50,
                value=0.20,
                step=0.05,
                key="xgb_clf_test_size"
            )

            n_estimators = st.slider(
                "Select number of trees",
                min_value=50,
                max_value=300,
                value=100,
                step=25,
                key="xgb_clf_estimators"
            )

            max_depth = st.slider(
                "Select max depth",
                min_value=1,
                max_value=10,
                value=4,
                key="xgb_clf_depth"
            )

            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=test_size, random_state=42, stratify=y_encoded
            )

            xgb_clf = XGBClassifier(
                n_estimators=n_estimators,
                max_depth=max_depth,
                random_state=42
            )
            xgb_clf.fit(X_train, y_train)
            y_pred = xgb_clf.predict(X_test)

            y_test_labels = pd.Series(label_encoder.inverse_transform(y_test))
            y_pred_labels = pd.Series(label_encoder.inverse_transform(y_pred))

            show_classification_results(y_test_labels, y_pred_labels)
            show_importances(X.columns, xgb_clf.feature_importances_)

else:
    st.info("No dataset is loaded yet. Go to the Data Cleaning page first if you want to work from a CSV.")
