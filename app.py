import os
from dotenv import load_dotenv

load_dotenv()

from flask import (
    Flask, render_template, request,
    redirect, url_for, flash, session
)

import psycopg2
from psycopg2.errors import UniqueViolation

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


app = Flask(__name__)

# Configuration
app.secret_key = os.environ["SECRET_KEY"]


# ==================================================
# DATABASE CONNECTION
# ==================================================

def get_db_connection():
    database_url = os.environ.get("DATABASE_URL")

    if database_url:
        conn = psycopg2.connect(database_url)
    else:
        conn = psycopg2.connect(
            host="localhost",
            database="course_registration",
            user="postgres",
            password=os.environ["DB_PASSWORD"],
            port="5432"
        )

    return conn


# ==================================================
# HOME AND LOGIN
# ==================================================

@app.route('/')
def home():

    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        role = request.form['role']
        email = request.form['email'].strip()
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()

        if role == 'student':

            cur.execute("""
                SELECT student_id, password, name
                FROM students
                WHERE email = %s
            """, (email,))

            user = cur.fetchone()

            if user and check_password_hash(user[1], password):

                session.clear()

                session['student_id'] = user[0]
                session['student_name'] = user[2]

                cur.close()
                conn.close()

                return redirect(url_for('StudentDashboard'))

            flash('Invalid Student Credentials!', 'danger')

        elif role == 'admin':

            cur.execute("""
                SELECT admin_id, password, full_name
                FROM admins
                WHERE email = %s
            """, (email,))

            user = cur.fetchone()

            if user and check_password_hash(user[1], password):

                session.clear()

                session['admin_id'] = user[0]
                session['admin_name'] = user[2]

                cur.close()
                conn.close()

                return redirect(url_for('AdminDashboard'))

            flash('Invalid Admin Credentials!', 'danger')

        else:

            flash('Please Select A Valid Role!', 'danger')

        cur.close()
        conn.close()

    return render_template('Login.html')


# ==================================================
# STUDENT REGISTRATION
# ==================================================

@app.route('/register')
def register():

    return render_template('RegistrationForm.html')


@app.route('/subreg', methods=['POST'])
def subreg():

    name = request.form['name']
    dob = request.form['dob']
    mobile = request.form['phone']
    email = request.form['email'].strip()
    year = request.form['year']
    branch = request.form['branch']
    address = request.form['address']
    gender = request.form['gender']
    password = request.form['password']

    hashed_password = generate_password_hash(password)

    conn = get_db_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            INSERT INTO students
            (name, dob, mobile, email, year, branch, address, gender, password)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            name, dob, mobile, email, year,
            branch, address, gender, hashed_password
        ))

        conn.commit()

        flash('Registration Successful! Please Login.', 'success')

    except UniqueViolation:

        conn.rollback()

        flash('Email Already Registered!', 'danger')

    finally:

        cur.close()
        conn.close()

    return redirect(url_for('login'))


# ==================================================
# STUDENT MODULE
# ==================================================


# Student Dashboard

@app.route('/StudentDashboard')
def StudentDashboard():

    if 'student_id' not in session:
        return redirect(url_for('login'))

    student_id = session['student_id']

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM courses
    """)

    total_courses = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM registrations
        WHERE student_id = %s
    """, (student_id,))

    enrolled_courses = cur.fetchone()[0]

    cur.execute("""
        SELECT COALESCE(SUM(c.credits), 0)
        FROM registrations r
        JOIN courses c ON r.course_id = c.course_id
        WHERE r.student_id = %s
    """, (student_id,))

    total_credits = cur.fetchone()[0]

    cur.execute("""
        SELECT
            c.course_name,
            c.course_code,
            c.credits,
            r.registration_date,
            r.registration_id
        FROM registrations r
        JOIN courses c ON r.course_id = c.course_id
        WHERE r.student_id = %s
        ORDER BY r.registration_date DESC
    """, (student_id,))

    my_courses = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        'StudentDashboard.html',
        total_courses=total_courses,
        enrolled_courses=enrolled_courses,
        total_credits=total_credits,
        my_courses=my_courses
    )


# Available Courses

