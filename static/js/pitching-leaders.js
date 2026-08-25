function numberEnding(number) {
    if (number >= 4 && number <= 20) {
        return "th";
    }

    const digit = number % 10;
    switch (digit) {
        case 1:
            return "st";
        case 2:
            return "nd";
        case 3:
            return "rd";
        default:
            return "th";
    }
}

function areAnyRowsHighlighted() {
    const rowsArray = Array.from(document.querySelectorAll("#pitching-stats tbody tr"));
    const highlightedRows = rowsArray.filter(tr => tr.classList.contains("highlight"));
    return highlightedRows.length > 0;
}

function updateDownloadButton() {
    const downloadButton = document.getElementById("download");
    if (areAnyRowsHighlighted()) {
        downloadButton.textContent = "Download selected rows as CSV";
    } else {
        downloadButton.textContent = "Download as CSV";
    }
}

let filteredRateStats = structuredClone(allRateStats);

function filterNonQualified() {
    const filterQualifiedChecked = document.querySelector("#filter-qualified").checked;

    filteredRateStats = structuredClone(allRateStats);
    if (filterQualifiedChecked) {
        for (const [key, arr] of Object.entries(filteredRateStats)) {
            filteredRateStats[key] = arr.filter((x) => x.qualified).map((x) => x.value);
        }

        document.querySelectorAll("#pitching-stats tbody tr").forEach((tr) => {
            if (!tr.classList.contains("qualified")) {
                tr.classList.add("hidden");
            }
        });
    } else {
        for (const [key, arr] of Object.entries(allRateStats)) {
            filteredRateStats[key] = arr.map((x) => x.value);
        }

        document.querySelectorAll("#pitching-stats tbody tr").forEach((tr) => {
            tr.classList.remove("hidden");
        });
    }

    // un-highlight any hidden rows
    document.querySelectorAll("#pitching-stats tbody tr.hidden.highlight").forEach((tr) => {
        tr.classList.remove("highlight");
    });
}

function setPercentileColours() {
    const higherIsBetter = {
        "ERA": false,
        "WHIP": false,
        "K/BB": true,
    };

    const goodColor = "#ff4b4b";
    const badColor = "#4b57ff";
    const neutralColor = "white";
    const percentileCutoff = 0.5;

    document.querySelectorAll("#pitching-stats tbody tr").forEach((tr) => {
        tr.querySelectorAll("td").entries().forEach(([index, td]) => {
            if (td.textContent === "-") {
                return;
            }

            const thName = document.querySelectorAll("#pitching-stats thead th")[index].textContent;
            if (!allRateStats[thName]) {
                return;
            }

            let numBelow;
            if (higherIsBetter[thName]) {
                numBelow = filteredRateStats[thName].filter((x) => x < td.textContent).length;
            } else {
                numBelow = filteredRateStats[thName].filter((x) => x > td.textContent).length;
            }
            const percentile = numBelow / filteredRateStats[thName].length;

            const percentileInt = Math.round(100 * percentile);
            const ending = numberEnding(percentileInt);
            const qualified = document.querySelector("#filter-qualified").checked ? "qualified" : "all";
            td.title = `${percentileInt}${ending} percentile in ${thName} (${qualified})`;

            if (percentile >= percentileCutoff) {
                let neutralPct = 1 - percentile;
                let goodPct = percentile - 1 + percentileCutoff;
                neutralPct = 100 * (neutralPct / percentileCutoff);
                goodPct = 100 * (goodPct / percentileCutoff);
                td.style.backgroundColor = `color-mix(in oklab, ${neutralColor} ${neutralPct}%, ${goodColor} ${goodPct}%)`;
            } else if (percentile <= percentileCutoff) {
                let neutralPct = percentile;
                let badPct = percentileCutoff - percentile;
                neutralPct = 100 * (neutralPct / percentileCutoff);
                badPct = 100 * (badPct / percentileCutoff);
                td.style.backgroundColor = `color-mix(in oklab, ${neutralColor} ${neutralPct}%, ${badColor} ${badPct}%)`;
            }
        });
    });
}

function getTableAsCSV() {
    const headings = Array.from(document.querySelectorAll("#pitching-stats thead th")).map(th => th.textContent);

    let rowsArray = Array.from(document.querySelectorAll("#pitching-stats tbody tr"));
    const filterQualified = document.querySelector("#filter-qualified").checked;
    const filterHighlighted = areAnyRowsHighlighted();
    if (filterQualified) {
        rowsArray = rowsArray.filter(tr => tr.classList.contains("qualified"));
    }
    if (filterHighlighted) {
        rowsArray = rowsArray.filter(tr => tr.classList.contains("highlight"));
    }

    const values = rowsArray.map(tr => Array.from(tr.querySelectorAll("td")).map(td => td.textContent));

    const rows = [headings].concat(values);
    const csv = rows.map(row => row.join(",")).join("\n");

    return csv;
}

function downloadTableAsCSV() {
    const csv = getTableAsCSV();
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);

    document.getElementById("download").href = url;
}

document.addEventListener("DOMContentLoaded", function () {
    new DataTable("#pitching-stats", {
        paging: false,
        info: false,
        layout: {
            topStart: "search",
            topEnd: null,
        },
        order: [[0, "asc"]],
    });

    // add heading titles
    document.querySelectorAll("#pitching-stats thead th").forEach((th) => {
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

    // filter qualified
    filterNonQualified();
    document.querySelector("#filter-qualified").addEventListener("change", _ => {
        filterNonQualified();
        setPercentileColours();
        updateDownloadButton();
    });

    // format the data
    document.querySelectorAll("#pitching-stats tbody tr").forEach((tr) => {
        tr.addEventListener("click", () => {
            tr.classList.toggle("highlight");
            updateDownloadButton();
        });
    });

    document.querySelectorAll("#pitching-stats tbody tr").forEach((tr) => {
        tr.querySelectorAll("td").entries().forEach(([index, td]) => {
            if (index <= 3) {
                return;
            }
            if (td.textContent === "nan") {
                td.textContent = "-";
                return;
            }
            if (!td.textContent.includes(".")) {
                return;
            }

            const decimals = td.textContent.split(".")[1];
            if (decimals.length < 2) {
                td.textContent += "0".repeat(2 - decimals.length);
            }
        });
    });

    // set colours by percentiles
    setPercentileColours();
});
