import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from pandas.api.types import is_numeric_dtype
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay, f1_score, mean_squared_error, precision_score, recall_score, roc_auc_score, roc_curve, root_mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier, plot_tree
from xgboost import XGBClassifier


st.set_page_config(page_title="Predictions", page_icon="📈", layout="wide")


# ── Helpers ──────────────────────────────────────────────────────────────────

def prepare_model_data(df, target, key_prefix):
    feature_candidates = [col for col in df.columns if col != target]
    numeric_features = df[feature_candidates].select_dtypes(include=["number"]).columns.tolist()

    st.markdown("### 🧩 Choose Input Variables")

    dummy_code = st.radio(
        "Include categorical predictor columns?",
        ["No", "Yes"],
        key=f"{key_prefix}_dummy_code",
        horizontal=True
    )

    usable_features = feature_candidates if dummy_code == "Yes" else numeric_features

    if dummy_code == "Yes":
        st.caption("Categorical columns will be converted into dummy variables automatically.")
    else:
        st.caption("Only numeric columns are shown. Turn this on if you want to include categorical predictors.")

    if not usable_features:
        st.warning("No usable input variables are available for this model.")
        return None

    selected_features = st.multiselect(
        "Select your input variables",
        usable_features,
        key=f"{key_prefix}_features"
    )

    if not selected_features:
        st.info("Choose at least one input variable to continue.")
        return None

    X = df[selected_features].copy()
    y = df[target].copy()

    if dummy_code == "Yes":
        X = pd.get_dummies(X, drop_first=True)

    return X, y


def handle_missing(modeling_df, target, key):
    missing_rows = int(modeling_df.isnull().any(axis=1).sum())

    if missing_rows == 0:
        st.success("✅ No missing values found in the data used for this model.")
        return modeling_df, False

    st.warning(f"⚠️ {missing_rows} rows contain missing values.")

    choice = st.radio(
        "How would you like to handle missing values?",
        ["Go back and clean the data", "Drop rows with missing values for this model"],
        key=key
    )

    if choice == "Drop rows with missing values for this model":
        modeling_df = modeling_df.dropna()
        st.info(f"Removed {missing_rows} rows with missing values for this run.")
        return modeling_df, False

    return modeling_df, True


def get_test_size(key):
    return st.slider(
        "📏 Test set size",
        min_value=0.10,
        max_value=0.50,
        value=0.20,
        step=0.05,
        key=key
    )


def show_regression_results(y_test, y_pred):
    st.markdown("### 📊 Regression Results")

    col1, col2, col3 = st.columns(3)
    col1.metric("MSE", f"{mean_squared_error(y_test, y_pred):.2f}", 
    help = "The average squared difference between estimated values and the actual value")
    col2.metric("RMSE", f"{root_mean_squared_error(y_test, y_pred):.2f}", 
    help = "The average difference between values predicted by a model and the actual observed values")
    col3.metric("R²", f"{r2_score(y_test, y_pred):.2f}", 
    help = "The proportion of variance in a dependent variable explained by a regression model's independent variable(s)")

    st.markdown("### 🔍 Actual vs Predicted")
    results_df = pd.DataFrame({
        "Actual": y_test.reset_index(drop=True),
        "Predicted": pd.Series(y_pred).round(2)
    })
    st.dataframe(results_df.head(10), use_container_width=True, height=250)


def show_classification_results(y_test, y_pred, y_score=None):
    st.markdown("### 📊 Classification Results")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Accuracy", f"{accuracy_score(y_test, y_pred):.2f}", 
    help = "The proportion of correct predictions made by a model out of the total number of predictions made")
    col2.metric("Precision", f"{precision_score(y_test, y_pred, average='weighted', zero_division=0):.2f}", 
    help = "The accuracy of positive predictions")
    col3.metric("Recall", f"{recall_score(y_test, y_pred, average='weighted', zero_division=0):.2f}", 
    help = "The ability of the model to identify all relevant instances of a positive class")
    col4.metric("F1 Score", f"{f1_score(y_test, y_pred, average='weighted', zero_division=0):.2f}", 
    help = "The harmonic mean of precision and recall")

    st.divider()

    labels = sorted(pd.Series(pd.concat([pd.Series(y_test), pd.Series(y_pred)])).astype(str).unique().tolist())
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("### 🧾 Confusion Matrix", text_alignment = "center")
        cm = confusion_matrix(pd.Series(y_test).astype(str), pd.Series(y_pred).astype(str), labels=labels)
        fig, ax = plt.subplots(figsize=(6, 6), constrained_layout=True)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
        disp.plot(ax=ax, cmap="Blues", colorbar=False)
        ax.set_aspect("equal", adjustable="box")
        st.pyplot(fig)
        plt.close(fig)

    with chart_col2:
        st.markdown("### 📈 ROC Curve", text_alignment = "center")
        if y_score is not None and len(pd.Series(y_test).unique()) == 2:
            positive_label = sorted(pd.Series(y_test).unique())[-1]
            y_true_binary = (pd.Series(y_test) == positive_label).astype(int)
            fpr, tpr, _ = roc_curve(y_true_binary, y_score)
            auc_score = roc_auc_score(y_true_binary, y_score)

            fig, ax = plt.subplots(figsize=(6, 6), constrained_layout=True)
            ax.plot(fpr, tpr, label=f"AUC = {auc_score:.2f}")
            ax.plot([0, 1], [0, 1], linestyle="--")
            ax.set_xlabel("False Positive Rate")
            ax.set_ylabel("True Positive Rate")
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_aspect("equal", adjustable="box")
            ax.legend(loc="lower right")
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.info("ROC curve is shown for binary classification models when probability scores are available.")

    st.divider()

    st.markdown("### 🔍 Actual vs Predicted")
    results_df = pd.DataFrame({
        "Actual": y_test.reset_index(drop=True),
        "Predicted": pd.Series(y_pred).reset_index(drop=True)
    })
    st.dataframe(results_df.head(10), use_container_width=True, height=250)


