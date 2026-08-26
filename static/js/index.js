function areAnyRowsHighlighted(tableId) {
    const rowsArray = Array.from(document.querySelectorAll(`#${tableId} tbody tr`));
    const highlightedRows = rowsArray.filter(tr => tr.classList.contains("highlight"));
    return highlightedRows.length > 0;
}

function getTableAsCSV(id) {
    const headings = Array.from(document.querySelectorAll(`#${id} thead th`)).map(th => th.textContent);

    let rowsArray = Array.from(document.querySelectorAll(`#${id} tbody tr`));
    if (areAnyRowsHighlighted(id)) {
        rowsArray = rowsArray.filter(tr => tr.classList.contains("highlight"));
    }

    const values = rowsArray.map(tr => Array.from(tr.querySelectorAll("td")).map(td => td.textContent));

    const rows = [headings].concat(values);
    const csv = rows.map(row => row.join(",")).join("\n");

    return csv;
}

function updateDownloadButton(tableId) {
    const downloadButton = document.getElementById(`download-${tableId}`);
    if (areAnyRowsHighlighted(tableId)) {
        downloadButton.textContent = "Download selected rows as CSV";
    } else {
        downloadButton.textContent = "Download as CSV";
    }
}

function downloadStandingsAsCSV() {
    const csv = getTableAsCSV("standings");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);

    document.getElementById("download-standings").href = url;
}

function setupStandingsTable() {
    new DataTable("#standings", {
        paging: false,
        info: false,
        layout: {
            topEnd: null,
        },
        order: [[4, "desc"]],
    });

    // add heading titles
    document.querySelectorAll("#standings thead th").forEach((th) => {
        switch (th.textContent.toLowerCase()) {
            case "w":
                th.title = "Wins";
                break;
            case "l":
                th.title = "Losses";
                break;
            case "t":
                th.title = "Ties";
                break;
            case "pct":
                th.title = "Win Percentage";
                break;
            case "gb":
                th.title = "Games Behind";
                break;
        }
    });

    // format the data
    document.querySelectorAll("#standings tbody tr").forEach((tr) => {
        tr.addEventListener("click", () => {
            tr.classList.toggle("highlight");
            updateDownloadButton("standings");
        });

        tr.querySelectorAll("td").entries().forEach(([index, td]) => {
            const thName = document.querySelectorAll("#standings thead th")[index].textContent;

            if (["W", "L", "T"].includes(thName) && td.textContent.includes(".")) {
                td.textContent = td.textContent.split(".")[0];
                return;
            }
            if (thName === "PCT") {
                td.textContent = td.textContent.replace(/^0\./, ".");
                const decimals = td.textContent.split(".")[1];
                if (decimals.length < 3) {
                    td.textContent += "0".repeat(3 - decimals.length);
                }
                return;
            }
            if (thName === "GB") {
                td.textContent = td.textContent.replace(/\.0$/, "");
                if (td.textContent === "0") {
                    td.textContent = "-";
                }
                return;
            }
        });
    });
}

function downloadLeagueBattingAsCSV() {
    const csv = getTableAsCSV("league-batting");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);

    document.getElementById("download-league-batting").href = url;
}

