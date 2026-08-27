from backend_utils.innings import (
    innings_pitched_decimal_to_fractional,
    innings_pitched_fractional_to_decimal,
)
from wpybl.data import GamesCollection

import duckdb
import os
import pandas as pd
import wpybl.stats.batting as wpybl_batting
import wpybl.stats.pitching as wpybl_pitching
import wpybl.stats.teams as wpybl_teams
import wpybl.stats.misc as wpybl_misc


GAMES = GamesCollection.all()

DB_DIR = "db"
if not os.path.exists(DB_DIR):
    os.mkdir(DB_DIR)

DATABASE_FILE = f"{DB_DIR}/data.duckdb"
TEMP_DB_FILE = f"{DB_DIR}/temp.duckdb"


def set_standings(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS standings (
            Team TEXT PRIMARY KEY,
            W INT,
            L INT,
            T INT,
            PCT REAL,
            GB INT
        )
    """)

    df = wpybl_teams.standings().reset_index()[  # noqa: F841
        [
            "Team",
            "W",
            "L",
            "T",
            "PCT",
            "GB",
        ]
    ]
    conn.execute("""
        INSERT OR REPLACE INTO standings
        SELECT * FROM df
    """)


def set_batting_leaders(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS batting_leaders (
            Name TEXT PRIMARY KEY,
            Team TEXT,
            G INT,
            AB INT,
            PA INT,
            H INT,
            _1B INT,
            _2B INT,
            _3B INT,
            HR INT,
            SO INT,
            BB INT,
            HBP INT,
            RBI INT,
            SF INT,
            AVG REAL,
            OBP REAL,
            SLG REAL,
            OPS REAL,
            wOBA REAL,
            qualified BOOLEAN
        )
    """)

    players_df = wpybl_teams.players().reset_index().set_index("Player")[["Team"]]
    counting_stats_df = wpybl_batting.batting_counting_stats(GAMES).rename(
        columns={
            "games": "G",
            "at_bats": "AB",
            "plate_appearances": "PA",
            "hits": "H",
            "singles": "1B",
            "doubles": "2B",
            "triples": "3B",
            "home_runs": "HR",
            "strikeouts": "SO",
            "bases_on_balls": "BB",
            "hit_by_pitches": "HBP",
            "rbi": "RBI",
            "sacrifice_flies": "SF",
        }
    )
    rate_stats_df = wpybl_batting.batting_rate_stats(
        GAMES, filter_qualified=False
    ).rename(
        columns={
            "avg": "AVG",
            "obp": "OBP",
            "slg": "SLG",
            "ops": "OPS",
            "woba": "wOBA",
        }
    )

    df = (  # noqa: F841
        players_df.merge(
            counting_stats_df,
            left_index=True,
            right_index=True,
        )
        .merge(
            rate_stats_df,
            left_index=True,
            right_index=True,
        )
        .reset_index()
    )

    conn.execute("""
        INSERT OR REPLACE INTO batting_leaders
        SELECT * FROM df
    """)


def set_pitching_leaders(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pitching_leaders (
            Name TEXT PRIMARY KEY,
            Team TEXT,
            G INT,
            IP REAL,
            H INT,
            R INT,
            ER INT,
            BB INT,
            SO INT,
            ERA REAL,
            WHIP REAL,
            K_BB REAL,
            qualified BOOLEAN
        )
    """)

    players_df = wpybl_teams.players().reset_index().set_index("Player")[["Team"]]
    counting_stats_df = wpybl_pitching.pitching_counting_stats(GAMES).rename(
        columns={
            "games": "G",
            "innings_pitched": "IP",
            "hits_allowed": "H",
            "runs_allowed": "R",
            "earned_runs_allowed": "ER",
            "bases_on_balls": "BB",
            "strikeouts": "SO",
        }
    )
    rate_stats_df = wpybl_pitching.pitching_rate_stats(
        GAMES, filter_qualified=False
    ).rename(
        columns={
            "era": "ERA",
            "whip": "WHIP",
            "k/bb": "K/BB",
        }
    )

    df = (  # noqa: F841
        players_df.merge(
            counting_stats_df,
            left_index=True,
            right_index=True,
        )
        .merge(
            rate_stats_df,
            left_index=True,
            right_index=True,
        )
        .reset_index()
    )

    conn.execute("""
        INSERT OR REPLACE INTO pitching_leaders
        SELECT * FROM df
    """)


def set_league_batting(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS league_batting (
            Team TEXT PRIMARY KEY,
            G INT,
            AB INT,
            PA INT,
            H INT,
            _1B INT,
            _2B INT,
            _3B INT,
            HR INT,
            SO INT,
            BB INT,
            HBP INT,
            RBI INT,
            SF INT,
            AVG REAL,
            OBP REAL,
            SLG REAL,
            OPS REAL,
            wOBA REAL
        )
    """)

    players_df = wpybl_teams.players().reset_index().set_index("Player")[["Team"]]
    counting_stats_df = (
        wpybl_batting.batting_counting_stats(GAMES)
        .rename(
            columns={
                "games": "G",
                "at_bats": "AB",
                "plate_appearances": "PA",
                "hits": "H",
                "singles": "1B",
                "doubles": "2B",
                "triples": "3B",
                "home_runs": "HR",
                "strikeouts": "SO",
                "bases_on_balls": "BB",
                "hit_by_pitches": "HBP",
                "rbi": "RBI",
                "sacrifice_flies": "SF",
            }
        )
        .drop(["G"], axis=1)
    )
    df = players_df.merge(counting_stats_df, left_index=True, right_index=True)
    df = df.groupby("Team").agg({k: "sum" for k in df.columns if k != "Team"})

    standings_df = wpybl_teams.standings()[["W", "L", "T"]]
    standings_df["G"] = standings_df["W"] + standings_df["L"] + standings_df["T"]
    standings_df = standings_df[["G"]]
    df = standings_df.merge(df, left_index=True, right_index=True)

    league = df.sum().to_frame().T
    league["Team"] = "League"
    league.set_index("Team", inplace=True)
    df = pd.concat([df, league])

    df["AVG"] = df["H"] / df["AB"]
    df["OBP"] = (df["H"] + df["BB"] + df["HBP"]) / (
        df["AB"] + df["BB"] + df["HBP"] + df["SF"]
    )
    df["SLG"] = (df["1B"] + 2 * df["2B"] + 3 * df["3B"] + 4 * df["HR"]) / df["AB"]
    df["OPS"] = df["OBP"] + df["SLG"]

    weights = wpybl_misc.woba_weights(GAMES).reset_index()
    weights = {k: v for k, v in weights.to_dict("tight")["data"]}
    numerator = (
        weights.get("walk", 0) * df["BB"]
        + weights.get("hit_by_pitch", 0) * df["HBP"]
        + weights.get("single", 0) * df["1B"]
        + weights.get("double", 0) * df["2B"]
        + weights.get("triple", 0) * df["3B"]
        + weights.get("home_run", 0) * df["HR"]
    )
    denominator = df["AB"] + df["BB"] + df["HBP"] + df["SF"]
    woba = numerator / denominator
    df["wOBA"] = woba

    df.reset_index(inplace=True)

    conn.execute("""
        INSERT OR REPLACE INTO league_batting
        SELECT * FROM df
    """)


