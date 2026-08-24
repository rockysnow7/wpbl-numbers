from datetime import datetime, timedelta, UTC

import duckdb
import json
import os
import pandas as pd


DB_DIR = "db"
if not os.path.exists(DB_DIR):
    os.mkdir(DB_DIR)

DATABASE_FILE = f"{DB_DIR}/data.duckdb"


def _midnight_tonight() -> datetime:
    return datetime.now(UTC).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    ) + timedelta(days=1)


class Database:
    def __init__(self) -> None:
        self.__conn = duckdb.connect(database=DATABASE_FILE, read_only=True)
        self.__refresh_at = _midnight_tonight()

    def __refresh(self) -> None:
        if datetime.now(UTC) >= self.__refresh_at:
            self.__conn = duckdb.connect(database=DATABASE_FILE, read_only=True)
            self.__refresh_at = _midnight_tonight()

    def __execute(self, query: str) -> duckdb.DuckDBPyConnection:
        self.__refresh()
        return self.__conn.execute(query)

    def get_standings(self) -> pd.DataFrame:
        result = self.__execute("SELECT * FROM standings")
        result = result.fetchall()

        df = pd.DataFrame(
            result,
            columns=[
                "Team",
                "W",
                "L",
                "T",
                "PCT",
                "GB",
            ],
        ).set_index("Team")
        df["PCT"] = df["PCT"].round(3)

        return df

    def get_batting_leaders(self) -> pd.DataFrame:
        result = self.__execute("SELECT * FROM batting_leaders")
        result = result.fetchall()

        df = (
            pd.DataFrame(
                result,
                columns=[
                    "Name",
                    "Team",
                    "G",
                    "AB",
                    "PA",
                    "H",
                    "_1B",
                    "_2B",
                    "_3B",
                    "HR",
                    "SO",
                    "BB",
                    "HBP",
                    "RBI",
                    "SF",
                    "AVG",
                    "OBP",
                    "SLG",
                    "OPS",
                    "qualified",
                ],
            )
            .set_index("Name")
            .rename(
                columns={
                    "_1B": "1B",
                    "_2B": "2B",
                    "_3B": "3B",
                }
            )
        )
        df["AVG"] = df["AVG"].round(3)
        df["OBP"] = df["OBP"].round(3)
        df["SLG"] = df["SLG"].round(3)
        df["OPS"] = df["OPS"].round(3)

        return df

    def get_pitching_leaders(self) -> pd.DataFrame:
        result = self.__execute("SELECT * FROM pitching_leaders")
        result = result.fetchall()

        df = (
            pd.DataFrame(
                result,
                columns=[
                    "Name",
                    "Team",
                    "G",
                    "IP",
                    "H",
                    "R",
                    "ER",
                    "BB",
                    "SO",
                    "ERA",
                    "WHIP",
                    "K_BB",
                    "qualified",
                ],
            )
            .set_index("Name")
            .rename(columns={"K_BB": "K/BB"})
        )
        df["IP"] = df["IP"].round(1)
        df["ERA"] = df["ERA"].round(2)
        df["WHIP"] = df["WHIP"].round(2)
        df["K/BB"] = df["K/BB"].round(2)

        return df
