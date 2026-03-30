from flask import Flask, render_template
from sqlalchemy import create_engine,text

app = Flask(__name__)


conn_str = "mysql://root:cset155@localhost/exam_website"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()

@app.route('/')
def register():
    return  render_template("index.html") 


@app.route('/all_acount')
def all_acount():
    return  render_template("all_acount.html") 

@app.route('/test_create')
def test_create():
    return render_template("test_create.html")

@app.route('/test_page',methods =["GET"])
def test_page():
    result = conn.execute(text("SELECT * FROM tests ORDER BY created_at DESC")).fetchall()
    return render_template("test_page.html",tests = result)

@app.route('/test_taken')
def test_taken():
    return render_template("test_taken.html")


if __name__ == '__main__':
    app.run(debug=True)