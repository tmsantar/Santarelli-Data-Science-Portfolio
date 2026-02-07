import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np

# Set page config for wide layout
st.set_page_config(page_title="NFL Receiving Stats Explorer", page_icon="🏈", layout="wide")

# Title of the app
st.title("🏈 NFL Receiving Stats Explorer")

# Load the dataset
receiving_df = pd.read_csv("data/nextgen_receiving_stats.csv")

# Sidebar navigation
st.sidebar.title("📊 Navigation")
page = st.sidebar.radio("Select Page", ["🏠 Home", "📈 Season Stats", "📅 Weekly Stats", "🎯 Advanced Stats"])

# HOME PAGE
if page == "🏠 Home":
    st.header("Welcome to the NFL Receiving Stats Explorer! 🎉")
    
    st.write("""
    ### 📖 About This Dataset
    
    This application allows you to explore comprehensive receiving statistics for NFL players 
    from the 2025 regular season using **Next Generation Stats** tracking data. The data includes 
    performance metrics for wide receivers, tight ends, running backs, and fullbacks. 🏃‍♂️
    
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
    
    #### ✨ Features:
    - **📈 Season Stats**: View full season statistics and top 10 performers
    - **📅 Weekly Stats**: Analyze week-by-week performance throughout the season
    - **🎯 Advanced Stats**: Compare players with interactive radar charts using Next Gen metrics
    
    #### 🚀 How to Use:
    1. Use the sidebar to navigate between pages
    2. Select **Season Stats** or **Weekly Stats** for basic performance data
    3. Select **Advanced Stats** for detailed player comparisons with Next Gen metrics
    4. Use the filters on each page to customize your view
    
    Get started by selecting a page from the sidebar! 👈
    """)
    
    # Optional: Display dataset overview
    st.subheader("📋 Dataset Overview")
    col1, col2, col3 = st.columns(3)
    
    total_players = receiving_df[receiving_df['Week'] == 0]['Player Name'].nunique()
    with col1:
        st.metric("👥 Total Players", total_players)
    with col2:
        st.metric("📅 Total Weeks", 18)
    with col3:
        st.metric("📊 Next Gen Stats Tracked", 12)

# SEASON STATS PAGE
elif page == "📈 Season Stats":
    st.header("📈 Season Statistics")
    
    # Filter for season stats (Week 0)
    season_data = receiving_df[receiving_df['Week'] == 0].copy()
    
    # Drop unnecessary columns
    columns_to_drop = ['Season', 'Season Type', 'Week', 'Player GSIS ID']
    season_data_clean = season_data.drop(columns=[col for col in columns_to_drop if col in season_data.columns])
    
    # Filters embedded in the page
    st.subheader("🎯 Filters")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        stat_column = st.selectbox(
            "Select Stat to Filter Top 10",
            ['Yards', 'Targets', 'Receptions', 'Receiving Touchdowns', 'Catch Percentage', 
             'Avg Yards After Catch', 'YAC Above Expectation', 'Avg Cushion', 'Avg Separation',
             'Avg Intended Air Yards', 'Share of Intended Air Yards (%)', 'Avg Expected YAC'],
            key="season_stat"
        )
    
    st.markdown("---")
    
    # Top 10 Bar Chart
    top_10_data = season_data.nlargest(10, stat_column)
    
    st.subheader(f"🏆 Top 10 Players Based on {stat_column}")
    
    # Bar chart for top 10 players' selected stat
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = sns.color_palette("viridis", 10)
    sns.barplot(x='Player Name', y=stat_column, data=top_10_data, ax=ax, palette=colors)
    ax.set_title(f"🏆 Top 10 Players Based on {stat_column}", fontsize=16, fontweight='bold')
    ax.set_xlabel("Player Name", fontsize=12)
    ax.set_ylabel(stat_column, fontsize=12)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)
    
    st.markdown("---")
    
    # Display full season dataframe
    st.subheader("📋 Complete Season Statistics")
    
    # Reorder columns for better display
    priority_cols = ['Player Name', 'Position', 'Team Abbreviation', 'Yards', 'Targets', 
                     'Receptions', 'Receiving Touchdowns', 'Catch Percentage']
    other_cols = [col for col in season_data_clean.columns if col not in priority_cols]
    ordered_cols = priority_cols + other_cols
    season_data_display = season_data_clean[ordered_cols]
    
    st.dataframe(season_data_display, hide_index=True, use_container_width=True, height=600)

