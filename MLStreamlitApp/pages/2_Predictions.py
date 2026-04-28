import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from pandas.api.types import is_numeric_dtype
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay, f1_score, mean_squared_error, precision_score, recall_score, roc_auc_score, roc_curve, root_mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier


# Configure the Predictions page.
st.set_page_config(page_title="Predictions", page_icon="📈", layout="wide")


# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------

# These functions are used in the main page code below to keep things organized and reusable.

def prepare_model_data(df, target, key_prefix):
    # Every column except the target is a possible predictor.
    feature_candidates = [col for col in df.columns if col != target]

    # Only numeric predictors can be used without dummy coding, so we identify those here.
    numeric_features = df[feature_candidates].select_dtypes(include=["number"]).columns.tolist()

    st.markdown("### Choose Input Variables")

    # If the user says "Yes", categorical predictors will be converted into dummy variables.
    dummy_code = st.radio(
        "Include categorical predictor columns?",
        ["No", "Yes"],
        # key is needed to prevent this widget from resetting when the user switches between models.
        key=f"{key_prefix}_dummy_code",
        horizontal=True
    )

    # With dummy coding on, all predictors are allowed.
    # Otherwise, only numeric predictors are shown.
    usable_features = feature_candidates if dummy_code == "Yes" else numeric_features

    if dummy_code == "Yes":
        st.caption("Categorical columns will be converted into dummy variables automatically.")
    else:
        st.caption("Only numeric columns are shown. Turn this on if you want to include categorical predictors.")

    if not usable_features:
        st.warning("No usable input variables are available for this model.")
        return None

    # Let the user pick which predictors they want to use.
    selected_features = st.multiselect(
        "Select your input variables",
        usable_features,
        key=f"{key_prefix}_features"
    )

    if not selected_features:
        st.info("Choose at least one input variable to continue.")
        return None

    # X contains the predictor columns.
    # y contains the target column we are trying to predict.
    X = df[selected_features].copy()
    y = df[target].copy()

    if dummy_code == "Yes":
        # Convert text/category predictors into 0/1 dummy columns.
        # drop_first=True avoids the dummy variable trap by leaving out one category as the baseline.
        X = pd.get_dummies(X, drop_first=True)

    return X, y


def handle_missing(modeling_df, target, key):
    # Count how many rows in the modeling dataset contain missing values.
    missing_rows = int(modeling_df.isnull().any(axis=1).sum())

    # If there are no missing values, we can skip the rest of this function and return the original dataframe.
    if missing_rows == 0:
        st.success("✅ No missing values found in the data used for this model.")
        return modeling_df, False

    st.warning(f"⚠️ {missing_rows} rows contain missing values.")

    # Give the user a choice to stop and clean the data,
    # or drop missing rows just for this model run.
    choice = st.radio(
        "How would you like to handle missing values?",
        ["Go back and clean the data", "Drop rows with missing values for this model"],
        key=key
    )

    # If the user chooses to drop rows with missing values, we do that just for this model run and return the cleaned dataframe.
    if choice == "Drop rows with missing values for this model":
        modeling_df = modeling_df.dropna()
        st.info(f"Removed {missing_rows} rows with missing values for this run.")
        return modeling_df, False

    # Returning True tells the calling code to stop before model training.
    return modeling_df, True


def get_test_size(key):
    # This slider controls how much data is held out for testing.
    return st.slider(
        "📏 Test set size",
        min_value=0.10,
        max_value=0.50,
        value=0.20,
        step=0.05,
        key=key
    )


