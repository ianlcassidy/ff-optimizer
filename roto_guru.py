import pandas as pd
import re
import requests


def create_name_position_key(name: str, team: str, position: str) -> str:
    """Attempts to create a unique key for each player"""
    if position == "D":
        return f"{team}-dst"

    names = [n.lower().strip() for n in name.split(",")]
    names = [re.sub("[^a-z ]+", "", n) for n in names]
    last_name = names[0].split(" ")[0]
    first_name = names[-1]
    return f"{first_name}-{last_name}-{position.lower()}"


def get_data() -> str:
    url = "http://rotoguru1.com/cgi-bin/fstats.cgi"
    params = {
        "pos": 0,
        "sort": 5,
        "game": "p",
        "colA": 0,
        "daypt": 0,
        "xavg": 1,
        "inact": 0,
        "maxprc": 99999,
        "outcsv": 1,
    }
    r = requests.get(url, params=params)
    assert r.status_code == 200

    return r.text


def convert_raw_data_to_df(raw: str) -> pd.DataFrame:
    # split on newlines
    split_newline = raw.split("\n")

    # if the first 4 characters in a line are digits, then it's player data (GID)
    players = [line for line in split_newline if line[:4].isdigit()]

    print("number of players scraped:", len(players))

    # combine the headers with each row of data
    headers = [
        "gid",
        "position",
        "name",
        "team",
        "opponent",
        "home/away",
        "salary",
        "salary_change",
        "total_points",
        "games_played",
        "points_per_game",
        "points_per_game_per_salary",
        "points_per_game_alt",
        "bye_week",
        "ytd_salary_high/low",
    ]
    data = []
    for row in players:
        split_row = row.split(";")
        d = {k: v for k, v in zip(headers, split_row)}
        d["name_position_key"] = create_name_position_key(
            d["name"], d["team"], d["position"]
        )
        if d["position"] == "D":
            d["position"] = "DST"
        data.append(d)

    # convert to a dataframe
    df = pd.DataFrame(data)

    # check that the name_position_key is unique
    assert df["name_position_key"].nunique() == len(df)

    # manipulate some columns
    df["salary"] = df["salary"].astype(int)
    df["salary_change"] = df["salary_change"].astype(int)
    df["points_per_game"] = df["points_per_game"].astype(float)
    df["points_per_game_per_salary"] = df["points_per_game_per_salary"].astype(float)
    return df


def scrape_and_save_data(week: int) -> pd.DataFrame:
    raw = get_data()
    df = convert_raw_data_to_df(raw)
    df.to_csv(f"data/roto_guru_data_week{week}.csv", index=False)
    return df