@app.route('/AvailableCourses')
def AvailableCourses():

    if 'student_id' not in session:
        return redirect(url_for('login'))

    student_id = session['student_id']

    search_query = request.args.get('search', '').strip()

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            c.course_id,
            c.course_name,
            c.course_code,
            c.description,
            c.credits,
            CASE
                WHEN r.registration_id IS NOT NULL THEN TRUE
                ELSE FALSE
            END
        FROM courses c
        LEFT JOIN registrations r
            ON c.course_id = r.course_id
            AND r.student_id = %s
        WHERE c.course_name ILIKE %s
           OR c.course_code ILIKE %s
        ORDER BY c.course_id
    """, (
        student_id,
        f'%{search_query}%',
        f'%{search_query}%'
    ))

    courses = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        'AvailableCourses.html',
        courses=courses,
        search_query=search_query
    )


# Enroll Course

@app.route('/EnrollCourse/<int:course_id>', methods=['POST'])
def EnrollCourse(course_id):

    if 'student_id' not in session:
        return redirect(url_for('login'))

    student_id = session['student_id']

    conn = get_db_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            INSERT INTO registrations (student_id, course_id)
            VALUES (%s, %s)
        """, (student_id, course_id))

        conn.commit()

        flash('Course Enrolled Successfully!', 'success')

    except UniqueViolation:

        conn.rollback()

        flash('You Are Already Enrolled In This Course!', 'warning')

    finally:

        cur.close()
        conn.close()

    return redirect(url_for('AvailableCourses'))


# Drop Course

@app.route('/DropCourse/<int:registration_id>', methods=['POST'])
def DropCourse(registration_id):

    if 'student_id' not in session:
        return redirect(url_for('login'))

    student_id = session['student_id']

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM registrations
        WHERE registration_id = %s
        AND student_id = %s
    """, (registration_id, student_id))

    if cur.rowcount > 0:

        conn.commit()

        flash('Course Dropped Successfully!', 'success')

    else:

        conn.rollback()

        flash('Registration Not Found!', 'danger')

    cur.close()
    conn.close()

    return redirect(url_for('StudentDashboard'))


# Student Profile

@app.route('/StudentProfile')
def StudentProfile():

    if 'student_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            student_id, name, mobile, dob, email,
            year, branch, address, gender, created_at
        FROM students
        WHERE student_id = %s
    """, (session['student_id'],))

    student = cur.fetchone()

    cur.close()
    conn.close()

    if student is None:

        flash('Student Not Found!', 'danger')

        return redirect(url_for('login'))

    return render_template(
        'StudentProfile.html',
        student=student
    )


# Update Student Profile

@app.route('/UpdateStudentProfile', methods=['POST'])
def UpdateStudentProfile():

    if 'student_id' not in session:
        return redirect(url_for('login'))

    name = request.form['name']
    mobile = request.form['mobile']
    dob = request.form['dob']
    email = request.form['email'].strip()
    year = request.form['year']
    branch = request.form['branch']
    address = request.form['address']
    gender = request.form['gender']

    conn = get_db_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            UPDATE students
            SET name = %s,
                mobile = %s,
                dob = %s,
                email = %s,
                year = %s,
                branch = %s,
                address = %s,
                gender = %s
            WHERE student_id = %s
        """, (
            name, mobile, dob, email, year,
            branch, address, gender,
            session['student_id']
        ))

        conn.commit()

        session['student_name'] = name

        flash('Profile Updated Successfully!', 'success')

    except UniqueViolation:

        conn.rollback()

        flash('Email Already Exists!', 'danger')

    finally:

        cur.close()
        conn.close()

    return redirect(url_for('StudentProfile'))


# Student Settings - Change Password

@app.route('/StudentSettings', methods=['GET', 'POST'])
def StudentSettings():

    if 'student_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':

        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT password
            FROM students
            WHERE student_id = %s
        """, (session['student_id'],))

        student = cur.fetchone()

        if not student or not check_password_hash(
            student[0], current_password
        ):

            flash('Current Password Is Incorrect!', 'danger')

        elif new_password != confirm_password:

            flash('New Passwords Do Not Match!', 'danger')

        elif len(new_password) < 8:

            flash('Password Must Be At Least 8 Characters!', 'danger')

        else:

            hashed_password = generate_password_hash(new_password)

            cur.execute("""
                UPDATE students
                SET password = %s
                WHERE student_id = %s
            """, (hashed_password, session['student_id']))

            conn.commit()

            flash('Password Changed Successfully!', 'success')

        cur.close()
        conn.close()

        return redirect(url_for('StudentSettings'))

    return render_template('StudentSettings.html')