def show_regression_results(y_test, y_pred):
    # Display the main regression performance metrics.
    st.markdown("### 📊 Regression Results")

    # These metrics are commonly used to evaluate regression models. Lower MSE and RMSE values 
    # indicate better fit, while R² closer to 1 means the model explains more variance.
    col1, col2, col3 = st.columns(3)
    col1.metric("MSE", f"{mean_squared_error(y_test, y_pred):.2f}",
    help="The average squared difference between estimated values and the actual value")
    col2.metric("RMSE", f"{root_mean_squared_error(y_test, y_pred):.2f}",
    help="The average difference between values predicted by the model and the actual observed values")
    col3.metric("R²", f"{r2_score(y_test, y_pred):.2f}",
    help="The proportion of variance in the dependent variable explained by a regression model's independent variable(s)")

    # Show a few actual values next to their predicted values.
    st.markdown("### 🔍 Actual vs Predicted")
    results_df = pd.DataFrame({
        "Actual": y_test.reset_index(drop=True),
        # pd.series is used to align the indices of y_pred with y_test in case any rows were dropped due to missing values.
        "Predicted": pd.Series(y_pred).round(2)
    })
    st.dataframe(results_df.head(10), use_container_width=True, height=250)


def show_classification_results(y_test, y_pred, y_score=None):
    st.markdown("### 📊 Classification Results")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Accuracy", f"{accuracy_score(y_test, y_pred):.2f}",
    help="The proportion of correct predictions made by a model out of the total number of predictions made")

    # ✅ ADD THIS (1 line fix)
    unique_classes = sorted(pd.Series(y_test).unique())

    if len(unique_classes) == 2:
        pos_label = unique_classes[-1]

        precision = precision_score(y_test, y_pred, pos_label=pos_label, zero_division=0)
        recall = recall_score(y_test, y_pred, pos_label=pos_label, zero_division=0)
        f1 = f1_score(y_test, y_pred, pos_label=pos_label, zero_division=0)

    else:
        precision = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        recall = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

    col2.metric("Precision", f"{precision:.2f}",
    help="The accuracy of positive predictions")

    col3.metric("Recall", f"{recall:.2f}",
    help="The ability of the model to identify all relevant instances of a positive class")

    col4.metric("F1 Score", f"{f1:.2f}",
    help="The harmonic mean of precision and recall")

    st.divider()

    # Build the label list so all classes appear in the confusion matrix.
    labels = sorted(pd.Series(pd.concat([pd.Series(y_test), pd.Series(y_pred)])).astype(str).unique().tolist())
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        # Confusion matrix shows where the classifier was correct and incorrect.
        # The rows of the confusion matrix represent the actual classes, while the columns represent the predicted classes.
        st.markdown("### Confusion Matrix")
        cm = confusion_matrix(y_test, y_pred)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm)
        fig, ax = plt.subplots()
        # The confusion matrix is plotted using a blue color map, and the aspect ratio is set to 
        # equal to ensure that the cells are square. The layout of the plot is adjusted to fit 
        # well within the Streamlit app, and the plot is displayed using st.pyplot. 
        disp.plot(ax=ax, cmap="Blues", colorbar=False)
        ax.set_aspect("equal", adjustable="box")
        fig.subplots_adjust(left=0.16, right=0.96, bottom=0.16, top=0.92)
        st.pyplot(fig, use_container_width=True)
        # Frees up memory by closing the figure after it's displayed.
        plt.close(fig)


    with chart_col2:
        # ROC/AUC is only shown for binary classification when probability scores exist.
        # The ROC curve plots the true positive rate against the false positive rate at various threshold settings,
        # while the AUC score summarizes the overall ability of the model to discriminate between classes.
        st.markdown("### ROC Curve")
        if y_score is not None and len(pd.Series(y_test).unique()) == 2:
            positive_label = sorted(pd.Series(y_test).unique())[-1]
            y_true_binary = (pd.Series(y_test) == positive_label).astype(int)
            fpr, tpr, _ = roc_curve(y_true_binary, y_score)
            auc_score = roc_auc_score(y_true_binary, y_score)

            # The ROC curve is plotted with the AUC score in the legend, and a dashed diagonal line is added to represent random guessing.
            # The axes are labeled and the aspect ratio is set to equal to ensure a square plot. 
            # The layout is adjusted for better fit in the Streamlit app, and the plot is displayed using st.pyplot. 
            fig, ax = plt.subplots(figsize=(6, 6))
            ax.plot(fpr, tpr, label=f"AUC = {auc_score:.2f}")
            ax.plot([0, 1], [0, 1], linestyle="--")
            ax.set_xlabel("False Positive Rate")
            ax.set_ylabel("True Positive Rate")
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_aspect("equal", adjustable="box")
            ax.legend(loc="lower right")
            fig.subplots_adjust(left=0.16, right=0.96, bottom=0.16, top=0.92)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
        else:
            st.info("ROC curve is shown for binary classification models when probability scores are available.")

    st.divider()

    # Show a few actual labels next to the predicted labels.
    st.markdown("### 🔍 Actual vs Predicted")
    results_df = pd.DataFrame({
        "Actual": y_test.reset_index(drop=True),
        "Predicted": pd.Series(y_pred).reset_index(drop=True)
    })
    st.dataframe(results_df.head(10), use_container_width=True, height=250)


