import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Advanced Stats", page_icon="🎯", layout="wide")

# Load data in a cached function for performance
@st.cache_data
def load_data():
    return pd.read_csv("data/nextgen_receiving_stats.csv")

receiving_df = load_data()

st.header("🎯 Advanced Player Analysis with Next Gen Stats")

st.write("""
Compare players using **Next Gen Stats** advanced metrics in an interactive radar chart. 
Select your comparison type and up to 2 players to see how they stack up!
""")

# Settings for comparison
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
        "Select Players to Compare (up to 2 players)",
        options=sorted(comparison_data['Player Name'].unique()),
        default=comparison_data.nlargest(2, 'Receiving Touchdowns')['Player Name'].tolist(),
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
            
            # Get the actual values
            actual_values = [player_data[stat] for stat in selected_stats]
            
            # Calculate true percentile rankings for each stat
            normalized_values = []
            for stat, actual_val in zip(selected_stats, actual_values):
                # Get all values for this stat
                all_values = comparison_data[stat].dropna()
                # Calculate percentile rank (percentage of players this player is better than)
                percentile = (all_values < actual_val).sum() / len(all_values) * 100
                normalized_values.append(percentile)
            
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

        fig.update_layout(hovermode="closest")

        for trace_data in player_traces:
            theta_closed = radar_labels + [radar_labels[0]]
            r_closed = trace_data['normalized_values'] + [trace_data['normalized_values'][0]]
            actual_closed = trace_data['actual_values'] + [trace_data['actual_values'][0]]
            customdata_closed = [[v] for v in actual_closed]

            fig.add_trace(go.Scatterpolar(
                r=r_closed,
                theta=theta_closed,
                fill='toself',
                name=trace_data['player'],
                fillcolor=colors[trace_data['idx']],
                line=dict(width=3, color=line_colors[trace_data['idx']]),
                mode="lines+markers",
                marker=dict(size=8),
                hoveron="points",
                hovertemplate=(
                    "<b>%{theta}</b><br>"
                    "Actual: %{customdata[0]:.1f}<br>"
                    "Percentile: %{r:.1f}%<extra></extra>"
                ),
                customdata=customdata_closed
            ))
    
        fig.update_layout(
            title="Player Comparison (Percentile Rankings - Higher is Better)",
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
            comparison_table = radar_data[['Player Name', 'Position', 'Team Abbreviation'] + selected_stats].copy()
            
            # Round all numeric columns to 1 decimal place
            for col in selected_stats:
                comparison_table[col] = comparison_table[col].round(1)
            
            # Set player names as columns and transpose
            comparison_table = comparison_table.set_index('Player Name').T
            
            st.dataframe(comparison_table, use_container_width=True)
        else:
            comparison_table = radar_data[['Player Name', 'Position', 'Team Abbreviation'] + selected_stats].copy()
            
            # Round all numeric columns to 1 decimal place
            for col in selected_stats:
                comparison_table[col] = comparison_table[col].round(1)
            
            st.dataframe(comparison_table, hide_index=True, use_container_width=True)
            
    else:
        st.info("👆 Please select at least one player to see the comparison chart!")