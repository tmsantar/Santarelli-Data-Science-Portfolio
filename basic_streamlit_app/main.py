import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

st.title("NFL Receiving Stats Explorer")

st.write("Explore the regular season statistics of NFL wide receivers, " \
"tight ends, running backs, and full backs from the 2025 season.")

st.write("Here is our NFL receiving stats dataset:")

receiving_df = pd.read_csv("data/sportsref_download_wr_data.csv")
# Filter to only include relevant positions
receiving_df = receiving_df[receiving_df["Pos"].isin(["WR", "TE", "RB", "FB"])]
# Remove index and change Rk columns to PFR Rank
# Clean other column names as well
receiving_df = receiving_df.drop(columns=["Unnamed: 0"]).rename(columns={
    "Rk": "PFR Rank", "Tm": "Team", "Yds": "Receiving Yards", "TD": "Receiving TDs",  "Rec": "Receptions", 
    "Y/R": "Yards per Reception", "Y/G": "Yards per Game"})

st.dataframe(receiving_df)