def show_coefficients(feature_names, coefficients, intercept, title="Feature Coefficients"):
    # Build a coefficient table so the user can see how each feature contributes.
    # list(feature_names) and list(coefficients) are used to ensure the data is in the correct 
    # format for the dataframe, especially if they come from a numpy array or pandas series.
    df_coef = pd.DataFrame({
        "Feature": list(feature_names),
        "Coefficient": list(coefficients)
    })

    # Add the intercept so the full model equation is represented.
    intercept_row = pd.DataFrame({
        "Feature": ["Intercept"],
        "Coefficient": [intercept]
    })

    # Sort by absolute size so the strongest effects appear first.
    df_coef = pd.concat([intercept_row, df_coef], ignore_index=True)
    df_coef = df_coef.reindex(df_coef["Coefficient"].abs().sort_values(ascending=False).index)

    st.markdown(f"### 🧠 {title}")
    st.caption("Larger absolute values usually mean a stronger effect on the prediction.")
    st.dataframe(df_coef[["Feature", "Coefficient"]].round(4), use_container_width=True, height=250)


def show_importances(feature_names, importances, title="Feature Importances"):
    # Tree-based models use feature importances instead of coefficients.
    df_imp = pd.DataFrame({
        "Feature": list(feature_names),
        "Importance": list(importances)
    }).sort_values("Importance", ascending=False)

    st.markdown(f"### 🌟 {title}")
    st.caption("Higher values indicate features the model relied on more heavily.")
    st.dataframe(df_imp.round(4), use_container_width=True, height=250)


def apply_scaling(X, key_suffix):
    # Standardize numeric features so they are centered and scaled.
    # This is most useful for linear and logistic regression.
    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns, index=X.index)
    st.info("📐 Numeric features were scaled using StandardScaler.")
    return X_scaled

# -----------------------------------------------------------------------------
# Main page content
# -----------------------------------------------------------------------------

# Main title and page instructions.
st.title("📈 Predictions")
st.markdown("Use your cleaned dataset to train a model and preview results.")

if "dataframe" not in st.session_state:
    # Stop here if the user has not loaded or cleaned a dataset yet.
    st.info("No dataset loaded yet. Go to the **Data Cleaning** page first.")
    st.stop()

# Pull the cleaned dataframe from session state.
df = st.session_state["dataframe"]

st.markdown("### 🎯 Step 1: Choose a Target Variable")
st.caption("The app will try to detect whether your problem is classification or regression.")

# The target is the column the user wants the model to predict.
target = st.selectbox("Target variable", df.columns)
target_series = df[target].dropna()

# Simple detection rule:
# non-numeric targets are treated as classification,
# and numeric targets with only a few unique values are usually classification too.
detected = "classification" if (not is_numeric_dtype(target_series) or target_series.nunique() <= 10) else "regression"

st.info(f"Detected problem type: **{detected.title()}**")

# Let the user keep the detected type or switch it manually.
problem_type = st.radio(
    "Keep the detected type or switch manually:",
    ["Classification", "Regression"],
    # index=0 means the first option (Classification) is selected if it's detected, otherwise index=1 selects Regression.
    index=0 if detected == "classification" else 1,
    horizontal=True
)

st.divider()

# Step 2 lets the user choose a model.
st.markdown("### 💻 Step 2: Choose a Model")

if problem_type == "Regression":
    # Regression currently uses Linear Regression only.
    model = "Linear Regression"
    st.success("Selected model: **Linear Regression**")
