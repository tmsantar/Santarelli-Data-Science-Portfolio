import nflreadpy as nfl
import pandas as pd

# Load season-level stats for a specific season (e.g., 2025)
print("Loading Next Gen receiving stats...")
# Load Next Gen receiving stats (use stat_type)
ng = nfl.load_nextgen_stats(seasons=[2025], stat_type="receiving")
print(f"✅ Next Gen receiving loaded! Shape: {ng.shape}")
print(f"Columns: {list(ng.columns)}")
ng = ng.to_pandas()

print("\nFirst 5 rows:")
print(ng.head(5))

# Drop the unnecessary columns
ng = ng.drop(columns=['player_first_name', 'player_last_name', 'player_jersey_number', 'player_short_name'])

# Manually rename the remaining columns
ng = ng.rename(columns={
    'season': 'Season',
    'season_type': 'Season Type',
    'week': 'Week',
    'player_display_name': 'Player Name',
    'player_position': 'Position',
    'team_abbr': 'Team Abbreviation',
    'avg_cushion': 'Avg Cushion',
    'avg_separation': 'Avg Separation',
    'avg_intended_air_yards': 'Avg Intended Air Yards',
    'percent_share_of_intended_air_yards': 'Share of Intended Air Yards (%)',
    'receptions': 'Receptions',
    'targets': 'Targets',
    'catch_percentage': 'Catch Percentage',
    'yards': 'Yards',
    'rec_touchdowns': 'Receiving Touchdowns',
    'avg_yac': 'Avg Yards After Catch',
    'avg_expected_yac': 'Avg Expected YAC',
    'avg_yac_above_expectation': 'YAC Above Expectation',
    'player_gsis_id': 'Player GSIS ID'
})

# Display the renamed columns
print("\nRenamed columns:")
print(list(ng.columns))

ng.to_csv("basic_streamlit_app/data/nextgen_receiving_stats.csv", index=False)
