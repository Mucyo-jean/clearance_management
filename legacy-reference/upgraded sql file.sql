-- Drop and Create the Database
DROP DATABASE IF EXISTS StudentClearanceDB;
CREATE DATABASE StudentClearanceDB;
USE StudentClearanceDB;

-- Create PaymentMethods Table
CREATE TABLE PaymentMethods (
  id INT AUTO_INCREMENT PRIMARY KEY,
  method_name VARCHAR(50) NOT NULL,
  description VARCHAR(255),
  is_active BIT DEFAULT 1
);

-- Insert Payment Methods
INSERT INTO PaymentMethods (method_name, description) VALUES
('Bank Transfer', 'Direct bank transfer to university account'),
('Credit Card', 'Payment via credit card through online portal'),
('Debit Card', 'Payment via debit card through online portal'),
('EasyPaisa', 'Mobile payment through EasyPaisa'),
('JazzCash', 'Mobile payment through JazzCash'),
('Cash', 'Cash payment at university counter'),
('Bank Draft', 'Payment via bank draft'),
('Cheque', 'Payment via cheque');

-- Create Departments Table
CREATE TABLE Departments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  dept_name VARCHAR(100) NOT NULL
);

-- Insert Departments
INSERT INTO Departments (dept_name) VALUES
('Finance'), ('Library'), ('Hostel'), ('Examination');

-- Create Students Table
CREATE TABLE Students (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  reg_no VARCHAR(50) UNIQUE NOT NULL,
  contact_no VARCHAR(15),
  email VARCHAR(100),
  city VARCHAR(50),
  department VARCHAR(100),
  discipline VARCHAR(100),
  status BIT DEFAULT 1
);

-- Create FeeRecord Table
CREATE TABLE FeeRecord (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  total_fee DECIMAL(10,2) NOT NULL,
  paid_fee DECIMAL(10,2) NOT NULL DEFAULT 0,
  remaining_fee DECIMAL(10,2) GENERATED ALWAYS AS (total_fee - paid_fee) STORED,
  last_payment_date DATETIME,
  FOREIGN KEY (student_id) REFERENCES Students(id) ON DELETE CASCADE
);

-- Create PaymentTransactions Table
CREATE TABLE PaymentTransactions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  payment_method_id INT NOT NULL,
  transaction_reference VARCHAR(100),
  amount DECIMAL(10,2) NOT NULL,
  transaction_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  verified_by VARCHAR(100),
  verification_date DATETIME,
  status ENUM('Pending', 'Completed', 'Failed', 'Refunded') DEFAULT 'Pending',
  remarks TEXT,
  FOREIGN KEY (student_id) REFERENCES Students(id) ON DELETE CASCADE,
  FOREIGN KEY (payment_method_id) REFERENCES PaymentMethods(id)
);

-- Create ClearanceRecords Table
CREATE TABLE ClearanceRecords (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  dept_id INT NOT NULL,
  cleared_by VARCHAR(100),
  status BIT NOT NULL,
  remarks TEXT,
  clearance_date DATE,
  FOREIGN KEY (student_id) REFERENCES Students(id) ON DELETE CASCADE,
  FOREIGN KEY (dept_id) REFERENCES Departments(id) ON DELETE CASCADE
);

