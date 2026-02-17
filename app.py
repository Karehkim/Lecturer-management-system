from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lecturer_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # admin, lecturer

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.Text)
    lecturers = db.relationship('Lecturer', backref='department', lazy=True)
    students = db.relationship('Student', backref='department', lazy=True)
    courses = db.relationship('Course', backref='department', lazy=True)

class Lecturer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    courses = db.relationship('Course', backref='lecturer', lazy=True)
    leaves = db.relationship('Leave', backref='lecturer', lazy=True)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturer.id'), nullable=True)
    description = db.Column(db.Text)
    enrollments = db.relationship('Enrollment', backref='course', lazy=True)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    enrollments = db.relationship('Enrollment', backref='student', lazy=True)
    attendances = db.relationship('StudentAttendance', backref='student', lazy=True)
    marks = db.relationship('Mark', backref='student', lazy=True)

class Mark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    marks = db.Column(db.Float, nullable=False)
    grade = db.Column(db.String(5))

class StudentAttendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(10), nullable=False)  # present, absent

class Leave(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturer.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(db.String(10), default='pending')  # approved, rejected, pending

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
@login_required
def dashboard():
    if current_user.role == 'lecturer':
        lecturer = Lecturer.query.filter_by(user_id=current_user.id).first()
        courses = Course.query.filter_by(lecturer_id=lecturer.id).all()
        students_count = sum(len(course.enrollments) for course in courses)
        marks = []
        for course in courses:
            marks.extend(Mark.query.filter_by(course_id=course.id).all())
        average_marks = sum(m.marks for m in marks) / len(marks) if marks else 0
        notifications = []  # Add course assignments or messages
        report_data = {}
        for mark in marks:
            course = mark.course.name
            if course not in report_data:
                report_data[course] = []
            report_data[course].append(mark.marks)
        return render_template('dashboard.html', courses=courses, students_count=students_count,
                               average_marks=round(average_marks, 2), notifications=notifications,
                               report_data=report_data, is_lecturer=True)
    else:
        departments_count = Department.query.count()
        lecturers_count = Lecturer.query.count()
        courses_count = Course.query.count()
        students_count = Student.query.count()
        marks = Mark.query.all()
        average_marks = sum(m.marks for m in marks) / len(marks) if marks else 0
        notifications = []  # For now, empty
        report_data = {}
        for mark in marks:
            course = mark.course.name
            if course not in report_data:
                report_data[course] = []
            report_data[course].append(mark.marks)
        return render_template('dashboard.html', departments_count=departments_count,
                               lecturers_count=lecturers_count, courses_count=courses_count,
                               students_count=students_count, average_marks=round(average_marks, 2),
                               notifications=notifications, report_data=report_data, is_lecturer=False)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Lecturer Management
@app.route('/lecturers')
@login_required
def lecturers():
    lecturers = Lecturer.query.all()
    return render_template('lecturers.html', lecturers=lecturers)

@app.route('/add_lecturer', methods=['GET', 'POST'])
@login_required
def add_lecturer():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        department_id = request.form.get('department_id')
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password, method='sha256')
        user = User(username=username, password=hashed_password, role='lecturer')
        db.session.add(user)
        db.session.commit()
        lecturer = Lecturer(user_id=user.id, department_id=department_id, name=name, email=email, phone=phone)
        db.session.add(lecturer)
        db.session.commit()
        flash('Lecturer added successfully')
        return redirect(url_for('lecturers'))
    departments = Department.query.all()
    return render_template('add_lecturer.html', departments=departments)

# Course Management
@app.route('/courses')
@login_required
def courses():
    courses = Course.query.all()
    return render_template('courses.html', courses=courses)

@app.route('/add_course', methods=['GET', 'POST'])
@login_required
def add_course():
    if request.method == 'POST':
        name = request.form.get('name')
        code = request.form.get('code')
        department_id = request.form.get('department_id')
        lecturer_id = request.form.get('lecturer_id')
        description = request.form.get('description')
        course = Course(name=name, code=code, department_id=department_id, lecturer_id=lecturer_id, description=description)
        db.session.add(course)
        db.session.commit()
        # Notification logic here
        if lecturer_id:
            lecturer = Lecturer.query.get(lecturer_id)
            # For simplicity, add to notifications list or send email
            flash(f'Lecturer {lecturer.name} has been assigned to course {name}')
        flash('Course added successfully')
        return redirect(url_for('courses'))
    departments = Department.query.all()
    lecturers = Lecturer.query.all()
    return render_template('add_course.html', departments=departments, lecturers=lecturers)

