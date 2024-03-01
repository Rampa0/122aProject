USE main;

--User table
CREATE TABLE Users (
    UCINetID VARCHAR(20) PRIMARY KEY NOT NULL,
    FirstName VARCHAR(50),
    MiddleName VARCHAR(50),
    LastName VARCHAR(50)
);
CREATE TABLE UserEmail (
  UCINetID VARCHAR(20)  NOT NULL,
  Email VARCHAR(1024),
  PRIMARY KEY (UCINetID, Email)
  FOREIGN KEY (UCINetID) REFERENCES Users (UCINetID)
    ON DELETE CASCADE
);


-- Student Delta Table
CREATE TABLE Students (
    UCINetID VARCHAR(20) PRIMARY KEY NOT NULL,
    FOREIGN KEY (UCINetID) REFERENCES Users(UCINetID)
      ON DELETE CASCADE
);


-- Administrator Delta Table
CREATE TABLE Administrators (
    UCINetID VARCHAR(20) NOT NULL,
    FOREIGN KEY (UCINetID) REFERENCES Users(UCINetID)
      ON DELETE CASCADE
);
CREATE TABLE AdministratorsShiftTiming (
    UCINetID VARCHAR(20) PRIMARY KEY NOT NULL,
    ShiftTiming VARCHAR(50),
    PRIMARY KEY (UCINetID, ShiftTiming)
    FOREIGN KEY (UCINetID) REFERENCES Administrators (UCINetID)
    ON DELETE CASCADE
);


-- Course Table
CREATE TABLE Courses (
    CourseID INT PRIMARY KEY NOT NULL,
    Title VARCHAR(100),
    Quarter VARCHAR(20)
);


-- Project Table
CREATE TABLE Projects (
    ProjectID INT PRIMARY KEY NOT NULL,
    Name VARCHAR(100),
    Description TEXT,
    CourseID INT NOT NULL,
    FOREIGN KEY (CourseID) REFERENCES Courses(CourseID)
);


-- Machine Table
CREATE TABLE Machines (
    MachineID INT PRIMARY KEY NOT NULL,
    IPAddress VARCHAR(15),
    OperationalStatus VARCHAR(50),
    Location VARCHAR(255)
);
CREATE TABLE MachineHostnames (
    MachineID INT NOT NULL,
    Hostname VARCHAR(255),
    PRIMARY KEY (MachineID, Hostname)
    FOREIGN KEY (MachineID) REFERENCES Machines (MachineID)
    ON DELETE CASCADE
);


-- Software Table
CREATE TABLE Software (
    SoftwareID INT PRIMARY KEY NOT NULL,
    Name VARCHAR(100),
    VersionNumber VARCHAR(50),
    LicenseKey VARCHAR(255)
);


-- Task Table
CREATE TABLE Tasks (
    TaskID INT PRIMARY KEY NOT NULL,
    MachineID INT NOT NULL,
    Description TEXT,
    PriorityLevel INT,
    AssignedDate  DATETIME,
    BeginTime DATETIME,
    EndTime DATETIME,
    FOREIGN KEY (MachineID) REFERENCES Machines (MachineID)
);


-- MaintenanceRecord Table
CREATE TABLE MaintenanceRecords (
    RecordID INT PRIMARY KEY NOT NULL,
    ServiceDate DATE,
    Duration INT,
    ServiceType VARCHAR(100),
    MachineID INT NOT NULL,
    FOREIGN KEY (MachineID) REFERENCES Machines(MachineID)
);


-- Install Relationship Table
CREATE TABLE SoftwareOfProjectInstallOnMachine (
    MachineID INT,
    SoftwareID INT,
    ProjectID INT,
    InstallDate DATE,
    PRIMARY KEY (MachineID, SoftwareID, ProjectID),
    FOREIGN KEY (MachineID) REFERENCES Machines(MachineID),
    FOREIGN KEY (SoftwareID) REFERENCES Software(SoftwareID),
    FOREIGN KEY (ProjectID) REFERENCES Software(ProjectID)
);


-- Use Relationship Table
CREATE TABLE StudentUseMachinesInProject (
    ProjectID INT,
    StudentUCINetID VARCHAR(20),
    MachineID INT,
    StartDate DATE,
    EndDate DATE,
    PRIMARY KEY (ProjectID, StudentUCINetID, MachineID),
    FOREIGN KEY (ProjectID) REFERENCES Projects(ProjectID),
    FOREIGN KEY (StudentUCINetID) REFERENCES Students(UCINetID),
    FOREIGN KEY (MachineID) REFERENCES Machines(MachineID)
);


-- Administrator Machine Management Table
CREATE TABLE AdministratorManageMachines (
    AdministratorUCINetID VARCHAR(20),
    MachineID INT,
    PRIMARY KEY (AdministratorUCINetID, MachineID),
    FOREIGN KEY (AdministratorUCINetID) REFERENCES Administrators(UCINetID),
    FOREIGN KEY (MachineID) REFERENCES Machines(MachineID)
);

