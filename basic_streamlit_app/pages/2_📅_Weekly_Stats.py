import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Set page configuration which gives the browser tab a title and icon, and sets the layout to wide.
st.set_page_config(page_title="Weekly Stats", page_icon="📅", layout="wide")

# Load data in a cached function for performance
@st.cache_data
def load_data():
    return pd.read_csv("data/nextgen_receiving_stats.csv")

receiving_df = load_data()

st.header("📅 Weekly Statistics")

# Create filters for weekly stats
st.subheader("🎯 Filters")

col1, col2, col3 = st.columns(3)

with col1:
    week = st.slider("Select Week 📆", min_value=1, max_value=18, value=1, key="weekly_week")

with col2:
    weekly_stat_column = st.selectbox(
        "Select Stat for Top 10",
        ['Yards', 'Targets', 'Receptions', 'Receiving Touchdowns', 'Catch Percentage', 
         'Avg Yards After Catch', 'YAC Above Expectation', 'Avg Cushion', 'Avg Separation',
         'Avg Intended Air Yards', 'Share of Intended Air Yards (%)', 'Avg Expected YAC'],
        key="weekly_stat"
    )

# Get week data for the selected week
week_data = receiving_df[receiving_df['Week'] == week].copy()


with col3:
    # Position filter
    all_positions = ['All Positions'] + sorted(week_data['Position'].unique().tolist())
    selected_position = st.selectbox(
        "Filter by Position",
        options=all_positions,
        key="weekly_position_filter"
    )

# Drop unnecessary columns
columns_to_drop = ['Season', 'Season Type', 'Week', 'Player GSIS ID']
week_data_clean = week_data.drop(columns=[col for col in columns_to_drop if col in week_data.columns])

# Apply filters when user selects them
filtered_data = week_data_clean.copy()
if selected_position != 'All Positions':
    filtered_data = filtered_data[filtered_data['Position'] == selected_position]

st.markdown("---")

# Top 10 Bar Chart for the selected stat and week
top_10_weekly = filtered_data.nlargest(10, weekly_stat_column)

# Create a bar chart using seaborn
if len(top_10_weekly) > 0:
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = sns.color_palette("rocket", len(top_10_weekly))
    sns.barplot(x='Player Name', y=weekly_stat_column, data=top_10_weekly, ax=ax, palette=colors)
    
    # Add filter information to the title
    filter_text = ""
    if selected_position != 'All Positions':
        filter_text += f" - {selected_position}"

    # Set title and labels of the chart    
    ax.set_title(f"Top {len(top_10_weekly)} Players in Week {week} Based on {weekly_stat_column}{filter_text}", 
                 fontsize=16, fontweight='bold')
    ax.set_xlabel("Player Name", fontsize=12)
    ax.set_ylabel(weekly_stat_column, fontsize=12)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)
else:
    st.warning("No data available for the selected filters.")

st.markdown("---")

# Display full weekly dataframe
st.subheader(f"Complete Week {week} Statistics")

col1, col2 = st.columns(2)

with col1:
    # Add searchable dropdown for a specific player
    all_players = ['All Players'] + sorted(week_data_clean['Player Name'].unique().tolist())
    selected_player = st.selectbox(
        "🔍 Search or Select Player", 
        options=all_players,
        index=0,
        key="weekly_search"
    )

with col2:
    # Add team filter for dataframe
    all_teams_df = ['All Teams'] + sorted(week_data_clean['Team Abbreviation'].unique().tolist())
    selected_team_df = st.selectbox(
        "Filter by Team",
        options=all_teams_df,
        key="weekly_team_df_filter"
    )

# Reorder columns for better display
priority_cols = ['Player Name', 'Position', 'Team Abbreviation', 'Yards', 'Targets', 
                'Receptions', 'Receiving Touchdowns', 'Catch Percentage']
other_cols = [col for col in week_data_clean.columns if col not in priority_cols]
ordered_cols = [col for col in priority_cols if col in week_data_clean.columns] + other_cols
week_data_display = week_data_clean[ordered_cols]

# Filter by selected player
if selected_player != 'All Players':
    week_data_display = week_data_display[
        week_data_display['Player Name'] == selected_player
    ]

# Filter by selected team
if selected_team_df != 'All Teams':
    week_data_display = week_data_display[
        week_data_display['Team Abbreviation'] == selected_team_df
    ]

st.dataframe(week_data_display, hide_index=True, width="stretch", height=600)

# Stats summary for the selected week
st.markdown("---")
st.subheader(f"📅 Week {week} Summary")

col1, col2, col3, col4 = st.columns(4)

# Use the displayed data for summary stats
summary_data = week_data_display

with col1:
    st.metric("🎯 Total Yards", f"{summary_data['Yards'].sum():,.0f}")
with col2:
    st.metric("✋ Total Receptions", f"{summary_data['Receptions'].sum():,.0f}")
with col3:
    st.metric("🔥 Total TDs", f"{summary_data['Receiving Touchdowns'].sum():,.0f}")
with col4:
    avg_catch_pct = summary_data['Catch Percentage'].mean()
    st.metric("📈 Avg Catch %", f"{avg_catch_pct:.1f}%")