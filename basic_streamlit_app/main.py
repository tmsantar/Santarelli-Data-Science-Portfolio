import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="NFL Receiving Stats Explorer", page_icon="🏈", layout="wide")

# Custom CSS for styling
st.markdown(
    """
    <style>
        .footer {
            margin-top: 2.5rem;
            padding-top: 1.2rem;
            border-top: 1px solid rgba(148,163,184,0.35);
            font-size: 0.9rem;
            color: #666;
        }
        .footer a {
            color: #0066cc;
            text-decoration: none;
            margin-right: 1rem;
        }
        .footer a:hover {
            text-decoration: none;
        }
        .social-icon {
            vertical-align: middle;
            margin-right: 0.30rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Load the dataset (cached for performance)
@st.cache_data
def load_data():
    return pd.read_csv("data/nextgen_receiving_stats.csv")

receiving_df = load_data()

# Main page content
st.title("NFL Receiving Stats Explorer 🏈")

st.header("Welcome to the NFL Receiving Stats Explorer!")

st.write("""
### About This Dataset:

This application allows you to explore comprehensive receiving statistics for NFL players 
from the 2025 regular season using **NFL Next Gen Stats** tracking data. The data includes 
performance metrics for wide receivers and tight ends.

Next Gen Stats uses real-time location data captured by sensors throughout the stadium 
that track tags on players' shoulder pads, measuring speed, acceleration, and positioning 
within inches on every play.

#### 📊 Available Statistics:

**Basic Stats:**
- **🎯 Yards**: Total receiving yards
- **👀 Targets**: Number of times the player was targeted
- **✋ Receptions**: Number of successful catches
- **🔥 Receiving Touchdowns**: Touchdowns scored from receptions
- **📈 Catch Percentage**: Percentage of targets that resulted in catches

**Next Gen Advanced Metrics:**
- **📏 Avg Cushion**: Average distance (in yards) between WR/TE and defender at snap on all targets
- **🏃 Avg Separation**: Average distance (in yards) between WR/TE and nearest defender at time of catch/incompletion
- **✈️ Avg Intended Air Yards**: Average air yards on all passing attempts where the receiver is targeted
- **📊 Share of Intended Air Yards (%)**: Percentage of team's total intended air yards
- **💨 Avg Yards After Catch**: Average yards gained after the catch
- **📈 Avg Expected YAC**: Expected yards after catch based on tracking data (openness, speed, defenders in space)
- **⚡ YAC Above Expectation**: Actual YAC compared to Expected YAC
""")

st.markdown("***")

st.header("Applications:")

st.subheader("1) Season Stats 📈")
col1_1, col1_2 = st.columns([1, 3])
with col1_1:
    st.markdown("📊")
with col1_2:
    st.markdown("###### View full season statistics and top 10 performers")
    st.markdown("###### Filter by player, team, or position to analyze season-long performance")

st.subheader("2) Weekly Stats 📅")
col2_1, col2_2 = st.columns([1, 3])
with col2_1:
    st.markdown("📆")
with col2_2:
    st.markdown("###### Analyze week-by-week performance throughout the season")
    st.markdown("###### Compare players across specific weeks with advanced filtering")

st.subheader("3) Advanced Stats 🎯")
col3_1, col3_2 = st.columns([1, 3])
with col3_1:
    st.markdown("⚔️")
with col3_2:
    st.markdown("###### Compare up to 2 players with interactive radar charts using Next Gen metrics")
    st.markdown("###### Customize which statistics to compare for deeper analysis")

st.markdown("***")

# Dataset overview section
st.subheader("📋 Dataset Overview")
col1, col2, col3 = st.columns(3)

total_players = receiving_df[receiving_df['Week'] == 0]['Player Name'].nunique()
with col1:
    st.metric("👥 Total Players", total_players)
with col2:
    st.metric("📅 Total Weeks", 18)
with col3:
    st.metric("📊 Next Gen Stats Tracked", 12)

st.markdown("***")

st.markdown("#### 🚀 How to Use:")
st.markdown("""
1. Use the sidebar to navigate between pages (👈 look left!)
2. Select **Season Stats** or **Weekly Stats** for performance data with player/team filtering
3. Select **Advanced Stats** for detailed player comparisons with Next Gen metrics
4. Each page includes interactive filters to customize your view
5. Use the dataframe search boxes to filter by specific players or teams
""")

# Footer
st.markdown(
    """
    <div class="footer">
        <div>
            Built by <strong>Tommy Santarelli</strong> — Business Analytics Major at Notre Dame<br/>
            This dashboard is powered by NFL Next Gen Stats dataset saved to
            <code>data/nextgen_receiving_stats.csv</code>.
        </div>
        <br/>
        <div>
            <a href="https://www.linkedin.com/in/tommy-santarelli-792651329/" target="_blank">
                <span class="social-icon">🔗</span>LinkedIn
            </a>
            <a href="https://github.com/tmsantar" target="_blank">
                <span class="social-icon">🐙</span>GitHub
            </a>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)