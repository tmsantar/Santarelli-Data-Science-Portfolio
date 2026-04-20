from pathlib import Path

import pandas as pd
import streamlit as st
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix
from sklearn.preprocessing import StandardScaler

DATA_FILE = Path(__file__).parent.parent / "data" / "nextgen_receiving_stats.csv"

# Set page configuration which gives the browser tab a title and icon, and sets the layout to wide.
st.set_page_config(page_title="Similar Players", page_icon="🎯", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv(DATA_FILE)

receiving_df = load_data()
receiving_df = receiving_df[receiving_df['Week'] == 0].copy()


# Display the title of the Streamlit app interface.
st.markdown("### Player Recommendation")

# Allow the user to select a player from a dropdown menu.
# The options are limited to the first 500 entries because of Streamlit limit.
player = st.selectbox('Type Target Player to View Similar Players:')


# Specify the columns from the DataFrame that are used for the KNN model.
# These columns represent player attributes considered in the recommendation algorithm.
df_columns = ['Yards', 'Targets', 'Receptions', 'Receiving Touchdowns', 'Catch Percentage', 
         'Avg Yards After Catch', 'YAC Above Expectation', 'Avg Cushion', 'Avg Separation',
         'Avg Intended Air Yards', 'Share of Intended Air Yards (%)', 'Avg Expected YAC']

# Prepare data for KNN model
knn_df = receiving_df[df_columns]

# Normalize the feature data using StandardScaler to have a mean of 0 and a variance of 1.
# This standardization improves the performance and accuracy of the KNN model.
scaler = StandardScaler()
knn_scaled = scaler.fit_transform(knn_df)

# Convert the normalized data back into a DataFrame to retain the original structure.
# This step allows for easier manipulation and access to the data moving forward.
knn_final = pd.DataFrame(data=knn_scaled, index=knn_df.index, columns=knn_df.columns)

# Convert the DataFrame to a compressed sparse row matrix to optimize memory usage.
# Sparse matrices are particularly useful when dealing with a large number of features.
feature_matrix = csr_matrix(knn_final.values)

# Initialize and fit the NearestNeighbors model using the cosine similarity metric.
# The 'brute' algorithm is specified for simplicity, but other algorithms could be considered for optimization.
knn_model = NearestNeighbors(metric='cosine', algorithm='brute')
knn_model.fit(feature_matrix)

# Initialize lists to store the results of the player recommendation algorithm.
player_list = []
rec_list = []

# Iterate through each player in the filtered DataFrame to find and store their nearest neighbors.
for _ in knn_final.index:
    player_data = knn_final.loc[_, :].values.reshape(1, -1)
    
    # Skip any players whose data does not match the expected shape (1, 71), indicating a potential issue with the data.
    if player_data.shape[1] != 71:
        print(f"Skipping {_} due to unexpected shape: {player_data.shape}")
        continue
    # Use the KNN model to find the 11 nearest neighbors for each player, based on the cosine similarity of their attributes.
    distances, indices = knn_model.kneighbors(knn_final.loc[_, :].values.reshape(1, -1), n_neighbors=11)

    # Store the results in lists, separating the first entry (the player themselves) from their recommendations.
    for elem in range(0, len(distances.flatten())):
        if elem == 0:
            # For the first element, which is the player itself, append to player_list
            player_list.append([player])
        else:
            # For other elements, which are the recommended neighbors, append to rec_list
            rec_list.append([_, elem, knn_final.index[indices.flatten()[elem]], distances.flatten()[elem]])
            
# Convert the list of recommendations into a DataFrame for easier display and manipulation in the Streamlit app.            
rec_df = pd.DataFrame(rec_list, columns=['search_player', 'rec_number', 'rec_player', 'distance_score'])

# Extract the top recommendations for the user-selected player to be displayed in the app.
top_recs = list(rec_df[rec_df['search_player'] == player]['rec_player'])


st.markdown(f"#### {player}")
st.markdown(f"##### Value: {receiving_df.loc[player]['Yards']}")
st.markdown(f"##### Targets: {receiving_df.loc[player]['Targets']}")
st.markdown(f"##### Receptions: {receiving_df.loc[player]['Receptions']}")
st.markdown(f"##### Receiving Touchdowns: {receiving_df.loc[player]['Receiving Touchdowns']}")
st.markdown(f"##### Catch Percentage: {receiving_df.loc[player]['Catch Percentage']}")
st.markdown(f"##### Avg Yards After Catch: {receiving_df.loc[player]['Avg Yards After Catch']}")
st.markdown(f"##### YAC Above Expectation: {receiving_df.loc[player]['YAC Above Expectation']}")
st.markdown(f"##### Avg Cushion: {receiving_df.loc[player]['Avg Cushion']}")
st.markdown(f"##### Avg Separation: {receiving_df.loc[player]['Avg Separation']}")
st.markdown(f"##### Avg Intended Air Yards: {receiving_df.loc[player]['Avg Intended Air Yards']}")
st.markdown(f"##### Share of Intended Air Yards (%): {receiving_df.loc[player]['Share of Intended Air Yards (%)']}")
st.markdown(f"##### Avg Expected YAC: {receiving_df.loc[player]['Avg Expected YAC']}")




st.markdown('***')

# Display a subheader in the app to introduce the section where the top 10 player recommendations will be shown.
st.subheader(f'10 Players Most Like {player}:')

# Loop through the list of recommended players. The enumerate function is used to get both the index (starting from 1) and the player name.
for i, rec_player in enumerate(top_recs, start=1):
    # Create two columns in the Streamlit interface using the columns method. This layout will display each player's photo on the left and their information on the right.
    col_left, col_right = st.columns(2)


        # Display the ranking number and player name as a header.
    st.markdown(f"#### {player}")
    st.markdown(f"##### Value: {receiving_df.loc[player]['Yards']}")
    st.markdown(f"##### Targets: {receiving_df.loc[player]['Targets']}")
    st.markdown(f"##### Receptions: {receiving_df.loc[player]['Receptions']}")
    st.markdown(f"##### Receiving Touchdowns: {receiving_df.loc[player]['Receiving Touchdowns']}")
    st.markdown(f"##### Catch Percentage: {receiving_df.loc[player]['Catch Percentage']}")
    st.markdown(f"##### Avg Yards After Catch: {receiving_df.loc[player]['Avg Yards After Catch']}")
    st.markdown(f"##### YAC Above Expectation: {receiving_df.loc[player]['YAC Above Expectation']}")
    st.markdown(f"##### Avg Cushion: {receiving_df.loc[player]['Avg Cushion']}")
    st.markdown(f"##### Avg Separation: {receiving_df.loc[player]['Avg Separation']}")
    st.markdown(f"##### Avg Intended Air Yards: {receiving_df.loc[player]['Avg Intended Air Yards']}")
    st.markdown(f"##### Share of Intended Air Yards (%): {receiving_df.loc[player]['Share of Intended Air Yards (%)']}")
    st.markdown(f"##### Avg Expected YAC: {receiving_df.loc[player]['Avg Expected YAC']}")



    # After displaying each player's details, insert a horizontal rule (markdown) as a visual separator before moving on to the next player.
    st.markdown('***')