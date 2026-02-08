import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="NFL Receiving Stats Explorer", 
    page_icon="🏈", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load the dataset (cached for performance)
@st.cache_data
def load_data():
    return pd.read_csv("data/nextgen_receiving_stats.csv")

receiving_df = load_data()

# Sidebar content
with st.sidebar:    
    # Social links
    st.markdown("### Connect")
    st.markdown(
        """
        <a href="https://www.linkedin.com/in/tommy-santarelli-792651329/" target="_blank" style="text-decoration: none;">
            <span style="font-size: 1.1rem;">🔗 LinkedIn</span>
        </a>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <a href="https://github.com/tmsantar" target="_blank" style="text-decoration: none;">
            <span style="font-size: 1.1rem;">🐙 GitHub</span>
        </a>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    st.markdown("Built by **Tommy Santarelli**")
    st.caption("Business Analytics Major at Notre Dame")

# Main page content
st.title("NFL Receiving Stats Explorer 🏈")

st.write("""
### About This Dashboard

Explore comprehensive receiving statistics for NFL players from the 2025 regular season using **NFL Next Gen Stats** tracking data.

Next Gen Stats uses real-time location data captured by sensors throughout the stadium that track tags on players' shoulder pads, measuring speed, acceleration, and positioning within inches on every play.
""")

st.markdown("***")

# Dataset overview section
st.subheader("Dataset Overview")
col1, col2, col3 = st.columns(3)

total_players = receiving_df[receiving_df['Week'] == 0]['Player Name'].nunique()
with col1:
    st.metric("👥 Total Players", total_players)
with col2:
    st.metric("📅 Total Weeks", 18)
with col3:
    st.metric("📊 Next Gen Stats Tracked", 12)

st.markdown("***")

st.subheader("Available Statistics")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Basic Stats:**")
    st.write("- **🎯 Yards**: Total receiving yards")
    st.write("- **👀 Targets**: Number of times the player was targeted")
    st.write("- **✋ Receptions**: Number of successful catches")
    st.write("- **🔥 Receiving Touchdowns**: Touchdowns scored from receptions")
    st.write("- **📈 Catch Percentage**: Percentage of targets that resulted in catches")

with col2:
    st.markdown("**Next Gen Advanced Metrics:**")
    st.write("- **📏 Avg Cushion**: Average distance (yards) between WR/TE and defender at snap")
    st.write("- **🏃 Avg Separation**: Average distance (yards) between WR/TE and nearest defender at catch")
    st.write("- **✈️ Avg Intended Air Yards**: Average air yards on all targets")
    st.write("- **📊 Share of Intended Air Yards (%)**: Percentage of team's total intended air yards")
    st.write("- **💨 Avg Yards After Catch**: Average yards gained after the catch")
    st.write("- **📈 Avg Expected YAC**: Expected yards after catch based on tracking data")
    st.write("- **⚡ YAC Above Expectation**: Actual YAC compared to Expected YAC")

st.markdown("***")

st.subheader("Available Pages")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📈 Season Stats")
    st.write("View full season statistics and top 10 performers. Filter by player, team, or position.")

with col2:
    st.markdown("### 📅 Weekly Stats")
    st.write("Analyze week-by-week performance throughout the season with advanced filtering.")

with col3:
    st.markdown("### 🎯 Advanced Stats")
    st.write("Compare up to 2 players with interactive radar charts using Next Gen metrics.")

st.markdown("***")

st.info("👈 Use the sidebar to navigate between pages and start exploring the data!")