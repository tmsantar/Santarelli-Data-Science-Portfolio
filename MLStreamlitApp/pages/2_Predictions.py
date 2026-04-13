import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from pandas.api.types import is_numeric_dtype
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import accuracy_score, mean_squared_error, root_mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier, plot_tree
from xgboost import XGBClassifier


st.set_page_config(page_title="Predictions", page_icon="📈", layout="wide")


# ── Helpers ──────────────────────────────────────────────────────────────────

def prepare_model_data(df, target, key_prefix):
    feature_candidates = [col for col in df.columns if col != target]
    numeric_features = df[feature_candidates].select_dtypes(include=["number"]).columns.tolist()

    dummy_code = st.radio(
        "Dummy-code categorical predictor columns?",
        ["No", "Yes"],
        key=f"{key_prefix}_dummy_code"
    )

    usable_features = feature_candidates if dummy_code == "Yes" else numeric_features
    if dummy_code == "Yes":
        st.caption("Categorical columns will be converted to dummy variables.")
    else:
        st.caption("Only numeric columns shown. Turn on dummy coding to include categorical columns.")

    if not usable_features:
        st.warning("No usable input variables available for this model.")
        return None

    selected_features = st.multiselect(
        "Input variables",
        usable_features,
        key=f"{key_prefix}_features"
    )

    if not selected_features:
        return None

    X = df[selected_features].copy()
    y = df[target].copy()

    if dummy_code == "Yes":
        X = pd.get_dummies(X, drop_first=True)

    return X, y


def handle_missing(modeling_df, target, key):
    missing_rows = int(modeling_df.isnull().any(axis=1).sum())
    if missing_rows == 0:
        return modeling_df, False

    st.warning(f"{missing_rows} rows contain missing values.")
    choice = st.radio(
        "How would you like to handle them?",
        ["Go back and clean the data", "Drop rows with missing values for this model"],
        key=key
    )
    if choice == "Drop rows with missing values for this model":
        modeling_df = modeling_df.dropna()
        st.info(f"Dropped {missing_rows} rows with missing values.")
        return modeling_df, False
    return modeling_df, True  # signal to stop


def get_test_size(key):
    return st.slider(
        "Test set size",
        min_value=0.10, max_value=0.50, value=0.20, step=0.05,
        key=key
    )


def show_regression_results(y_test, y_pred):
    st.subheader("Results")
    col1, col2, col3 = st.columns(3)
    col1.metric("MSE", f"{mean_squared_error(y_test, y_pred):.2f}")
    col2.metric("RMSE", f"{root_mean_squared_error(y_test, y_pred):.2f}")
    col3.metric("R²", f"{r2_score(y_test, y_pred):.2f}")

    st.subheader("Actual vs Predicted")
    results_df = pd.DataFrame({
        "Actual": y_test.reset_index(drop=True),
        "Predicted": pd.Series(y_pred).round(2)
    })
    st.dataframe(results_df.head(10), use_container_width=True, height=250)


def show_classification_results(y_test, y_pred):
    st.subheader("Results")
    st.metric("Accuracy", f"{accuracy_score(y_test, y_pred):.2f}")

    st.subheader("Actual vs Predicted")
    results_df = pd.DataFrame({
        "Actual": y_test.reset_index(drop=True),
        "Predicted": pd.Series(y_pred).reset_index(drop=True)
    })
    st.dataframe(results_df.head(10), use_container_width=True, height=250)


def show_coefficients(feature_names, coefficients, intercept, title="Feature Coefficients"):
    df_coef = pd.DataFrame({"Feature": list(feature_names), "Coefficient": list(coefficients)})
    intercept_row = pd.DataFrame({"Feature": ["Intercept"], "Coefficient": [intercept]})
    df_coef = pd.concat([intercept_row, df_coef], ignore_index=True)
    df_coef = df_coef.reindex(df_coef["Coefficient"].abs().sort_values(ascending=False).index)

    st.subheader(title)
    st.caption("Larger absolute values indicate stronger contribution to the prediction.")
    st.dataframe(df_coef[["Feature", "Coefficient"]].round(4), use_container_width=True, height=250)


def show_importances(feature_names, importances, title="Feature Importances"):
    df_imp = pd.DataFrame({"Feature": list(feature_names), "Importance": list(importances)})
    df_imp = df_imp.sort_values("Importance", ascending=False)

    st.subheader(title)
    st.caption("Higher values indicate features the model relied on more heavily.")
    st.dataframe(df_imp.round(4), use_container_width=True, height=250)


def apply_scaling(X, key_suffix):
    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns, index=X.index)
    st.info("Numeric features were scaled using StandardScaler.")
    return X_scaled


# ── Main ─────────────────────────────────────────────────────────────────────

st.title("Predictions")

if "dataframe" not in st.session_state:
    st.info("No dataset loaded. Go to the Data Cleaning page first.")
    st.stop()

df = st.session_state["dataframe"]

st.markdown("Select a **target variable** to get started. The app will detect the problem type automatically.")

target = st.selectbox("Target variable", df.columns)
target_series = df[target].dropna()

detected = "classification" if (not is_numeric_dtype(target_series) or target_series.nunique() <= 10) else "regression"
st.write(f"Detected problem type: **{detected.title()}**")

