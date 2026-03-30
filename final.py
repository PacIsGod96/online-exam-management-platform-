from flask import Flask, render_template,request,url_for,redirect
from sqlalchemy import create_engine,text
from datetime import datetime

app = Flask(__name__)


conn_str = "mysql://root:cset155@localhost/exam_website"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()

@app.route('/')
def register():
    return  render_template("index.html") 






@app.route('/all_acount')
def all_acount():
    result = conn.execute(text("SELECT * FROM acounts ORDER BY created_at DESC")).fetchall()
    
    return  render_template("all_acount.html") 





@app.route('/test_page',methods =["GET"])
def test_page():
    result = conn.execute(text("SELECT * FROM accounts ORDER BY created_at DESC")).fetchall()
    return render_template("test_page.html",accounts = result)





@app.route('/test_taken')
def test_taken():
    return render_template("test_taken.html")







@app.route('/test_create',methods=["GET", "POST"])
def test_create():
    if request.method == "POST":
        title = request.form["title"]
        test_disc = request.form ["test_disc"]
        created_by = request.form ["created_by"]

        conn.execute(
            text(
                "INSERT INTO tests (title, test_disc, created_by) "
                "VALUES (:title, :test_disc, :created_by)"
            ),
            {"title": title, "test_disc": test_disc, "created_by": created_by}
        )
    return render_template("test_create.html")





@app.route('/delete', methods =["POST"])
def delete():
    test_id = request.form['test_id']
    
    conn.execute(
        text("DELETE FROM tests WHERE test_id = :test_id"),
        {"test_id": test_id}
    )
    return  redirect (url_for("test_page")) 



if __name__ == '__main__':
    app.run(debug=True)