# WEEKLY STATS PAGE
elif page == "📅 Weekly Stats":
    st.header("📅 Weekly Statistics")
    
    # Filters embedded in the page
    st.subheader("🎯 Filters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        week = st.slider("Select Week 📆", min_value=1, max_value=18, value=1, key="weekly_week")
    
    with col2:
        weekly_stat_column = st.selectbox(
            "Select Stat to Filter Top 10",
            ['Yards', 'Targets', 'Receptions', 'Receiving Touchdowns', 'Catch Percentage', 
             'Avg Yards After Catch', 'YAC Above Expectation', 'Avg Cushion', 'Avg Separation',
             'Avg Intended Air Yards', 'Share of Intended Air Yards (%)', 'Avg Expected YAC'],
            key="weekly_stat"
        )
    
    week_data = receiving_df[receiving_df['Week'] == week].copy()
    
    # Drop unnecessary columns (including Week since it's shown above)
    columns_to_drop = ['Season', 'Season Type', 'Week', 'Player GSIS ID']
    week_data_clean = week_data.drop(columns=[col for col in columns_to_drop if col in week_data.columns])
    
    st.markdown("---")
    
    st.write(f"### 📊 Displaying data for Week {week}")
    
    # Top 10 Bar Chart
    top_10_weekly = week_data.nlargest(10, weekly_stat_column)
    
    st.subheader(f"🏆 Top 10 Players in Week {week} Based on {weekly_stat_column}")
    
    # Bar chart for top 10 players' selected stat
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = sns.color_palette("rocket", 10)
    sns.barplot(x='Player Name', y=weekly_stat_column, data=top_10_weekly, ax=ax, palette=colors)
    ax.set_title(f"🏆 Top 10 Players in Week {week} Based on {weekly_stat_column}", fontsize=16, fontweight='bold')
    ax.set_xlabel("Player Name", fontsize=12)
    ax.set_ylabel(weekly_stat_column, fontsize=12)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)
    
    st.markdown("---")
    
    # Display full weekly dataframe
    st.subheader(f"📋 Complete Week {week} Statistics")
    
    # Reorder columns for better display (no Week column)
    priority_cols = ['Player Name', 'Position', 'Team Abbreviation', 'Yards', 'Targets', 
                     'Receptions', 'Receiving Touchdowns', 'Catch Percentage']
    other_cols = [col for col in week_data_clean.columns if col not in priority_cols]
    ordered_cols = [col for col in priority_cols if col in week_data_clean.columns] + other_cols
    week_data_display = week_data_clean[ordered_cols]
    
    st.dataframe(week_data_display, hide_index=True, use_container_width=True, height=600)
    
    # Add some stats summary
    st.markdown("---")
    st.subheader(f"📈 Week {week} Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎯 Total Yards", f"{week_data['Yards'].sum():,.0f}")
    with col2:
        st.metric("✋ Total Receptions", f"{week_data['Receptions'].sum():,.0f}")
    with col3:
        st.metric("🔥 Total TDs", f"{week_data['Receiving Touchdowns'].sum():,.0f}")
    with col4:
        avg_catch_pct = week_data['Catch Percentage'].mean()
        st.metric("📈 Avg Catch %", f"{avg_catch_pct:.1f}%")

