from pathlib import Path
import pandas as pd
import streamlit as st
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

DATA_FILE = Path(__file__).parent.parent / "data" / "nextgen_receiving_stats.csv"

STAT_COLUMNS = ["Yards", "Targets", "Receptions", "Receiving Touchdowns", "Catch Percentage",
    "Avg Yards After Catch", "YAC Above Expectation", "Avg Cushion", "Avg Separation",
    "Avg Intended Air Yards", "Share of Intended Air Yards (%)","Avg Expected YAC",]

st.set_page_config(page_title="Similar Player Tool", page_icon="🧬", layout="wide")


@st.cache_data
def load_data():
    return pd.read_csv(DATA_FILE)


def format_stat(value):
    return f"{float(value):.2f}"


def format_match_percent(distance):
    match_percent = max(0, min(100, (1 - float(distance)) * 100))
    return f"{match_percent:.2f}%"


def render_player(player_data, title, distance=None):
    st.markdown(f"### {title}")
    info_col, stats_col = st.columns([1, 2])
    with info_col:
        st.markdown(f"#### {player_data['Player Name']} | {player_data['Position']}")
        st.markdown(f"##### Team: {player_data['Team Abbreviation']}")
        if pd.notna(player_data.get("Headshot")) and player_data["Headshot"]:
            st.image(player_data["Headshot"], width=250)
        else:
            st.info("Sorry no player headshot was found")

    with stats_col:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"##### 🎯 Yards: {format_stat(player_data['Yards'])}")
            st.markdown(f"##### 👀 Targets: {format_stat(player_data['Targets'])}")
            st.markdown(f"##### ✋ Receptions: {format_stat(player_data['Receptions'])}")
            st.markdown(f"##### 🔥 Receiving Touchdowns: {format_stat(player_data['Receiving Touchdowns'])}")
            st.markdown(f"##### 💯 Catch Percentage: {format_stat(player_data['Catch Percentage'])}")
            st.markdown(f"##### 💨 Avg YAC: {format_stat(player_data['Avg Yards After Catch'])}")

        with col2:
            st.markdown(f"##### ⚡ YAC Above Expectation: {format_stat(player_data['YAC Above Expectation'])}")
            st.markdown(f"##### 📏 Avg Cushion: {format_stat(player_data['Avg Cushion'])}")
            st.markdown(f"##### 🏃 Avg Separation: {format_stat(player_data['Avg Separation'])}")
            st.markdown(f"##### ✈️ Avg Intended Air Yards: {format_stat(player_data['Avg Intended Air Yards'])}")
            st.markdown(f"##### 📊 Share of Intended Air Yards (%): {format_stat(player_data['Share of Intended Air Yards (%)'])}")
            st.markdown(f"##### 📈 Avg Expected YAC: {format_stat(player_data['Avg Expected YAC'])}")


receiving_df = load_data()
receiving_df = receiving_df[receiving_df["Week"] == 0].copy()

st.markdown("## 🎯 Similar Player Tool")
st.caption("Pick a receiver and explore the three closest statistical matches.")

player = st.selectbox(
    "Choose a player",
    options=sorted(receiving_df["Player Name"].unique()),)

scaled_stats = StandardScaler().fit_transform(receiving_df[STAT_COLUMNS])
knn_model = NearestNeighbors(metric="cosine", algorithm="brute")
knn_model.fit(scaled_stats)

selected_index = receiving_df.index[receiving_df["Player Name"] == player][0]
distances, indices = knn_model.kneighbors(
[scaled_stats[receiving_df.index.get_loc(selected_index)]], n_neighbors=4,)

selected_player = receiving_df.loc[selected_index]
recommendations = [{"player_data": receiving_df.loc[neighbor_index], "distance": distance_score,}
    for neighbor_index, distance_score in zip(indices.flatten()[1:], distances.flatten()[1:])]

st.markdown("---")
render_player(selected_player, "🌟 Selected Player")
st.markdown("---")

st.subheader(f"Top 3 Similar Players to {player}")
tabs = st.tabs(
    [f"#{i} {rec['player_data']['Player Name']}" 
    for i, rec in enumerate(recommendations, start=1)]
)

for i, (tab, rec) in enumerate(zip(tabs, recommendations), start=1):
    with tab:
        render_player(
            rec["player_data"],
            f"🎯 Match #{i} | {format_match_percent(rec['distance'])} Match",
            rec["distance"])
