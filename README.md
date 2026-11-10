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
├── database.sql
├── requirements.txt
├── README.md
├── .gitignore
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

### 5. Configure PostgreSQL Database

- Install PostgreSQL on your system.
- Open pgAdmin or your preferred PostgreSQL client.
- Create a database named `course_registration`.

### 6. Create Database Tables

The project includes a `database.sql` file containing the complete database schema.

To create the tables:

1. Open pgAdmin.
2. Select the `course_registration` database.
3. Open the Query Tool.
4. Open or copy the contents of `database.sql`.
5. Execute the SQL queries.

The following four tables will be created:

- `students`
- `admins`
- `courses`
- `registrations`

### 7. Configure Environment Variables

Create a `.env` file in the root project directory.

Add your own PostgreSQL credentials:

```env
DB_PASSWORD=your_postgresql_password
SECRET_KEY=your_random_secret_key
```

**Important:** Never upload your `.env` file or database credentials to GitHub.

### 8. Create Initial Admin Account

Before using the Admin Login, create an initial admin account in the `admins` table.

Generate a secure password hash using Werkzeug's `generate_password_hash()` and insert the admin details into the database.

### 9. Run the Application

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000/
```

## Database Structure

The application uses four main tables:

| Table | Description |
|---|---|
| students | Stores student information and login credentials. |
| admins | Stores administrator information and login credentials. |
| courses | Stores available course details. |
| registrations | Maintains student-course enrollment records. |

Passwords are stored as secure hashes rather than plain text.

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