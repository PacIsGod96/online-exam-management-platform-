
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
    try:
        user = conn.execute(
        text("SELECT account_id, role, first_name, last_name FROM accounts WHERE account_id = :id"),
        {"id": user_id}
        ).mappings().fetchone()

        teacher_name = user['first_name'] + " " + user['last_name']

        if user['role'] == 'teacher':
            tests = conn.execute(
                text("SELECT * FROM tests ORDER BY test_id DESC")
            ).mappings().fetchall()
        else:
            tests = conn.execute(
                text("SELECT * FROM tests WHERE published = TRUE ORDER BY test_id DESC")
            ).mappings().fetchall()

            taken_tests = [row['test_id'] for row in conn.execute(
                text("SELECT test_id FROM StudentAnswers WHERE student_id=:sid"),
                {"sid": user_id}
            ).mappings().fetchall()]

        return render_template("test_page.html", tests=tests, user=user, taken_tests=taken_tests if user['role']=='student' else [])
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error: {e}", 500





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
    text("SELECT account_id, role, first_name, last_name FROM accounts WHERE account_id = :id"),
    {"id": user_id}
    ).mappings().fetchone()
    if request.method == "POST":
        title = request.form["title"]
        test_disc = request.form ["test_disc"]
        created_by = request.form ["created_by"]
        teacher_name = user['first_name'] + " " + user['last_name']

        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO tests (title, test_disc, created_by) "
                    "VALUES (:title, :test_disc, :created_by)"
                ),
                {"title": title, "test_disc": test_disc, "created_by": created_by}
            )

        return redirect(url_for('test_page', user_id=user_id))


    return render_template("test_create.html",user=user)


@app.route('/publish_test/<int:user_id>/<int:test_id>', methods=["POST"])
def publish_test(user_id, test_id):
    conn.execute(
        text("UPDATE tests SET published = TRUE WHERE test_id = :tid"),
        {"tid": test_id}
    )
    conn.commit()
    return redirect(url_for('test_page', user_id=user_id))


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






@app.route('/add_question/<int:user_id>/<int:test_id>', methods=['GET', 'POST'])
def add_question(user_id, test_id):
    user = conn.execute(
        text("SELECT account_id, role FROM accounts WHERE account_id = :id"),
        {"id": user_id}
    ).mappings().fetchone()

    print("DEBUG: user =", user)
    print("DEBUG: test_id =", test_id)

    questions = []

    if request.method == "POST":
        question_text = request.form['question_text']
        points = int(request.form['points'])
        question_type = request.form['question_type']

        result = conn.execute(
            text("INSERT INTO questions (question_text, question_type, points) VALUES (:text, :qtype, :points)"),
            {"text": question_text, "qtype": question_type, "points": points}
        )
        question_id = result.lastrowid

        conn.execute(
            text("INSERT INTO test_questions (test_id, question_id) VALUES (:test_id, :question_id)"),
            {"test_id": test_id, "question_id": question_id}
        )

        if question_type == "MCQ":
            for i in range(1, 5): 
                answer_text = request.form.get(f"answer_text_{i}")
                is_correct = 1 if request.form.get(f"is_correct_{i}") else 0
                if answer_text:
                    conn.execute(
                        text("INSERT INTO answers (question_id, answer_text, is_correct) VALUES (:qid, :text, :correct)"),
                        {"qid": question_id, "text": answer_text, "correct": is_correct}
                    )

        questions = conn.execute(
            text("""SELECT q.* FROM questions q
                    JOIN test_questions tq ON q.question_id = tq.question_id
                    WHERE tq.test_id = :test_id
                    ORDER BY tq.question_order"""),
            {"test_id": test_id}
        ).fetchall()

        conn.commit()

    return render_template("add_question.html", user=user, questions=questions, test_id=test_id)

