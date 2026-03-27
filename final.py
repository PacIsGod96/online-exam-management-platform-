from flask import Flask, render_template
from sqlalchemy import create_engine

app = Flask(__name__)


conn_str = "mysql://root:cset155@localhost/exam_website"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()




@app.route('/all_acount')
def index():
    return  render_template("all_acount.html") 
@app.route('/')
def home():
    return render_template("base.html")





if __name__ == '__main__':
    app.run(debug=True)