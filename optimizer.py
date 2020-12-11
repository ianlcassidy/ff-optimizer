import typing as T

import pandas as pd
import time
from itertools import combinations
import random

from utils import what_week_is_it
from domain import Player, Team
from loader import get_players_df, get_valid_teams_and_team_points_mapping


def filter_and_convert_players(
    df_players: pd.DataFrame, valid_teams: T.Tuple[str], team_points_mapping: T.Dict
) -> T.List[Player]:
    # e.g., injured_players = ["Jones, Aaron", "Tonyan, Robert"]
    injured_players = []

    df_filtered = df_players[
        (df_players["team"].isin(valid_teams))
        & (df_players["salary"] > 0)
        & (df_players["projected_points"] > 0)
        & (~df_players["name"].isin(injured_players))
        & (df_players["start_sit_score"] >= 2.33)  # start/sit grade >= C+
    ]

    position_filters = [
        {"position": "QB", "salary": 5000, "ppps": 2.5, "max": 10},
        {"position": "RB", "salary": 4000, "ppps": 2.0, "max": 20},
        {"position": "WR", "salary": 4000, "ppps": 2.0, "max": 20},
        {"position": "TE", "salary": 3000, "ppps": 2.0, "max": 10},
        {"position": "DST", "salary": 2000, "ppps": 1.5, "max": 10},
    ]

    players = []
    for row in position_filters:
        df_pos = df_filtered[
            (df_filtered["position"] == row["position"])
            & (df_filtered["salary"] >= row["salary"])
            & (df_filtered["projected_points_per_salary"] > row["ppps"])
        ]
        df_pos = df_pos.sort_values(
            by="projected_points_per_salary", ascending=False
        ).head(row["max"])
        print(f"number of feasible {row['position']}: {len(df_pos)}")
        for i, p in df_pos.iterrows():
            players.append(Player.from_raw_data(p, team_points_mapping))
    print("total number of feasible players:", len(players))
    return players


def create_feasible_teams(
    players: T.List[Player],
    fraction_wr_combinations: float = 1.0,
    fraction_rb_combinations: float = 1.0,
) -> T.List[Team]:
    # decompose players by position
    qb_players = [p for p in players if p.position == "QB"]
    te_players = [p for p in players if p.position == "TE"]
    dst_players = [p for p in players if p.position == "DST"]
    wr_players = [p for p in players if p.position == "WR"]
    rb_players = [p for p in players if p.position == "RB"]

    # get all combinations of 4 WR and 2 RB (assume flex is RB)
    # we can change this if we want a team where the flex is a RB
    wr_combinations = list(combinations(wr_players, r=4))
    rb_combinations = list(combinations(rb_players, r=2))

    # filter combinations to only include one player per team
    wr_combinations = [
        c for c in wr_combinations if len(c) == len(set([p.team for p in c]))
    ]
    rb_combinations = [
        c for c in rb_combinations if len(c) == len(set([p.team for p in c]))
    ]

    total_num_combinations = (
        len(wr_combinations)
        * len(rb_combinations)
        * len(qb_players)
        * len(te_players)
        * len(dst_players)
    )
    print("total number of combinations:", total_num_combinations)

    # randomly down sample the WR/RB combinations
    random_wr_combs = random.sample(
        wr_combinations, k=round(fraction_wr_combinations * len(wr_combinations))
    )
    random_rb_combs = random.sample(
        rb_combinations, k=round(fraction_rb_combinations * len(rb_combinations))
    )

    start_time = time.time()
    total_count = 0
    feasible_teams = []

    # loop through each position, create a team, and filter
    for qb in qb_players:
        for te in te_players:
            for dst in dst_players:
                for wrs in random_wr_combs:
                    for rbs in random_rb_combs:
                        team = Team(
                            QB=qb,
                            RB1=rbs[0],
                            RB2=rbs[1],
                            WR1=wrs[0],
                            WR2=wrs[1],
                            WR3=wrs[2],
                            Flex=wrs[3],  # flex can be RB or WR
                            TE=te,
                            DST=dst,
                        )
                        # filter teams that
                        #  1) match the salary constraint;
                        #  2) offenive players not playing defense;
                        #  3) have no more than 2 players on the same team;
                        #  4) QB and RB are not on the same team;
                        #  5) QB and WR are on same team; and
                        #  6) WR and TE are not on the same team.
                        if (
                            49500 <= team.total_salary <= 50000
                            and not team.offense_playing_defense
                            and team.max_num_players_same_team <= 2
                            and not team.qb_rb_same_team
                            and team.qb_wr_same_team
                            and not team.te_wr_same_team
                        ):
                            feasible_teams.append(team)

                        total_count += 1

    elapsed_time = time.time() - start_time
    print(f"total run time: {round(elapsed_time / 60, 1)} minutes")
    print(f"number of feasible teams found: {len(feasible_teams)}")
    print(f"percent feasible: {round(len(feasible_teams) / total_count * 100, 1)}%")
    return feasible_teams