@app.route('/take_test/<int:student_id>/<int:test_id>', methods=['GET','POST'])
def take_test(student_id, test_id):
    user = conn.execute(
        text("SELECT * FROM accounts WHERE account_id = :id"),
        {"id": student_id}
    ).mappings().fetchone()

    already_taken = conn.execute(
        text("SELECT * FROM StudentAnswers WHERE student_id=:sid AND test_id=:tid"),
        {"sid": student_id, "tid": test_id}
    ).fetchone()
    
    if already_taken:
        return "You have already taken this test.", 403
    
    if request.method == "POST":
        for key in request.form:
            if key.startswith("q_"):
                qid = int(key.split("_")[1])
                value = request.form[key]
                
                qtype = conn.execute(
                    text("SELECT question_type FROM questions WHERE question_id=:qid"),
                    {"qid": qid}
                ).scalar()

                if qtype == "MCQ" and value.isdigit():
                    answer_id = int(value)
                    submitted_answer = None

                    result = conn.execute(
                        text("SELECT is_correct FROM answers WHERE answer_id=:aid"),
                        {"aid": answer_id}
                    ).fetchone()
                    
                    if result:
                        is_correct = result[0]
                    else: 
                        answer_id = None
                        is_correct = 0
                else:
                    answer_id = None
                    submitted_answer = value
                    is_correct = 0

                conn.execute(
                    text("""
                        INSERT INTO StudentAnswers
                        (student_id, test_id, question_id, answer_id, submitted_answer, is_correct)
                        Values (:sid, :tid, :qid, :aid, :sub_ans, :correct)
                    """),
                    {"sid": student_id, "tid":test_id, "qid": qid, "aid": answer_id, "sub_ans": submitted_answer, "correct": is_correct}
                )
        conn.commit()
        return redirect(url_for('test_taken', user_id=student_id))
    rows = conn.execute(
        text("""
            SELECT q.question_id, q.question_text, q.question_type, q.points, a.answer_id, a.answer_text
            FROM test_questions tq
            JOIN questions q ON tq.question_id = q.question_id
            LEFT JOIN answers a ON q.question_id = a.question_id
            WHERE tq.test_id=:tid
            ORDER BY tq.question_order
        """), {"tid": test_id}
    ).fetchall()

    questions = {}

    for row in rows:
        qid = row.question_id
        if qid not in questions:
            questions[qid] = {
                "text": row.question_text,
                "type": row.question_type,
                "answers": []
            }
        if row.answer_id:
            questions[qid]["answers"].append({"id":row.answer_id, "text": row.answer_text})

    return render_template("take_test.html", user=user, test_id=test_id, questions=questions)

@app.route('/test_taken/<int:user_id>')
def test_results(user_id):
    user = conn.execute(
        text("SELECT * FROM accounts WHERE account_id = :id"),
        {"id": user_id}
    ).mappings().fetchone()

    return render_template("test_taken.html", user=user)
    
@app.route('/submit_test/<int:user_id>/<int:test_id>', methods=['POST'])
def submit_test(user_id, test_id):
    for key in request.form:
        if key.startwith("q_"):
            question_id = int(key.split("_")[1])
            value = request.form[key]

            answer_id = None 
            submitted_text = None

            if value.isdigit():
                answer_id = int(value)
            else: 
                submitted_text = value

            is_correct = 0
            if answer_id:
                result = conn.execute(text("""
                    SELECT is_correct FROM answers
                    WHERE answer_id = :aid
                """), {"aid": answer_id}).fetchnone()

                if result and result[0] == 1:
                    is_correct = 1

            conn.execute(text("""
                INSERT INTO StudentAnswers
                (student_id, test_id, question_id, answer_id, submitted_id, is_correct)
                VALUES  (:student_id, :test_id, :question_id, :answer_id, :submitted_answer, :is_correct)
            """), {
                "student_id": user_id,
                "test_id": test_id,
                "question_id": question_id,
                "answer_id": answer_id,
                "submitted_answer": submitted_text,
                "is_correct": is_correct
            })
        conn.commit()

        return redirect(url_for('test_taken', user_id=user_id))
    
@app.route('/tests/,int:user_id')
def all_tests(user_id):
    user = conn.execute(
        text("SELECT account_id, role, FROM accounts WHERE account_id = :id"),
        {"id": user_id}
    ).mappings().fetchone()

    tests = conn.execute(
        text("SELECT * FROM tests WHERE published = TRUE ORDER BY test_id DESC")
    ).mappings().fetchall()

    taken_tests = set()
    if user['role'] == 'student':
        rows = conn.execute(
            text("SELECT DISTINCT test_id FROM StudentAnswers WHERE student_id = :sid"),
            {"sid": user_id}
        ).fetchall()
        taken_tests = {row['test_id'] for row in rows}

        tests = [t for t in tests if t['test_id'] not in taken_tests]

    return render_template("all_tests.html", user=user, tests=tests, taken_tests=taken_tests)

@app.route('/test_results/<int:teacher_id>/<int:test_id>', methods=['Get'])
def view_test_results(teacher_id, test_id):
    responses = conn.execute(
        text("""
            SELECT sa.student_id, a.first_name, a.last_name,
            sa.question_id, q.question_text, sa.submitted_answer,
            a2.answer_text AS correct_answer, sa.is_correct, sa.points_earned
            FROM StudentAnswers sa
            JOIN accounts a ON sa.student_id = a.account_id
            JOIN questions q ON sa.question_id = q.question_id
            LEFT JOIN answers a2 ON sa.answer_id = a2.answer_id
        """), {"tid": test_id}
    ).mappings().fetchall()

    print(responses)

    return render_template("test_results.html", responses=responses, test_id=test_id)

@app.route('/update_marks/<int:teacher_id>/<int:test_id>', methods=['POST'])
def update_marks(teacher_id, test_id):
    for key in request.form:
        if key.startwith("marks_"):
            student_id = int(key.split("_")[1])
            total_marks = float(request.form[key])

            conn.execute(
                text("""
                    UPDATE StudentAnswers
                    SET points_earned = :marks
                    WHERE student_id = :sid AND test_is = :tid
                """), {"marks": total_marks, "sid": student_id, "tid": test_id}
            )
    conn.commit()
    return redirect(url_for('test_results', teacher_id=teacher_id, test_id=test_id))

if __name__ == '__main__':
    app.run(debug=True)
