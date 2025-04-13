import numpy as np
import cv2
import csv
import pandas as pd

def get_video_fps(video_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    return fps

def calculate_average_speed(player_stats, player_1, player_2):
    player_1_avg_speed = player_stats[f'player_{player_1}_last_player_speed'].replace(0, np.nan).mean()
    player_2_avg_speed = player_stats[f'player_{player_2}_last_player_speed'].replace(0, np.nan).mean()

    player_1_avg_shot_speed = player_stats[f'player_{player_1}_last_shot_speed'].replace(0, np.nan).mean()
    player_2_avg_shot_speed = player_stats[f'player_{player_2}_last_shot_speed'].replace(0, np.nan).mean()

    return player_1_avg_speed, player_2_avg_speed, player_1_avg_shot_speed, player_2_avg_shot_speed

def draw_player_stats(output_video_frames, player_stats, player_1, player_2, FPS):
    player_stats["player_1_acceleration"] = player_stats[f"player_{player_1}_last_player_speed"].diff().fillna(0)
    player_stats["player_2_acceleration"] = player_stats[f"player_{player_2}_last_player_speed"].diff().fillna(0)

    player_stats["player_1_shot_inconsistency"] = (
        player_stats[f"player_{player_1}_last_shot_speed"]
        .dropna()
        .rolling(5, min_periods=1)
        .std()
        .fillna(0)
    )    
    player_stats["player_2_shot_inconsistency"] = (
        player_stats[f"player_{player_2}_last_shot_speed"]
        .dropna()
        .rolling(5, min_periods=1)
        .std()
        .fillna(0)
    )

    frame_time = 1 / FPS  

    player_stats["player_1_distance_covered"] = (player_stats[f"player_{player_1}_last_player_speed"] * frame_time).cumsum()
    player_stats["player_2_distance_covered"] = (player_stats[f"player_{player_2}_last_player_speed"] * frame_time).cumsum()

    player_stats["player_1_rally_contribution"] = (player_stats[f"player_{player_1}_last_shot_speed"].diff() > 0).astype(int).cumsum()
    player_stats["player_2_rally_contribution"] = (player_stats[f"player_{player_2}_last_shot_speed"].diff() > 0).astype(int).cumsum()

    player_stats["player_1_total_shots"] = (player_stats[f"player_{player_1}_last_shot_speed"]
                                        .diff()
                                        .gt(0)
                                        .cumsum())   
     
    player_stats["player_2_total_shots"] = (player_stats[f"player_{player_2}_last_shot_speed"]
                                        .diff()
                                        .gt(0)
                                        .cumsum())

    player_stats["player_1_rally_percentage"] = (player_stats["player_1_rally_contribution"] / player_stats["player_1_total_shots"]).fillna(0) * 100
    player_stats["player_2_rally_percentage"] = (player_stats["player_2_rally_contribution"] / player_stats["player_2_total_shots"]).fillna(0) * 100

    for index, row in player_stats.iterrows():
        if index >= len(output_video_frames):
            continue  

        def safe_value(val):
            return val if not np.isnan(val) else 0  

        player_stats_dict = {
            "shot_speed_1": safe_value(row[f'player_{player_1}_last_shot_speed']),
            "shot_speed_2": safe_value(row[f'player_{player_2}_last_shot_speed']),
            "speed_1": safe_value(row[f'player_{player_1}_last_player_speed']),
            "speed_2": safe_value(row[f'player_{player_2}_last_player_speed']),
            "acceleration_1": safe_value(row["player_1_acceleration"]),
            "acceleration_2": safe_value(row["player_2_acceleration"]),
            "shot_inconsistency_1": safe_value(row["player_1_shot_inconsistency"]),
            "shot_inconsistency_2": safe_value(row["player_2_shot_inconsistency"]),
            "distance_covered_1": safe_value(row["player_1_distance_covered"]),
            "distance_covered_2": safe_value(row["player_2_distance_covered"]),
            "rally_contribution_1": safe_value(row["player_1_rally_contribution"]),
            "rally_contribution_2": safe_value(row["player_2_rally_contribution"]),
        }

    return output_video_frames

import pandas as pd

def generate_report_max_only(player_stats, player_1, player_2):
    avg_speed_1, avg_speed_2, avg_shot_speed_1, avg_shot_speed_2 = calculate_average_speed(player_stats, player_1, player_2)

    max_stats = {
        f"player_{player_1}_max_shot_speed": [player_stats[f'player_{player_1}_last_shot_speed'].max()],
        f"player_{player_2}_max_shot_speed": [player_stats[f'player_{player_2}_last_shot_speed'].max()],
        f"player_{player_1}_avg_shot_speed": [avg_shot_speed_1],
        f"player_{player_2}_avg_shot_speed": [avg_shot_speed_2],
        f"player_{player_1}_max_speed": [player_stats[f'player_{player_1}_last_player_speed'].max()],
        f"player_{player_2}_max_speed": [player_stats[f'player_{player_2}_last_player_speed'].max()],
        f"player_{player_1}_avg_speed": [avg_speed_1],
        f"player_{player_2}_avg_speed": [avg_speed_2],
        f"player_{player_1}_max_acceleration": [player_stats["player_1_acceleration"].max()],
        f"player_{player_2}_max_acceleration": [player_stats["player_2_acceleration"].max()],
        f"player_{player_1}_max_shot_inconsistency": [player_stats["player_1_shot_inconsistency"].max()],
        f"player_{player_2}_max_shot_inconsistency": [player_stats["player_2_shot_inconsistency"].max()],
        f"player_{player_1}_max_distance_covered": [player_stats["player_1_distance_covered"].max()],
        f"player_{player_2}_max_distance_covered": [player_stats["player_2_distance_covered"].max()],
        f"player_{player_1}_max_rally_contribution": [player_stats["player_1_rally_contribution"].max()],
        f"player_{player_2}_max_rally_contribution": [player_stats["player_2_rally_contribution"].max()],
        f"player_{player_1}_total_shots": [player_stats["player_1_total_shots"].max()],
        f"player_{player_2}_total_shots": [player_stats["player_2_total_shots"].max()],
        f"player_{player_1}_max_rally_percentage": [player_stats["player_1_rally_percentage"].max()],
        f"player_{player_2}_max_rally_percentage": [player_stats["player_2_rally_percentage"].max()],
    }

    df = pd.DataFrame(max_stats)
    
    df.to_csv("max_game_report.csv", index=True)

    return df


