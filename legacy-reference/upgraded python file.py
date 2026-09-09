import mysql.connector
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime # Added datetime
from tkinter import font as tkfont
import re
import os
from PIL import Image, ImageTk

# --- Database connection ---
def create_db_connection():
    """Creates and returns a database connection object."""
    try:
        conn = mysql.connector.connect(
            host="localhost",        # Replace if your DB is not on localhost
            user="root",             # Replace with your MySQL username
            password="Saimumer@2409",  # Replace with your actual MySQL password
            database="StudentClearanceDB"
        )
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error connecting to database: {err}")
        return None

# Establish the global connection and cursor
conn = create_db_connection()
if conn:
    cursor = conn.cursor(dictionary=True) # dictionary=True allows accessing columns by name
else:
    # If connection fails at startup, inform the user and exit.
    if messagebox.askokcancel("Database Error", "Failed to connect to the database. The application cannot start.\nCheck database server and credentials.\n\nExit application?"):
        exit()

# --- Login window ---
class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Clearance System - Login")
        self.geometry("700x550")
        self.resizable(False, False)
        self.configure(bg="#e6f2ff")

        self.eval('tk::PlaceWindow . center') # Center the window

        # Fonts
        title_font = tkfont.Font(family="Helvetica", size=20, weight="bold")
        label_font = tkfont.Font(family="Helvetica", size=11)

        main_frame = tk.Frame(self, bg="#e6f2ff", padx=30, pady=30)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Logo (with fallback)
        logo_frame = tk.Frame(main_frame, bg="#e6f2ff")
        logo_frame.pack(pady=(0, 25))
        try:
            logo_path = "logo.png"
            if not os.path.exists(logo_path): # Fallback if logo.png is missing
                from tkinter import Canvas
                logo_canvas = Canvas(logo_frame, width=120, height=120, bg="#e6f2ff", highlightthickness=0)
                logo_canvas.pack()
                logo_canvas.create_oval(10, 10, 110, 110, fill="#3399ff", outline="#2e8bda")
                logo_canvas.create_text(60, 60, text="SCS", fill="white", font=("Helvetica", 28, "bold"))
            else:
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((120, 120), Image.Resampling.LANCZOS)
                self.logo = ImageTk.PhotoImage(logo_img)
                tk.Label(logo_frame, image=self.logo, bg="#e6f2ff").pack()
        except Exception as e:
            print(f"Error loading logo: {e}")
            fallback_label = tk.Label(logo_frame, text="SCS", font=("Helvetica", 28, "bold"), bg="#3399ff", fg="white", width=6, height=3)
            fallback_label.pack()

        tk.Label(main_frame, text="Student Clearance System", font=title_font, bg="#e6f2ff", fg="#003366").pack(pady=(0, 20))

        # Login Form
        form_frame = tk.Frame(main_frame, bg="#ffffff", bd=2, relief=tk.RIDGE)
        form_frame.pack(padx=30, pady=10)
        inner_frame = tk.Frame(form_frame, bg="#ffffff", padx=25, pady=25)
        inner_frame.pack()

        tk.Label(inner_frame, text="Username:", font=label_font, bg="#ffffff").grid(row=0, column=0, sticky=tk.W, pady=10)
        self.username_entry = ttk.Entry(inner_frame, width=30)
        self.username_entry.grid(row=0, column=1, pady=10, padx=10)
        self.username_entry.focus()

        tk.Label(inner_frame, text="Password:", font=label_font, bg="#ffffff").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.password_entry = ttk.Entry(inner_frame, show="•", width=30)
        self.password_entry.grid(row=1, column=1, pady=10, padx=10)

        self.show_password_var = tk.IntVar()
        show_pass_check = ttk.Checkbutton(inner_frame, text="Show password", variable=self.show_password_var,
                                    command=self.toggle_password_visibility)
        show_pass_check.grid(row=2, column=1, sticky=tk.W, pady=(5,10))

        login_btn = ttk.Button(main_frame, text="Login", command=self.check_login, style="Accent.TButton")
        login_btn.pack(pady=20)

        forgot_link = tk.Label(main_frame, text="Forgot password?", fg="#0052cc", cursor="hand2", bg="#e6f2ff", font=("Helvetica", 10, "underline"))
        forgot_link.pack()
        forgot_link.bind("<Button-1>", lambda e: messagebox.showinfo("Forgot Password", "Please contact system administrator."))

        self.bind('<Return>', lambda event: self.check_login()) # Allow login with Enter key

        # Styling for the login button
        self.style = ttk.Style()
        self.style.configure("Accent.TButton", foreground="white", background="#3399ff", font=("Helvetica", 10, "bold"), padding=6)
        self.style.map("Accent.TButton",
                       foreground=[('pressed', 'white'), ('active', 'white')],
                       background=[('pressed', '#2e8bda'), ('active', '#2e8bda')])

    def toggle_password_visibility(self):
        """Toggles the visibility of the password in the entry field."""
        if self.show_password_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="•")

    def check_login(self):
        """Validates user credentials and opens the main application if successful."""
        user = self.username_entry.get()
        pwd = self.password_entry.get()

        if not user or not pwd:
            messagebox.showerror("Login Failed", "Both username and password are required!")
            return

        # Hardcoded credentials as per original requirement
        if user == "admin" and pwd == "admin":
            self.destroy() # Close the login window
            MainApp()      # Open the main application
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")
            self.password_entry.delete(0, tk.END) # Clear password field
            self.password_entry.focus()

