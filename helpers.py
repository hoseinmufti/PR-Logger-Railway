from flask import request


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
