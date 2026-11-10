-- ==========================================
-- Course Registration Management System
-- Database Tables
-- PostgreSQL
-- ==========================================

-- 1. Students Table

CREATE TABLE IF NOT EXISTS students (
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


-- 2. Admins Table

CREATE TABLE IF NOT EXISTS admins (
    admin_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- 3. Courses Table

CREATE TABLE IF NOT EXISTS courses (
    course_id SERIAL PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL,
    course_code VARCHAR(20) UNIQUE NOT NULL,
    description TEXT,
    credits INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- 4. Registrations Table

CREATE TABLE IF NOT EXISTS registrations (
    registration_id SERIAL PRIMARY KEY,

    student_id INT NOT NULL
        REFERENCES students(student_id)
        ON DELETE CASCADE,

    course_id INT NOT NULL
        REFERENCES courses(course_id)
        ON DELETE CASCADE,

    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(student_id, course_id)
);