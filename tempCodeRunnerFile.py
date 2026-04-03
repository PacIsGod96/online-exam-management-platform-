@app.route('/test_create/<int:user_id>',methods=["GET", "POST"])
def test_create(user_id):
    user = conn.execute(
    text("SELECT account_id, role, first_name, last_name FROM accounts WHERE account_id = :id"),
    {"id": user_id}
    ).mappings().fetchone()
    if request.method == "POST":
        title = request.form["title"]
        test_disc = request.form ["test_disc"]
        created_by = request.form ["created_by"]
        teacher_name = user['first_name'] + " " + user['last_name']

        conn.execute(
            text(
                "INSERT INTO tests (title, test_disc, created_by) "
                "VALUES (:title, :test_disc, :created_by)"
            ),
            {"title": title, "test_disc": test_disc, "created_by": teacher_name}
        )

        conn.commit()


    return render_template("test_create.html",user=user)