from flask import request
import json


def get_pr_logs(db):
    pr_logs = db.execute(
                        """
                        SELECT *
                        FROM pr_logs
                        WHERE (pr_no, id) IN (
                            SELECT pr_no, MAX(id)
                            FROM pr_logs
                            GROUP BY pr_no
                        )
                        ORDER BY pr_no DESC;
                        """
                        )
    return pr_logs


def get_pr_log(db, pr_no, max_pr_id):
    pr_log = db.execute("""
                        SELECT * FROM pr_logs WHERE pr_no = ?
                        AND
                        id = ?;
                        """, pr_no, max_pr_id)[0]
    return pr_log


def get_max_pr_id(db, pr_no):
    max_pr_id = db.execute("""
                        SELECT MAX(id) as id
                        FROM pr_logs
                        WHERE pr_no = ?;""", pr_no)[0]['id']
    return max_pr_id


def get_pr_entries(db, pr_no, max_pr_id):
    pr_entries = db.execute("""SELECT * FROM pr_entries
                            JOIN pr_logs
                            ON pr_entries.pr_id = pr_logs.id
                            WHERE pr_logs.pr_no = ?
                            AND pr_logs.id = ?;""", pr_no, max_pr_id)
    return pr_entries


def get_pr_no(db, pr_id):
    pr_no = db.execute("""
                       SELECT pr_no
                       FROM pr_logs
                       WHERE id = ?
                       ;""", pr_id)[0]["pr_no"]
    return pr_no


def get_new_pr_no(db):
    new_pr_no = db.execute(
                            """
                            SELECT COALESCE(MAX(pr_no), 0) + 1 as new_pr_no
                            FROM pr_logs;
                            """
                            )[0]['new_pr_no']
    return new_pr_no


def get_log_form_data():
    log_form_attributes = ("pr-no", "title", "currency", "budget-line", "date", "total-cost")
    log_data = []
    for attribute in log_form_attributes:
        log_data.append(request.form.get(attribute))

    return log_data


def get_entries_form_data(db):
    entries_data_attributes = ("index[]", "description[]", "cost[]", "quantity[]", "total[]")
    entries_data = []
    for attribute in entries_data_attributes:
        entries_data.append(request.form.getlist(attribute))

    return entries_data


def get_pr_revisions(db, pr_no):
    pr_revisions = db.execute("""
                              SELECT *
                              FROM pr_revisions
                              JOIN pr_logs
                              ON pr_revisions.pr_id = pr_logs.id
                              WHERE pr_logs.pr_no = ?
                              ORDER BY datetime DESC;
                              """, pr_no)
    return pr_revisions


def insert_pr_log(db, pr_no, title, currency, budget_line, creation_date, total_cost):
    db.execute("""INSERT INTO pr_logs (pr_no, title, currency, budget_line, creation_date, total_cost) VALUES (?, ?, ?, ?, ?, ?);""",
               pr_no, title, currency, budget_line, creation_date, total_cost)


def get_latest_pr_id(db):
    return db.execute("SELECT MAX(id) as pr_id FROM pr_logs;")[0]['pr_id']


def insert_pr_entry(db, pr_id, index, description, cost, quantity, total):
    db.execute("""INSERT INTO pr_entries (pr_id, "index", description, cost, quantity, total) VALUES (?, ?, ?, ?, ?, ?);""",
               pr_id, index, description, cost, quantity, total)


def get_status_details(status):
    if status == "delete":
        return 1, "deleted", "danger"
    else:
        return 0, "restored", "success"


def update_pr_status(db, pr_no, status_bool):
    db.execute("""UPDATE pr_logs SET deleted = ? WHERE pr_no = ?;""", status_bool, pr_no)


def get_pr_log_by_id(db, pr_id):
    return db.execute("""SELECT * FROM pr_logs WHERE id = ?""", pr_id)[0]


def get_pr_entries_by_id(db, pr_id):
    return db.execute("""SELECT * FROM pr_entries WHERE pr_id = ?;""", pr_id)


def get_next_pr_id(db):
    return (db.execute("""SELECT MAX(id) as id FROM pr_logs;""")[0]['id']) + 1


def detect_changes(db, current_pr_id, current_pr_logs, revised_pr_logs, current_pr_entries, revised_pr_entries):
    bool_change = False
    log_change = {"type": "none", "changes": {}}

    for key, value in revised_pr_logs.items():
        cpl_value = current_pr_logs[key]
        if value != cpl_value:
            bool_change = True
            log_change["type"] = "modified"
            log_change["changes"][key] = cpl_value

    entries_changes = []
    max_len = max(len(current_pr_entries), len(revised_pr_entries))

    for i in range(max_len):
        entry_change = {"index": 0, "revision": {"type": "none", "changes": {}}}
        current_index = i + 1

        try:
            current_pr_entry = current_pr_entries[i]
            revised_pr_entry = revised_pr_entries[i]
            current_pr_entry.pop("revision")
            current_pr_entry.pop("pr_id")
            current_pr_entry.pop("id")

            for key, value in current_pr_entry.items():
                rpe_value = revised_pr_entry[key]
                if str(value) != str(rpe_value):
                    entry_change["revision"]["changes"][key] = value
                    entry_change["revision"]["type"] = "modified"
                    bool_change = True

        except IndexError:
            bool_change = True
            if len(current_pr_entries) > len(revised_pr_entries):
                entry_change["revision"]["type"] = "removed"
            else:
                entry_change["revision"]["type"] = "added"
                db.execute("""INSERT INTO pr_entries (pr_id, "index", description, cost, quantity, total) VALUES (?, ?, ?, ?, ?, ?);""",
                           current_pr_id, current_index, "", 0, 0, 0)

        entry_change["index"] = current_index
        entries_changes.append(entry_change)

    return bool_change, log_change, entries_changes


def update_revisions(db, current_pr_id, log_change, entries_changes):
    log_change_json = json.dumps(log_change)
    entries_changes_json = [{"index": entry_change["index"], "changes": json.dumps(entry_change["revision"])} for entry_change in entries_changes]

    db.execute("""UPDATE pr_logs SET revision = ? WHERE id = ?;""", log_change_json, current_pr_id)
    for entry_change_json in entries_changes_json:
        db.execute("""UPDATE pr_entries SET revision = ? WHERE pr_id = ? AND "index" = ?;""",
                   entry_change_json["changes"], current_pr_id, entry_change_json["index"])


def insert_pr_revision(db, current_pr_id):
    db.execute("""INSERT INTO pr_revisions (pr_id) VALUES (?);""", current_pr_id)
