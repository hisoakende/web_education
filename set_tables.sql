CREATE TABLE teachers
(
    id           SERIAL PRIMARY KEY,
    first_name   VARCHAR(20)  NOT NULL,
    second_name  VARCHAR(20)  NOT NULL,
    patronymic   VARCHAR(20)  NOT NULL,
    email        VARCHAR(256) NOT NULL,
    password     CHAR(64)     NOT NULL,
    about_person VARCHAR      NOT NULL
);

CREATE TABLE classes
(
    id                   SERIAL PRIMARY KEY,
    number               INT                          NOT NULL,
    letter               CHAR(1)                      NOT NULL,
    classroom_teacher_id INT REFERENCES teachers (id) NOT NULL
);

CREATE TABLE students
(
    id          SERIAL PRIMARY KEY,
    first_name  VARCHAR(20)                 NOT NULL,
    second_name VARCHAR(20)                 NOT NULL,
    patronymic  VARCHAR(20)                 NOT NULl,
    email       VARCHAR(256)                NOT NULL,
    password    CHAR(64)                    NOT NULL,
    class_id    INT REFERENCES classes (id) NOT NULL
);

CREATE TABLE subjects
(
    id   SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE subject_class_teacher
(
    teacher_id INT REFERENCES teachers (id) NOT NULL,
    subject_id INT REFERENCES subjects (id) NOT NULL,
    class_id   INT REFERENCES classes (id)  NOT NULL
);

CREATE TABLE grades
(
    id         SERIAL PRIMARY KEY,
    value      INT                          NOT NULL,
    student_id INT REFERENCES students (id) NOT NULL,
    subject_id INT REFERENCES subjects (id) NOT NULL,
    teacher_id INT REFERENCES teachers (id) NOT NULL,
    date       DATE                         NOT NULL
);

CREATE TABLE administrators
(
    id          SERIAL PRIMARY KEY,
    first_name  VARCHAR(20)  NOT NULL,
    second_name VARCHAR(20)  NOT NULL,
    patronymic  VARCHAR(20)  NOT NULL,
    email       VARCHAR(256) NOT NULL,
    password    CHAR(64)     NOT NULL
);