else:
    # Classification gives the user several model choices.
    model = st.selectbox(
        "Classification model",
        ["Logistic Regression", "Decision Tree Classifier", "XGBoost Classifier"]
    )

# Sidebar contains settings that depend on the selected model.
with st.sidebar:
    st.subheader("⚙️ Model Options")

    if model in ("Linear Regression", "Logistic Regression"):
        # Scaling matters most for linear and logistic regression.
        scale_data = st.toggle("Scale numeric features")
        st.caption("Helpful for linear and logistic regression.")
    else:
        # Tree-based models usually do not need scaling.
        scale_data = False
        st.caption("Scaling is only used for Linear / Logistic Regression.")

st.divider()

# -----------------------------------------------------------------------------
# Linear Regression
# -----------------------------------------------------------------------------
if model == "Linear Regression":
    st.markdown("## 📈 Linear Regression")
    st.caption("Best for predicting continuous numeric outcomes.")

    # Build the predictors and target based on user selections.
    # The prepare_model_data function handles the feature selection and dummy coding based on user inputs, 
    # returning the predictor matrix X and target vector y ready for modeling.
    prepared = prepare_model_data(df, target, "linear")


    if prepared:
        # X contains the predictor columns, and y contains the target column we are trying to predict.
        X, y = prepared

        st.markdown("### Missing Data Check")

        # Combine X and y so the missing-value check covers the full modeling dataset.
        mdf = pd.concat([X, y], axis=1)
        mdf, should_stop = handle_missing(mdf, target, "linear_missing")

        if should_stop:
            st.stop()

        # Split the combined dataframe back into predictors and target.
        X, y = mdf.drop(columns=[target]), mdf[target]

        st.markdown("### ⚙️ Training Settings")
        test_size = get_test_size("linear_test_size")

        # If the user chose to scale numeric features, we apply standard scaling to the predictor matrix X.
        if scale_data:
            X = apply_scaling(X, "linear")

        # Split the data into training and testing sets.
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=42
        )

        # Train the linear regression model.
        model_obj = LinearRegression().fit(X_train, y_train)

        # Show evaluation results and coefficients.
        # show_regression_results calculates and displays key regression metrics like MSE, RMSE, and R²,
        show_regression_results(y_test, model_obj.predict(X_test))
        # while show_coefficients displays the coefficients for each feature, indicating their influence on the predictions.
        show_coefficients(X.columns, model_obj.coef_, model_obj.intercept_)

        st.success("✅ Linear Regression model trained successfully.")

# -----------------------------------------------------------------------------
# Logistic Regression
# -----------------------------------------------------------------------------
elif model == "Logistic Regression":
    st.markdown("## 📊 Logistic Regression")
    st.caption("Best for classification problems with labeled categories.")

    # Build the predictors and target based on user selections.
    # The prepare_model_data function handles the feature selection and dummy coding based on user inputs, 
    # returning the predictor matrix X and target vector y ready for modeling.
    prepared = prepare_model_data(df, target, "logistic")

    if prepared:
        X, y = prepared

        st.markdown("### Missing Data Check")
        mdf = pd.concat([X, y], axis=1)
        mdf, should_stop = handle_missing(mdf, target, "logistic_missing")

        if should_stop:
            st.stop()

        X, y = mdf.drop(columns=[target]), mdf[target]

        # Logistic regression needs at least two target classes.
        if y.nunique() < 2:
            st.warning("Logistic Regression needs at least two target classes.")
            st.stop()

        st.markdown("### ⚙️ Training Settings")
        test_size = get_test_size("logistic_test_size")

        if scale_data:
            X = apply_scaling(X, "logistic")

        # stratify=y keeps the class balance similar in train and test sets.
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=42,
            stratify=y
        )

        # Train the logistic regression model.
        # max_iter=1000 allows more iterations for convergence, which can be helpful for complex datasets.
        model_obj = LogisticRegression(max_iter=1000).fit(X_train, y_train)

        y_pred = model_obj.predict(X_test)

        # For binary classification, probabilities are used to draw the ROC curve.
        y_score = model_obj.predict_proba(X_test)[:, 1] if y.nunique() == 2 else None
        show_classification_results(y_test, y_pred, y_score)

        # Binary logistic regression has one coefficient row.
        # Multiclass logistic regression has one row per class, so this shows averages.
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

