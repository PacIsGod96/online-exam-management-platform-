from flask import Flask, render_template, request, url_for, redirect
from sqlalchemy import create_engine,text

app = Flask(__name__)


conn_str = "mysql://root:cset155@localhost/exam_website"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()

@app.route('/', methods = ['GET'])
def register():
    return  render_template("index.html") 

@app.route('/', methods = ['POST'])
def register_post():
    username = request.form['username']
    password_hash = request.form['password_hash']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    role = request.form['role']
    role_id = request.form['role_id']

    if role == "student":
        teacher_id = role_id
        student_id = None
    else:
        student_id = role_id
        teacher_id = None
    
    sql = text("""
        INSERT INTO accounts
        (username, password_hash, first_name, last_name, role, teacher_id, student_id)
        VALUES 
        (:username, :password_hash, :first_name, :last_name, :role, :teacher_id, :student_id)
    """)

    conn.execute(sql, {
        'username': username,
        'password_hash': password_hash,
        'first_name': first_name,
        'last_name': last_name,
        "role": role,
        'teacher_id': teacher_id,
        'student_id': student_id
    })
    conn.commit()

    return render_template("index.html")

@app.route('/login', methods=['POST'])
def login():
    username = request.form['login_username']
    password = request.form['login_password']

    sql = text("SELECT username, password_hash FROM accounts WHERE username = :username")
    result = conn.execute(sql, {'username': username}).fetchone()

    if result:
        stored_password = result[1]
        if stored_password == password:
            return redirect(url_for('test_page'))
        else:
            return "Incoorect password"
    else:
        return "Username not found"

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