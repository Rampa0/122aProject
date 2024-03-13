-- User Table
CREATE TABLE User (
    UCINetID VARCHAR(255) PRIMARY KEY,
    name_first VARCHAR(255),
    name_middle VARCHAR(255),
    name_last VARCHAR(255)
);
CREATE TABLE UserEmail (
  UCINetID VARCHAR(20) NOT NULL,
  Email VARCHAR(255),
  PRIMARY KEY (UCINetID, Email),
  FOREIGN KEY (UCINetID) REFERENCES User(UCINetID)
        ON DELETE CASCADE
);


-- Student Table
CREATE TABLE Student (
    UCINetID VARCHAR(255) PRIMARY KEY NOT NULL,
    FOREIGN KEY (UCINetID) REFERENCES User(UCINetID)
        ON DELETE CASCADE
);

-- Administrator Table
CREATE TABLE Administrator (
    UCINetID VARCHAR(255) PRIMARY KEY NOT NULL,
    FOREIGN KEY (UCINetID) REFERENCES User(UCINetID)
        ON DELETE CASCADE
);

-- Course Table
CREATE TABLE Course (
    course_id INT PRIMARY KEY NOT NULL,
    title VARCHAR(255),
    quarter VARCHAR(255)
);

-- Project Table | folded with course
CREATE TABLE Project (
    project_id INT PRIMARY KEY NOT NULL,
    description TEXT,
    name VARCHAR(255),
    course_id INT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES Course(course_id)
);

-- Machine Table
CREATE TABLE Machine (
    machine_id INT PRIMARY KEY NOT NULL,
    hostname VARCHAR(255),
    IP_address VARCHAR(255),
    operational_status VARCHAR(255),
    location VARCHAR(255)
);

-- Use Relationship
CREATE TABLE StudentUseMachineInProject (
    project_id INT,
    UCINetID VARCHAR(255),
    machine_id INT,
    start_date DATE,
    end_date DATE,
    PRIMARY KEY (UCINetID, project_id, machine_id),
    FOREIGN KEY (UCINetID) REFERENCES Student(UCINetID),
    FOREIGN KEY (project_id) REFERENCES Project(project_id),
    FOREIGN KEY (machine_id) REFERENCES Machine(machine_id)
);


-- Manage (Machine-Administrator Relationship) Table
CREATE TABLE AdministratorManageMachine  (
    UCINetID VARCHAR(255),
    machine_id INT,
    PRIMARY KEY (UCINetID, machine_id),
    FOREIGN KEY (UCINetID) REFERENCES Administrator(UCINetID),
    FOREIGN KEY (machine_id) REFERENCES Machine(machine_id)
);