def sort_and_display_top_teams(teams: T.List[Team]):
    # sort and score by total ppg (higher is better)
    by_total_ppg = sorted(teams, key=lambda x: x.total_ppg, reverse=True)
    team_score_by_total_ppg = {
        team: 1 - i / len(by_total_ppg) for i, team in enumerate(by_total_ppg)
    }

    # sort and score by total expected team points (higher is better)
    by_total_expected_team_points = sorted(
        teams, key=lambda x: x.total_expected_team_points, reverse=True
    )
    team_score_by_total_expected_team_points = {
        team: 1 - i / len(by_total_expected_team_points)
        for i, team in enumerate(by_total_expected_team_points)
    }

    # sort and score by projected points (higher is better)
    by_total_projected_points = sorted(
        teams, key=lambda x: x.total_projected_points, reverse=True
    )
    team_score_by_total_projected_points = {
        team: 1 - i / len(by_total_projected_points)
        for i, team in enumerate(by_total_projected_points)
    }

    # sort and score by start/sit score (higher is better)
    by_start_sit_score = sorted(
        teams, key=lambda x: x.avg_start_sit_score, reverse=True
    )
    team_score_by_start_sit_score = {
        team: 1 - i / len(by_start_sit_score)
        for i, team in enumerate(by_start_sit_score)
    }

    # sort and score by percent player owned score (higher is better)
    by_owned_pct = sorted(teams, key=lambda x: x.avg_player_owned_pct, reverse=True)
    team_score_by_owned_pct = {
        team: 1 - i / len(by_owned_pct) for i, team in enumerate(by_owned_pct)
    }

    # create tuples of teams and weighted average score
    team_score = []
    for team in teams:
        score1 = team_score_by_total_ppg[team]
        score2 = team_score_by_total_expected_team_points[team]
        score3 = team_score_by_total_projected_points[team]
        score4 = team_score_by_start_sit_score[team]
        score5 = team_score_by_owned_pct[team]
        weighted_avg_score = (
            0 * score1 + 0.3 * score2 + 0.6 * score3 + 0.1 * score4 + 0.0 * score5
        )
        team_score.append((team, weighted_avg_score))

    # sort by score
    by_score = sorted(team_score, key=lambda x: x[1], reverse=True)[:3]

    # print out the details
    print("")
    for i, team_score in enumerate(by_score):
        team = team_score[0]
        print(f"***** team #{i + 1} *****")
        for pos in team.__annotations__.keys():
            p = getattr(team, pos)
            print(
                f"{pos}: {p.name} ({p.team.upper()}) | ${p.salary} | Proj: {p.projected_points} | Grade: {p.start_sit_grade} | Pos Rank: {p.position_rank}"
            )
        print(f"total projected points: {team.total_projected_points}")
        print("")


if __name__ == "__main__":
    week = what_week_is_it()
    df_players = get_players_df(week)
    valid_teams, team_points_mapping = get_valid_teams_and_team_points_mapping(week)
    print("number of teams playing on sunday at 1pm or 4pm:", len(valid_teams))
    players = filter_and_convert_players(df_players, valid_teams, team_points_mapping)
    teams = create_feasible_teams(
        players, fraction_wr_combinations=0.1, fraction_rb_combinations=0.5
    )
    sort_and_display_top_teams(teams)
