# Machine Learning Streamlit App

Interactive Streamlit application for supervised machine learning. Users can upload their own CSV files or choose from sample datasets, clean the data, select a target variable, train a model, adjust settings, and review model performance.

## Project Overview

The goal of this project is to give users a simple, hands-on way to explore supervised machine learning. The app is designed to walk users through a practical workflow:

1. Load a dataset
2. Clean missing values and inspect data types
3. Choose a target variable
4. Select a model
5. Adjust model settings and preprocessing options
6. Review training results and model evaluation

The app currently supports both regression and classification tasks depending on the selected target variable.

## Live App

Add your deployed Streamlit Community Cloud URL here:

`PASTE_DEPLOYED_APP_URL_HERE`

## Features

### Data Cleaning Page

- Upload a CSV file or choose a sample dataset
- View the current working dataset
- Inspect column data types, non-null counts, and missing values
- Apply multiple cleaning steps in sequence
- Reset back to the original dataset at any time
- Handle missing data by:
  - dropping rows
  - dropping rows for specific missing variables
  - dropping columns with more than 50% missing values
  - dropping selected columns
  - filling numeric columns with mean, median, or zero

### Predictions Page

- Automatically detect whether the target looks like a regression or classification problem
- Allow the user to keep the detected problem type or switch it manually
- Select predictor columns
- Optionally include categorical predictors through dummy coding
- Optionally scale numeric features for linear and logistic regression
- Train and evaluate multiple supervised learning models

## Models Used

### Regression

- Linear Regression

### Classification

- Logistic Regression
- Decision Tree Classifier
- XGBoost Classifier

## Model Settings and Hyperparameters

Users can experiment with model behavior through Streamlit widgets.

### Shared Settings

- test set size
- input variable selection
- target variable selection
- optional dummy coding for categorical predictors

### Linear Regression

- optional feature scaling with `StandardScaler`

### Logistic Regression

- optional feature scaling with `StandardScaler`

### Decision Tree Classifier

- max depth

### XGBoost Classifier

- number of trees
- max depth

## Evaluation Metrics

### Regression Metrics

- Mean Squared Error (MSE)
- Root Mean Squared Error (RMSE)
- R-squared Score
- actual vs predicted table
- feature coefficient table with intercept

### Classification Metrics

- Accuracy
- Precision
- Recall
- F1 Score
- Confusion Matrix
- ROC Curve and AUC for binary classification
- actual vs predicted table
- feature importance or coefficient output depending on the model

## How to Run Locally

1. Open a terminal in the portfolio repository.
2. Move into the app folder:

```powershell
cd MLStreamlitApp
```

3. Install the required libraries:

```powershell
pip install -r requirements.txt
```

4. Run the app:

```powershell
streamlit run main.py
```

5. Open the local URL shown in the terminal, usually:

`http://localhost:8501`

## Required Libraries

These are the main libraries used by the app:

- `streamlit==1.53.0`
- `pandas==2.3.3`
- `matplotlib==3.10.8`
- `scikit-learn==1.8.0`
- `xgboost==3.2.0`

## Project Structure

```text
MLStreamlitApp/
|-- main.py
|-- README.md
|-- requirements.txt
|-- data/
|-- pages/
|   |-- 1_Data_Cleaning.py
|   |-- 2_Predictions.py
```

## References

These course notebooks helped guide the models and app logic used in this project:

- [Week 7: Linear Regression](../Week%207/IDS_Week_7_FINAL.ipynb)
- [Week 9: Logistic Regression](../Week%209/IDS%20Week%209_1_FINAL.ipynb)
- [Week 9: Decision Tree Classifier](../Week%209/IDS%20Week%209_2_FINAL.ipynb)
- [Week 10: XGBoost Classifier](../Week%2010/IDS%20Week%2010_1_FINAL.ipynb)

## Visual Examples

Add screenshots here before submitting. Good options would be:

- the Data Cleaning page
- the Predictions page with model metrics
- a confusion matrix and ROC curve example
- a decision tree diagram

Placeholder section:

`INSERT_SCREENSHOT_1_HERE`

`INSERT_SCREENSHOT_2_HERE`

`INSERT_SCREENSHOT_3_HERE`

## Author

Tommy Santarelli  
Business Analytics Major, University of Notre Dame
