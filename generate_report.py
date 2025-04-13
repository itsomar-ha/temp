import pandas as pd
import markdown
import pdfkit

WKHTMLTOPDF_PATH = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe" 
CONFIG = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)

CSS_STYLE = """
<style>
    body { font-family: Arial, sans-serif; padding: 20px; line-height: 1.6; }
    h1, h2, h3 { color: #333; }
    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
    th { background-color: #f4f4f4; }
    ul { list-style-type: square; }
</style>
"""

def generate_paragraph(metric, value):
    explanations = {
        "Shot Speed": (
            "Shot speed is one of the most crucial factors in modern tennis. A faster shot means the opponent has less time to react, leading to more forced errors. "
            "Players with high shot speed often dominate baseline rallies and put immense pressure on their opponents. However, pure power without control can lead to errors. "
            "To be an elite player, a balance between speed and accuracy is essential.",
            80, 50, "an exceptional level, allowing aggressive and dominant play.", 
            "a solid level, giving a competitive edge in exchanges.", 
            "a weaker area, requiring improvement to add more power to shots."
        ),
        "Player Speed": (
            "Speed is fundamental in reaching tough shots and maintaining court coverage. A fast player can transition between offense and defense seamlessly, making them unpredictable. "
            "Top players rely on speed not just to chase balls but to create angles and dictate play. Without good speed, a player may struggle against aggressive opponents.",
            12, 8, "remarkable agility, enabling rapid movement across the court.", 
            "a decent level, providing good coverage but leaving room for improvement.", 
            "below par, which may cause issues in retrieving difficult shots."
        ),
        "Acceleration": (
            "Acceleration determines how quickly a player can change direction. This is vital in responding to drop shots and sudden attacks. "
            "Players with explosive acceleration can quickly close in on the net and react to unexpected plays, making them dangerous opponents.",
            10, 5, "excellent, allowing instant reaction and court coverage.", 
            "adequate, supporting decent movement under pressure.", 
            "insufficient, leading to slow reaction times in key moments."
        ),
        "Shot Consistency": (
            "Consistency is what separates top players from average competitors. A player who can maintain high shot consistency minimizes errors and forces the opponent to take risks. "
            "It is particularly crucial in long rallies, where mental and physical endurance play a big role.",
            30, 15, "highly reliable, ensuring steady and effective play.", 
            "moderately stable, though still room for refinement.", 
            "inconsistent, increasing the risk of unforced errors."
        ),
    }

    for key, (desc, high, mid, high_text, mid_text, low_text) in explanations.items():
        if key in metric:
            if value > high:
                rating = high_text
            elif value > mid:
                rating = mid_text
            else:
                rating = low_text

            return f"{desc} Currently, {metric} is recorded at {value:.2f}, indicating {rating}"

    return f"{metric} is recorded at {value:.2f}, providing insight into the player's performance."

def evaluate_talent(player_stats, player):
    high_skills = 0
    mid_skills = 0
    weak_skills = 0

    thresholds = {
        "Shot Speed": 80,
        "Speed": 12,
        "Acceleration": 10,
        "Shot inConsistency": 30,
    }

    for metric, high_value in thresholds.items():
        mid_value = high_value * 0.6
        value = player_stats.get(f"player_{player}_{metric.lower().replace(' ', '_')}", [0])[0]

        if value > high_value:
            high_skills += 1
        elif value > mid_value:
            mid_skills += 1
        else:
            weak_skills += 1

    summary = f"{player} has been evaluated based on multiple key performance metrics. "

    if high_skills >= 4:
        summary += "This player demonstrates an elite level of talent. Their shot speed, speed, and consistency indicate they can compete at a professional or semi-professional level. "
        summary += "They have the potential to become a top-tier athlete with continued training."
    elif high_skills >= 2 and mid_skills >= 2:
        summary += "This player is highly skilled and shows strong potential. While they have areas of excellence, a few aspects still need refinement. "
        summary += "With dedicated training, they can significantly improve and become a top contender."
    else:
        summary += "This player has foundational skills but still requires considerable improvement. Weaknesses in key areas such as speed or consistency may hinder their competitive performance. "
        summary += "Targeted coaching and training programs are essential for unlocking their full potential."

    return summary

def generate_player_report(player_stats, player, md_output, pdf_output):
    if player_stats.empty:
        print("EMPTY!")
        return None

    content = f"""# Tennis Player Report - {player}

## Key Metrics Overview

| Metric | Value |
|--------|-------|
"""

    metrics = [
        ("Max Shot Speed", f"player_{player}_max_shot_speed"),
        ("Avg Shot Speed", f"player_{player}_avg_shot_speed"),
        ("Max Player Speed", f"player_{player}_max_speed"),
        ("Avg Player Speed", f"player_{player}_avg_speed"),
        ("Max Acceleration", f"player_{player}_max_acceleration"),
        ("Shot inConsistency", f"player_{player}_max_shot_inconsistency")
    ]

    for metric, key in metrics:
        value = player_stats.get(key, [0])[0]
        content += f"| {metric} | {value:.2f} |\n"

    content += "\n## Key Metrics Analysis\n"

    for metric, key in metrics:
        value = player_stats.get(key, [0])[0]
        content += f"### {metric}\n{generate_paragraph(metric, value)}\n\n"

    summary = evaluate_talent(player_stats, player)

    content += f"""## Overall Summary\n{summary}\n"""

    with open(md_output, "w", encoding="utf-8") as file:
        file.write(content)

    print(f"✅ Markdown report saved as {md_output}")

    convert_md_to_pdf(md_output, pdf_output)

def convert_md_to_pdf(md_file, pdf_file):
    with open(md_file, "r", encoding="utf-8") as file:
        md_content = file.read()

    html_content = CSS_STYLE + markdown.markdown(md_content, extensions=["extra", "tables"])

    pdfkit.from_string(html_content, pdf_file, configuration=CONFIG)

    print(f"✅ PDF report saved as {pdf_file}")
