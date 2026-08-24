function setupStandingsTable() {
    new DataTable("#standings", {
        paging: false,
        info: false,
        layout: {
            topStart: null,
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
        });
    });

    document.querySelectorAll("#standings tbody tr").forEach((tr) => {
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

document.addEventListener("DOMContentLoaded", function () {
    setupStandingsTable();
});
