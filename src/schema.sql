-- User Table
CREATE TABLE User (
    UCINetID VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255),
    name_first VARCHAR(255),
    name_middle VARCHAR(255),
    name_last VARCHAR(255)
);

-- Student Table
CREATE TABLE Student (
    UCINetID VARCHAR(255) PRIMARY KEY,
    FOREIGN KEY (UCINetID) REFERENCES User(UCINetID) ON DELETE CASCADE
);

-- Administrator Table
CREATE TABLE Administrator (
    UCINetID VARCHAR(255) PRIMARY KEY,
    FOREIGN KEY (UCINetID) REFERENCES User(UCINetID) ON DELETE CASCADE
);

-- Course Table
CREATE TABLE Course (
    course_id INT PRIMARY KEY,
    title VARCHAR(255),
    quarter VARCHAR(255)
);

-- Project Table
CREATE TABLE Project (
    project_id INT PRIMARY KEY,
    description TEXT,
    name VARCHAR(255)
);

-- Machine Table
CREATE TABLE Machine (
    machine_id INT PRIMARY KEY,
    hostname VARCHAR(255),
    IP_address VARCHAR(255),
    operational_status VARCHAR(255),
    location VARCHAR(255)
);

-- Use Table
CREATE TABLE UseRecord (
    start_date DATE,
    end_date DATE,
    UCINetID VARCHAR(255),
    project_id INT,
    machine_id INT,
    PRIMARY KEY (start_date, end_date, UCINetID, project_id, machine_id),
    FOREIGN KEY (UCINetID) REFERENCES User(UCINetID),
    FOREIGN KEY (project_id) REFERENCES Project(project_id),
    FOREIGN KEY (machine_id) REFERENCES Machine(machine_id)
);

-- Have (Course-Project Relationship) Table
CREATE TABLE Have (
    course_id INT,
    project_id INT,
    PRIMARY KEY (course_id, project_id),
    FOREIGN KEY (course_id) REFERENCES Course(course_id),
    FOREIGN KEY (project_id) REFERENCES Project(project_id)
);

-- Manage (Machine-Administrator Relationship) Table
CREATE TABLE Manage (
    machine_id INT,
    UCINetID VARCHAR(255),
    PRIMARY KEY (machine_id, UCINetID),
    FOREIGN KEY (machine_id) REFERENCES Machine(machine_id),
    FOREIGN KEY (UCINetID) REFERENCES Administrator(UCINetID)
);