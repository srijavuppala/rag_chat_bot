-- Create a database for the RAG chatbot
-- Run this with: psql -U your_username -d postgres -f database_setup.sql

-- Create the database (uncomment if needed)
-- CREATE DATABASE rag_chatbot;

-- Connect to the database
-- \c rag_chatbot;

-- Create a table to hold course information
CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    course_code VARCHAR(10) NOT NULL,
    course_name VARCHAR(255) NOT NULL,
    description TEXT,
    prerequisites VARCHAR(255),
    credits INTEGER DEFAULT 3,
    department VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert comprehensive sample data for university courses
INSERT INTO courses (course_code, course_name, description, prerequisites, credits, department) VALUES
('CS101', 'Introduction to Programming', 'Learn the fundamentals of programming using Python. Covers variables, loops, functions, and basic data structures.', 'None', 3, 'Computer Science'),
('CS102', 'Data Structures', 'Study of fundamental data structures including arrays, linked lists, stacks, queues, trees, and graphs.', 'CS101', 4, 'Computer Science'),
('CS201', 'Object-Oriented Programming', 'Advanced programming concepts including classes, inheritance, polymorphism, and design patterns.', 'CS102', 3, 'Computer Science'),
('DS202', 'Data Science Fundamentals', 'An introduction to data analysis, visualization, and machine learning using Python and R.', 'CS101, MATH201', 4, 'Data Science'),
('DS301', 'Machine Learning', 'Comprehensive study of machine learning algorithms including supervised and unsupervised learning.', 'DS202, MATH202', 4, 'Data Science'),
('AI404', 'Advanced Natural Language Processing', 'Deep dive into modern NLP techniques including transformers, BERT, and GPT models.', 'DS301, CS201', 4, 'Artificial Intelligence'),
('AI301', 'Introduction to AI', 'Foundational concepts in artificial intelligence including search algorithms, knowledge representation.', 'CS201', 3, 'Artificial Intelligence'),
('MATH201', 'Statistics for Data Science', 'Statistical methods and probability theory for data analysis and machine learning.', 'None', 3, 'Mathematics'),
('MATH202', 'Linear Algebra', 'Vector spaces, matrices, eigenvalues, and applications to machine learning and computer graphics.', 'MATH201', 3, 'Mathematics'),
('DB301', 'Database Systems', 'Design and implementation of database systems, SQL, NoSQL, and database optimization.', 'CS102', 3, 'Computer Science'),
('WEB201', 'Web Development', 'Full-stack web development using HTML, CSS, JavaScript, and modern frameworks.', 'CS101', 3, 'Computer Science'),
('SEC401', 'Cybersecurity Fundamentals', 'Introduction to cybersecurity principles, cryptography, and network security.', 'CS201, DB301', 4, 'Cybersecurity');

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_courses_code ON courses(course_code);
CREATE INDEX IF NOT EXISTS idx_courses_department ON courses(department);
CREATE INDEX IF NOT EXISTS idx_courses_name ON courses(course_name);

-- Create a view for course search
CREATE OR REPLACE VIEW course_search AS
SELECT 
    id,
    course_code,
    course_name,
    description,
    prerequisites,
    credits,
    department,
    course_code || ' - ' || course_name || ': ' || description AS full_text
FROM courses;