# Department Management
@app.route('/departments')
@login_required
def departments():
    departments = Department.query.all()
    return render_template('departments.html', departments=departments)

@app.route('/add_department', methods=['GET', 'POST'])
@login_required
def add_department():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        department = Department(name=name, description=description)
        db.session.add(department)
        db.session.commit()
        flash('Department added successfully')
        return redirect(url_for('departments'))
    return render_template('add_department.html')

# Students
@app.route('/students')
@login_required
def students():
    students = Student.query.all()
    courses = Course.query.all()
    return render_template('students.html', students=students, courses=courses)

@app.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        department_id = request.form.get('department_id')
        student = Student(name=name, email=email, department_id=department_id)
        db.session.add(student)
        db.session.commit()
        flash('Student added successfully')
        return redirect(url_for('students'))
    departments = Department.query.all()
    return render_template('add_student.html', departments=departments)

@app.route('/enroll_student', methods=['POST'])
@login_required
def enroll_student():
    student_id = request.form.get('student_id')
    course_id = request.form.get('course_id')
    enrollment = Enrollment(student_id=student_id, course_id=course_id)
    db.session.add(enrollment)
    db.session.commit()
    flash('Student enrolled successfully')
    return redirect(url_for('students'))

@app.route('/input_marks', methods=['GET', 'POST'])
@login_required
def input_marks():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        course_id = request.form.get('course_id')
        marks = float(request.form.get('marks'))
        grade = request.form.get('grade')
        mark = Mark(student_id=student_id, course_id=course_id, marks=marks, grade=grade)
        db.session.add(mark)
        db.session.commit()
        flash('Marks added successfully')
        return redirect(url_for('students'))
    students = Student.query.all()
    courses = Course.query.all()
    return render_template('input_marks.html', students=students, courses=courses)

# Attendance
@app.route('/attendance')
@login_required
def attendance():
    if current_user.role == 'lecturer':
        lecturer = Lecturer.query.filter_by(user_id=current_user.id).first()
        courses = Course.query.filter_by(lecturer_id=lecturer.id).all()
        attendances = []
        for course in courses:
            atts = StudentAttendance.query.filter_by(course_id=course.id).all()
            attendances.extend(atts)
        return render_template('attendance.html', attendances=attendances, courses=courses, lecturer=lecturer)
    else:
        attendances = StudentAttendance.query.all()
        courses = Course.query.all()
        students = Student.query.all()
        return render_template('attendance.html', attendances=attendances, courses=courses, students=students)

@app.route('/mark_attendance', methods=['POST'])
@login_required
def mark_attendance():
    student_id = request.form.get('student_id')
    course_id = request.form.get('course_id')
    date = request.form.get('date')
    status = request.form.get('status')
    attendance = StudentAttendance(student_id=student_id, course_id=course_id, date=date, status=status)
    db.session.add(attendance)
    db.session.commit()
    flash('Attendance marked')
    return redirect(url_for('attendance'))

# Leave
@app.route('/leave')
@login_required
def leave():
    leaves = Leave.query.all()
    lecturers = Lecturer.query.all()
    return render_template('leave.html', leaves=leaves, lecturers=lecturers)

@app.route('/apply_leave', methods=['POST'])
@login_required
def apply_leave():
    lecturer_id = request.form.get('lecturer_id')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    reason = request.form.get('reason')
    leave = Leave(lecturer_id=lecturer_id, start_date=start_date, end_date=end_date, reason=reason)
    db.session.add(leave)
    db.session.commit()
    flash('Leave applied')
    return redirect(url_for('leave'))

# Timetable
@app.route('/timetable')
@login_required
def timetable():
    courses = Course.query.all()
    return render_template('timetable.html', courses=courses)

# Calendar
@app.route('/calendar')
@login_required
def calendar():
    courses = Course.query.all()
    return render_template('calendar.html', courses=courses)

# Messages
@app.route('/messages')
@login_required
def messages():
    # For simplicity, show recent notifications
    notifications = []  # In real app, store in DB
    return render_template('messages.html', notifications=notifications)

# Reporting
@app.route('/reports')
@login_required
def reports():
    # Reporting logic
    marks = Mark.query.all()
    report_data = {}
    for mark in marks:
        course = mark.course.name
        if course not in report_data:
            report_data[course] = []
        report_data[course].append(mark.marks)
    return render_template('reports.html', report_data=report_data)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            hashed_password = generate_password_hash('admin', method='sha256')
            admin_user = User(username='admin', password=hashed_password, role='admin')
            db.session.add(admin_user)
            db.session.commit()
    app.run(debug=True)