# --- Main Application Window ---
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Clearance Management System")
        self.geometry("1200x700")
        self.state('zoomed') # Start maximized

        self.style = ttk.Style()
        self.style.theme_use('clam') # A modern theme
        self.configure_styles() # Apply custom styles

        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        self.create_header()
        self.create_tabs_widget() # Renamed for clarity
        self.create_status_bar()

        self.payment_methods_map = {} # To store 'method_name' -> 'id'
        self.departments_map = {}     # To store 'dept_name' -> 'id'

        # Initialize data for fee update and clearance tabs
        self.current_fee_student_id = None
        self.current_student_total_fee = 0.0
        self.current_student_paid_fee = 0.0
        self.current_clearance_student_id = None


        self.refresh_all_data() # Load initial data into treeviews
        self.eval('tk::PlaceWindow . center')


    def configure_styles(self):
        """Configures custom ttk styles for the application."""
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Helvetica', 10))
        self.style.configure('TButton', font=('Helvetica', 10), padding=5)
        self.style.configure('Treeview', font=('Helvetica', 10), rowheight=25)
        self.style.configure('Treeview.Heading', font=('Helvetica', 10, 'bold'))
        self.style.map('Treeview', background=[('selected', '#0078D7')], foreground=[('selected', 'white')])
        self.style.configure('Accent.TButton', foreground='white', background='#4CAF50', font=('Helvetica', 10, 'bold'))
        self.style.map('Accent.TButton',
                       foreground=[('pressed', 'white'), ('active', 'white')],
                       background=[('pressed', '#45a049'), ('active', '#45a049')])
        self.style.configure('Warning.TButton', foreground='white', background='#f44336', font=('Helvetica', 10, 'bold'))
        self.style.map('Warning.TButton',
                      foreground=[('pressed', 'white'), ('active', 'white')],
                      background=[('pressed', '#d32f2f'), ('active', '#d32f2f')])
        self.style.configure('Header.TFrame', background='#e1e1e1')
        self.style.configure('Header.TLabel', background='#e1e1e1')
        self.style.configure('Status.TFrame', background='#d0d0d0') # Style for status bar
        self.style.configure('Status.TLabel', background='#d0d0d0')

    def create_header(self):
        """Creates the header frame with title and logout button."""
        header_frame = ttk.Frame(self.main_container, style='Header.TFrame', padding=5)
        header_frame.pack(fill=tk.X, padx=10, pady=(10,5))

        title_font = tkfont.Font(family="Helvetica", size=16, weight="bold")
        ttk.Label(header_frame, text="Student Clearance Management System",
                 font=title_font, style='Header.TLabel').pack(side=tk.LEFT, padx=10)

        logout_btn = ttk.Button(header_frame, text="Logout", command=self.logout, style='Warning.TButton')
        logout_btn.pack(side=tk.RIGHT, padx=10)

    def create_tabs_widget(self):
        """Creates the notebook widget and its tabs."""
        self.tabs_notebook = ttk.Notebook(self.main_container) # Renamed for clarity
        self.tabs_notebook.pack(expand=1, fill='both', padx=10, pady=(0, 5))

        # Define frames for each tab
        self.all_students_tab = ttk.Frame(self.tabs_notebook, padding=10)
        self.dues_tab = ttk.Frame(self.tabs_notebook, padding=10)
        self.clearance_tab = ttk.Frame(self.tabs_notebook, padding=10)
        self.add_student_tab = ttk.Frame(self.tabs_notebook, padding=10)
        self.update_fee_tab = ttk.Frame(self.tabs_notebook, padding=10)
        self.mark_clearance_tab = ttk.Frame(self.tabs_notebook, padding=10)
        self.search_tab = ttk.Frame(self.tabs_notebook, padding=10)

        # Add tabs to the notebook
        self.tabs_notebook.add(self.all_students_tab, text="All Students")
        self.tabs_notebook.add(self.dues_tab, text="Students with Dues")
        self.tabs_notebook.add(self.clearance_tab, text="Clearance Status")
        self.tabs_notebook.add(self.search_tab, text="Search Student")
        self.tabs_notebook.add(self.add_student_tab, text="Add Student")
        self.tabs_notebook.add(self.update_fee_tab, text="Update Fee Payment")
        self.tabs_notebook.add(self.mark_clearance_tab, text="Mark Clearance")

        # Build the content of each tab
        self.build_all_students_tab()
        self.build_dues_tab()
        self.build_clearance_tab()
        self.build_add_student_tab()
        self.build_update_fee_tab() # This is the critical one for the user's problem
        self.build_mark_clearance_tab()
        self.build_search_tab()

    def create_status_bar(self):
        """Creates the status bar at the bottom of the window."""
        status_bar_frame = ttk.Frame(self.main_container, style='Status.TFrame', relief=tk.SUNKEN)
        status_bar_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(0,10))

        self.status_label = ttk.Label(status_bar_frame, text="Ready", anchor=tk.W, style='Status.TLabel')
        self.status_label.pack(side=tk.LEFT, padx=5, pady=2)

        self.timestamp_label = ttk.Label(status_bar_frame, text="", anchor=tk.E, style='Status.TLabel')
        self.timestamp_label.pack(side=tk.RIGHT, padx=5, pady=2)
        self.update_timestamp() # Start updating timestamp

    def update_timestamp(self):
        """Updates the timestamp in the status bar every second."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.timestamp_label.config(text=f"Timestamp: {now}")
        except tk.TclError: # Window might be destroyed
            return
        self.after(1000, self.update_timestamp) # Schedule next update

    def set_status(self, message):
        """Sets a message in the status bar."""
        self.status_label.config(text=message)
        self.update_idletasks() # Force UI update

    def refresh_all_data(self):
        """Refreshes data in all relevant treeviews and loads combobox data."""
        self.set_status("Refreshing data...")
        self.refresh_all_students()
        self.refresh_dues()
        self.refresh_clearance()
        self.load_payment_methods_for_combobox() # Crucial for fee update tab
        self.load_departments_for_combobox()     # Crucial for mark clearance tab
        self.set_status("All data refreshed successfully.")

    # --- Tab Building Methods ---
    def build_all_students_tab(self):
        """Builds the UI for the 'All Students' tab."""
        main_frame = ttk.Frame(self.all_students_tab)
        main_frame.pack(fill=tk.BOTH, expand=True)

        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0,5))

        y_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        x_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        
        cols = ("ID", "Name", "Reg No", "Contact No", "Email", "City", "Department", "Discipline")
        self.all_students_tree = ttk.Treeview(tree_frame, columns=cols, show='headings',
                                             yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.all_students_tree.pack(fill=tk.BOTH, expand=True)

        y_scroll.config(command=self.all_students_tree.yview)
        x_scroll.config(command=self.all_students_tree.xview)

        for col in cols:
            self.all_students_tree.heading(col, text=col)
            self.all_students_tree.column(col, anchor=tk.W if col == "Name" else tk.CENTER, width=120, minwidth=80)

        self.setup_treeview_context_menu(self.all_students_tree)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Button(btn_frame, text="Refresh Students", command=self.refresh_all_students, style='Accent.TButton').pack(side=tk.LEFT)

    def refresh_all_students(self):
        """Refreshes the data in the 'All Students' treeview."""
        self.all_students_tree.delete(*self.all_students_tree.get_children())
        try:
            if not conn or not cursor:
                self.set_status("Error: No database connection to refresh students.")
                return
            cursor.execute("SELECT id, name, reg_no, contact_no, email, city, department, discipline FROM Students WHERE status=1 ORDER BY name")
            rows = cursor.fetchall()
            for row in rows:
                self.all_students_tree.insert("", tk.END, values=tuple(row.values()))
            self.set_status(f"Loaded {len(rows)} active students.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading students: {err}")
            self.set_status(f"Error: Could not load students - {err}")
        except tk.TclError: pass # Window closed

    def build_dues_tab(self):
        """Builds the UI for the 'Students with Dues' tab."""
        main_frame = ttk.Frame(self.dues_tab)
        main_frame.pack(fill=tk.BOTH, expand=True)
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0,5))

        y_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        x_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        
        cols = ("ID", "Name", "Reg No", "Total Fee", "Paid Fee", "Dues", "Dues Status")
        self.dues_tree = ttk.Treeview(tree_frame, columns=cols, show='headings',
                                    yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.dues_tree.pack(fill=tk.BOTH, expand=True)
        
        y_scroll.config(command=self.dues_tree.yview)
        x_scroll.config(command=self.dues_tree.xview)

        for col in cols:
            self.dues_tree.heading(col, text=col)
            self.dues_tree.column(col, anchor=tk.W if col == "Name" else tk.CENTER, width=120, minwidth=80)

        self.setup_treeview_context_menu(self.dues_tree)
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Button(btn_frame, text="Refresh Dues", command=self.refresh_dues, style='Accent.TButton').pack(side=tk.LEFT)

    def refresh_dues(self):
        """Refreshes data in the 'Students with Dues' treeview."""
        self.dues_tree.delete(*self.dues_tree.get_children())
        try:
            if not conn or not cursor:
                self.set_status("Error: No database connection to refresh dues.")
                return
            query = """
            SELECT s.id, s.name, s.reg_no, fr.total_fee, fr.paid_fee,
                   fr.remaining_fee AS dues,
                   CASE WHEN fr.remaining_fee > 0 THEN 'Pending' ELSE 'Cleared' END AS dues_status
            FROM Students s
            JOIN FeeRecord fr ON s.id = fr.student_id
            WHERE s.status=1
            ORDER BY dues DESC, s.name
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                self.dues_tree.insert("", tk.END, values=(
                    row['id'], row['name'], row['reg_no'],
                    f"{row['total_fee']:.2f}", f"{row['paid_fee']:.2f}",
                    f"{row['dues']:.2f}", row['dues_status']
                ))
            self.set_status(f"Loaded {len(rows)} student fee records.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading dues: {err}")
            self.set_status(f"Error: Could not load fee dues - {err}")
        except tk.TclError: pass

    def build_clearance_tab(self):
        """Builds the UI for the 'Clearance Status' tab."""
        main_frame = ttk.Frame(self.clearance_tab)
        main_frame.pack(fill=tk.BOTH, expand=True)
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0,5))

        y_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        x_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)

        cols = ("Student Name", "Department", "Status", "Remarks", "Clearance Date", "Cleared By")
        self.clearance_tree = ttk.Treeview(tree_frame, columns=cols, show='headings',
                                         yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.clearance_tree.pack(fill=tk.BOTH, expand=True)

        y_scroll.config(command=self.clearance_tree.yview)
        x_scroll.config(command=self.clearance_tree.xview)

        for col in cols:
            self.clearance_tree.heading(col, text=col)
            self.clearance_tree.column(col, anchor=tk.W if col in ["Student Name", "Remarks"] else tk.CENTER, width=150, minwidth=100)

        self.setup_treeview_context_menu(self.clearance_tree)
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Button(btn_frame, text="Refresh Clearance", command=self.refresh_clearance, style='Accent.TButton').pack(side=tk.LEFT)

    def refresh_clearance(self):
        """Refreshes data in the 'Clearance Status' treeview."""
        self.clearance_tree.delete(*self.clearance_tree.get_children())
        try:
            if not conn or not cursor:
                self.set_status("Error: No database connection to refresh clearance.")
                return
            query = """
            SELECT s.name, d.dept_name,
              CASE WHEN cr.status=1 THEN 'Cleared' ELSE 'Pending' END AS clearance_status,
              cr.remarks, cr.clearance_date, cr.cleared_by
            FROM ClearanceRecords cr
            JOIN Students s ON cr.student_id = s.id
            JOIN Departments d ON cr.dept_id = d.id
            WHERE s.status=1
            ORDER BY s.name, d.dept_name
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                clearance_date_str = row['clearance_date'].strftime("%Y-%m-%d") if row['clearance_date'] else "N/A"
                self.clearance_tree.insert("", tk.END, values=(
                    row['name'], row['dept_name'], row['clearance_status'],
                    row['remarks'], clearance_date_str, row['cleared_by']
                ))
            self.set_status(f"Loaded {len(rows)} clearance records.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading clearance records: {err}")
            self.set_status(f"Error: Could not load clearance records - {err}")
        except tk.TclError: pass

    def build_add_student_tab(self):
        """Builds the UI for the 'Add Student' tab."""
        main_frame = ttk.Frame(self.add_student_tab)
        main_frame.pack(fill=tk.BOTH, expand=True)

        form_frame = ttk.Frame(main_frame, padding=10)
        form_frame.pack(anchor=tk.N, pady=10)

        labels = ["Name*", "Reg No*", "Contact No", "Email", "City", "Department", "Discipline", "Initial Total Fee*"]
        self.add_entries = {}

        for i, label_text in enumerate(labels):
            lbl = ttk.Label(form_frame, text=label_text + ":")
            lbl.grid(row=i, column=0, sticky=tk.W, pady=5, padx=5)
            ent = ttk.Entry(form_frame, width=40)
            ent.grid(row=i, column=1, pady=5, padx=5, sticky=tk.EW)
            self.add_entries[label_text] = ent
            if label_text == "Name*": ent.focus()

        # Input Validations
        self.add_entries["Contact No"].config(validate="key", validatecommand=(self.register(self.validate_digit_input), '%P'))
        self.add_entries["Email"].bind('<FocusOut>', lambda e, entry=self.add_entries["Email"]: self.validate_email_format(entry, self.add_student_status))
        self.add_entries["Initial Total Fee*"].config(validate="key", validatecommand=(self.register(self.validate_decimal_input), '%P'))

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0), anchor=tk.N, padx=10)
        ttk.Button(btn_frame, text="Add Student", command=self.insert_student, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear Form", command=self.clear_add_student_form).pack(side=tk.LEFT)

        self.add_student_status = ttk.Label(main_frame, text="", foreground="blue")
        self.add_student_status.pack(pady=10, anchor=tk.N)

    def clear_add_student_form(self):
        """Clears all entry fields in the 'Add Student' form."""
        for ent in self.add_entries.values():
            ent.delete(0, tk.END)
        self.add_entries["Name*"].focus()
        self.add_student_status.config(text="Form cleared.", foreground="blue")

    def insert_student(self):
        """Inserts a new student and their initial fee record into the database."""
        vals = {label.replace("*",""): ent.get().strip() for label, ent in self.add_entries.items()}

        if not vals["Name"] or not vals["Reg No"] or not vals["Initial Total Fee"]:
            self.add_student_status.config(text="Name, Reg No, and Initial Total Fee are required!", foreground="red")
            return
        try:
            initial_total_fee = float(vals["Initial Total Fee"])
            if initial_total_fee < 0:
                self.add_student_status.config(text="Initial Total Fee cannot be negative.", foreground="red"); return
        except ValueError:
            self.add_student_status.config(text="Initial Total Fee must be a valid number.", foreground="red"); return
        if vals["Email"] and not re.match(r"[^@]+@[^@]+\.[^@]+", vals["Email"]):
            self.add_student_status.config(text="Invalid email format.", foreground="red"); return

        try:
            if not conn or not cursor: self.add_student_status.config(text="DB connection error.", foreground="red"); return
            cursor.execute("""
                INSERT INTO Students (name, reg_no, contact_no, email, city, department, discipline, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
            """, (vals["Name"], vals["Reg No"], vals["Contact No"] or None, vals["Email"] or None,
                  vals["City"] or None, vals["Department"] or None, vals["Discipline"] or None))
            student_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO FeeRecord (student_id, total_fee, paid_fee, last_payment_date)
                VALUES (%s, %s, 0, NULL)
            """, (student_id, initial_total_fee))
            conn.commit()
            self.add_student_status.config(text=f"Student '{vals['Name']}' added (ID: {student_id}).", foreground="green")
            self.clear_add_student_form()
            self.refresh_all_data()
        except mysql.connector.Error as err:
            conn.rollback()
            if err.errno == 1062: # Duplicate entry for UNIQUE key (e.g., reg_no)
                self.add_student_status.config(text="Error: Reg No already exists.", foreground="red")
            else:
                self.add_student_status.config(text=f"DB Error: {err}", foreground="red")
                messagebox.showerror("Database Error", f"Error adding student: {err}")

    # --- UPDATE FEE PAYMENT TAB (CRITICAL FOR USER'S ISSUE) ---
    def build_update_fee_tab(self):
        """Builds the UI for the 'Update Fee Payment' tab."""
        main_frame = ttk.Frame(self.update_fee_tab)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Student Search Section
        search_student_frame = ttk.LabelFrame(main_frame, text="Search Student", padding=10)
        search_student_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(search_student_frame, text="Student Reg No*:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.fee_reg_no_entry = ttk.Entry(search_student_frame, width=30)
        self.fee_reg_no_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.fee_reg_no_entry.bind('<Return>', lambda event: self.search_student_for_fee())
        ttk.Button(search_student_frame, text="Search", command=self.search_student_for_fee, style='Accent.TButton').grid(row=0, column=2, padx=10, pady=5)
        search_student_frame.grid_columnconfigure(1, weight=1)


        # Student Information Display Section
        self.student_info_display_frame = ttk.LabelFrame(main_frame, text="Student Information", padding=10)
        self.student_info_display_frame.pack(fill=tk.X, padx=10, pady=(0,10))
        self.student_info_labels_map = {
            "Name": ttk.Label(self.student_info_display_frame, text="Name: N/A"),
            "Department": ttk.Label(self.student_info_display_frame, text="Department: N/A"),
            "Total Fee": ttk.Label(self.student_info_display_frame, text="Total Fee: N/A"),
            "Paid Fee": ttk.Label(self.student_info_display_frame, text="Paid Fee: N/A"),
            "Remaining Fee": ttk.Label(self.student_info_display_frame, text="Remaining Fee: N/A")
        }
        for i, label_widget in enumerate(self.student_info_labels_map.values()):
            label_widget.grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)

        # Payment Details Form Section
        payment_details_frame = ttk.LabelFrame(main_frame, text="Payment Details", padding=10)
        payment_details_frame.pack(fill=tk.X, padx=10, pady=(0,10))

        entry_width = 35
        ttk.Label(payment_details_frame, text="Payment Amount*:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.fee_payment_amount_entry = ttk.Entry(payment_details_frame, width=entry_width, validate="key", validatecommand=(self.register(self.validate_decimal_input), '%P'))
        self.fee_payment_amount_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)

        ttk.Label(payment_details_frame, text="Payment Method*:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.payment_method_cb = ttk.Combobox(payment_details_frame, state="readonly", width=entry_width-3) # slightly less width for combobox arrow
        self.payment_method_cb.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        # self.load_payment_methods_for_combobox() # Called in refresh_all_data

        ttk.Label(payment_details_frame, text="Transaction Ref/Receipt No*:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.transaction_ref_entry = ttk.Entry(payment_details_frame, width=entry_width)
        self.transaction_ref_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)

        ttk.Label(payment_details_frame, text="Verified By*:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.verified_by_entry = ttk.Entry(payment_details_frame, width=entry_width)
        self.verified_by_entry.insert(0, "System Admin") # Default value
        self.verified_by_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(payment_details_frame, text="Remarks:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.payment_remarks_entry = ttk.Entry(payment_details_frame, width=entry_width)
        self.payment_remarks_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.EW)
        
        payment_details_frame.grid_columnconfigure(1, weight=1)


        # Action Buttons
        btn_frame = ttk.Frame(main_frame, padding=(0,10,0,0))
        btn_frame.pack(fill=tk.X, padx=10)
        ttk.Button(btn_frame, text="Record Payment", command=self.update_fee_payment, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear Payment Form", command=self.clear_fee_form).pack(side=tk.LEFT) # More specific name

        self.fee_status_label = ttk.Label(main_frame, text="", foreground="blue")
        self.fee_status_label.pack(pady=10, padx=10, fill=tk.X)


    def load_payment_methods_for_combobox(self):
        """Loads active payment methods from the database into the combobox."""
        try:
            if not conn or not cursor:
                self.payment_method_cb['values'] = ["DB Error"]
                if self.payment_method_cb['values']: self.payment_method_cb.current(0)
                return

            cursor.execute("SELECT id, method_name FROM PaymentMethods WHERE is_active = 1 ORDER BY method_name")
            methods = cursor.fetchall()
            
            self.payment_methods_map.clear() # Clear previous map
            method_names = []
            if methods:
                for m in methods:
                    self.payment_methods_map[m['method_name']] = m['id']
                    method_names.append(m['method_name'])
            
            if not method_names:
                 method_names = ["No methods available"]

            self.payment_method_cb['values'] = method_names
            if method_names and method_names[0] not in ["No methods available", "DB Error"]:
                self.payment_method_cb.current(0)
            elif method_names : # If only "No methods available" or "DB Error"
                 self.payment_method_cb.current(0)

        except mysql.connector.Error as err:
            messagebox.showerror("DB Error", f"Failed to load payment methods: {err}")
            self.payment_method_cb['values'] = ["DB Error"]
            if self.payment_method_cb['values']: self.payment_method_cb.current(0)
        except tk.TclError: pass # Combobox might not exist if tab isn't fully built/visible

    def search_student_for_fee(self):
        """Searches for a student by registration number and displays their fee info."""
        reg_no = self.fee_reg_no_entry.get().strip()
        if not reg_no:
            self.fee_status_label.config(text="Please enter a registration number to search.", foreground="red")
            return

        try:
            if not conn or not cursor: self.fee_status_label.config(text="DB connection error.", foreground="red"); return
            cursor.execute("""
                SELECT s.id, s.name, s.department, fr.total_fee, fr.paid_fee, fr.remaining_fee
                FROM Students s
                JOIN FeeRecord fr ON s.id = fr.student_id
                WHERE s.reg_no = %s AND s.status = 1
            """, (reg_no,))
            student = cursor.fetchone()

            if not student:
                self.fee_status_label.config(text="Student not found or is inactive.", foreground="red")
                self.clear_student_info_display()
                self.current_fee_student_id = None
                return

            self.current_fee_student_id = student['id']
            self.current_student_total_fee = float(student['total_fee'])
            self.current_student_paid_fee = float(student['paid_fee'])
            remaining_fee = float(student['remaining_fee'])

            self.student_info_labels_map["Name"].config(text=f"Name: {student['name']}")
            self.student_info_labels_map["Department"].config(text=f"Department: {student['department'] or 'N/A'}")
            self.student_info_labels_map["Total Fee"].config(text=f"Total Fee: {self.current_student_total_fee:.2f}")
            self.student_info_labels_map["Paid Fee"].config(text=f"Paid Fee: {self.current_student_paid_fee:.2f}")
            self.student_info_labels_map["Remaining Fee"].config(text=f"Remaining Fee: {remaining_fee:.2f}")
            self.fee_status_label.config(text="Student found. Enter payment details.", foreground="green")
            self.fee_payment_amount_entry.focus()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error searching student: {err}")
            self.fee_status_label.config(text=f"Error searching student: {err}", foreground="red")
            self.clear_student_info_display()
            self.current_fee_student_id = None
            
    def clear_student_info_display(self):
        """Clears the displayed student information labels."""
        for label in self.student_info_labels_map.values():
            base_text = label.cget("text").split(":")[0] # Get "Name", "Department" etc.
            label.config(text=f"{base_text}: N/A")
        self.current_fee_student_id = None
        self.current_student_total_fee = 0.0
        self.current_student_paid_fee = 0.0


    def clear_fee_form(self):
        """Clears all fields in the fee payment form and student info display."""
        self.fee_reg_no_entry.delete(0, tk.END)
        self.fee_payment_amount_entry.delete(0, tk.END)
        if self.payment_method_cb.cget('values') and \
           self.payment_method_cb.cget('values')[0] not in ["DB Error", "No methods available"]:
             self.payment_method_cb.current(0)
        else:
            self.payment_method_cb.set('') # Clear selection if only error/no methods
            
        self.transaction_ref_entry.delete(0, tk.END)
        self.verified_by_entry.delete(0, tk.END)
        self.verified_by_entry.insert(0, "System Admin") # Reset default
        self.payment_remarks_entry.delete(0, tk.END)

        self.clear_student_info_display() # Also clears current_fee_student_id
        self.fee_reg_no_entry.focus()
        self.fee_status_label.config(text="Fee payment form cleared.", foreground="blue")

    def update_fee_payment(self):
        """Processes the fee payment by calling the MakePayment stored procedure."""
        if self.current_fee_student_id is None:
            self.fee_status_label.config(text="Please search for and select a student first.", foreground="red"); return

        payment_amount_str = self.fee_payment_amount_entry.get().strip()
        selected_method_name = self.payment_method_cb.get()
        transaction_ref = self.transaction_ref_entry.get().strip()
        verified_by = self.verified_by_entry.get().strip()
        remarks = self.payment_remarks_entry.get().strip()

        # --- Input Validations ---
        if not payment_amount_str:
            self.fee_status_label.config(text="Payment amount is required.", foreground="red"); return
        try:
            amount = float(payment_amount_str)
            if amount <= 0:
                self.fee_status_label.config(text="Payment amount must be > 0.", foreground="red"); return
        except ValueError:
            self.fee_status_label.config(text="Invalid payment amount format.", foreground="red"); return
        
        if not selected_method_name or selected_method_name in ["DB Error", "No methods available"]:
            self.fee_status_label.config(text="Please select a valid payment method.", foreground="red"); return
        
        payment_method_id = self.payment_methods_map.get(selected_method_name)
        if payment_method_id is None: # Should not happen if combobox and map are correct
             self.fee_status_label.config(text="Internal Error: Payment method ID not found.", foreground="red"); return

        if not transaction_ref:
            self.fee_status_label.config(text="Transaction Reference/Receipt No is required.", foreground="red"); return
        if not verified_by:
            self.fee_status_label.config(text="Verified By is required.", foreground="red"); return

        # --- Overpayment Check (Optional but good practice) ---
        remaining_fee = self.current_student_total_fee - self.current_student_paid_fee
        if amount > remaining_fee and remaining_fee > 0: # Allow payment if remaining is 0 or negative (overpaid)
            if not messagebox.askyesno("Overpayment Warning",
                                     f"Payment (${amount:.2f}) exceeds remaining dues (${remaining_fee:.2f}).\n"
                                     f"This will result in an overpayment of (${amount - remaining_fee:.2f}).\n\n"
                                     "Proceed with this payment?", icon='warning'):
                self.fee_status_label.config(text="Overpayment cancelled by user.", foreground="blue"); return
        elif remaining_fee <= 0 and self.current_student_total_fee > 0 and amount > 0: # Already fully paid or overpaid
             self.fee_status_label.config(text="Account is already fully paid or overpaid. No further payment needed for dues.", foreground="orange")
             if not messagebox.askyesno("Payment Confirmation",
                                     f"The account shows no pending dues (Remaining: ${remaining_fee:.2f}).\n"
                                     "Do you still want to record this additional payment?", icon='info'):
                self.fee_status_label.config(text="Additional payment cancelled.", foreground="blue"); return


        # --- Call Stored Procedure ---
        try:
            if not conn or not cursor: self.fee_status_label.config(text="DB connection error.", foreground="red"); return
            
            args = (
                self.current_fee_student_id, # p_student_id INT
                payment_method_id,           # p_payment_method_id INT
                transaction_ref,             # p_transaction_reference VARCHAR(100)
                amount,                      # p_amount DECIMAL(10,2)
                verified_by,                 # p_verified_by VARCHAR(100)
                remarks if remarks else None # p_remarks TEXT
            )
            
            # Debug print (Optional: remove for production)
            print(f"Calling MakePayment with args: {args}")

            cursor.callproc('MakePayment', args)
            conn.commit() 

            self.fee_status_label.config(text=f"Payment of ${amount:.2f} for student ID {self.current_fee_student_id} recorded successfully!", foreground="green")
            
            paid_student_reg_no_on_fee_tab = self.fee_reg_no_entry.get().strip()
            current_student_id_for_payment = self.current_fee_student_id # Capture before it's potentially changed by search_student_for_fee

            # Refresh student's fee info on the current "Update Fee Payment" tab
            self.search_student_for_fee() 

            # --- NEW: Auto-clear Finance department if fee is fully paid ---
            finance_dept_id = None
            if hasattr(self, 'departments_map') and self.departments_map:
                for dept_name, dept_id_val in self.departments_map.items():
                    if dept_name.lower() == "finance": 
                        finance_dept_id = dept_id_val
                        break
            
            if finance_dept_id is not None and current_student_id_for_payment is not None:
                try:
                    cursor.execute("SELECT remaining_fee FROM FeeRecord WHERE student_id = %s", (current_student_id_for_payment,))
                    fee_row = cursor.fetchone()
                    
                    if fee_row and float(fee_row['remaining_fee']) <= 0:
                        auto_cleared_by = self.verified_by_entry.get().strip() if self.verified_by_entry.get().strip() else "System Auto-Clear"
                        auto_remarks = "Fee automatically cleared upon full payment."
                        
                        cursor.execute("SELECT id, status FROM ClearanceRecords WHERE student_id = %s AND dept_id = %s",
                                       (current_student_id_for_payment, finance_dept_id))
                        existing_clearance = cursor.fetchone()
                        
                        if existing_clearance:
                            if existing_clearance['status'] != 1: 
                                cursor.execute("""
                                    UPDATE ClearanceRecords 
                                    SET status=1, cleared_by=%s, clearance_date=%s, remarks=%s
                                    WHERE id=%s
                                """, (auto_cleared_by, date.today(), auto_remarks, existing_clearance['id']))
                                conn.commit() 
                                print(f"Finance department clearance automatically UPDATED for student ID: {current_student_id_for_payment}")
                            else:
                                print(f"Finance department already marked cleared for student ID: {current_student_id_for_payment}")
                        else:
                            cursor.execute("""
                                INSERT INTO ClearanceRecords (student_id, dept_id, cleared_by, status, remarks, clearance_date) 
                                VALUES (%s, %s, %s, 1, %s, %s)
                            """, (current_student_id_for_payment, finance_dept_id, auto_cleared_by, auto_remarks, date.today()))
                            conn.commit() 
                            print(f"Finance department clearance automatically INSERTED for student ID: {current_student_id_for_payment}")
                except mysql.connector.Error as db_err:
                    print(f"DB Error during auto-clearance of Finance dept: {db_err}")
                except Exception as e_auto_clear:
                    print(f"Python Error during auto-clearance of Finance dept: {e_auto_clear}")
            # --- END OF NEW Auto-clear Finance department ---

            # Refresh the "Students with Dues" tab
            self.refresh_dues()
            
            # Refresh the main "Clearance Status" tab treeview (this will pick up the auto-finance clearance)
            self.refresh_clearance()

            # If the student whose fee was just updated is also the one whose reg_no is currently
            # in the entry field of the "Mark Clearance" tab, refresh that tab's student info.
            if hasattr(self, 'clear_reg_no_entry') and \
               self.clear_reg_no_entry.get().strip() == paid_student_reg_no_on_fee_tab:
                print(f"Refreshing Mark Clearance tab for student Reg No: {paid_student_reg_no_on_fee_tab}") # Debug
                self.search_student_for_clearance() # Re-trigger search on Mark Clearance tab

            # Clear only payment-specific fields for the next potential payment
            self.fee_payment_amount_entry.delete(0, tk.END)
            self.payment_remarks_entry.delete(0, tk.END)
            self.fee_payment_amount_entry.focus()

        except mysql.connector.Error as err:
            conn.rollback() # Rollback on any DB error during the procedure call or commit
            if "Student does not exist" in str(err):
                 self.fee_status_label.config(text="Error: The selected student ID does not exist in the database.", foreground="red")
            else:
                 self.fee_status_label.config(text=f"Database Error: {err}", foreground="red")
            messagebox.showerror("Database Error", f"Error recording payment: {err}")
            print(f"DB Error during payment: {err}") # For console debugging
        except Exception as e: # Catch other potential Python errors
            conn.rollback()
            self.fee_status_label.config(text=f"Application Error: {e}", foreground="red")
            messagebox.showerror("Application Error", f"An unexpected error occurred: {e}")
            print(f"App Error during payment: {e}") # For console debugging

    def build_mark_clearance_tab(self):
        """Builds the UI for the 'Mark Clearance' tab."""
        main_frame = ttk.Frame(self.mark_clearance_tab)
        main_frame.pack(fill=tk.BOTH, expand=True)

        search_clearance_frame = ttk.LabelFrame(main_frame, text="Search Student", padding=10)
        search_clearance_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(search_clearance_frame, text="Student Reg No*:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.clear_reg_no_entry = ttk.Entry(search_clearance_frame, width=30)
        self.clear_reg_no_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.clear_reg_no_entry.bind('<Return>', lambda event: self.search_student_for_clearance())
        ttk.Button(search_clearance_frame, text="Search", command=self.search_student_for_clearance, style='Accent.TButton').grid(row=0, column=2, padx=10, pady=5)
        search_clearance_frame.grid_columnconfigure(1, weight=1)

        self.clearance_student_info_frame = ttk.LabelFrame(main_frame, text="Student Information", padding=10)
        self.clearance_student_info_frame.pack(fill=tk.X, padx=10, pady=(0,10))
        self.clearance_student_labels_map = {
            "Name": ttk.Label(self.clearance_student_info_frame, text="Name: N/A"),
            "Student Dept": ttk.Label(self.clearance_student_info_frame, text="Student Dept: N/A"),
            "Fee Status": ttk.Label(self.clearance_student_info_frame, text="Fee Status: N/A")
        }
        for i, label_widget in enumerate(self.clearance_student_labels_map.values()):
            label_widget.grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)

        clearance_details_frame = ttk.LabelFrame(main_frame, text="Clearance Details", padding=10)
        clearance_details_frame.pack(fill=tk.X, padx=10, pady=(0,10))
        entry_width = 35
        ttk.Label(clearance_details_frame, text="Department to Clear*:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.clear_dept_cb = ttk.Combobox(clearance_details_frame, state="readonly", width=entry_width-3)
        self.clear_dept_cb.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)

        ttk.Label(clearance_details_frame, text="Cleared By*:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.clear_cleared_by_entry = ttk.Entry(clearance_details_frame, width=entry_width)
        self.clear_cleared_by_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)

        ttk.Label(clearance_details_frame, text="Status*:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.clear_status_var = tk.IntVar(value=1) 
        status_radio_frame = ttk.Frame(clearance_details_frame)
        status_radio_frame.grid(row=2, column=1, sticky=tk.W, pady=2, padx=5)
        ttk.Radiobutton(status_radio_frame, text="Cleared", variable=self.clear_status_var, value=1).pack(side=tk.LEFT, padx=(0,10))
        ttk.Radiobutton(status_radio_frame, text="Not Cleared", variable=self.clear_status_var, value=0).pack(side=tk.LEFT)
        
        ttk.Label(clearance_details_frame, text="Remarks:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.clear_remarks_entry = ttk.Entry(clearance_details_frame, width=entry_width)
        self.clear_remarks_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)
        clearance_details_frame.grid_columnconfigure(1, weight=1)

        btn_frame = ttk.Frame(main_frame, padding=(0,10,0,0))
        btn_frame.pack(fill=tk.X, padx=10)
        ttk.Button(btn_frame, text="Update Clearance", command=self.mark_clearance, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear Clearance Form", command=self.clear_clearance_form).pack(side=tk.LEFT)

        self.clearance_status_label = ttk.Label(main_frame, text="", foreground="blue")
        self.clearance_status_label.pack(pady=10, padx=10, fill=tk.X)
        # self.load_departments_for_combobox() # Called in refresh_all_data


    def load_departments_for_combobox(self):
        """Loads active departments from the database into the combobox."""
        try:
            if not conn or not cursor:
                self.clear_dept_cb['values'] = ["DB Error"]
                if self.clear_dept_cb['values']: self.clear_dept_cb.current(0)
                return

            cursor.execute("SELECT id, dept_name FROM Departments ORDER BY dept_name")
            departments = cursor.fetchall()
            
            self.departments_map.clear()
            dept_names = []
            if departments:
                for dept in departments:
                    self.departments_map[dept['dept_name']] = dept['id']
                    dept_names.append(dept['dept_name'])
            
            if not dept_names:
                 dept_names = ["No depts available"]

            self.clear_dept_cb['values'] = dept_names
            if dept_names and dept_names[0] not in ["No depts available", "DB Error"]:
                self.clear_dept_cb.current(0)
            elif dept_names:
                 self.clear_dept_cb.current(0)

        except mysql.connector.Error as err:
            messagebox.showerror("DB Error", f"Error loading departments: {err}")
            self.clear_dept_cb['values'] = ["DB Error"]
            if self.clear_dept_cb['values']: self.clear_dept_cb.current(0)
        except tk.TclError: pass

    def search_student_for_clearance(self):
        """Searches for a student and displays their info for clearance marking."""
        reg_no = self.clear_reg_no_entry.get().strip() # Use the entry from this tab
        if not reg_no:
            self.clearance_status_label.config(text="Please enter a registration number.", foreground="red"); return

        try:
            if not conn or not cursor: self.clearance_status_label.config(text="DB connection error.", foreground="red"); return
            cursor.execute("""
                SELECT s.id, s.name, s.department, fr.remaining_fee
                FROM Students s
                LEFT JOIN FeeRecord fr ON s.id = fr.student_id
                WHERE s.reg_no = %s AND s.status = 1
            """, (reg_no,))
            student = cursor.fetchone()

            if not student:
                self.clearance_status_label.config(text="Student not found or is inactive.", foreground="red")
                self.clear_clearance_student_info_display(); self.current_clearance_student_id = None; return

            self.current_clearance_student_id = student['id'] # Store the ID of student active on this tab
            self.clearance_student_labels_map["Name"].config(text=f"Name: {student['name']}")
            self.clearance_student_labels_map["Student Dept"].config(text=f"Student Dept: {student['department'] or 'N/A'}")
            fee_status_text = "No Fee Record"
            if student['remaining_fee'] is not None:
                fee_status_text = "Cleared" if float(student['remaining_fee']) <= 0 else f"Dues: {float(student['remaining_fee']):.2f}"
            self.clearance_student_labels_map["Fee Status"].config(text=f"Fee Status: {fee_status_text}")
            self.clearance_status_label.config(text="Student found. Select department and clearance details.", foreground="green")
            self.clear_dept_cb.focus()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error searching student: {err}")
            self.clearance_status_label.config(text=f"Error searching student: {err}", foreground="red")
            self.clear_clearance_student_info_display(); self.current_clearance_student_id = None

    def clear_clearance_student_info_display(self):
        """Clears student info on the clearance tab."""
        for label in self.clearance_student_labels_map.values():
            base_text = label.cget("text").split(":")[0]
            label.config(text=f"{base_text}: N/A")
        # Do not clear self.current_clearance_student_id here,
        # it should only be cleared when the form itself is cleared or a new search fails.

    def clear_clearance_form(self):
        """Clears the mark clearance form."""
        self.clear_reg_no_entry.delete(0, tk.END)
        self.clear_cleared_by_entry.delete(0, tk.END)
        self.clear_remarks_entry.delete(0, tk.END)
        self.clear_status_var.set(1)
        if self.clear_dept_cb.cget('values') and \
           self.clear_dept_cb.cget('values')[0] not in ["No depts available", "DB Error"]:
            self.clear_dept_cb.current(0)
        else:
            self.clear_dept_cb.set('')
        
        # Clear displayed student info and the stored ID for this tab
        for label in self.clearance_student_labels_map.values():
            base_text = label.cget("text").split(":")[0]
            label.config(text=f"{base_text}: N/A")
        self.current_clearance_student_id = None

        self.clear_reg_no_entry.focus()
        self.clearance_status_label.config(text="Clearance form cleared.", foreground="blue")

    def mark_clearance(self):
        """Marks or updates a student's clearance status for a department."""
        if self.current_clearance_student_id is None:
            self.clearance_status_label.config(text="Please search for a student first.", foreground="red"); return

        selected_dept_name = self.clear_dept_cb.get()
        cleared_by = self.clear_cleared_by_entry.get().strip()
        status_val = self.clear_status_var.get()
        remarks = self.clear_remarks_entry.get().strip()
        clearance_date_val = date.today()

        if not selected_dept_name or selected_dept_name in ["No depts available", "DB Error"]:
            self.clearance_status_label.config(text="Please select a department.", foreground="red"); return
        dept_id = self.departments_map.get(selected_dept_name)
        if dept_id is None:
            self.clearance_status_label.config(text="Internal Error: Department ID not found.", foreground="red"); return
        if not cleared_by:
            self.clearance_status_label.config(text="Cleared By field is required.", foreground="red"); return

        try:
            if not conn or not cursor: self.clearance_status_label.config(text="DB connection error.", foreground="red"); return
            cursor.execute("SELECT id FROM ClearanceRecords WHERE student_id = %s AND dept_id = %s",
                           (self.current_clearance_student_id, dept_id))
            existing_record = cursor.fetchone()
            action_text = ""
            if existing_record:
                cursor.execute("""
                    UPDATE ClearanceRecords SET cleared_by = %s, status = %s, remarks = %s, clearance_date = %s
                    WHERE id = %s
                """, (cleared_by, status_val, remarks or None, clearance_date_val, existing_record['id']))
                action_text = "updated"
            else:
                cursor.execute("""
                    INSERT INTO ClearanceRecords (student_id, dept_id, cleared_by, status, remarks, clearance_date)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (self.current_clearance_student_id, dept_id, cleared_by, status_val, remarks or None, clearance_date_val))
                action_text = "recorded"
            conn.commit()
            self.clearance_status_label.config(text=f"Clearance for {selected_dept_name} {action_text}.", foreground="green")
            self.refresh_clearance() # Refresh the main clearance status treeview
            
            # After successfully marking clearance, re-fetch student info for this tab to reflect any changes
            # (though this specific action doesn't change fee status, it's good practice for consistency if it did)
            self.search_student_for_clearance()


        except mysql.connector.Error as err:
            conn.rollback()
            self.clearance_status_label.config(text=f"DB Error: {err}", foreground="red")
            messagebox.showerror("Database Error", f"Error marking clearance: {err}")

    def build_search_tab(self):
        """Builds the UI for the 'Search Student' tab."""
        main_frame = ttk.Frame(self.search_tab)
        main_frame.pack(fill=tk.BOTH, expand=True)

        search_controls_frame = ttk.LabelFrame(main_frame, text="Search Criteria", padding=10)
        search_controls_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(search_controls_frame, text="Search by:").grid(row=0, column=0, sticky=tk.W, padx=(0,5), pady=5)
        self.search_type_cb = ttk.Combobox(search_controls_frame,
                                      values=["Name", "Reg No", "Department", "Discipline", "City"],
                                      state="readonly", width=15)
        self.search_type_cb.current(0)
        self.search_type_cb.grid(row=0, column=1, padx=5, pady=5)

        self.search_term_entry = ttk.Entry(search_controls_frame, width=40)
        self.search_term_entry.grid(row=0, column=2, padx=5, pady=5, sticky=tk.EW)
        search_controls_frame.grid_columnconfigure(2, weight=1)
        self.search_term_entry.bind('<Return>', lambda event: self.perform_search())
        ttk.Button(search_controls_frame, text="Search", command=self.perform_search, style='Accent.TButton').grid(row=0, column=3, padx=(10,0), pady=5)

        results_tree_frame = ttk.Frame(main_frame)
        results_tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))
        y_scroll = ttk.Scrollbar(results_tree_frame, orient=tk.VERTICAL)
        x_scroll = ttk.Scrollbar(results_tree_frame, orient=tk.HORIZONTAL)
        cols = ("ID", "Name", "Reg No", "Contact No", "Email", "City", "Department", "Discipline")
        self.search_results_tree = ttk.Treeview(results_tree_frame, columns=cols, show='headings',
                                      yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.search_results_tree.pack(fill=tk.BOTH, expand=True)
        y_scroll.config(command=self.search_results_tree.yview)
        x_scroll.config(command=self.search_results_tree.xview)
        for col in cols:
            self.search_results_tree.heading(col, text=col)
            self.search_results_tree.column(col, anchor=tk.W if col == "Name" else tk.CENTER, width=120, minwidth=80)
        self.setup_treeview_context_menu(self.search_results_tree)

        self.search_status_label = ttk.Label(main_frame, text="Enter search criteria and click Search.", foreground="blue")
        self.search_status_label.pack(pady=(5,0), padx=10, fill=tk.X)

    def perform_search(self):
        """Performs a student search based on selected criteria and term."""
        search_by_field = self.search_type_cb.get()
        search_term = self.search_term_entry.get().strip()
        if not search_term:
            self.search_status_label.config(text="Please enter a search term.", foreground="red"); return

        self.search_results_tree.delete(*self.search_results_tree.get_children())
        column_map = {"Name": "name", "Reg No": "reg_no", "Department": "department", "Discipline": "discipline", "City": "city"}
        db_column = column_map.get(search_by_field)
        if not db_column:
            self.search_status_label.config(text="Invalid search type.", foreground="red"); return

        try:
            if not conn or not cursor: self.search_status_label.config(text="DB connection error.", foreground="red"); return
            query = f"SELECT id, name, reg_no, contact_no, email, city, department, discipline FROM Students WHERE {db_column} LIKE %s AND status=1 ORDER BY {db_column}, name"
            like_term = f"%{search_term}%"
            cursor.execute(query, (like_term,))
            rows = cursor.fetchall()
            if not rows:
                self.search_status_label.config(text="No matching students found.", foreground="orange"); return
            for row in rows:
                self.search_results_tree.insert("", tk.END, values=tuple(row.values()))
            self.search_status_label.config(text=f"Found {len(rows)} matching student(s).", foreground="green")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error searching students: {err}")
            self.search_status_label.config(text=f"Error during search: {err}", foreground="red")
        except tk.TclError: pass

    # --- Input Validation Helper Methods ---
    def validate_digit_input(self, P):
        """Validates that the input P contains only digits or is empty."""
        if P == "" or P.isdigit():
            return True
        self.bell() # Audible feedback for invalid input
        return False

    def validate_decimal_input(self, P):
        """Validates that the input P is a valid decimal number or is empty."""
        if P == "": return True
        try:
            float(P)
            return True
        except ValueError:
            self.bell()
            return False
            
    def validate_email_format(self, entry_widget, status_label_widget):
        """Validates email format on FocusOut event."""
        email = entry_widget.get()
        if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            status_label_widget.config(text="Invalid email format.", foreground="red")
            # entry_widget.focus() # Optionally refocus, can be annoying
        else:
            status_label_widget.config(text="")


    # --- Treeview Context Menu ---
    def setup_treeview_context_menu(self, treeview):
        """Sets up a right-click context menu for copying treeview rows."""
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Copy Selected Row", command=lambda tv=treeview: self.copy_treeview_item(tv))

        def show_menu(event):
            item = treeview.identify_row(event.y)
            if item:
                treeview.selection_set(item) # Select the item under cursor before showing menu
                menu.post(event.x_root, event.y_root)
        treeview.bind("<Button-3>", show_menu) # Button-3 for right-click on most systems

    def copy_treeview_item(self, treeview):
        """Copies the selected treeview row's values to the clipboard."""
        selected_item_id = treeview.selection()
        if not selected_item_id:
            messagebox.showinfo("Copy", "No item selected to copy.", parent=self)
            return
        item_values = treeview.item(selected_item_id[0])['values']
        if not item_values:
            messagebox.showinfo("Copy", "Selected item has no values.", parent=self)
            return
        try:
            self.clipboard_clear()
            self.clipboard_append("\t".join(str(v if v is not None else "") for v in item_values))
            self.set_status("Selected row copied to clipboard.")
        except tk.TclError: # Might happen if clipboard is not accessible
            messagebox.showerror("Copy Error", "Could not access clipboard.", parent=self)

    def logout(self):
        """Logs out the current user and shows the login window."""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.destroy()
            # Re-create and show the login window.
            # This assumes the global 'conn' and 'cursor' might be reused or re-established by LoginWindow if needed.
            if conn and conn.is_connected():
                print("DB connection is still active for new login window.")
            else:
                print("DB connection was closed or lost. Login window will attempt to reconnect.")
            
            login_app = LoginWindow()
            login_app.mainloop()

# --- Main application execution ---
if __name__ == "__main__":
    # The global 'conn' and 'cursor' are initialized at the start.
    # We only proceed if the initial connection was successful.
    if conn and cursor:
        try:
            app = LoginWindow() # Start with the login window
            app.mainloop()
        finally:
            # This block executes when mainloop ends (e.g., main window closed)
            # or if an unhandled exception occurs within the try block of mainloop.
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
                print("Database connection closed.")
    else:
        # This else block corresponds to the 'if conn and cursor:' at the module level.
        # If the initial database connection failed, this message is printed.
        print("Application did not start due to initial database connection failure")
