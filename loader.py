import typing as T

import pandas as pd


def get_players_df(week: int) -> pd.DataFrame:
    # load projections and salary data
    df_projections = pd.read_csv(f"data/fantasy_pros_data_week{week}.csv")
    df_salary = pd.read_csv(f"data/roto_guru_data_week{week}.csv")

    # only keep a few projection columns
    df_projections_merge = df_projections[
        [
            "name_position_key",
            "start_sit_score",
            "start_sit_grade",
            "projected_points",
            "position_rank",
            "player_owned_pct",
        ]
    ]

    # merge data
    df_players = pd.merge(
        left=df_salary, right=df_projections_merge, how="left", on="name_position_key"
    )

    # fill NaN with 0
    df_players["start_sit_score"] = df_players["start_sit_score"].fillna(0)
    df_players["projected_points"] = df_players["projected_points"].fillna(0)
    df_players["position_rank"] = df_players["position_rank"].fillna(99).astype(int)
    df_players["player_owned_pct"] = df_players["player_owned_pct"].fillna(0)
    df_players["projected_points_per_salary"] = (
        df_players["projected_points"] / df_players["salary"] * 1000
    )

    return df_players


def get_valid_teams_and_team_points_mapping(week: int) -> T.Tuple[T.Tuple[str], T.Dict]:
    # load schedule data
    df_schedule = pd.read_csv(f"data/football_locks_data_week{week}.csv")
    df_schedule["datetime"] = pd.to_datetime(
        df_schedule["datetime"], infer_datetime_format=True
    )
    df_schedule["hour"] = df_schedule["datetime"].dt.hour

    # find valid games in the schedule (Sunday 1pm and 4pm games only)
    df_schedule_valid = df_schedule[df_schedule["hour"].isin([1, 4])]
    valid_teams = (
        df_schedule_valid["favorite"].unique().tolist()
        + df_schedule_valid["underdog"].unique().tolist()
    )

    # create a mapping of expected points per team based on the over/under and line
    # note the line is negative for the favored team, so we subtract it from the
    #  favorite and add it to the underdog
    team_points_mapping = {}
    for row in df_schedule_valid.itertuples():
        team_points_mapping[row.favorite] = (row.over_under - row.line) / 2
        team_points_mapping[row.underdog] = (row.over_under + row.line) / 2
    return valid_teams, team_points_mapping
