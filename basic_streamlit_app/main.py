from pathlib import Path

import pandas as pd
import streamlit as st


DATA_FILE = Path(__file__).parent / "data" / "nextgen_receiving_stats.csv"
IMAGE_FILE = Path(__file__).parent / "images" / "Next_Gen_Logo.jpg"

# Set page configuration which gives the browser tab a title and icon, and sets the layout to wide.
st.set_page_config( page_title="NFL Receiving Stats Explorer", page_icon="🏈", layout="wide")

# Load data in a cached function for performance
@st.cache_data
def load_data():
    return pd.read_csv(DATA_FILE)

receiving_df = load_data()

# Sidebar content
with st.sidebar:   

    # About me portion of the sidebar with links to LinkedIn and GitHub
    st.markdown("Built by **Tommy Santarelli**")
    st.caption("Business Analytics Major at Notre Dame")
    st.markdown("🔗 [LinkedIn](https://www.linkedin.com/in/tommy-santarelli-792651329/)")
    st.markdown("🐙 [GitHub](https://github.com/tmsantar)")
    st.markdown("---")

    # Description of where the data is sourced from
    st.markdown("The dataset used is sourced from the [NFL Next Gen Stats]"
    "(https://nextgenstats.nfl.com/stats/receiving#yards) for the 2025 regular season.")

# Header section with title and logo
col1, col2 = st.columns([3, 1])
with col1:
    st.title("NFL Receiving Stats Explorer 🏈")
with col2:
    st.image(str(IMAGE_FILE), width="stretch")

# Introduction and app description
st.write("""
### About This App

Explore NFL receiving statistics for wide receivers and tight ends during 2025 regular season using **NFL Next Gen Stats**.

Next Gen Stats uses real-time player tracking to capture detailed movement and positioning data throughout each game. This dataset only includes players who recorded at least 45 targets during the 2025 regular season.
""")

st.markdown("---")

# Dataset overview section with broad statistics about the dataset
st.subheader("Dataset Overview")
col1, col2, col3 = st.columns(3)

total_players = receiving_df[receiving_df['Week'] == 0]['Player Name'].nunique()
with col1:
    st.metric("👥 Total Players", total_players)
with col2:
    st.metric("📅 Total Weeks", 18)
with col3:
    st.metric("📊 Next Gen Stats Tracked", 12)

st.markdown("---")

# Available statistics section with descriptions of the different stats available in the dataset
st.subheader("Available Statistics")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Basic Stats:**")
    st.write("- **🎯 Yards**: Total receiving yards")
    st.write("- **👀 Targets**: Number of times the player was targeted")
    st.write("- **✋ Receptions**: Number of successful catches")
    st.write("- **🔥 Receiving Touchdowns**: Touchdowns scored from receptions")
    st.write("- **💯 Catch Percentage**: Percentage of targets that resulted in catches")

with col2:
    st.markdown("**Next Gen Stats:**")
    st.write("- **📏 Avg Cushion**: Average distance (yards) between WR/TE and defender at snap")
    st.write("- **🏃 Avg Separation**: Average distance (yards) between WR/TE and nearest defender at catch")
    st.write("- **✈️ Avg Intended Air Yards**: Average air yards on all targets")
    st.write("- **📊 Share of Intended Air Yards (%)**: Percentage of team's total intended air yards")
    st.write("- **💨 Avg Yards After Catch**: Average yards gained after the catch")
    st.write("- **📈 Avg Expected YAC**: Expected yards after catch based on tracking data")
    st.write("- **⚡ YAC Above Expectation**: Actual YAC compared to Expected YAC")

st.markdown("---")

# Available pages section with descriptions of the different pages available in the app
st.subheader("Available Pages")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📈 Season Stats")
    st.write("View full season statistics and top 10 performers. Filter by player, team, or position.")

with col2:
    st.markdown("### 📅 Weekly Stats")
    st.write("Analyze week-by-week performance throughout the season with advanced filtering.")

col3, col4 = st.columns(2)

with col3:
    st.markdown("### 🎯 Advanced Stats")
    st.write("Compare up to 2 players with interactive radar charts using Next Gen metrics.")

with col4:
    st.markdown("### 🧬 Similar Player Tool")
    st.write("Find the top 3 most similar players for any receiver using standardized stats and profile matching.")

st.markdown("---")

# Final note encouraging users to explore the app
st.info("👈 Use the sidebar to navigate between pages and start exploring the data!")
