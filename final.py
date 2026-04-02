
from flask import Flask, render_template, request, url_for, redirect,session
from sqlalchemy import create_engine,text
from datetime import datetime

app = Flask(__name__)


conn_str = "mysql://root:cset155@localhost/exam_website"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()

@app.route('/', methods = ['GET'])
def register():
    return  render_template("index.html",user=None) 

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

    return render_template("index.html",user=None)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['login_username']
    password = request.form['login_password']

    sql = text("SELECT account_id,username, password_hash FROM accounts WHERE username = :username")
    result = conn.execute(sql, {'username': username}).mappings().fetchone()

    if result:
        account_id = result['account_id'] 
        stored_password = result['password_hash']
        if stored_password == password:
            return redirect(url_for('test_page',user_id=account_id))
        else:
            return "Incorrect password"
    else:
        return "Username not found"






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





@app.route('/test_page/<int:user_id>',methods =["GET"])
def test_page(user_id):
    user = conn.execute(
    text("SELECT account_id, role FROM accounts WHERE account_id = :id"),
    {"id": user_id}
    ).mappings().fetchone()
    result = conn.execute(text("SELECT * FROM tests ORDER BY test_id DESC")).fetchall()
    return render_template("test_page.html",tests=result,user=user)





@app.route('/test_taken/<int:user_id>')
def test_taken(user_id):
    user = conn.execute(
    text("SELECT account_id, role FROM accounts WHERE account_id = :id"),
    {"id": user_id}
    ).mappings().fetchone()
    return render_template("test_taken.html",user=user)







@app.route('/test_create/<int:user_id>',methods=["GET", "POST"])
def test_create(user_id):
    user = conn.execute(
    text("SELECT account_id, role FROM accounts WHERE account_id = :id"),
    {"id": user_id}
    ).mappings().fetchone()
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
    return render_template("test_create.html",user=user)





@app.route('/delete/<int:user_id>', methods =["POST"])
def delete(user_id):
    test_id = request.form['test_id']
    user = conn.execute(
    text("SELECT account_id, role FROM accounts WHERE account_id = :id"),
    {"id": user_id}
    ).mappings().fetchone()
    conn.execute(
        text("DELETE FROM tests WHERE test_id = :test_id"),
        {"test_id": test_id}
    )
    return  redirect (url_for("test_page", user_id=user['account_id'])) 


@app.route('/logout')
def logout(): 
    return redirect(url_for('register'))



@app.route('/add_question/<int:user_id>', methods=['GET', 'POST'])
def add_question(user_id):
    user = conn.execute(
        text("SELECT account_id, role FROM accounts WHERE account_id = :id"),
        {"id": user_id}
    ).mappings().fetchone()

    questions = []

    if request.method == "POST":
        test_id = int(request.form['test_id'])
        question_text = request.form['question_text']
        points = int(request.form['points'])

        result = conn.execute(
            text("INSERT INTO questions (question_text, question_type, points) VALUES (:text, 'Short Answer', :points)"),
            {"text": question_text, "points": points}
        )
        question_id = result.lastrowid

        conn.execute(
            text("INSERT INTO test_questions (test_id, question_id) VALUES (:test_id, :question_id)"),
            {"test_id": test_id, "question_id": question_id}
        )
        
        questions = conn.execute(
            text("""SELECT q.* FROM questions q
                    JOIN test_questions tq ON q.question_id = tq.question_id
                    WHERE tq.test_id = :test_id
                    ORDER BY tq.question_order"""),
            {"test_id": test_id}
        ).fetchall()

    return render_template("add_question.html", user=user, questions=questions)


if __name__ == '__main__':
    app.run(debug=True)
