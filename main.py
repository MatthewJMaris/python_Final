from flask import Flask, render_template, request
from sqlalchemy import create_engine, text
app = Flask(__name__)

conn_str = "mysql://root:Lorx3492345!@localhost/pythonFinal"
engine = create_engine(conn_str, echo=True)
connection = engine.connect()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/teachersignup', methods=['GET', 'POST'])
def teachersignup():
    if request.method == 'GET':
        result = connection.execute(text("select max(teacher_id) from teachers")).fetchone() or 0
        max_id = result[0] or 0
        return render_template('teacher_sign_up.html', next_teacher_id=max_id + 1)
    elif request.method == 'POST':
        teacher_id = request.form['teacher_id']
        result = connection.execute(text("select * from teachers where teacher_id = :id").bindparams(id=teacher_id))
        existing_entry = result.fetchone()
        if existing_entry:
            return render_template('teacher_sign_up.html', created="Id already exists")
        else:
            connection.execute(text("insert into teachers values (:teacher_id, :name, :grade)"), request.form)
            result = connection.execute(text("select max(teacher_id) from teachers")).fetchone() or 0
            max_id = result[0] or 0
            connection.commit()
            return render_template('teacher_sign_up.html', created='Teacher registered', next_teacher_id=max_id + 1)


@app.route('/studentsignup', methods=['GET', 'POST'])
def studentsignup():
    if request.method == 'GET':
        result = connection.execute(text("select max(student_id) from students")).fetchone() or 0
        max_id = result[0] or 0
        return render_template('student_sign_up.html', next_student_id=max_id + 1)
    elif request.method == 'POST':
        student_id = request.form['student_id']
        result = connection.execute(text("select * from students where student_id = :id").bindparams(id=student_id))
        existing_entry = result.fetchone()
        if existing_entry:
            return render_template('student_sign_up.html', created="Id already exists")
        else:
            connection.execute(text("insert into students values (:student_id, :name, :grade)"), request.form)
            result = connection.execute(text("select max(student_id) from students")).fetchone() or 0
            max_id = result[0] or 0
            connection.commit()
            return render_template('student_sign_up.html', created='Student registered', next_student_id=max_id + 1)


@app.route('/viewAll', methods=['GET', 'POST'])
def viewAll():
    if request.method == 'GET':
        students = connection.execute(text("select * from students")).all()
        teachers = connection.execute(text("select * from teachers")).all()
        return render_template('view_all.html', students=students, teachers=teachers)
    elif request.method == 'POST':
        if request.form['button'] == 'Students':
            students = connection.execute(text("select * from students")).all()
            return render_template('view_all.html', students=students)
        elif request.form['button'] == 'Teachers':
            teachers = connection.execute(text("select * from teachers")).all()
            return render_template('view_all.html', teachers=teachers)
        elif request.form['button'] == 'All':
            students = connection.execute(text("select * from students")).all()
            teachers = connection.execute(text("select * from teachers")).all()
            return render_template('view_all.html', students=students, teachers=teachers)
        else:
            students = connection.execute(text("select * from students")).all()
            teachers = connection.execute(text("select * from teachers")).all()
            return render_template('view_all.html', students=students, teachers=teachers)


@app.route('/createTest', methods=['GET', 'POST'])
def createTest():
    if request.method == 'GET':
        result = connection.execute(text("select max(test_id) from test")).fetchone() or 0
        max_id = result[0] or 0
        return render_template('create_test.html', next_test_id=max_id + 1)
    elif request.method == 'POST':
        teacher_id = request.form['teacher_id']
        result = connection.execute(text("select * from teachers where teacher_id = :id").bindparams(id=teacher_id))
        existing_entry = result.fetchone()
        if existing_entry:
            connection.execute(text("insert into test values (:test_id, :teacher_id, :question1, :question2, :question3,"
                                    " :question4)"), request.form)
            result = connection.execute(text("select max(test_id) from test")).fetchone() or 0
            max_id = result[0] or 0
            connection.commit()
            return render_template('create_test.html', created='Test created', next_test_id=max_id + 1)
        else:
            return render_template('create_test.html', created="Test with this ID already exists")


@app.route('/test')
def test():
    tests = connection.execute(text("select * from test")).all()
    return render_template('test.html', tests=tests)


@app.route('/editTest', methods=['GET', 'POST'])
def editTest():
    if request.method == 'GET':
        return render_template('edit_test.html')
    elif request.method == 'POST':
        test_id = request.form['test_id']
        test = connection.execute((text("select * from test where test_id = :id").bindparams(id=test_id)))
        existing_entry = test.fetchone()
        if existing_entry:
            connection.execute(text("update test set teacher_id = :teacher_id, question_1 = :question_1, question_2 = "
                              ":question_2, question_3 = :question_3, question_4 = :question_4 where test_id = :test_id"
                                    ), request.form)
            connection.commit()
            return render_template('edit_test.html', edited='Test edited')
        else:
            return render_template('edit_test.html', edited="Test with this ID does not exist")


@app.route('/deleteTest', methods=['GET', 'POST'])
def deleteTest():
    if request.method == 'GET':
        return render_template('delete_test.html')
    elif request.method == 'POST':
        test_id = request.form['test_id']
        test = connection.execute((text("select * from test where test_id = :id").bindparams(id=test_id)))
        existing_entry = test.fetchone()
        if existing_entry:
            connection.execute(text("delete from student_submissions where test_id = :test_id"), request.form)
            connection.execute(text("delete from test where test_id = :test_id"), request.form)
            connection.commit()
            return render_template('delete_test.html', deleted='Test deleted')
        else:
            return render_template('delete_test.html', deleted="Test with this ID does not exist")


@app.route('/takeTest', methods=['GET', 'POST'])
def takeTest():
    test_id = request.form['test_id']
    test = connection.execute((text("select * from test where test_id = :id").bindparams(id=test_id)))
    return render_template('take_test.html', test=test)


@app.route('/testSubmitted', methods=['GET', 'POST'])
def testSubmitted():
    student_id = request.form['student_id']
    result = connection.execute(text("select * from students where student_id = :id").bindparams(id=student_id))
    existing_entry = result.fetchone()
    if existing_entry:
        connection.execute(text("insert into student_submissions values (:test_id, :student_id, :ans_1, :ans_2, "" :ans_3, :ans_4)"), request.form)
        connection.commit()
        return render_template('test_submitted.html', submitted='Test submitted')
    else:
        test_id = request.form['test_id']
        test = connection.execute((text("select * from test where test_id = :id").bindparams(id=test_id)))
        return render_template('take_test.html', submitted="Student ID does not exist", test=test)


if __name__ == '__main__':
    app.run(debug=True)
