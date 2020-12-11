import typing as T

from collections import Counter


class Player(T.NamedTuple):
    name: str
    position: str
    team: str
    opponent: str
    salary: int
    points_per_game: float
    points_per_game_per_salary: float
    expected_team_points: float
    expected_opponent_points: float
    projected_points: float
    start_sit_score: float
    start_sit_grade: str
    position_rank: int
    player_owned_pct: float

    @classmethod
    def from_raw_data(cls, data: T.Dict, team_points_mapping: T.Dict):
        return cls(
            name=data["name"],
            position=data["position"],
            team=data["team"],
            opponent=data["opponent"],
            salary=data["salary"],
            points_per_game=data["points_per_game"],
            points_per_game_per_salary=data["points_per_game_per_salary"],
            expected_team_points=team_points_mapping[data["team"]],
            expected_opponent_points=team_points_mapping[data["opponent"]],
            projected_points=data["projected_points"],
            start_sit_score=data["start_sit_score"],
            start_sit_grade=data["start_sit_grade"],
            position_rank=data["position_rank"],
            player_owned_pct=data["player_owned_pct"],
        )


class Team(T.NamedTuple):
    QB: Player
    RB1: Player
    RB2: Player
    WR1: Player
    WR2: Player
    WR3: Player
    TE: Player
    Flex: Player
    DST: Player

    @property
    def total_salary(self) -> int:
        keys = self.__annotations__.keys()
        salaries = [self.__getattribute__(k).salary for k in keys]
        return sum(salaries)

    @property
    def offense_playing_defense(self) -> bool:
        keys = self.__annotations__.keys()
        offense_teams = [self.__getattribute__(k).team for k in keys if k != "DST"]
        if self.DST.opponent in offense_teams:
            return True
        return False

    @property
    def max_num_players_same_team(self) -> int:
        keys = self.__annotations__.keys()
        teams = [self.__getattribute__(k).team for k in keys]
        return max(Counter(teams).values())

    @property
    def total_ppg_ps(self) -> float:
        keys = self.__annotations__.keys()
        ppg_ps = [self.__getattribute__(k).points_per_game_per_salary for k in keys]
        return round(sum(ppg_ps), 2)

    @property
    def total_ppg(self) -> float:
        keys = self.__annotations__.keys()
        ppg = [self.__getattribute__(k).points_per_game for k in keys]
        return round(sum(ppg), 2)

    @property
    def total_expected_team_points(self) -> float:
        keys = self.__annotations__.keys()
        offense_points = sum(
            [self.__getattribute__(k).expected_team_points for k in keys if k != "DST"]
        )
        points = offense_points - self.DST.expected_opponent_points
        return round(points, 2)

    @property
    def total_projected_points(self) -> float:
        keys = self.__annotations__.keys()
        scores = [self.__getattribute__(k).projected_points for k in keys]
        return round(sum(scores), 2)

    @property
    def total_start_sit_score(self) -> float:
        keys = self.__annotations__.keys()
        scores = [self.__getattribute__(k).start_sit_score for k in keys]
        return round(sum(scores), 2)

    @property
    def avg_start_sit_score(self) -> float:
        keys = self.__annotations__.keys()
        scores = [self.__getattribute__(k).start_sit_score for k in keys]
        return round(sum(scores) / len(scores), 2)

    @property
    def avg_player_owned_pct(self) -> float:
        keys = self.__annotations__.keys()
        pcts = [self.__getattribute__(k).player_owned_pct for k in keys]
        return round(sum(pcts) / len(pcts), 2)

    @property
    def qb_rb_same_team(self) -> bool:
        keys = self.__annotations__.keys()
        rb_teams = [
            self.__getattribute__(k).team
            for k in keys
            if self.__getattribute__(k).position == "RB"
        ]
        if self.QB.team in rb_teams:
            return True
        return False

    @property
    def qb_wr_same_team(self) -> bool:
        keys = self.__annotations__.keys()
        wr_teams = [
            self.__getattribute__(k).team
            for k in keys
            if self.__getattribute__(k).position == "WR"
        ]
        if self.QB.team in wr_teams:
            return True
        return False

    @property
    def te_wr_same_team(self) -> bool:
        keys = self.__annotations__.keys()
        wr_teams = [
            self.__getattribute__(k).team
            for k in keys
            if self.__getattribute__(k).position == "WR"
        ]
        if self.TE.team in wr_teams:
            return True
        return False
