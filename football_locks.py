import typing as T

from utils import is_float
import constants

import requests
from bs4 import BeautifulSoup
import datetime
import pandas as pd


def scrape_and_filter_data(week: int) -> T.List:
    r = requests.get("http://www.footballlocks.com/nfl_lines.shtml")
    assert r.status_code == 200

    soup = BeautifulSoup(r.text, "html.parser")
    spans = [
        s for s in soup.body.findAll("span") if f"NFL Lines For Week {week}" in s.text
    ]
    line_span = spans[-1]
    trs = line_span.find_all_next("tr", limit=20)

    keep = []
    for tr in trs:
        tds = tr.find_all("td")
        if len(tds) == 5 and is_float(tds[4].text):
            keep.append(tr)

    print("number of games found:", len(keep))
    return keep


def process_and_convert_data_to_df(keep: T.List) -> pd.DataFrame:
    headers = ["datetime", "favorite", "line", "underdog", "over_under", "home"]
    parsed = []
    for tr in keep:
        # get tds
        tds = tr.find_all("td")
        # parse game datetime
        game_dt = tds[0].text[:10].strip()
        game_dt = datetime.datetime.strptime(f"20/{game_dt}", "%y/%m/%d %H:%M")
        # parse favorite, underdog, and home team
        favorite = tds[1].text.lower()
        underdog = tds[3].text.lower()
        home_team = favorite.replace("at ", "")
        if "at " in underdog:
            home_team = underdog.replace("at ", "")
        favorite = favorite.replace("at ", "")
        underdog = underdog.replace("at ", "")
        # parse line and O/U
        line = tds[2].text
        if not is_float(line):
            line = 0.0
        line = float(line)
        over_under = float(tds[4].text)
        # merge data and headers
        data = [game_dt, favorite, line, underdog, over_under, home_team]
        merged = {k: v for k, v in zip(headers, data)}
        parsed.append(merged)

    df = pd.DataFrame(parsed)
    df["favorite"] = df["favorite"].map(constants.FOOTBALL_LOCKS_TEAM_MAPPING)
    df["underdog"] = df["underdog"].map(constants.FOOTBALL_LOCKS_TEAM_MAPPING)
    df["home"] = df["home"].map(constants.FOOTBALL_LOCKS_TEAM_MAPPING)
    return df


def scrape_and_save_data(week: int):
    keep = scrape_and_filter_data(week)
    df = process_and_convert_data_to_df(keep)
    df.to_csv(f"data/football_locks_data_week{week}.csv", index=False)