# ADVANCED STATS PAGE
elif page == "🎯 Advanced Stats":
    st.header("🎯 Advanced Player Analysis with Next Gen Stats")
    
    st.write("""
    Compare players using **Next Generation Stats** advanced metrics in an interactive radar chart. 
    Select your comparison type and up to 2 players to see how they stack up! 📊
    """)
    
    # Filters
    st.subheader("⚙️ Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        comparison_type = st.radio(
            "Select Comparison Type",
            ["Season Stats", "Weekly Stats"],
            key="comparison_type"
        )
    
    with col2:
        if comparison_type == "Weekly Stats":
            week = st.slider("Select Week 📆", min_value=1, max_value=18, value=1, key="advanced_week")
            comparison_data = receiving_df[receiving_df['Week'] == week]
            st.info(f"📅 Comparing Week {week} performance")
        else:
            comparison_data = receiving_df[receiving_df['Week'] == 0]
            st.info("📈 Comparing full season performance")
    
    st.markdown("---")
    
    # Radar chart for comparing players
    st.subheader("⚔️ Player Comparison Radar Chart")
    
    # Stat selection
    st.write("**Choose which stats to compare:**")
    
    available_stats = {
        'Yards': 'Yards',
        'Targets': 'Targets', 
        'Receptions': 'Receptions',
        'Receiving Touchdowns': 'Rec TDs',
        'Catch Percentage': 'Catch %',
        'Avg Yards After Catch': 'Avg YAC',
        'Avg Expected YAC': 'xYAC',
        'YAC Above Expectation': 'YAC+',
        'Avg Cushion': 'Cushion',
        'Avg Separation': 'Separation',
        'Avg Intended Air Yards': 'Air Yards',
        'Share of Intended Air Yards (%)': 'Air Yard %'
    }
    
    selected_stats = st.multiselect(
        "Select 3-7 statistics for comparison",
        options=list(available_stats.keys()),
        default=['Yards', 'Targets', 'Receptions', 'Receiving Touchdowns', 'Catch Percentage'],
        max_selections=7,
        key="radar_stats"
    )
    
    if len(selected_stats) < 3:
        st.warning("⚠️ Please select at least 3 statistics for a meaningful comparison!")
    else:
        # Player selection
        selected_players = st.multiselect(
            "Select Players to Compare (up to 2 players) 👇",
            options=sorted(comparison_data['Player Name'].unique()),
            default=comparison_data.nlargest(2, 'Yards')['Player Name'].tolist(),
            max_selections=2,
            key="advanced_players"
        )
        
        # Prepare data for radar chart
        if len(selected_players) > 0:
            radar_data = comparison_data[comparison_data['Player Name'].isin(selected_players)]
            
            # Get shortened labels
            radar_labels = [available_stats[stat] for stat in selected_stats]
            
            # Create the radar chart with Plotly
            fig = go.Figure()
            
            # Better color palette
            colors = ['rgba(0, 123, 255, 0.6)', 'rgba(255, 99, 71, 0.6)']
            line_colors = ['rgb(0, 123, 255)', 'rgb(255, 99, 71)']
            
            # Calculate normalized values for all players first
            player_traces = []
            for idx, player in enumerate(selected_players):
                player_data = radar_data[radar_data['Player Name'] == player].iloc[0]
                
                # Get the actual values and normalize them to 0-100 scale (percentile)
                actual_values = [player_data[stat] for stat in selected_stats]
                max_values = [comparison_data[stat].max() for stat in selected_stats]
                normalized_values = [(actual / max_val * 100) if max_val > 0 else 0 
                                    for actual, max_val in zip(actual_values, max_values)]
                
                # Calculate average to determine which player should be drawn first
                avg_value = sum(normalized_values) / len(normalized_values)
                
                player_traces.append({
                    'player': player,
                    'normalized_values': normalized_values,
                    'actual_values': actual_values,
                    'avg_value': avg_value,
                    'idx': idx
                })
            
            # Sort by average value (descending) so larger polygons are drawn first
            player_traces.sort(key=lambda x: x['avg_value'], reverse=True)
        
            # Add traces in order (largest first, so smallest is on top and clickable)
            for trace_data in player_traces:
                fig.add_trace(go.Scatterpolar(
                    r=trace_data['normalized_values'],
                    theta=radar_labels,
                    fill='toself',
                    name=trace_data['player'],
                    fillcolor=colors[trace_data['idx']],
                    line=dict(width=3, color=line_colors[trace_data['idx']]),
                    hovertemplate='<b>%{theta}</b><br>Actual: %{customdata[0]:.1f}<br>Percentile: %{r:.1f}%<extra></extra>',
                    customdata=[[val] for val in trace_data['actual_values']]
                ))
        
            fig.update_layout(
                title="⚔️ Player Comparison (Percentile of Maximum Performance)",
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100],
                        ticksuffix='%',
                        gridcolor='lightgray'
                    ),
                    angularaxis=dict(
                        gridcolor='lightgray'
                    ),
                    bgcolor='rgba(240, 240, 240, 0.5)'
                ),
                showlegend=True,
                legend=dict(
                    font=dict(size=14)
                ),
                height=650,
                hovermode='closest'
            )
        
            st.plotly_chart(fig, use_container_width=True)
            
            # Show comparison table
            st.markdown("---")
            st.subheader("📊 Side-by-Side Comparison")
            
            if len(selected_players) == 2:
                comparison_table = radar_data[['Player Name', 'Position', 'Team Abbreviation'] + selected_stats]
                st.dataframe(comparison_table.T, use_container_width=True)
            else:
                comparison_table = radar_data[['Player Name', 'Position', 'Team Abbreviation'] + selected_stats]
                st.dataframe(comparison_table, hide_index=True, use_container_width=True)
                
        else:
            st.info("👆 Please select at least one player to see the comparison chart!")