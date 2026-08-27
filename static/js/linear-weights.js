function toTitleCase(str) {
    return str.replace(
        /\w\S*/g,
        text => text.charAt(0).toUpperCase() + text.substring(1).toLowerCase()
    );
}

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

function downloadRE24AsCSV() {
    const csv = getTableAsCSV("re24");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);

    document.getElementById("download-re24").href = url;
}

function setupRE24Table() {
    new DataTable("#re24", {
        paging: false,
        info: false,
        layout: {
            topEnd: null,
        },
    });

    // format the data
    document.querySelectorAll("#re24 tbody tr").forEach((tr) => {
        tr.addEventListener("click", () => {
            tr.classList.toggle("highlight");
            updateDownloadButton("re24");
        });

        tr.querySelectorAll("td").entries().forEach(([index, td]) => {
            if (index === 0) {
                return;
            }

            const decimals = td.textContent.split(".")[1];
            if (decimals.length < 2) {
                td.textContent += "0".repeat(2 - decimals.length);
            }
        });
    });
}

function downloadRunValuesAsCSV() {
    const csv = getTableAsCSV("run-values");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);

    document.getElementById("download-run-values").href = url;
}

function setupRunValuesTable() {
    new DataTable("#run-values", {
        paging: false,
        info: false,
        layout: {
            topEnd: null,
        },
    });

    // format the data
    document.querySelectorAll("#run-values tbody tr").forEach((tr) => {
        tr.addEventListener("click", () => {
            tr.classList.toggle("highlight");
            updateDownloadButton("run-values");
        });

        // make event type names prettier
        tr.querySelectorAll("td").entries().forEach(([index, td]) => {
            const thName = document.querySelectorAll("#run-values thead th")[index].textContent;
            switch (thName) {
                case "Event Type":
                    td.textContent = td.textContent.replaceAll("_", " ");
                    td.textContent = toTitleCase(td.textContent);
                    td.textContent = td.textContent.replaceAll("By", "by");
                    td.textContent = td.textContent.replaceAll("On", "on");
                    td.textContent = td.textContent.replaceAll("Fielders", "Fielder's");
                    break;
                case "Run Value":
                    const decimals = td.textContent.split(".")[1];
                    if (decimals.length < 3) {
                        td.textContent += "0".repeat(3 - decimals.length);
                    }
                    break;
            }
        });
    });
}

function downloadWOBAWeightsAsCSV() {
    const csv = getTableAsCSV("woba-weights");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);

    document.getElementById("download-woba-weights").href = url;
}

function setupWOBAWeightsTable() {
    new DataTable("#woba-weights", {
        paging: false,
        info: false,
        layout: {
            topEnd: null,
        },
    });

    // format the data
    document.querySelectorAll("#woba-weights tbody tr").forEach((tr) => {
        tr.addEventListener("click", () => {
            tr.classList.toggle("highlight");
            updateDownloadButton("woba-weights");
        });

        // make event type names prettier
        tr.querySelectorAll("td").entries().forEach(([index, td]) => {
            const thName = document.querySelectorAll("#woba-weights thead th")[index].textContent;
            switch (thName) {
                case "Event Type":
                    td.textContent = td.textContent.replaceAll("_", " ");
                    td.textContent = toTitleCase(td.textContent);
                    td.textContent = td.textContent.replaceAll("By", "by");
                    break;
                case "Weight":
                    const decimals = td.textContent.split(".")[1];
                    if (decimals.length < 3) {
                        td.textContent += "0".repeat(3 - decimals.length);
                    }
                    break;
            }
        });
    });
}

document.addEventListener("DOMContentLoaded", function () {
    setupRE24Table();
    setupRunValuesTable();
    setupWOBAWeightsTable();
});