# ==================================================
# ADMIN MODULE
# ==================================================


# Admin Dashboard

@app.route('/AdminDashboard')
def AdminDashboard():

    if 'admin_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM students")
    total_students = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM courses")
    total_courses = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM registrations")
    total_registrations = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM admins")
    total_admins = cur.fetchone()[0]

    cur.execute("""
        SELECT
            s.student_id,
            s.name,
            s.email,
            c.course_name,
            r.registration_date
        FROM registrations r
        JOIN students s ON r.student_id = s.student_id
        JOIN courses c ON r.course_id = c.course_id
        ORDER BY r.registration_date DESC
        LIMIT 5
    """)

    recent_registrations = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        'AdminDashboard.html',
        total_students=total_students,
        total_courses=total_courses,
        total_registrations=total_registrations,
        total_admins=total_admins,
        recent_registrations=recent_registrations
    )


# ==================================================
# MANAGE COURSES
# ==================================================


@app.route('/ManageCourses')
def ManageCourses():

    if 'admin_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT course_id, course_name, course_code, credits
        FROM courses
        ORDER BY course_id
    """)

    courses = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        'ManageCourses.html',
        courses=courses
    )


# Add Course

@app.route('/AddCourse', methods=['POST'])
def AddCourse():

    if 'admin_id' not in session:
        return redirect(url_for('login'))

    course_name = request.form['course_name']
    course_code = request.form['course_code']
    description = request.form['description']
    credits = request.form['credits']

    conn = get_db_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            INSERT INTO courses
            (course_name, course_code, description, credits)
            VALUES (%s, %s, %s, %s)
        """, (
            course_name, course_code,
            description, credits
        ))

        conn.commit()

        flash('Course Added Successfully!', 'success')

    except UniqueViolation:

        conn.rollback()

        flash('Course Code Already Exists!', 'danger')

    finally:

        cur.close()
        conn.close()

    return redirect(url_for('ManageCourses'))


# Edit Course

@app.route('/EditCourse/<int:course_id>', methods=['GET', 'POST'])
def EditCourse(course_id):

    if 'admin_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':

        course_name = request.form['course_name']
        course_code = request.form['course_code']
        description = request.form['description']
        credits = request.form['credits']

        try:

            cur.execute("""
                UPDATE courses
                SET course_name = %s,
                    course_code = %s,
                    description = %s,
                    credits = %s
                WHERE course_id = %s
            """, (
                course_name, course_code,
                description, credits, course_id
            ))

            conn.commit()

            flash('Course Updated Successfully!', 'success')

        except UniqueViolation:

            conn.rollback()

            flash('Course Code Already Exists!', 'danger')

        finally:

            cur.close()
            conn.close()

        return redirect(url_for('ManageCourses'))

    cur.execute("""
        SELECT course_id, course_name, course_code,
               description, credits
        FROM courses
        WHERE course_id = %s
    """, (course_id,))

    course = cur.fetchone()

    cur.close()
    conn.close()

    if course is None:

        flash('Course Not Found!', 'danger')

        return redirect(url_for('ManageCourses'))

    return render_template(
        'EditCourse.html',
        course=course
    )


# Delete Course

@app.route('/DeleteCourse/<int:course_id>', methods=['POST'])
def DeleteCourse(course_id):

    if 'admin_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM courses
        WHERE course_id = %s
    """, (course_id,))

    if cur.rowcount > 0:

        conn.commit()

        flash('Course Deleted Successfully!', 'success')

    else:

        conn.rollback()

        flash('Course Not Found!', 'danger')

    cur.close()
    conn.close()

    return redirect(url_for('ManageCourses'))


# ==================================================
# MANAGE STUDENTS
# ==================================================


@app.route('/ManageStudents')
def ManageStudents():

    if 'admin_id' not in session:
        return redirect(url_for('login'))

    search_query = request.args.get('search', '').strip()

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT student_id, name, email, mobile, year, branch
        FROM students
        WHERE name ILIKE %s OR email ILIKE %s
        ORDER BY student_id DESC
    """, (
        f'%{search_query}%',
        f'%{search_query}%'
    ))

    students = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        'ManageStudents.html',
        students=students,
        search_query=search_query
    )


