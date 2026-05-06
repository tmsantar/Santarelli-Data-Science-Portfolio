import streamlit as st

# Similar to singular markdown hashtag - creates a large header text
st.title("Hello, Streamlit!")
st.markdown("# Hello, Streamlit!")

st.write("This is my first Streamlit app.")

if st.button("Click Me!"):
    st.write("You clicked the button!")
else:
    st.write("Click the button and see what happens!.")

### Loading our CSV file and displaying it in a table

import pandas as pd

st.subheader("Exploring our Dataset")

# Load in the CSV file
df = pd.read_csv("data/sample_data-1.csv")


st.write("Here's our data!")
st.dataframe(df)

city = st.selectbox("Select a city", df["City"].unique(), index=None)
filtered_df = df[df["City"] == city]

st.write(f"People in {city}")
st.dataframe(filtered_df)

## Add bar chart
st.bar_chart(df["Salary"])

import seaborn as sns
import matplotlib.pyplot as plt

st.subheader("Salary Distribution by City")
box_plot1 = sns.boxplot(x="City", y="Salary", data=df)
plt.title("Salary Distribution by City")
st.pyplot(box_plot1.get_figure())