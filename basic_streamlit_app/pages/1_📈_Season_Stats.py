import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Set page configuration which gives the browser tab a title and icon, and sets the layout to wide.
st.set_page_config(page_title="Season Stats", page_icon="📈", layout="wide")

# Load data in a cached function for performance
@st.cache_data
def load_data():
    return pd.read_csv("data/nextgen_receiving_stats.csv")

receiving_df = load_data()

st.header("📈 Season Statistics")

# Filter for season stats (Week 0 in the dataset represents season totals)
season_data = receiving_df[receiving_df['Week'] == 0].copy()

# Drop unnecessary columns for season stats
columns_to_drop = ['Season', 'Season Type', 'Week', 'Player GSIS ID']
season_data_clean = season_data.drop(columns=[col for col in columns_to_drop if col in season_data.columns])

# Create filters for season stats
st.subheader("🎯 Filters")

col1, col2, col3 = st.columns(3)

with col1:
    stat_column = st.selectbox(
        "Select Stat for Top 10",
        ['Yards', 'Targets', 'Receptions', 'Receiving Touchdowns', 'Catch Percentage', 
         'Avg Yards After Catch', 'YAC Above Expectation', 'Avg Cushion', 'Avg Separation',
         'Avg Intended Air Yards', 'Share of Intended Air Yards (%)', 'Avg Expected YAC'],
        key="season_stat"
    )

with col2:
    # Team filter
    all_teams = ['All Teams'] + sorted(season_data['Team Abbreviation'].unique().tolist())
    selected_team = st.selectbox(
        "Filter by Team",
        options=all_teams,
        key="season_team_filter"
    )

with col3:
    # Position filter
    all_positions = ['All Positions'] + sorted(season_data['Position'].unique().tolist())
    selected_position = st.selectbox(
        "Filter by Position",
        options=all_positions,
        key="season_position_filter"
    )

# Apply filters when user selects them
filtered_data = season_data_clean.copy()
if selected_team != 'All Teams':
    filtered_data = filtered_data[filtered_data['Team Abbreviation'] == selected_team]
if selected_position != 'All Positions':
    filtered_data = filtered_data[filtered_data['Position'] == selected_position]

st.markdown("---")

# Top 10 Bar Chart for the selected stat
top_10_data = filtered_data.nlargest(10, stat_column)

# Create a bar chart using seaborn
if len(top_10_data) > 0:
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = sns.color_palette("viridis", len(top_10_data))
    sns.barplot(x='Player Name', y=stat_column, data=top_10_data, ax=ax, palette=colors)
    
    # Add filter information to the title
    filter_text = ""
    if selected_team != 'All Teams':
        filter_text += f" - {selected_team}"
    if selected_position != 'All Positions':
        filter_text += f" - {selected_position}"
    
    # Set title and labels of the chart
    ax.set_title(f"Top {len(top_10_data)} Players Based on {stat_column}{filter_text}", fontsize=16, fontweight='bold')
    ax.set_xlabel("Player Name", fontsize=12)
    ax.set_ylabel(stat_column, fontsize=12)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)
else:
    st.warning("No data available for the selected filters.")

st.markdown("---")

# Display full season dataframe
st.subheader("Complete Season Statistics")

col1, col2 = st.columns(2)

with col1:
    # Add searchable dropdown for a specific player
    all_players = ['All Players'] + sorted(season_data_clean['Player Name'].unique().tolist())
    selected_player = st.selectbox(
        "🔍 Search or Select Player", 
        options=all_players,
        index=0,
        key="season_search"
    )

with col2:
    # Add team filter for dataframe
    all_teams_df = ['All Teams'] + sorted(season_data_clean['Team Abbreviation'].unique().tolist())
    selected_team_df = st.selectbox(
        "Filter by Team",
        options=all_teams_df,
        key="season_team_df_filter"
    )

# Reorder columns for better display
priority_cols = ['Player Name', 'Position', 'Team Abbreviation', 'Yards', 'Targets', 
                'Receptions', 'Receiving Touchdowns', 'Catch Percentage']
other_cols = [col for col in season_data_clean.columns if col not in priority_cols]
ordered_cols = priority_cols + other_cols
season_data_display = season_data_clean[ordered_cols]

# Filter by selected player
if selected_player != 'All Players':
    season_data_display = season_data_display[
        season_data_display['Player Name'] == selected_player
    ]

# Filter by selected team
if selected_team_df != 'All Teams':
    season_data_display = season_data_display[
        season_data_display['Team Abbreviation'] == selected_team_df
    ]

st.dataframe(season_data_display, hide_index=True, width="stretch", height=600)

# Stats summary for 2025 season
st.markdown("---")
st.subheader(f"📈 2025 Season Summary")

col1, col2, col3, col4 = st.columns(4)

# Use the displayed data for summary stats
summary_data = season_data_display

with col1:
    st.metric("🎯 Total Yards", f"{summary_data['Yards'].sum():,.0f}")
with col2:
    st.metric("✋ Total Receptions", f"{summary_data['Receptions'].sum():,.0f}")
with col3:
    st.metric("🔥 Total TDs", f"{summary_data['Receiving Touchdowns'].sum():,.0f}")
with col4:
    avg_catch_pct = summary_data['Catch Percentage'].mean()
    st.metric("📈 Avg Catch %", f"{avg_catch_pct:.1f}%")