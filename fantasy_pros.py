import typing as T

import constants

import requests
from bs4 import BeautifulSoup
import re
import json
import pandas as pd


def get_and_scrape_position_data(position: str) -> T.List[T.Dict]:
    path = position.lower()
    if position in ["WR", "RB", "TE"]:
        path = f"ppr-{path}"

    r = requests.get(f"https://www.fantasypros.com/nfl/rankings/{path}.php")
    assert r.status_code == 200

    soup = BeautifulSoup(r.text, "html.parser")
    scripts = soup.find_all("script")

    filtered_scripts = [s for s in scripts if "var ecrData" in str(s)]
    assert len(filtered_scripts) == 1

    filtered = str(filtered_scripts[0].string)
    ecr_data = re.findall(
        r"var ecrData.*?=\s*(.*?)};", filtered, re.DOTALL | re.MULTILINE
    )
    assert len(ecr_data) == 1

    json_loadable_data = ecr_data[0].replace("/'", "'") + "}"
    data = json.loads(json_loadable_data)
    return data["players"]


def create_name_position_key(data: T.Dict) -> str:
    """Attempts to create a unique key for each player"""
    if data["position"] == "DST":
        team = data["team"]
        return f"{team}-dst"

    lower = data["name"].lower()
    cleaned = re.sub("[^a-z ]+", "", lower)
    names = cleaned.split(" ")
    positions = data["position"].lower().split(",")
    return f"{names[0]}-{names[1]}-{positions[0]}"


def get_all_position_data_and_convert_to_df() -> pd.DataFrame:
    positions = ["QB", "RB", "WR", "TE", "DST"]
    data = []
    for pos in positions:
        players = get_and_scrape_position_data(pos)
        print(f"number of {pos} found from Fantasy Pros: {len(players)}")
        data.extend(players)

    print("total number of players found from Fantasy Pros:", len(data))

    df = pd.DataFrame(data)
    df = df[
        [
            "player_name",
            "player_team_id",
            "player_eligibility",
            "player_opponent_id",
            "start_sit_grade",
            "r2p_pts",
            "rank_ecr",
            "player_owned_avg",
        ]
    ]
    df.columns = [
        "name",
        "team",
        "position",
        "opponent",
        "start_sit_grade",
        "projected_points",
        "position_rank",
        "player_owned_pct",
    ]
    df["start_sit_score"] = df["start_sit_grade"].map(constants.START_SIT_MAPPING)
    df["projected_points"] = df["projected_points"].astype(float)
    df["team"] = df["team"].map(constants.FANTASY_PROS_TEAM_MAPPING)
    df["opponent"] = df["opponent"].map(constants.FANTASY_PROS_TEAM_MAPPING)
    df["name_position_key"] = df.apply(lambda x: create_name_position_key(x), axis=1)
    return df


def scrape_and_save_data(week: int):
    df = get_all_position_data_and_convert_to_df()
    df.to_csv(f"data/fantasy_pros_data_week{week}.csv", index=False)
