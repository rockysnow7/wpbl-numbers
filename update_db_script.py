from db import DB_DIR, DATABASE_FILE
from wpybl.data import GamesCollection

import duckdb
import os
import wpybl.stats.batting as wpybl_batting
import wpybl.stats.pitching as wpybl_pitching
import wpybl.stats.teams as wpybl_teams


GAMES = GamesCollection.all()

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

    df = wpybl_teams.standings().reset_index()[
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
        }
    )

    df = (
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

    df = (
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


if __name__ == "__main__":
    conn = duckdb.connect(database=TEMP_DB_FILE)

    set_standings(conn)
    set_batting_leaders(conn)
    set_pitching_leaders(conn)

    conn.close()

    os.rename(TEMP_DB_FILE, DATABASE_FILE)