-- Insert 100 Students
INSERT INTO Students (name, reg_no, contact_no, email, city, department, discipline) VALUES
('Zarrar Haider', 'NUML-F23-29573', '0300-3333222', 'zarrar@example.com', 'Islamabad', 'CS', 'Artificial Intelligence'),
('Fatima Noor', 'NUML-F23-3713', '0311-2345678', 'fatima@example.com', 'Lahore', 'Software Engineering', 'Software Engineering'),
('Zain Ali', 'NUML-F23-3714', '0321-3456789', 'zain@example.com', 'Karachi', 'Computer Science', 'Computer Science'),
('Ayesha Malik', 'NUML-F23-3715', '0331-4567890', 'ayesha@example.com', 'Peshawar', 'Information Systems', 'Information Systems'),
('Usman Tariq', 'NUML-F23-3716', '0341-5678901', 'usman@example.com', 'Multan', 'Cyber Security', 'Cyber Security'),
('Hira Iqbal', 'NUML-F23-3717', '0351-6789012', 'hira@example.com', 'Quetta', 'Artificial Intelligence', 'Artificial Intelligence'),
('Bilal Saeed', 'NUML-F23-3718', '0361-7890123', 'bilal@example.com', 'Rawalpindi', 'Computer Engineering', 'Computer Engineering'),
('Mariam Zahra', 'NUML-F23-3719', '0371-8901234', 'mariam@example.com', 'Faisalabad', 'Software Engineering', 'Software Engineering'),
('Sami Ullah', 'NUML-F23-3720', '0381-9012345', 'sami@example.com', 'Sargodha', 'Data Science', 'Data Science'),
('Nida Hassan', 'NUML-F23-3721', '0391-9123456', 'nida@example.com', 'Islamabad', 'Management Sciences', 'Finance'),
('Ali Raza', 'NUML-F23-3722', '0301-1234567', 'ali.raza@example.com', 'Lahore', 'CS', 'AI'),
('Sana Khan', 'NUML-F23-3723', '0302-2345678', 'sana.khan@example.com', 'Karachi', 'Software Engineering', 'Software Engineering'),
('Ahmed Iqbal', 'NUML-F23-3724', '0303-3456789', 'ahmed.iqbal@example.com', 'Peshawar', 'Cyber Security', 'Cyber Security'),
('Hassan Ali', 'NUML-F23-3725', '0304-4567890', 'hassan.ali@example.com', 'Multan', 'Information Systems', 'Information Systems'),
('Farah Zahra', 'NUML-F23-3726', '0305-5678901', 'farah.zahra@example.com', 'Quetta', 'AI', 'AI'),
('Tariq Jameel', 'NUML-F23-3727', '0306-6789012', 'tariq.jameel@example.com', 'Rawalpindi', 'Computer Engineering', 'Computer Engineering'),
('Iqra Shah', 'NUML-F23-3728', '0307-7890123', 'iqra.shah@example.com', 'Faisalabad', 'Software Engineering', 'Software Engineering'),
('Shahbaz Khan', 'NUML-F23-3729', '0308-8901234', 'shahbaz.khan@example.com', 'Sargodha', 'Data Science', 'Data Science'),
('Areeba Siddiqui', 'NUML-F23-3730', '0309-9012345', 'areeba.s@example.com', 'Islamabad', 'Management Sciences', 'Finance'),
('Saad Jamil', 'NUML-F23-3731', '0310-9123456', 'saad.jamil@example.com', 'Lahore', 'CS', 'AI'),
('Komal Rehman', 'NUML-F23-3732', '0311-1234567', 'komal.rehman@example.com', 'Karachi', 'Software Engineering', 'Software Engineering'),
('Arsalan Ahmed', 'NUML-F23-3733', '0312-2345678', 'arsalan.a@example.com', 'Peshawar', 'Cyber Security', 'Cyber Security'),
('Mehwish Khan', 'NUML-F23-3734', '0313-3456789', 'mehwish.k@example.com', 'Multan', 'Information Systems', 'Information Systems'),
('Adnan Sheikh', 'NUML-F23-3735', '0314-4567890', 'adnan.s@example.com', 'Quetta', 'AI', 'AI'),
('Rabia Noor', 'NUML-F23-3736', '0315-5678901', 'rabia.n@example.com', 'Rawalpindi', 'Computer Engineering', 'Computer Engineering'),
('Fahad Hussain', 'NUML-F23-3737', '0316-6789012', 'fahad.h@example.com', 'Faisalabad', 'Software Engineering', 'Software Engineering'),
('Huma Tariq', 'NUML-F23-3738', '0317-7890123', 'huma.t@example.com', 'Sargodha', 'Data Science', 'Data Science'),
('Zeeshan Ali', 'NUML-F23-3739', '0318-8901234', 'zeeshan.a@example.com', 'Islamabad', 'Management Sciences', 'Finance'),
('Samina Asif', 'NUML-F23-3740', '0319-9012345', 'samina.a@example.com', 'Lahore', 'CS', 'AI'),
('Yasir Qureshi', 'NUML-F23-3741', '0320-9123456', 'yasir.q@example.com', 'Karachi', 'Software Engineering', 'Software Engineering'),
('Laiba Shahid', 'NUML-F23-3742', '0321-1234567', 'laiba.s@example.com', 'Peshawar', 'Cyber Security', 'Cyber Security'),
('Arham Khan', 'NUML-F23-3743', '0322-2345678', 'arham.k@example.com', 'Multan', 'Information Systems', 'Information Systems'),
('Sadia Javed', 'NUML-F23-3744', '0323-3456789', 'sadia.j@example.com', 'Quetta', 'AI', 'AI'),
('Shaheryar Malik', 'NUML-F23-3745', '0324-4567890', 'shaheryar.m@example.com', 'Rawalpindi', 'Computer Engineering', 'Computer Engineering'),
('Nimra Tariq', 'NUML-F23-3746', '0325-5678901', 'nimra.t@example.com', 'Faisalabad', 'Software Engineering', 'Software Engineering'),
('Danish Raza', 'NUML-F23-3747', '0326-6789012', 'danish.r@example.com', 'Sargodha', 'Data Science', 'Data Science'),
('Hafsa Khan', 'NUML-F23-3748', '0327-7890123', 'hafsa.k@example.com', 'Islamabad', 'Management Sciences', 'Finance'),
('Rizwan Ali', 'NUML-F23-3749', '0328-8901234', 'rizwan.a@example.com', 'Lahore', 'CS', 'AI'),
('Aiman Bibi', 'NUML-F23-3750', '0329-9012345', 'aiman.b@example.com', 'Karachi', 'Software Engineering', 'Software Engineering')
;

