from apscheduler.schedulers.background import BackgroundScheduler
from bottle import jinja2_view, route, run, static_file
from db import Database, run_update_db_script

import numpy as np
import os
import pandas as pd


db = Database()


@route("/static/<filepath:path>")
def server_static(filepath):
    return static_file(filepath, root="static")


@route("/")
@jinja2_view("index")
def index():
    standings_df = db.get_standings()
    standings = {k: v.to_dict() for k, v in standings_df.T.items()}

    league_batting_df = db.get_league_batting()
    league_batting = {k: v.to_dict() for k, v in league_batting_df.T.items()}

    league_pitching_df = db.get_league_pitching()
    league_pitching = {k: v.to_dict() for k, v in league_pitching_df.T.items()}

    return {
        "standings": standings,
        "league_batting": league_batting,
        "league_pitching": league_pitching,
    }


def get_all_rate_stats_from_df(stats_df: pd.DataFrame) -> dict[dict[str, list[float]]]:
    all_rate_stats = {k: v.tolist() for k, v in stats_df.items()}
    all_rate_stats_final = {
        "all": {k: [] for k in all_rate_stats if k != "qualified"},
        "qualified": {k: [] for k in all_rate_stats if k != "qualified"},
    }
    for key in all_rate_stats_final["all"]:
        for i, value in enumerate(all_rate_stats[key]):
            if np.isnan(value):
                continue

            all_rate_stats_final["all"][key].append(value)
            if all_rate_stats["qualified"][i]:
                all_rate_stats_final["qualified"][key].append(value)
    return all_rate_stats_final


@route("/batting-leaders")
@jinja2_view("batting-leaders")
def batting_leaders():
    stats_df = db.get_batting_leaders()
    stats = {k: v.to_dict() for k, v in stats_df.T.items()}

    all_rate_stats_df = stats_df[
        [
            "AVG",
            "OBP",
            "SLG",
            "OPS",
            "wOBA",
            "qualified",
        ]
    ]
    all_rate_stats = get_all_rate_stats_from_df(all_rate_stats_df)

    return {
        "stats": stats,
        "all_rate_stats": all_rate_stats,
    }


@route("/pitching-leaders")
@jinja2_view("pitching-leaders")
def pitching_leaders():
    stats_df = db.get_pitching_leaders()
    stats = {k: v.to_dict() for k, v in stats_df.T.items()}

    all_rate_stats_df = stats_df[
        [
            "ERA",
            "WHIP",
            "K/BB",
            "qualified",
        ]
    ]
    all_rate_stats = get_all_rate_stats_from_df(all_rate_stats_df)

    return {
        "stats": stats,
        "all_rate_stats": all_rate_stats,
    }


@route("/linear-weights")
@jinja2_view("linear-weights")
def linear_weights():
    re24_df = db.get_re24()
    re24 = re24_df.to_dict()["expected_runs"]

    run_values_df = db.get_run_values().rename(columns={"run_value": "Run Value"})
    run_values = {k: v.to_dict() for k, v in run_values_df.T.items()}

    woba_weights_df = db.get_woba_weights().rename(columns={"weight": "Weight"})
    woba_weights = {k: v.to_dict() for k, v in woba_weights_df.T.items()}

    return {
        "re24": re24,
        "run_values": run_values,
        "woba_weights": woba_weights,
    }


if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_update_db_script, "cron", hour=16, minute=7)
    scheduler.start()

    run(host="localhost", port=8080, debug=True)
