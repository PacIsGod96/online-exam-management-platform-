@app.route('/test_create')
def test_create():
    return render_template("test_create.html")

@app.route('/test_page',method =["GET"])
def test_page():
    result = conn.execute(text("SELECT * FROM tests ORDER BY created_at DESC")).fetchall()
    return render_template("test_page.html",tests = result)

@app.route('/test_taken')
def test_taken():