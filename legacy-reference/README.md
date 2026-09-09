# 🎓 Student Clearance Management System

A complete **Student Clearance Management System** built with **MySQL** and **Python (GUI frontend)**.  
This project manages student clearance processes, fee records, department clearances, and payment transactions in an educational institution.

---

## 🚀 Features

✅ **Student Records Management**  
- Add, edit, delete, and search student records  
- Store details: name, registration number, contact, email, city, department, discipline  

✅ **Fee Management**  
- Record total fee, paid fee, remaining dues  
- Automatic fee balance calculation  
- Trigger to auto-update paid amounts on transaction insert  

✅ **Payment Transactions**  
- Supports multiple payment methods (Bank Transfer, EasyPaisa, JazzCash, Cash, etc.)  
- Track payments with status, verified by, remarks, reference number  

✅ **Department Clearance**  
- Manage clearance records for Finance, Library, Hostel, Examination  
- Mark students as cleared or pending in each department  

✅ **Reports & Views**  
- Payment summaries: total fee, paid, dues, status  
- Clearance summaries: cleared / not cleared  
- Payment history  
- List of students with pending dues  

✅ **Python Frontend**  
- Simple login screen  
- GUI to manage student, payment, and clearance records  
- Search and filter options  
- Generate clearance and dues reports  

---

## ⚙️ Tech Stack

- **Backend Database:** MySQL  
- **Frontend:** Python (Tkinter / PyQt / Custom GUI)  
- **SQL:** Triggers, Stored Procedures, Views  

---

## 📂 Database Structure

- **Students** — Stores student info  
- **FeeRecord** — Stores fee and payment details  
- **PaymentMethods** — List of accepted payment methods  
- **PaymentTransactions** — Tracks payments and transactions  
- **Departments** — List of clearance departments  
- **ClearanceRecords** — Tracks department clearance status  

---

## 💻 How to Run

1️⃣ Clone or download the project repository  
2️⃣ Import the SQL schema in your MySQL server  
3️⃣ Run the Python frontend application  
4️⃣ Login and start managing student clearance records  

---

## 📈 Future Improvements

- Add admin roles with access levels  
- Export reports to PDF/Excel  
- Email / SMS notifications for dues and clearance updates  

---

## 📌 Author

**Zarrar Haider**  
*Artificial Intelligence Student*  
