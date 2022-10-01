CREATE TABLE teachers
(
    id           SERIAL PRIMARY KEY,
    first_name   VARCHAR(20)  NOT NULL,
    second_name  VARCHAR(20)  NOT NULL,
    patronymic   VARCHAR(20)  NOT NULL,
    email        VARCHAR(256) NOT NULL UNIQUE,
    password     CHAR(64)     NOT NULL,
    about_person VARCHAR      NOT NULL
);

CREATE TABLE classes
(
    id                   SERIAL PRIMARY KEY,
    number               INT                                            NOT NULL,
    letter               CHAR(1)                                        NOT NULL,
    classroom_teacher_id INT REFERENCES teachers (id) ON DELETE CASCADE NOT NULL
);

CREATE TABLE students
(
    id              SERIAL PRIMARY KEY,
    first_name      VARCHAR(20)                                   NOT NULL,
    second_name     VARCHAR(20)                                   NOT NULL,
    patronymic      VARCHAR(20)                                   NOT NULl,
    email           VARCHAR(256)                                  NOT NULL UNIQUE,
    password        CHAR(64)                                      NOT NULL,
    school_class_id INT REFERENCES classes (id) ON DELETE CASCADE NOT NULL
);

CREATE TABLE subjects
(
    id   SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE subject_class_teacher
(
    id              SERIAL PRIMARY KEY,
    teacher_id      INT REFERENCES teachers (id) ON DELETE CASCADE NOT NULL,
    subject_id      INT REFERENCES subjects (id) ON DELETE CASCADE NOT NULL,
    school_class_id INT REFERENCES classes (id) ON DELETE CASCADE  NOT NULL
);

CREATE TABLE grades
(
    id         SERIAL PRIMARY KEY,
    value      INT                                            NOT NULL,
    student_id INT REFERENCES students (id) ON DELETE CASCADE NOT NULL,
    subject_id INT REFERENCES subjects (id) ON DELETE CASCADE NOT NULL,
    teacher_id INT REFERENCES teachers (id) ON DELETE CASCADE NOT NULL,
    date       DATE                                           NOT NULL
);

CREATE TABLE administrators
(
    id          SERIAL PRIMARY KEY,
    first_name  VARCHAR(20)  NOT NULL,
    second_name VARCHAR(20)  NOT NULL,
    patronymic  VARCHAR(20)  NOT NULL,
    email       VARCHAR(256) NOT NULL UNIQUE,
    password    CHAR(64)     NOT NULL
);

CREATE TABLE periods
(
    id         SERIAL PRIMARY KEY,
    start      DATE NOT NULL,
    finish     DATE NOT NULL,
    is_current BOOLEAN
);