# View Student

@app.route('/ViewStudent/<int:student_id>')
def ViewStudent(student_id):

    if 'admin_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            student_id, name, mobile, dob, email,
            year, branch, address, gender, created_at
        FROM students
        WHERE student_id = %s
    """, (student_id,))

    student = cur.fetchone()

    cur.close()
    conn.close()

    if student is None:

        flash('Student Not Found!', 'danger')

        return redirect(url_for('ManageStudents'))

    return render_template(
        'ViewStudent.html',
        student=student
    )


# Delete Student

@app.route('/DeleteStudent/<int:student_id>', methods=['POST'])
def DeleteStudent(student_id):

    if 'admin_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM students
        WHERE student_id = %s
    """, (student_id,))

    if cur.rowcount > 0:

        conn.commit()

        flash('Student Deleted Successfully!', 'success')

    else:

        conn.rollback()

        flash('Student Not Found!', 'danger')

    cur.close()
    conn.close()

    return redirect(url_for('ManageStudents'))


# ==================================================
# MANAGE REGISTRATIONS
# ==================================================


@app.route('/ManageRegistrations')
def ManageRegistrations():

    if 'admin_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            r.registration_id,
            s.student_id,
            s.name,
            s.email,
            c.course_name,
            c.course_code,
            r.registration_date
        FROM registrations r
        JOIN students s ON r.student_id = s.student_id
        JOIN courses c ON r.course_id = c.course_id
        ORDER BY r.registration_date DESC
    """)

    registrations = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        'ManageRegistrations.html',
        registrations=registrations
    )


# Delete Registration - Admin

@app.route('/DeleteRegistration/<int:registration_id>', methods=['POST'])
def DeleteRegistration(registration_id):

    if 'admin_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM registrations
        WHERE registration_id = %s
    """, (registration_id,))

    if cur.rowcount > 0:

        conn.commit()

        flash('Registration Removed Successfully!', 'success')

    else:

        conn.rollback()

        flash('Registration Not Found!', 'danger')

    cur.close()
    conn.close()

    return redirect(url_for('ManageRegistrations'))


# ==================================================
# ADMIN PROFILE
# ==================================================


@app.route('/AdminProfile')
def AdminProfile():

    if 'admin_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT admin_id, full_name, username, email, created_at
        FROM admins
        WHERE admin_id = %s
    """, (session['admin_id'],))

    admin = cur.fetchone()

    cur.close()
    conn.close()

    if admin is None:

        session.clear()

        flash('Admin Not Found!', 'danger')

        return redirect(url_for('login'))

    return render_template(
        'AdminProfile.html',
        admin=admin
    )


# Update Admin Profile

@app.route('/UpdateAdminProfile', methods=['POST'])
def UpdateAdminProfile():

    if 'admin_id' not in session:
        return redirect(url_for('login'))

    full_name = request.form['full_name'].strip()
    username = request.form['username'].strip()
    email = request.form['email'].strip()

    conn = get_db_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            UPDATE admins
            SET full_name = %s,
                username = %s,
                email = %s
            WHERE admin_id = %s
        """, (
            full_name,
            username,
            email,
            session['admin_id']
        ))

        conn.commit()

        session['admin_name'] = full_name

        flash('Profile Updated Successfully!', 'success')

    except UniqueViolation:

        conn.rollback()

        flash('Username or Email Already Exists!', 'danger')

    finally:

        cur.close()
        conn.close()

    return redirect(url_for('AdminProfile'))


# ==================================================
# ADMIN SETTINGS AND MANAGE ADMINS
# ==================================================


# Admin Settings - View Admins + Change Password

@app.route('/AdminSettings', methods=['GET', 'POST'])
def AdminSettings():

    if 'admin_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':

        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT password
            FROM admins
            WHERE admin_id = %s
        """, (session['admin_id'],))

        admin = cur.fetchone()

        if not admin or not check_password_hash(
            admin[0], current_password
        ):

            flash('Current Password Is Incorrect!', 'danger')

        elif new_password != confirm_password:

            flash('New Passwords Do Not Match!', 'danger')

        elif len(new_password) < 8:

            flash('Password Must Be At Least 8 Characters!', 'danger')

        else:

            hashed_password = generate_password_hash(new_password)

            cur.execute("""
                UPDATE admins
                SET password = %s
                WHERE admin_id = %s
            """, (hashed_password, session['admin_id']))

            conn.commit()

            flash('Password Changed Successfully!', 'success')

        cur.close()
        conn.close()

        return redirect(url_for('AdminSettings'))

    # Fetch All Admins

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT admin_id, full_name, username, email, created_at
        FROM admins
        ORDER BY admin_id
    """)

    admins = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        'AdminSettings.html',
        admins=admins
    )


