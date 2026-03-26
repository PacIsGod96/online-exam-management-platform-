USE exam_website;
CREATE TABLE accounts (
	account_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    teacher_id INT NOT NULL,
    student_id INT NOT NULL,
    role ENUM('student', 'teacher') NOT NULL
);

CREATE TABLE tests (
	test_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    test_disc VARCHAR(1000) NOT NULL,
    created_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE questions (
	question_id INT PRIMARY KEY AUTO_INCREMENT,
	question_text VARCHAR(1000) NOT NULL,
    question_type ENUM('MCQ', 'True/False', 'Short Answer') NOT NULL,
    points INT NOT NULL
);

CREATE TABLE answers (
	answer_id INT PRIMARY KEY AUTO_INCREMENT,
    question_id INT NOT NULL,
    answer_text VARCHAR(500) NOT NULL,
    is_correct TINYINT(1) NOT NULL DEFAULT 0,
    FOREIGN KEY (question_id) REFERENCES questions(question_id)
);

CREATE TABLE test_questions (
	test_id INT NOT NULL,
    question_id INT NOT NULL,
	question_order INT DEFAULT 1,
    PRIMARY KEY (test_id, question_id),
    FOREIGN KEY (test_id) REFERENCES tests(test_id),
    FOREIGN KEY (question_id) REFERENCES questions(question_id)
);

CREATE TABLE StudentAnswers (
	student_id INT NOT NULL,
    test_id INT NOT NULL,
    question_id INT NOT NULL, 
    answer_id INT,
    submitted_answer VARCHAR(1000),
    is_correct TINYINT(1) NOT NULL,
    points_earned DECIMAL(5,2) DEFAULT 0,
    PRIMARY KEY (student_id, test_id, question_id),
    FOREIGN KEY (student_id) REFERENCES accounts(account_id),
    FOREIGN KEY (test_id) REFERENCES tests(test_id),
    FOREIGN KEY (question_id) REFERENCES questions(question_id),
    FOREIGN KEY (answer_id) REFERENCES answers(answer_id)
);

SHOW TABLES 

