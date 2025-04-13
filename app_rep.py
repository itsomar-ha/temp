import pandas as pd
import json

# Thresholds
thresholds = {
    "max_shot_speed": {"High": 55, "Med": 51, "Low": 47},
    "avg_shot_speed": {"High": 49, "Med": 45, "Low": 41},
    "max_speed": {"High": 10, "Med": 8, "Low": 6},
    "avg_speed": {"High": 7, "Med": 6.5, "Low": 6.0},
    "max_acceleration": {"High": 8.5, "Med": 6, "Low": 4},
    "max_shot_inconsistency": {"High": 23, "Med": 28, "Low": 36},
    "max_distance_covered": {"High": 48, "Med": 40, "Low": 32},
    "max_rally_contribution": {"High": 2, "Med": 1, "Low": 0},
    "total_shots": {"High": 2, "Med": 1, "Low": 0},
    "max_rally_percentage": {"High": 96, "Med": 88, "Low": 75}
}

def calculate_points(value, stat_name):
    if stat_name not in thresholds:
        return 0
    th = thresholds[stat_name]
    
    if stat_name == "max_shot_inconsistency":
        if value <= th['High']: 
            return 3
        elif value <= th['Med']:
            return 2
        elif value <= th['Low']:
            return 1
        else:
            return 0
    
    if value >= th['High']:
        return 3
    elif value >= th['Med']:
        return 2
    elif value >= th['Low']:
        return 1
    else:
        return 0

def calculate_player_scores(data):
    df = pd.DataFrame(data)

    for col in df.columns:
        if not (col.startswith("player_1_") or col.startswith("player_2_")):
            continue

        stat_name = "_".join(col.split("_")[2:])
        if stat_name in thresholds:
            df[f'{col}_Points'] = df[col].apply(lambda x: calculate_points(x, stat_name))

    df['player_1_Total_Score'] = df[[c for c in df.columns if c.startswith('player_1') and '_Points' in c]].sum(axis=1)
    df['player_2_Total_Score'] = df[[c for c in df.columns if c.startswith('player_2') and '_Points' in c]].sum(axis=1)

    max_score = 30
    df['player_1_Score_Percentage'] = (df['player_1_Total_Score'] / max_score) * 100
    df['player_2_Score_Percentage'] = (df['player_2_Total_Score'] / max_score) * 100

    player_1_data = df[['player_1_Score_Percentage', 'player_1_Total_Score'] + [col for col in df.columns if col.startswith('player_1_')]].to_dict(orient='records')[0]
    player_2_data = df[['player_2_Score_Percentage', 'player_2_Total_Score'] + [col for col in df.columns if col.startswith('player_2_')]].to_dict(orient='records')[0]

    with open('player_1_data.json', 'w') as file_1:
        json.dump(player_1_data, file_1, indent=4)
    
    with open('player_2_data.json', 'w') as file_2:
        json.dump(player_2_data, file_2, indent=4)

    return df[['player_1_Score_Percentage','player_2_Score_Percentage']]