# 🧠 Unsupervised Learning Streamlit App

Interactive Streamlit application for exploring unsupervised machine learning. Users can upload their own CSV file or choose from curated sample datasets, clean the data, select numeric features, and explore hidden patterns using K-Means clustering, hierarchical clustering, and Principal Component Analysis.

![Unsupervised Learning](images/unsupervised.png)

---

## 📌 Project Overview

The goal of this project is to give users a hands-on way to explore unsupervised learning without needing to write code. Instead of predicting a target variable, this app focuses on discovering structure in data.

The app walks users through a practical workflow:

1. 📂 Load a dataset
2. 🧹 Review and clean missing values
3. 🔢 Select numeric features
4. 🧠 Choose an unsupervised learning method
5. ⚙️ Adjust model settings
6. 📊 Interpret clusters, PCA plots, silhouette scores, elbow plots, and dendrograms

This project currently supports **K-Means clustering**, **hierarchical clustering**, and **PCA**.

---

## ✨ Features

### 🧹 Data Cleaning Page

- Upload a CSV file or choose from five sample datasets
- View the current working dataset
- Inspect column data types, non-null counts, and missing values
- Apply cleaning steps one at a time
- Reset back to the original dataset
- Handle missing data by:
  - Dropping rows
  - Dropping rows for specific missing variables
  - Dropping columns with more than 50% missing values
  - Dropping selected columns
  - Filling numeric columns with mean, median, or zero

### 📈 Unsupervised Learning Lab

- Choose between K-Means clustering, hierarchical clustering, and PCA
- Select numeric features for analysis
- Optionally scale numeric variables with `StandardScaler`
- Compare cluster counts using elbow plots and silhouette plots
- View cluster assignments and cluster sizes
- Visualize clusters with PCA scatter plots
- Build dendrograms for hierarchical clustering
- Choose dendrogram labels, such as country names or row numbers
- View explanations below each graph to help interpret results

---

## 📂 Sample Datasets

The app includes five sample datasets so users can test different unsupervised learning methods quickly.

- **Country Democracy Indicators**  
  Best for hierarchical clustering because the dendrogram can show how countries group together based on democracy, election, and government-structure features.

- **Breast Cancer Measurements**  
  Good for all three methods: PCA, K-Means, and hierarchical clustering. The dataset has many numeric medical measurement columns.

- **Soccer Injury Risk**  
  Good for K-Means and PCA because users can look for player risk profiles based on training, fitness, recovery, and injury-related variables.

- **Gaming and Academic Performance**  
  Good for K-Means and PCA because it includes many behavior-based numeric features related to gaming, studying, wellness, and grades.

- **Teen Mental Health**  
  Good for all three methods because users can explore wellness-related groups and patterns using screen time, sleep, stress, activity, and mental-health indicators.

---

## 🧠 Methods Used

### K-Means Clustering

K-Means separates rows into a selected number of clusters. The app lets users compare different values of `k` with an elbow plot and a silhouette plot before viewing the final cluster assignments.

### Hierarchical Clustering

Hierarchical clustering builds groups step by step and displays the structure in a dendrogram. Users can choose the linkage method and decide how many clusters to create.

### Principal Component Analysis

PCA reduces many numeric features into fewer principal components. The app shows explained variance, a PCA scatter plot, and the transformed PCA dataframe.

---

## 📊 Visual Outputs

The app includes several visual tools:

- Elbow plots for comparing cluster counts
- Silhouette plots for evaluating cluster separation
- PCA scatter plots for visualizing rows in two dimensions
- Dendrograms for hierarchical clustering structure
- PCA explained variance bar charts

Each graph includes a short explanation below it so users can understand what the visual is showing.

---

## 🚀 How to Run Locally

1. Open a terminal in the portfolio repository.
2. Move into the app folder:

```powershell
cd MLUnsupervisedApp
```

3. Install the required libraries:

```powershell
pip install streamlit pandas numpy matplotlib scikit-learn scipy
```

4. Run the app:

```powershell
streamlit run main.py
```

5. Open the local URL shown in the terminal, usually:

`http://localhost:8501`

---

## 📦 Required Libraries

These are the main libraries used by the app:

- `streamlit`
- `pandas`
- `numpy`
- `matplotlib`
- `scikit-learn`
- `scipy`

---

## 📚 References

These course notebooks helped guide the unsupervised learning methods used in this project:

- [Week 12: PCA](../Week%2012/IDS_12_2_IN_CLASS.ipynb)
- [Week 13: Hierarchical Clustering](../Week%2013/IDS_13_2_IN_CLASS.ipynb)

---

## 👨‍💻 Author

**Tommy Santarelli**  
Business Analytics Major, University of Notre Dame

- LinkedIn: [Tommy Santarelli](https://www.linkedin.com/in/tommy-santarelli-792651329/)
- GitHub: [@tmsantar](https://github.com/tmsantar)