def show_coefficients(feature_names, coefficients, intercept, title="Feature Coefficients"):
    df_coef = pd.DataFrame({
        "Feature": list(feature_names),
        "Coefficient": list(coefficients)
    })

    intercept_row = pd.DataFrame({
        "Feature": ["Intercept"],
        "Coefficient": [intercept]
    })

    df_coef = pd.concat([intercept_row, df_coef], ignore_index=True)
    df_coef = df_coef.reindex(df_coef["Coefficient"].abs().sort_values(ascending=False).index)

    st.markdown(f"### 🧠 {title}")
    st.caption("Larger absolute values usually mean a stronger effect on the prediction.")
    st.dataframe(df_coef[["Feature", "Coefficient"]].round(4), use_container_width=True, height=250)


def show_importances(feature_names, importances, title="Feature Importances"):
    df_imp = pd.DataFrame({
        "Feature": list(feature_names),
        "Importance": list(importances)
    }).sort_values("Importance", ascending=False)

    st.markdown(f"### 🌟 {title}")
    st.caption("Higher values indicate features the model relied on more heavily.")
    st.dataframe(df_imp.round(4), use_container_width=True, height=250)


def apply_scaling(X, key_suffix):
    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns, index=X.index)
    st.info("📐 Numeric features were scaled using StandardScaler.")
    return X_scaled


# ── Main ─────────────────────────────────────────────────────────────────────

st.title("📈 Predictions")
st.markdown("Use your cleaned dataset to train a model and preview results.")

if "dataframe" not in st.session_state:
    st.info("No dataset loaded yet. Go to the **Data Cleaning** page first.")
    st.stop()

df = st.session_state["dataframe"]

st.markdown("### 🎯 Step 1: Choose a Target Variable")
st.caption("The app will try to detect whether your problem is classification or regression.")

target = st.selectbox("Target variable", df.columns)
target_series = df[target].dropna()

detected = "classification" if (not is_numeric_dtype(target_series) or target_series.nunique() <= 10) else "regression"

st.info(f"Detected problem type: **{detected.title()}**")

problem_type = st.radio(
    "Keep the detected type or switch manually:",
    ["Classification", "Regression"],
    index=0 if detected == "classification" else 1,
    horizontal=True
)

st.divider()

# Model selection
st.markdown("### 💻 Step 2: Choose a Model")

if problem_type == "Regression":
    model = "Linear Regression"
    st.success("Selected model: **Linear Regression**")
else:
    model = st.selectbox(
        "Classification model",
        ["Logistic Regression", "Decision Tree Classifier", "XGBoost Classifier"]
    )

# Sidebar
with st.sidebar:
    st.subheader("⚙️ Model Options")

    if model in ("Linear Regression", "Logistic Regression"):
        scale_data = st.toggle("Scale numeric features")
        st.caption("Helpful for linear and logistic regression.")
    else:
        scale_data = False
        st.caption("Scaling is only used for Linear / Logistic Regression.")

st.divider()

# ── Linear Regression ─────────────────────────────────────────────────────────
if model == "Linear Regression":
    st.markdown("## 📈 Linear Regression")
    st.caption("Best for predicting continuous numeric outcomes.")

    prepared = prepare_model_data(df, target, "linear")

    if prepared:
        X, y = prepared

        st.markdown("### 🧼 Missing Data Check")
        mdf = pd.concat([X, y], axis=1)
        mdf, should_stop = handle_missing(mdf, target, "linear_missing")

        if should_stop:
            st.stop()

        X, y = mdf.drop(columns=[target]), mdf[target]

        st.markdown("### ⚙️ Training Settings")
        test_size = get_test_size("linear_test_size")

        if scale_data:
            X = apply_scaling(X, "linear")

        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=42
        )

        model_obj = LinearRegression().fit(X_train, y_train)

        show_regression_results(y_test, model_obj.predict(X_test))
        show_coefficients(X.columns, model_obj.coef_, model_obj.intercept_)

        st.success("✅ Linear Regression model trained successfully.")

