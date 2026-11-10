# Course Registration Management System

A web-based Course Registration Management System developed using Python Flask and PostgreSQL. The application allows students to register, log in, explore available courses, enroll in courses, and manage their profiles. Administrators can manage students, courses, registrations, and admin accounts.

## Features

### Student Module
- Student Registration and Login
- Secure Password Hashing
- Student Dashboard
- View Available Courses
- Search Courses by Name or Code
- Enroll in Courses
- Drop Enrolled Courses
- View and Update Student Profile
- Change Password

### Admin Module
- Admin Login
- Admin Dashboard
- Manage Courses (Add, Edit, Delete)
- Manage Students
- View Student Details
- Manage Course Registrations
- Manage Admin Accounts
- Update Admin Profile
- Change Password

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend Programming |
| Flask | Web Framework |
| PostgreSQL | Database |
| HTML5 | Page Structure |
| CSS3 | Styling |
| Bootstrap 5 | Responsive UI |
| psycopg2 | PostgreSQL Connectivity |
| Werkzeug | Password Hashing |

## Project Structure

```text
Course_Registration_Management_System/
│
├── app.py
├── requirements.txt
├── .gitignore
├── README.md
│
├── templates/
│   ├── Login.html
│   ├── RegistrationForm.html
│   ├── StudentDashboard.html
│   ├── AvailableCourses.html
│   ├── StudentProfile.html
│   ├── StudentSettings.html
│   ├── AdminDashboard.html
│   ├── AdminSettings.html
│   └── ...
│
└── static/
    └── css/
        ├── login.css
        ├── registration.css
        ├── StudentDashboard.css
        ├── AdminDashboard.css
        └── ...
```

## Installation and Setup

Follow these steps to run the project locally.

### 1. Clone the Repository

```bash
git clone https://github.com/KrishMakhija/Course_Registration_Management_System.git
```

### 2. Open the Project Folder

```bash
cd Course_Registration_Management_System
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure PostgreSQL

- Install PostgreSQL.
- Create a database named `course_registration`.
- Open the database in pgAdmin or your preferred SQL client.
- Execute the following SQL commands to create the required tables.

```sql
CREATE TABLE students (
    student_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    mobile VARCHAR(15) NOT NULL,
    dob DATE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    year INT NOT NULL CHECK (year BETWEEN 1 AND 4),
    branch VARCHAR(100) NOT NULL,
    address TEXT NOT NULL,
    gender VARCHAR(20) NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE admins (
    admin_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE courses (
    course_id SERIAL PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL,
    course_code VARCHAR(20) UNIQUE NOT NULL,
    description TEXT,
    credits INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE registrations (
    registration_id SERIAL PRIMARY KEY,
    student_id INT NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    course_id INT NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, course_id)
);
```

### 6. Configure Environment Variables

Create a `.env` file in the root project directory.

Add your own credentials:

```env
DB_PASSWORD=your_postgresql_password
SECRET_KEY=your_random_secret_key
```

**Important:** Never upload your `.env` file or database credentials to GitHub.

### 7. Run the Application

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000/
```

## Database

The application uses four main tables:

- **students:** Stores student information and login credentials.
- **admins:** Stores administrator information and login credentials.
- **courses:** Stores available course details.
- **registrations:** Maintains student-course enrollment records.

Passwords are stored as secure hashes rather than plain text.

**Initial Admin Setup:** A first admin account must be created in the database before using the Admin Login. Use Werkzeug's `generate_password_hash()` to generate the password hash before inserting the account.

## Future Enhancements

- Email Notifications
- Course Capacity Management
- Course Approval Workflow
- Advanced Student Analytics
- Improved Security and Role-Based Permissions

## Author

**Krish Makhija**

GitHub: https://github.com/KrishMakhija

---

*Developed as a project using Python Flask and PostgreSQL.*