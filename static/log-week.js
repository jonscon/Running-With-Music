/** Running Log Functions */

const input = document.getElementById("select-week"); // Dropdown
const table = document.getElementById("running-log"); // Table container
const tableRows = document.getElementsByTagName("tr"); // All rows in the table
const weekHeader = document.getElementById("week-header"); // Week header
const week = document.getElementsByClassName("week"); // Week column
const deleteButtons = document.getElementsByClassName("log-x-button"); // Delete buttons for each run

/* --------- Filter By Week Function --------- */

function filterByWeek() {
    // If user selects the default option:
    if (input.value === "--Select a week to filter by--") {
        weekHeader.classList.add("hidden"); // Hide "Week" header
        Array.from(week).forEach(w =>  w.classList.remove("hidden")); // Show "Week" column
        Array.from(tableRows).forEach(run => run.classList.remove("hidden")); // Show all rows
        return;
    }

    // Change header to reflect the week chosen
    weekHeader.innerHTML = input.value;
    weekHeader.classList.remove("hidden");

    // Hide the "Week" column for a cleaner look
    Array.from(week).forEach(w =>  w.classList.add("hidden"));

    for (let i = 0; i < tableRows.length; i++) {
        td = tableRows[i].getElementsByTagName("td")[1];
        if (td) {
            if (td.innerHTML.indexOf(input.value) > -1) {
                tableRows[i].classList.remove("hidden");
            }
            else {
                tableRows[i].classList.add("hidden");
            }
        }
    }
}

/* --------- Delete Run Function --------- */

// Delete run on client side
function deleteRunOnClient(row) {
    row.remove();
}

// Delete run on server side
function deleteRun(e) {
    e.preventDefault();

    // Run ID to reference which record to delete
    let run_id = e.target.parentElement.parentElement.id

    // Set up dictionary with the run id and stringify it
    const dict = {'run_id' : run_id};
    const s = JSON.stringify(dict)

    // Send an AJAX request to app.py to delete run from database
    $.ajax({
        url: '/delete-run',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(s),
        success: deleteRunOnClient(e.target.parentElement.parentElement)
    })
}

/* --------- Event Listeners --------- */

(Array.from(deleteButtons)).forEach(button => {
    button.addEventListener('click', deleteRun);
})