problem_type = st.radio(
    "Keep detected type or switch?",
    ["Classification", "Regression"],
    index=0 if detected == "classification" else 1
)

st.divider()

# Model selection
if problem_type == "Regression":
    model = "Linear Regression"
    st.write("Model: **Linear Regression**")
else:
    model = st.selectbox("Classification model", ["Logistic Regression", "Decision Tree Classifier", "XGBoost Classifier"])

# Sidebar
with st.sidebar:
    st.subheader("Model Options")
    if model in ("Linear Regression", "Logistic Regression"):
        scale_data = st.toggle("Scale numeric features")
    else:
        scale_data = False
        st.caption("Scaling applies to Linear / Logistic Regression only.")

st.divider()

# ── Linear Regression ─────────────────────────────────────────────────────────
if model == "Linear Regression":
    prepared = prepare_model_data(df, target, "linear")
    if prepared:
        X, y = prepared
        mdf = pd.concat([X, y], axis=1)
        mdf, should_stop = handle_missing(mdf, target, "linear_missing")
        if should_stop:
            st.stop()
        X, y = mdf.drop(columns=[target]), mdf[target]

        test_size = get_test_size("linear_test_size")
        if scale_data:
            X = apply_scaling(X, "linear")

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
        model_obj = LinearRegression().fit(X_train, y_train)

        show_regression_results(y_test, model_obj.predict(X_test))
        show_coefficients(X.columns, model_obj.coef_, model_obj.intercept_)

# ── Logistic Regression ───────────────────────────────────────────────────────
elif model == "Logistic Regression":
    prepared = prepare_model_data(df, target, "logistic")
    if prepared:
        X, y = prepared
        mdf = pd.concat([X, y], axis=1)
        mdf, should_stop = handle_missing(mdf, target, "logistic_missing")
        if should_stop:
            st.stop()
        X, y = mdf.drop(columns=[target]), mdf[target]

        if y.nunique() < 2:
            st.warning("Logistic Regression needs at least two target classes.")
            st.stop()

        test_size = get_test_size("logistic_test_size")
        if scale_data:
            X = apply_scaling(X, "logistic")

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42, stratify=y)
        model_obj = LogisticRegression(max_iter=1000).fit(X_train, y_train)

        show_classification_results(y_test, model_obj.predict(X_test))

        if len(model_obj.coef_) == 1:
            show_coefficients(X.columns, model_obj.coef_[0], model_obj.intercept_[0])
        else:
            avg = pd.DataFrame(model_obj.coef_, columns=X.columns).abs().mean()
            show_coefficients(X.columns, avg.values, pd.Series(model_obj.intercept_).abs().mean(), "Average Feature Coefficients")

# ── Decision Tree ─────────────────────────────────────────────────────────────
elif model == "Decision Tree Classifier":
    prepared = prepare_model_data(df, target, "tree_clf")
    if prepared:
        X, y = prepared
        missing = int(pd.concat([X, y], axis=1).isnull().any(axis=1).sum())
        if missing:
            st.info(f"{missing} rows have missing values — Decision Trees can still run.")

        if y.nunique() < 2:
            st.warning("Decision Tree needs at least two target classes.")
            st.stop()

        test_size = get_test_size("tree_clf_test_size")
        max_depth = st.slider("Max depth", 1, 15, 4, key="tree_clf_depth")

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42, stratify=y)
        model_obj = DecisionTreeClassifier(max_depth=max_depth, random_state=42).fit(X_train, y_train)

        show_classification_results(y_test, model_obj.predict(X_test))
        show_importances(X.columns, model_obj.feature_importances_)

        st.subheader("Decision Tree Diagram")
        fig, ax = plt.subplots(figsize=(20, 10))
        plot_tree(model_obj, feature_names=X.columns,
                  class_names=[str(l) for l in sorted(y.unique())],
                  filled=True, rounded=True, fontsize=8, ax=ax)
        st.pyplot(fig)
        plt.close(fig)

# ── XGBoost ───────────────────────────────────────────────────────────────────
elif model == "XGBoost Classifier":
    prepared = prepare_model_data(df, target, "xgb_clf")
    if prepared:
        X, y = prepared
        missing = int(pd.concat([X, y], axis=1).isnull().any(axis=1).sum())
        if missing:
            st.info(f"{missing} rows have missing values — XGBoost can still run.")

        if y.nunique() < 2:
            st.warning("XGBoost needs at least two target classes.")
            st.stop()

        le = LabelEncoder()
        y_enc = le.fit_transform(y)

        test_size = get_test_size("xgb_clf_test_size")
        n_estimators = st.slider("Number of trees", 50, 300, 100, step=25, key="xgb_clf_estimators")
        max_depth = st.slider("Max depth", 1, 10, 4, key="xgb_clf_depth")

        X_train, X_test, y_train, y_test = train_test_split(X, y_enc, test_size=test_size, random_state=42, stratify=y_enc)
        model_obj = XGBClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42).fit(X_train, y_train)

        show_classification_results(
            pd.Series(le.inverse_transform(y_test)),
            pd.Series(le.inverse_transform(model_obj.predict(X_test)))
        )
        show_importances(X.columns, model_obj.feature_importances_)