# Add New Admin

@app.route('/AddAdmin', methods=['POST'])
def AddAdmin():

    if 'admin_id' not in session:
        return redirect(url_for('login'))

    full_name = request.form['full_name'].strip()
    username = request.form['username'].strip()
    email = request.form['email'].strip()
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    if not full_name or not username or not email:

        flash('All Fields Are Required!', 'danger')

        return redirect(url_for('AdminSettings'))

    if password != confirm_password:

        flash('Passwords Do Not Match!', 'danger')

        return redirect(url_for('AdminSettings'))

    if len(password) < 8:

        flash('Password Must Be At Least 8 Characters!', 'danger')

        return redirect(url_for('AdminSettings'))

    hashed_password = generate_password_hash(password)

    conn = get_db_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            INSERT INTO admins
            (full_name, username, email, password)
            VALUES (%s, %s, %s, %s)
        """, (
            full_name,
            username,
            email,
            hashed_password
        ))

        conn.commit()

        flash('New Admin Added Successfully!', 'success')

    except UniqueViolation:

        conn.rollback()

        flash('Username or Email Already Exists!', 'danger')

    finally:

        cur.close()
        conn.close()

    return redirect(url_for('AdminSettings'))


# Update Managed Admin

@app.route('/UpdateManagedAdmin/<int:admin_id>', methods=['POST'])
def UpdateManagedAdmin(admin_id):

    if 'admin_id' not in session:
        return redirect(url_for('login'))

    full_name = request.form['full_name'].strip()
    username = request.form['username'].strip()
    email = request.form['email'].strip()

    if not full_name or not username or not email:

        flash('All Fields Are Required!', 'danger')

        return redirect(url_for('AdminSettings'))

    conn = get_db_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            UPDATE admins
            SET full_name = %s,
                username = %s,
                email = %s
            WHERE admin_id = %s
        """, (
            full_name,
            username,
            email,
            admin_id
        ))

        if cur.rowcount == 0:

            conn.rollback()

            flash('Admin Not Found!', 'danger')

        else:

            conn.commit()

            if admin_id == session['admin_id']:

                session['admin_name'] = full_name

            flash('Admin Details Updated Successfully!', 'success')

    except UniqueViolation:

        conn.rollback()

        flash('Username or Email Already Exists!', 'danger')

    finally:

        cur.close()
        conn.close()

    return redirect(url_for('AdminSettings'))


# Delete Admin

@app.route('/DeleteAdmin/<int:admin_id>', methods=['POST'])
def DeleteAdmin(admin_id):

    if 'admin_id' not in session:
        return redirect(url_for('login'))

    # Prevent deleting own account

    if admin_id == session['admin_id']:

        flash('You Cannot Delete Your Own Admin Account!', 'danger')

        return redirect(url_for('AdminSettings'))

    conn = get_db_connection()
    cur = conn.cursor()

    try:

        # Check Total Admins

        cur.execute("""
            SELECT COUNT(*)
            FROM admins
        """)

        total_admins = cur.fetchone()[0]

        if total_admins <= 1:

            flash('At Least One Admin Account Must Exist!', 'danger')

        else:

            cur.execute("""
                DELETE FROM admins
                WHERE admin_id = %s
            """, (admin_id,))

            if cur.rowcount > 0:

                conn.commit()

                flash('Admin Deleted Successfully!', 'success')

            else:

                conn.rollback()

                flash('Admin Not Found!', 'danger')

    finally:

        cur.close()
        conn.close()

    return redirect(url_for('AdminSettings'))


# ==================================================
# LOGOUT
# ==================================================


@app.route('/logout')
def logout():

    session.clear()

    flash('Logged Out Successfully!', 'success')

    return redirect(url_for('login'))


# ==================================================
# RUN APPLICATION
# ==================================================


if __name__ == '__main__':

    app.run(debug=True)