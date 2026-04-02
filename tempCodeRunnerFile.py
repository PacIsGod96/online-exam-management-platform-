@app.route('/all_acount/<int:user_id>')
def all_acount(user_id):
    role = request.args.get("role")
    user = conn.execute(
        text("SELECT account_id, role FROM accounts WHERE account_id = :id"),
        {"id": user_id}
    ).mappings().fetchone()
    if role:
        sql = text("""
            SELECT *
            FROM accounts
            WHERE role = :role
            ORDER BY account_id DESC
        """)
        result = conn.execute(sql, {"role": role}).fetchall()
    else:
        result = conn.execute(
            text("SELECT * FROM accounts ORDER BY account_id DESC")
        ).fetchall()

    return render_template("all_acount.html", accounts=result,user=user)