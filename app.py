from flask import Flask, flash, redirect, render_template, request, url_for
from flask_session import Session
from cs50 import SQL
import helpers
import json

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///pr_logger.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"

    return response


# Head to index
@app.route("/")
def index():
    # Display logs from db
    pr_logs = helpers.get_pr_logs(db)

    return render_template("index.html", pr_logs=pr_logs)


# Create PR
@app.route("/create_pr", methods=["GET", "POST"])
def create_pr():
    if request.method == "GET":
        new_pr_no = helpers.get_new_pr_no(db)
        creation = True

        return render_template("process_pr_form.html", new_pr_no=new_pr_no, creation=creation)

    # Get form data
    pr_no, pr_title, pr_currency, pr_budget_line, pr_date, pr_total_cost = helpers.get_log_form_data()
    pr_indices, pr_descriptions, pr_costs, pr_quantities, pr_totals = helpers.get_entries_form_data(db)

    # Enter new pr values into db
    db.execute("""INSERT INTO pr_logs (pr_no, title, currency, budget_line, creation_date, total_cost) VALUES (?, ?, ?, ?, ?, ?);""",
                pr_no, pr_title, pr_currency, pr_budget_line, pr_date, pr_total_cost)

    # Assign pr id to connect indices with pr log
    pr_id = db.execute("SELECT MAX(id) as pr_id FROM pr_logs;")[0]['pr_id']

    for i in range(len(pr_indices)):
        db.execute("""INSERT INTO pr_entries (pr_id, "index", description, cost, quantity, total) VALUES (?, ?, ?, ?, ?, ?);""",
                    pr_id, pr_indices[i], pr_descriptions[i], pr_costs[i], pr_quantities[i], pr_totals[i])

    flash(f"PR {pr_no} was created successfully.", "info")
    return redirect("/")


@app.route("/toggle_pr_status", methods=["POST"])
def toggle_pr_status():
    pr_no = request.form.get('pr-no')
    status = request.form.get('status')

    if status == "delete":
        status_bool = 1
        status_text = "deleted"
        message_style = "danger"
    else:
        status_bool = 0
        status_text = "restored"
        message_style = "success"

    db.execute("""
               UPDATE pr_logs
               SET deleted = ?
               WHERE pr_no = ?;
               """, status_bool, pr_no)

    flash(f"PR {pr_no} has been {status_text} successfully.", message_style)

    return redirect("/")


@app.route("/view_pr")
def view_pr():
    pr_no = request.args.get('pr_no')
    max_pr_id = helpers.get_max_pr_id(db, pr_no)
    pr_log = helpers.get_pr_log(db, pr_no, max_pr_id)
    pr_entries = helpers.get_pr_entries(db, pr_no, max_pr_id)
    pr_revisions =  helpers.get_pr_revisions(db, pr_no)

    return render_template("view_pr.html", pr_log=pr_log, pr_entries=pr_entries, pr_revisions=pr_revisions)


@app.route("/view_revision")
def view_revision():
    pr_id = request.args.get('pr-id')
    pr_no = helpers.get_pr_no(db, pr_id)

    pr_log = db.execute("""
                         SELECT * FROM pr_logs WHERE id = ?
                         """, pr_id)[0]

    pr_entries = db.execute("""
                            SELECT * FROM pr_entries
                            WHERE pr_id = ?;
                            """, pr_id)

    pr_revisions = helpers.get_pr_revisions(db, pr_no)

    # Load back log revision json
    log_loaded_revision = json.loads(pr_log["revision"])
    pr_log["revision"] = log_loaded_revision

    # Load back entries revision json
    for entry in pr_entries:
        entry_loaded_revision = json.loads(entry["revision"])
        entry["revision"] = entry_loaded_revision

    # Boolean for if its a revision, to display the view_pr page differently
    bool_revision = True

    return render_template("view_pr.html", bool_revision=bool_revision, pr_log=pr_log, pr_entries=pr_entries, pr_revisions=pr_revisions)


@app.route("/revise_pr")
def revise_pr():
    pr_no = request.args.get('pr_no')
    max_pr_id = helpers.get_max_pr_id(db, pr_no)
    pr_log = helpers.get_pr_log(db, pr_no, max_pr_id)
    pr_entries = helpers.get_pr_entries(db, pr_no, max_pr_id)

    return render_template("process_pr_form.html", pr_log=pr_log, pr_entries=pr_entries)