# -----------------------------------------------------------------------------
# Decision Tree Classifier
# -----------------------------------------------------------------------------
elif model == "Decision Tree Classifier":
    st.markdown("## 🌳 Decision Tree Classifier")
    st.caption("Useful for interpretable classification models with branching logic.")

    # Build the predictors and target based on user selections.
    prepared = prepare_model_data(df, target, "tree_clf")

    if prepared:
        X, y = prepared

        st.markdown("### Missing Data Check")
        mdf = pd.concat([X, y], axis=1)
        mdf, should_stop = handle_missing(mdf, target, "tree_missing")

        if should_stop:
            st.stop()

        # Split the combined dataframe back into predictors and target after handling missing values.
        X, y = mdf.drop(columns=[target]), mdf[target]

        # A classifier still needs at least two target classes.
        if y.nunique() < 2:
            st.warning("Decision Tree needs at least two target classes.")
            st.stop()

        st.markdown("### ⚙️ Training Settings")
        test_size = get_test_size("tree_clf_test_size")

        # max_depth controls how complex the tree is allowed to become.
        max_depth = st.slider("🌲 Max depth", 1, 15, 3, key="tree_clf_depth")

        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=42,
            stratify=y
        )

        # Train the decision tree classifier.
        model_obj = DecisionTreeClassifier(max_depth=max_depth, random_state=42).fit(X_train, y_train)

        y_pred = model_obj.predict(X_test)
        y_score = model_obj.predict_proba(X_test)[:, 1] if y.nunique() == 2 else None
        show_classification_results(y_test, y_pred, y_score)
        show_importances(X.columns, model_obj.feature_importances_)

        st.success("✅ Decision Tree model trained successfully.")

# -----------------------------------------------------------------------------
# XGBoost Classifier
# -----------------------------------------------------------------------------
elif model == "XGBoost Classifier":
    st.markdown("## ⚡ XGBoost Classifier")
    st.caption("A powerful boosting model for classification tasks.")

    # Build the predictors and target based on user selections.
    prepared = prepare_model_data(df, target, "xgb_clf")

    if prepared:
        X, y = prepared

        # XGBoost can usually still run with missing predictor values,
        # so the user is informed instead of being forced to drop rows.
        missing = int(pd.concat([X, y], axis=1).isnull().any(axis=1).sum())
        if missing:
            st.info(f"ℹ️ {missing} rows have missing values. XGBoost can usually still run without dropping them first.")

        if y.nunique() < 2:
            st.warning("XGBoost needs at least two target classes.")
            st.stop()

        # XGBoost expects numeric class labels, so convert text labels to integers.
        # LabelEncoder is used to convert the target variable y into numeric labels that XGBoost can work with.
        le = LabelEncoder()
        y_enc = le.fit_transform(y)

        st.markdown("### ⚙️ Training Settings")
        test_size = get_test_size("xgb_clf_test_size")

        # These sliders let the user experiment with model complexity.
        n_estimators = st.slider("🌲 Number of trees", 50, 300, 100, step=25, key="xgb_clf_estimators")
        max_depth = st.slider("📏 Max depth", 1, 10, 3, key="xgb_clf_depth")

        X_train, X_test, y_train, y_test = train_test_split(
            X, y_enc,
            test_size=test_size,
            random_state=42,
            stratify=y_enc
        )

        # Train the XGBoost classifier.
        model_obj = XGBClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=42
        ).fit(X_train, y_train)

        y_pred = model_obj.predict(X_test)

        # Convert the encoded predictions back to the original class names for display.
        y_pred_labels = pd.Series(le.inverse_transform(y_pred))
        y_test_labels = pd.Series(le.inverse_transform(y_test))
        y_score = model_obj.predict_proba(X_test)[:, 1] if len(le.classes_) == 2 else None
        show_classification_results(y_test_labels, y_pred_labels, y_score)
        show_importances(X.columns, model_obj.feature_importances_)

        st.success("✅ XGBoost model trained successfully.")
