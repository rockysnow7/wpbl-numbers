from bottle import jinja2_view, route, run, static_file
from db import Database

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


def get_all_rate_stats_from_df(stats_df: pd.DataFrame) -> dict:
    all_rate_stats = {k: v.dropna().tolist() for k, v in stats_df.items()}
    all_rate_stats_final = {k: [] for k in all_rate_stats if k != "qualified"}
    for key, values in all_rate_stats_final.items():
        for i, value in enumerate(all_rate_stats[key]):
            v = {
                "value": value,
                "qualified": all_rate_stats["qualified"][i],
            }
            values.append(v)
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


if __name__ == "__main__":
    run(host="localhost", port=8080, debug=True, reloader=True)