def set_league_pitching(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS league_pitching (
            Team TEXT PRIMARY KEY,
            G INT,
            IP REAL,
            H INT,
            R INT,
            ER INT,
            BB INT,
            SO INT,
            ERA REAL,
            WHIP REAL,
            K_BB REAL
        )
    """)

    players_df = wpybl_teams.players().reset_index().set_index("Player")[["Team"]]
    counting_stats_df = (
        wpybl_pitching.pitching_counting_stats(GAMES)
        .rename(
            columns={
                "games": "G",
                "innings_pitched": "IP",
                "hits_allowed": "H",
                "runs_allowed": "R",
                "earned_runs_allowed": "ER",
                "bases_on_balls": "BB",
                "strikeouts": "SO",
            }
        )
        .drop(["G"], axis=1)
    )
    counting_stats_df["IP"] = counting_stats_df["IP"].map(
        innings_pitched_fractional_to_decimal
    )
    df = players_df.merge(counting_stats_df, left_index=True, right_index=True)
    df = df.groupby("Team").agg({k: "sum" for k in df.columns if k != "Team"})
    df["IP"] = df["IP"].map(innings_pitched_decimal_to_fractional)

    standings_df = wpybl_teams.standings()[["W", "L", "T"]]
    standings_df["G"] = standings_df["W"] + standings_df["L"] + standings_df["T"]
    standings_df = standings_df[["G"]]
    df = standings_df.merge(df, left_index=True, right_index=True)

    league = df.sum().to_frame().T
    league["Team"] = "League"
    league.set_index("Team", inplace=True)
    df = pd.concat([df, league])

    df["ERA"] = df["H"] / df["ER"]
    df["WHIP"] = (df["BB"] + df["H"] + df["SO"]) / (df["IP"] + df["BB"] + df["SO"])
    df["K/BB"] = df["H"] / df["BB"]

    df.reset_index(inplace=True)

    conn.execute("""
        INSERT OR REPLACE INTO league_pitching
        SELECT * FROM df
    """)


def set_re24(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS re24 (
            state TEXT PRIMARY KEY,
            expected_runs REAL
        )
    """)

    df = (
        wpybl_misc.re24(GAMES)
        .reset_index()
        .rename(columns={"runs_remaining": "expected_runs"})
    )
    df["expected_runs"] = df["expected_runs"].round(2)

    conn.execute("""
        INSERT OR REPLACE INTO re24
        SELECT * FROM df
    """)


def set_run_values(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS run_values (
            event_type TEXT PRIMARY KEY,
            run_value REAL
        )
    """)

    df = wpybl_misc.run_values(GAMES).reset_index()
    conn.execute("""
        INSERT OR REPLACE INTO run_values
        SELECT * FROM df
    """)


def set_woba_weights(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS woba_weights (
            event_type TEXT PRIMARY KEY,
            weight REAL
        )
    """)

    df = wpybl_misc.woba_weights(GAMES).reset_index()
    conn.execute("""
        INSERT OR REPLACE INTO woba_weights
        SELECT * FROM df
    """)


if __name__ == "__main__":
    conn = duckdb.connect(database=TEMP_DB_FILE)

    set_standings(conn)
    set_batting_leaders(conn)
    set_pitching_leaders(conn)
    set_league_batting(conn)
    set_league_pitching(conn)
    set_re24(conn)
    set_run_values(conn)
    set_woba_weights(conn)

    conn.close()

    os.rename(TEMP_DB_FILE, DATABASE_FILE)