function setupLeagueBattingTable() {
    new DataTable("#league-batting", {
        paging: false,
        info: false,
        layout: {
            topEnd: null,
        },
    });

    // add heading titles
    document.querySelectorAll("#league-batting thead th").forEach((th) => {
        switch (th.textContent.toLowerCase()) {
            case "g":
                th.title = "Games Played";
                break;
            case "ab":
                th.title = "At Bats";
                break;
            case "pa":
                th.title = "Plate Appearances";
                break;
            case "h":
                th.title = "Hits";
                break;
            case "1b":
                th.title = "Singles";
                break;
            case "2b":
                th.title = "Doubles";
                break;
            case "3b":
                th.title = "Triples";
                break;
            case "hr":
                th.title = "Home Runs";
                break;
            case "so":
                th.title = "Strikeouts";
                break;
            case "bb":
                th.title = "Bases on Balls";
                break;
            case "hbp":
                th.title = "Hit by Pitches";
                break;
            case "rbi":
                th.title = "Runs Batted In";
                break;
            case "sf":
                th.title = "Sacrifice Flies";
                break;
            case "avg":
                th.title = "Batting Average";
                break;
            case "obp":
                th.title = "On-Base Percentage";
                break;
            case "slg":
                th.title = "Slugging Percentage";
                break;
            case "ops":
                th.title = "On-base Plus Slugging";
                break;
        }
    });

    // format the data
    document.querySelectorAll("#league-batting tbody tr").forEach((tr) => {
        tr.addEventListener("click", () => {
            tr.classList.toggle("highlight");
            updateDownloadButton("league-batting");
        });

        const team = tr.children[0].textContent;
        if (team === "League") {
            tr.classList.add("league");
        }

        tr.querySelectorAll("td").entries().forEach(([index, td]) => {
            const thName = document.querySelectorAll("#league-batting thead th")[index].textContent;

            if (!td.textContent.includes(".")) {
                return;
            }
            if (!["AVG", "OBP", "SLG", "OPS", "wOBA"].includes(thName)) {
                td.textContent = td.textContent.split(".")[0];
            } else {
                td.textContent = td.textContent.replace(/^0\./, ".");
                const decimals = td.textContent.split(".")[1];
                if (decimals.length < 3) {
                    td.textContent += "0".repeat(3 - decimals.length);
                }
            }
        });
    });
}

function downloadLeaguePitchingAsCSV() {
    const csv = getTableAsCSV("league-pitching");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);

    document.getElementById("download-league-pitching").href = url;
}

function setupLeaguePitchingTable() {
    new DataTable("#league-pitching", {
        paging: false,
        info: false,
        layout: {
            topEnd: null,
        },
    });

    // add heading titles
    document.querySelectorAll("#league-pitching thead th").forEach((th) => {
        switch (th.textContent.toLowerCase()) {
            case "g":
                th.title = "Games Played";
                break;
            case "ip":
                th.title = "Innings Pitched";
                break;
            case "h":
                th.title = "Hits Allowed";
                break;
            case "r":
                th.title = "Runs Allowed";
                break;
            case "er":
                th.title = "Earned Runs Allowed";
                break;
            case "bb":
                th.title = "Bases on Balls";
                break;
            case "so":
                th.title = "Strikeouts";
                break;
            case "era":
                th.title = "Earned Run Average";
                break;
            case "whip":
                th.title = "Walks Plus Hits per Inning Pitched";
                break;
            case "k/bb":
                th.title = "Strikeout to Walk Ratio";
                break;
        }
    });

    // format the data
    document.querySelectorAll("#league-pitching tbody tr").forEach((tr) => {
        tr.addEventListener("click", () => {
            tr.classList.toggle("highlight");
            updateDownloadButton("league-pitching");
        });

        const team = tr.children[0].textContent;
        if (team === "League") {
            tr.classList.add("league");
        }

        tr.querySelectorAll("td").entries().forEach(([index, td]) => {
            const thName = document.querySelectorAll("#league-pitching thead th")[index].textContent;

            if (!td.textContent.includes(".")) {
                return;
            }
            if (thName === "IP") {
                const decimals = td.textContent.split(".")[1];
                if (decimals.length < 1) {
                    td.textContent += "0";
                }
            } else if (!["ERA", "WHIP", "K/BB"].includes(thName)) {
                td.textContent = td.textContent.split(".")[0];
            } else {
                td.textContent = td.textContent.replace(/^0\./, ".");
                const decimals = td.textContent.split(".")[1];
                if (decimals.length < 2) {
                    td.textContent += "0".repeat(2 - decimals.length);
                }
            }
        });
    });
}

document.addEventListener("DOMContentLoaded", function () {
    setupStandingsTable();
    setupLeagueBattingTable();
    setupLeaguePitchingTable();
});