@app.route("/update_pr", methods=["POST"])
def update_pr():
    # Get revised pr_logs from form data
    pr_no, pr_title, pr_currency, pr_budget_line, pr_date, pr_total_cost = helpers.get_log_form_data()
    pr_indices, pr_descriptions, pr_costs, pr_quantities, pr_totals = helpers.get_entries_form_data(db)

    current_pr_id = db.execute("""
                    SELECT MAX(id) as id FROM pr_logs
                    WHERE pr_no = ?
                    ;""", pr_no)[0]['id']

    revised_pr_id = (db.execute("""
                        SELECT MAX(id) as id FROM pr_logs
                        ;""")[0]['id']) + 1

    # Comparison between current and revised dicts to determine changes for highlighting in View PR
    # Get current log data
    current_pr_logs = db.execute("""
                                Select *
                                FROM pr_logs
                                WHERE id = ?;
                                """, current_pr_id)[0]

    # Get current entries data
    current_pr_entries = db.execute("""
                                    Select *
                                    FROM pr_entries
                                    WHERE pr_id = ?;
                                    """, current_pr_id)

    # Prepare revised log dict for comparison
    revised_pr_logs = {
                    "budget_line": pr_budget_line,
                    "creation_date": pr_date,
                    "currency": pr_currency,
                    "title": pr_title,
                    "total_cost": float(pr_total_cost),
                    }

    revised_pr_entries = []

    for i in range(len(pr_indices)):
        revised_pr_entry =   {
                        "cost": pr_costs[i],
                        "description": pr_descriptions[i],
                        "index": pr_indices[i],
                        "quantity": pr_quantities[i],
                        "total": pr_totals[i],
                        }

        revised_pr_entries.append(revised_pr_entry)

    # Compare between current and revised log dicts
    # If no changes, dont register anything into db. and return to page with message.
    bool_change = False

    #Assign dict template for later storing into db
    log_change = {
        "type": "none",
        "changes": {
        },
    }

    for key, value in revised_pr_logs.items():
        # Get current key's pr_logs value
        cpl_value = current_pr_logs[key]
        if value != cpl_value:
            bool_change = True
            log_change["type"] = "modified"
            log_change["changes"][key] = cpl_value

    # Entry changes
    # Assign dict template for later storing into db
    entries_changes = []
    max_len = 0
    len_cpe = len(current_pr_entries)
    len_rpe = len(revised_pr_entries)

    # if len is less then len_rpe, else if equal or more, just choose len_cpe
    if len_cpe < len_rpe:
        max_len = len_rpe
    else:
        max_len = len_cpe

    for i in range(max_len):
        entry_change = {
            "index": 0,
            "revision": {
                "type": "none",
                "changes": {},
                },
            }

        current_index = i + 1

        # Check if they're equal, if not then either added or removed
        try:
            current_pr_entry = current_pr_entries[i]
            revised_pr_entry = revised_pr_entries[i]

            # Remove columns that dont matter for comparison
            current_pr_entry.pop("revision")
            current_pr_entry.pop("pr_id")
            current_pr_entry.pop("id")

            for key, value in current_pr_entry.items():
                # Assign revised pr entry's value for comparison
                rpe_value = revised_pr_entry[key]

                if str(value) != str(rpe_value):
                    entry_change["revision"]["changes"][key] = value
                    entry_change["revision"]["type"] = "modified"
                    bool_change = True

        except IndexError:
            bool_change = True

            # If removed
            if len_cpe > len_rpe:
                #return [current_pr_entry, revised_pr_entry]
                entry_change["revision"]["type"] = "removed"

            # If added
            else:
                entry_change["revision"]["type"] = "added"

                db.execute("""
                            INSERT INTO pr_entries (pr_id, "index", description, cost , quantity , total)
                            VALUES (?, ?, ?, ?, ?, ?);
                           """, current_pr_id, current_index, "", 0, 0, 0)

        entry_change["index"] = current_index
        entries_changes.append(entry_change)

    if bool_change == False:
        #return to the same revision page
        flash("No changes detected, cannot submit revision.", "danger")
        return redirect(url_for('revise_pr', pr_no=pr_no))

    else:
        # Convert log_change dict into json format
        log_change_json = json.dumps(log_change)

        # Convert entry_changes dict into json format
        entries_changes_json = []

        for entry_change in entries_changes:
            entry_changes_json = {
                "index": entry_change["index"],
                "changes": json.dumps(entry_change["revision"]),
            }

            entries_changes_json.append(entry_changes_json)

        # Update log changes for the prev pr
        db.execute("""
                    UPDATE pr_logs
                    SET revision = ?
                    WHERE id = ?;
                """, log_change_json, current_pr_id)

        # Update entry changes for the prev pr
        for entry_change_json in entries_changes_json:
            db.execute("""
                        UPDATE pr_entries
                        SET revision = ?
                        WHERE pr_id = ?
                        AND "index" = ?;
                        """, entry_change_json["changes"], current_pr_id, entry_change_json["index"])

        # Enter new log into pr_logs
        db.execute("""
                    INSERT INTO pr_logs (pr_no, title, currency, budget_line , creation_date , total_cost)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,pr_no, pr_title, pr_currency, pr_budget_line, pr_date, pr_total_cost)

        # Enter new entries into pr_entries
        for i in range(len(pr_indices)):
            db.execute("""INSERT INTO pr_entries (pr_id, "index", description, cost, quantity, total)
                    VALUES (?, ?, ?, ?, ?, ?);""",
                        (revised_pr_id), pr_indices[i], pr_descriptions[i], pr_costs[i], pr_quantities[i], pr_totals[i])

        # Enter change into revision
        db.execute("""
                INSERT INTO pr_revisions (pr_id)
                VALUES (?);
                """, current_pr_id)

        #return current_log
        flash(f"PR {pr_no} was revised successfully.", "info")
        return redirect(url_for('view_pr', pr_no=pr_no))


@app.route("/cancel")
def cancel():
    flash("No changes were made.", "danger")
    return redirect("/")


if __name__ == "__main__":
    app.run()