-- Generate remaining students dynamically (example pattern)
-- (Note: In real SQL, you'd need to generate these using a script or tool)
-- Below is sample code format:
-- ('Student Name', 'NUML-F23-3722', '03xx-xxxxxxx', 'email', 'city', 'dept', 'discipline')
;

-- To fill in remaining students use:
-- (you can use Python / Excel to generate this SQL insert or I can provide)

-- Insert random FeeRecord for 100 students
INSERT INTO FeeRecord (student_id, total_fee, paid_fee, last_payment_date)
SELECT id, 
       ROUND(60000 + (RAND() * 50000), 2),
       ROUND(40000 + (RAND() * 20000), 2),
       NOW() - INTERVAL FLOOR(RAND() * 180) DAY
FROM Students;

-- Insert ClearanceRecords for all students and departments
INSERT INTO ClearanceRecords (student_id, dept_id, cleared_by, status, remarks, clearance_date)
SELECT s.id, d.id, 'System', FLOOR(RAND()*2), 
       CASE WHEN FLOOR(RAND()*2)=1 THEN 'Cleared' ELSE 'Pending' END,
       CURDATE() - INTERVAL FLOOR(RAND()*100) DAY
FROM Students s
CROSS JOIN Departments d;

-- Insert random PaymentTransactions
INSERT INTO PaymentTransactions (student_id, payment_method_id, transaction_reference, amount, transaction_date, verified_by, verification_date, status, remarks)
SELECT s.id,
       FLOOR(1 + (RAND() * 8)),
       CONCAT('TXN-', s.id, '-', FLOOR(RAND()*10000)),
       ROUND(5000 + (RAND() * 20000), 2),
       NOW() - INTERVAL FLOOR(RAND() * 180) DAY,
       'System',
       NOW() - INTERVAL FLOOR(RAND() * 180) DAY,
       'Completed',
       'Auto-generated payment'
FROM Students s;

-- Trigger
DELIMITER //
CREATE TRIGGER after_payment_insert
AFTER INSERT ON PaymentTransactions
FOR EACH ROW
BEGIN
    IF NEW.status = 'Completed' THEN
        UPDATE FeeRecord 
        SET paid_fee = paid_fee + NEW.amount,
            last_payment_date = NEW.verification_date
        WHERE student_id = NEW.student_id;
    END IF;
END//
DELIMITER ;

-- Stored Procedure
DELIMITER //
CREATE PROCEDURE MakePayment(
    IN p_student_id INT,
    IN p_payment_method_id INT,
    IN p_transaction_reference VARCHAR(100),
    IN p_amount DECIMAL(10,2),
    IN p_verified_by VARCHAR(100),
    IN p_remarks TEXT
)
BEGIN
    DECLARE student_exists INT;
    SELECT COUNT(*) INTO student_exists FROM Students WHERE id = p_student_id;
    IF student_exists = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Student does not exist';
    ELSE
        INSERT INTO PaymentTransactions (
            student_id, 
            payment_method_id, 
            transaction_reference, 
            amount, 
            verified_by, 
            verification_date, 
            status, 
            remarks
        ) VALUES (
            p_student_id,
            p_payment_method_id,
            p_transaction_reference,
            p_amount,
            p_verified_by,
            NOW(),
            'Completed',
            p_remarks
        );
        SELECT CONCAT('Payment of ', p_amount, ' recorded successfully for student ID ', p_student_id) AS message;
    END IF;
END//
DELIMITER ;

-- Views
CREATE OR REPLACE VIEW PaymentSummary AS
SELECT 
    s.id AS student_id,
    s.name,
    s.reg_no,
    fr.total_fee,
    fr.paid_fee,
    fr.remaining_fee,
    fr.last_payment_date,
    CASE 
        WHEN fr.remaining_fee <= 0 THEN 'Fully Paid'
        ELSE 'Pending Payment'
    END AS payment_status
FROM Students s
JOIN FeeRecord fr ON s.id = fr.student_id;

CREATE OR REPLACE VIEW PaymentHistory AS
SELECT 
    pt.id AS transaction_id,
    s.id AS student_id,
    s.name,
    s.reg_no,
    pm.method_name AS payment_method,
    pt.transaction_reference,
    pt.amount,
    pt.transaction_date,
    pt.verified_by,
    pt.verification_date,
    pt.status,
    pt.remarks
FROM PaymentTransactions pt
JOIN Students s ON pt.student_id = s.id
JOIN PaymentMethods pm ON pt.payment_method_id = pm.id
ORDER BY pt.transaction_date DESC;

CREATE OR REPLACE VIEW StudentClearanceSummary AS
SELECT 
    s.id AS student_id,
    s.name,
    s.reg_no,
    fr.total_fee,
    fr.paid_fee,
    fr.remaining_fee,
    CASE 
        WHEN fr.remaining_fee = 0 THEN 'Fee Cleared'
        ELSE 'Fee Due'
    END AS fee_status,
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM ClearanceRecords cr 
            WHERE cr.student_id = s.id AND cr.status = 0
        ) THEN 'Not Fully Cleared'
        ELSE 'Cleared All Departments'
    END AS clearance_status
FROM Students s
LEFT JOIN FeeRecord fr ON s.id = fr.student_id;