# ── Logistic Regression ───────────────────────────────────────────────────────
elif model == "Logistic Regression":
    st.markdown("## 📊 Logistic Regression")
    st.caption("Best for classification problems with labeled categories.")

    prepared = prepare_model_data(df, target, "logistic")

    if prepared:
        X, y = prepared

        st.markdown("### 🧼 Missing Data Check")
        mdf = pd.concat([X, y], axis=1)
        mdf, should_stop = handle_missing(mdf, target, "logistic_missing")

        if should_stop:
            st.stop()

        X, y = mdf.drop(columns=[target]), mdf[target]

        if y.nunique() < 2:
            st.warning("Logistic Regression needs at least two target classes.")
            st.stop()

        st.markdown("### ⚙️ Training Settings")
        test_size = get_test_size("logistic_test_size")

        if scale_data:
            X = apply_scaling(X, "logistic")

        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=42,
            stratify=y
        )

        model_obj = LogisticRegression(max_iter=1000).fit(X_train, y_train)

        y_pred = model_obj.predict(X_test)
        y_score = model_obj.predict_proba(X_test)[:, 1] if y.nunique() == 2 else None
        show_classification_results(y_test, y_pred, y_score)

        if len(model_obj.coef_) == 1:
            show_coefficients(X.columns, model_obj.coef_[0], model_obj.intercept_[0])
        else:
            avg = pd.DataFrame(model_obj.coef_, columns=X.columns).abs().mean()
            show_coefficients(
                X.columns,
                avg.values,
                pd.Series(model_obj.intercept_).abs().mean(),
                "Average Feature Coefficients"
            )

        st.success("✅ Logistic Regression model trained successfully.")

# ── Decision Tree ─────────────────────────────────────────────────────────────
elif model == "Decision Tree Classifier":
    st.markdown("## 🌳 Decision Tree Classifier")
    st.caption("Useful for interpretable classification models with branching logic.")

    prepared = prepare_model_data(df, target, "tree_clf")

    if prepared:
        X, y = prepared

        st.markdown("### 🧼 Missing Data Check")
        mdf = pd.concat([X, y], axis=1)
        mdf, should_stop = handle_missing(mdf, target, "tree_missing")

        if should_stop:
            st.stop()

        X, y = mdf.drop(columns=[target]), mdf[target]

        if y.nunique() < 2:
            st.warning("Decision Tree needs at least two target classes.")
            st.stop()

        st.markdown("### ⚙️ Training Settings")
        test_size = get_test_size("tree_clf_test_size")
        max_depth = st.slider("🌲 Max depth", 1, 15, 3, key="tree_clf_depth")

        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=42,
            stratify=y
        )

        model_obj = DecisionTreeClassifier(max_depth=max_depth, random_state=42).fit(X_train, y_train)

        y_pred = model_obj.predict(X_test)
        y_score = model_obj.predict_proba(X_test)[:, 1] if y.nunique() == 2 else None
        show_classification_results(y_test, y_pred, y_score)
        show_importances(X.columns, model_obj.feature_importances_)

        st.success("✅ Decision Tree model trained successfully.")

# ── XGBoost ───────────────────────────────────────────────────────────────────
elif model == "XGBoost Classifier":
    st.markdown("## ⚡ XGBoost Classifier")
    st.caption("A powerful boosting model for classification tasks.")

    prepared = prepare_model_data(df, target, "xgb_clf")

    if prepared:
        X, y = prepared

        missing = int(pd.concat([X, y], axis=1).isnull().any(axis=1).sum())
        if missing:
            st.info(f"ℹ️ {missing} rows have missing values. XGBoost can usually still run without dropping them first.")

        if y.nunique() < 2:
            st.warning("XGBoost needs at least two target classes.")
            st.stop()

        le = LabelEncoder()
        y_enc = le.fit_transform(y)

        st.markdown("### ⚙️ Training Settings")
        test_size = get_test_size("xgb_clf_test_size")
        n_estimators = st.slider("🌲 Number of trees", 50, 300, 100, step=25, key="xgb_clf_estimators")
        max_depth = st.slider("📏 Max depth", 1, 10, 3, key="xgb_clf_depth")

        X_train, X_test, y_train, y_test = train_test_split(
            X, y_enc,
            test_size=test_size,
            random_state=42,
            stratify=y_enc
        )

        model_obj = XGBClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=42
        ).fit(X_train, y_train)

        y_pred = model_obj.predict(X_test)
        y_pred_labels = pd.Series(le.inverse_transform(y_pred))
        y_test_labels = pd.Series(le.inverse_transform(y_test))
        y_score = model_obj.predict_proba(X_test)[:, 1] if len(le.classes_) == 2 else None
        show_classification_results(y_test_labels, y_pred_labels, y_score)
        show_importances(X.columns, model_obj.feature_importances_)

        st.success("✅ XGBoost model trained successfully.")
