from flask import render_template, request, redirect, url_for, flash, g, session
from codes.transcripts import app, db, bcrypt, credittable,mail
from codes.transcripts.forms import LoginForm, RegistrationForm, TranscriptForm
from codes.transcripts.models import User
from flask_login import current_user, login_user, login_required, logout_user
import sqlite3
from datetime import datetime

def sendmail(username,password,email):
    mail.send_message('New message from college-admin',
                      sender="admin@rajat.com",
                      recipients=[email],
                      body="Login credentials for getting transcript - " + "\n" +
                      "Username : "+username+"\n"+"Password : "+password+"\n"+
                      "This is a system generated mail, please do not reply to it."
                      )
def testdb():
    for row in g.cursor.execute("select * from student"):
        print(row)
    for row in g.cursor.execute("select * from college"):
        print(row)
    for row in g.cursor.execute("select * from department"):
        print(row)
    for row in g.cursor.execute("select * from course"):
        print(row)
    for row in g.cursor.execute("select * from location"):
        print(row)
    for row in g.cursor.execute("select * from student_course"):
        print(row)


def createdb():
    db_con = sqlite3.connect('tables.db')
    # with app.open_resource("queries.sql",mode='r')as f:
    #     db_con.cursor().executescript(f.read())
    #     db_con.commit()
    return db_con


@app.before_request
def before_request():
    # db.create_all()
    g.conDB = createdb()
    g.cursor = g.conDB.cursor()


@app.route("/", methods=['GET', 'POST'])
def login():
    # cursor=g.db.execute("select * from student")
    # authors=[row for row in cursor.fetchall()]
    # print(authors)
    # return authors[0][1]
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid EmailId or Password!!', 'warning')

    return render_template('login.html', title='login', form=form)


@app.route("/dashboard")
@login_required
def dashboard():
    location_id = g.cursor.execute("select location_id from student where student_id = ?",
                                   (current_user.id - 1,)).fetchone()
    topperformers=g.cursor.execute("").fetchall();
    location = None
    if location_id:
        location = g.cursor.execute("select * from location where location_id = ?", (location_id[0],)).fetchone()
    return render_template("home.html", location=location)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/register", methods=['GET', 'POST'])
@login_required
def register():
    if current_user.is_authenticated:
        if current_user.username == 'admin':
            form = RegistrationForm()
            if form.validate_on_submit():
                hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
                user = User(username=form.username.data, email=form.email.data, password=hashed_password)
                db.session.add(user)
                db.session.commit()
                #enable smtp to send mails
                #sendmail(user.username,form.password.data,user.email)
                flash('The student account has been created Succesfully!', 'success')
                return redirect(url_for('dashboard'))
        else:
            flash('You are not authorized to access the page!', 'warning')
            return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/getTranscript", methods=['GET', 'POST'])
@login_required
def getTranscript():
    form = TranscriptForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            row = g.cursor.execute("select * from student where sname=? and ssnum=?",
                                   (current_user.username.lower(), form.SSID.data)).fetchone()
            if (row):
                return redirect(url_for('viewTranscript', id=current_user.id))
            else:
                flash('Invalid UserName or SSID', 'warning')
    return render_template('transcriptform.html', title='Get Transcript', form=form)


@app.route("/view", methods=['GET', 'POST'])
@login_required
def viewstudents():
    viewusers = None
    if current_user.username == 'admin':
        if request.method == 'GET':
            viewusers = User.query.filter_by().all()
    else:
        flash('You are not authorized to access the page!', 'warning')
        return redirect(url_for('dashboard'))
    return render_template("viewstudents.html", title='View Students', users=viewusers)


@app.route("/record/<action>/<int:item_id>")
@login_required
def deleterecord(action=None, item_id=None):
    if action == 'delete' and current_user.username == 'admin':
        sturecord = User.query.get(item_id)
        db.session.delete(sturecord)
        db.session.commit()
        flash('Student record deleted successfully!!', 'success')

    else:
        flash('unable to delete student record !! please try again.', 'warning')
    return redirect(url_for('viewstudents'))


@app.route("/viewtranscript/<int:id>")
@login_required
def viewTranscript(id=None):
    if current_user.username == 'admin' or request.referrer == 'http://127.0.0.1:5000/getTranscript':
        if id == current_user.id or current_user.username == 'admin':
            student = g.cursor.execute("select * from student where student_id = ?", ((id - 1),)).fetchone()

            college = g.cursor.execute("""select * from 
                                        college C INNER JOIN location L 
                                        ON C.location_id=L.location_id 
                                        where college_id = ?""", (student[0],)).fetchone()

            student_course_details = g.cursor.execute("""select * from 
                                                        student_course SC INNER JOIN course C 
                                                        ON SC.course_code=C.course_code 
                                                        where SC.student_id = ? order by SC.taken_in_sem""",
                                                      (student[0],)).fetchall()

            department_details = g.cursor.execute("select * from department where department_id=?",
                                                  (student[8],)).fetchone()

            totalcredits = g.cursor.execute("""select sum(C.credits) 
                                            from student_course SC INNER JOIN course C 
                                            ON SC.course_code=C.course_code 
                                            where SC.student_id = ?""", ((id - 1),)).fetchone()
            totalcredits=totalcredits[0]*10
            student_data = dict(sname=student[2], emailID=student[1], dob=student[3], phone=student[4],
                                ssid=student[5], sdate=student[6], edate=student[7])

            courses_data = [dict(course_code=row[1], cname=row[5],
                                 credits=row[6], hrs=row[7], sem=row[2],
                                 grade=row[3]) for row in student_course_details]
            creditsearned = sum([credittable[row[3]][1] * row[6] for row in student_course_details])

            todaysdate = datetime.now().strftime("%c")

            return render_template('transcriptdoc.html', student_data=student_data,
                                   courses_data=courses_data, college=college,
                                   department_details=department_details,
                                   totalcredits=totalcredits, credittable=credittable,
                                   creditsearned=creditsearned, date=todaysdate)
    session.pop('_flashes', None)
    flash("Access Denied to Page!!", 'danger')
    return redirect(url_for('getTranscript'))
