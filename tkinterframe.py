import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
from fpdf import FPDF
import google.generativeai as genai
import datetime
import os

# --- CONFIGURATION ---
# REPLACE WITH YOUR NEW KEY
API_KEY = "AIzaSyAavkTnLdKDL40AtxJJkV2ri3GfodD3dgc"

# Configure Gemini
try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
except Exception as e:
    print(f"API Configuration Error: {e}")

# --- PART 1: GEMINI AI LOGIC ---
def get_ai_prediction(symptoms, history, allergies):
    if not API_KEY or API_KEY == "YOUR_GEMINI_API_KEY":
        return "Error: Please set a valid Gemini API Key in the code."
    
    # Enhanced prompt that considers history and allergies
    prompt = f"""
    Act as a senior medical consultant. Analyze this patient:
    
    Patient Medical History: {history}
    Patient Allergies: {allergies}
    Current Symptoms: "{symptoms}"
    
    Provide a structured output:
    1. Potential Diagnosis: (Most likely condition)
    2. Differential Diagnosis: (Other possibilities)
    3. Reasoning: (Connect symptoms to history if relevant)
    4. Recommended Tests: (specific labs/imaging)
    5. Treatment Plan: (Immediate care steps)
    
    Disclaimer: Add a disclaimer that this is AI-assisted and requires doctor verification.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"API Error: {str(e)}"

# --- PART 2: DATABASE HANDLING ---
class Database:
    def __init__(self, db_name="hospital_v2.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        # Expanded Schema
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                age TEXT,
                gender TEXT,
                phone TEXT,
                address TEXT,
                visit_date TEXT,
                emer_name TEXT,
                emer_phone TEXT,
                emer_rel TEXT,
                blood_group TEXT,
                history TEXT,
                allergies TEXT,
                symptoms TEXT,
                diagnosis TEXT
            )
        """)
        self.conn.commit()

    def insert_patient(self, data):
        self.cursor.execute("""
            INSERT INTO patients (
                name, age, gender, phone, address, visit_date,
                emer_name, emer_phone, emer_rel,
                blood_group, history, allergies,
                symptoms, diagnosis
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, data)
        self.conn.commit()
        return self.cursor.lastrowid

    def get_patient(self, pid):
        self.cursor.execute("SELECT * FROM patients WHERE id=?", (pid,))
        return self.cursor.fetchone()

# --- PART 3: PRO PDF REPORT ---
class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'General Hospital - Medical Report', 0, 1, 'C')
        self.line(10, 20, 200, 20)
        self.ln(15)

    def section_title(self, label):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255) # Light blue background
        self.cell(0, 8, label, 0, 1, 'L', True)
        self.ln(2)

    def field_value(self, label, value):
        self.set_font('Arial', 'B', 10)
        self.cell(40, 6, label, 0, 0)
        self.set_font('Arial', '', 10)
        self.cell(0, 6, str(value), 0, 1)

    def generate(self, data):
        self.add_page()
        
        # Unpack data (15 items including ID)
        (pid, name, age, gender, phone, addr, date, 
         e_name, e_phone, e_rel, 
         blood, history, allergy, sym, diag) = data

        # 1. Patient Info
        self.section_title("Patient Information")
        self.field_value("Patient ID:", pid)
        self.field_value("Name:", name)
        self.field_value("Age/Gender:", f"{age} / {gender}")
        self.field_value("Phone:", phone)
        self.field_value("Address:", addr)
        self.field_value("Date of Visit:", date)
        self.ln(5)

        # 2. Emergency Contact
        self.section_title("Emergency Contact")
        self.field_value("Name:", e_name)
        self.field_value("Relationship:", e_rel)
        self.field_value("Phone:", e_phone)
        self.ln(5)

        # 3. Medical Profile
        self.section_title("Medical Profile")
        self.field_value("Blood Group:", blood)
        self.field_value("Allergies:", allergy)
        self.multi_cell(0, 6, f"Medical History: {history}")
        self.ln(5)

        # 4. Clinical Details
        self.section_title("Clinical Assessment")
        self.set_font('Arial', 'B', 10)
        self.cell(0, 6, "Reported Symptoms:", 0, 1)
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 6, sym)
        self.ln(5)

        self.section_title("AI Diagnosis & Recommendations")
        # Handle unicode issues lightly
        clean_diag = diag.encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(0, 6, clean_diag)
        
        filename = f"Patient_{pid}_{name}.pdf"
        self.output(filename)
        return filename

# --- PART 4: ENHANCED GUI ---
class HospitalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Doctor's Intelligent Assistant v2.0")
        self.root.geometry("1100x800")
        
        self.db = Database()
        self.pdf = PDFReport()
        
        # Main Container with Scrollbar (optional but good for small screens)
        # For simplicity, we use standard pack layout
        
        self.create_forms()

    def create_forms(self):
        # --- Top Section: Personal Info & Emergency ---
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill="x", padx=10, pady=5)

        # 1. Personal Info Frame
        p_frame = tk.LabelFrame(top_frame, text="Patient Information", padx=10, pady=5, font=("Arial", 10, "bold"))
        p_frame.pack(side="left", fill="both", expand=True, padx=5)

        self.entry_name = self.create_field(p_frame, "Full Name:", 0)
        self.entry_age = self.create_field(p_frame, "Age:", 1)
        
        tk.Label(p_frame, text="Gender:").grid(row=2, column=0, sticky="w")
        self.combo_gender = ttk.Combobox(p_frame, values=["Male", "Female", "Other"])
        self.combo_gender.grid(row=2, column=1, padx=5, pady=2)
        
        self.entry_phone = self.create_field(p_frame, "Phone No:", 3)
        self.entry_addr = self.create_field(p_frame, "Address:", 4)
        
        # Date defaults to today
        tk.Label(p_frame, text="Date:").grid(row=5, column=0, sticky="w")
        self.entry_date = tk.Entry(p_frame)
        self.entry_date.insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))
        self.entry_date.grid(row=5, column=1, padx=5, pady=2)

        # 2. Emergency Contact Frame
        e_frame = tk.LabelFrame(top_frame, text="Emergency Contact", padx=10, pady=5, font=("Arial", 10, "bold"))
        e_frame.pack(side="left", fill="both", expand=True, padx=5)

        self.entry_ename = self.create_field(e_frame, "Contact Name:", 0)
        self.entry_ephone = self.create_field(e_frame, "Contact Phone:", 1)
        self.entry_erel = self.create_field(e_frame, "Relationship:", 2)

        # --- Middle Section: Medical Details ---
        med_frame = tk.LabelFrame(self.root, text="Medical Profile", padx=10, pady=5, font=("Arial", 10, "bold"))
        med_frame.pack(fill="x", padx=15, pady=5)

        tk.Label(med_frame, text="Blood Group:").grid(row=0, column=0, sticky="w")
        self.combo_blood = ttk.Combobox(med_frame, values=["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
        self.combo_blood.grid(row=0, column=1, padx=5, pady=5)

        self.entry_allergies = self.create_field(med_frame, "Allergies:", 0, col=2)
        
        tk.Label(med_frame, text="Medical History:").grid(row=1, column=0, sticky="nw")
        self.txt_history = tk.Text(med_frame, height=3, width=80)
        self.txt_history.grid(row=1, column=1, columnspan=3, padx=5, pady=5)

        # --- Bottom Section: Symptoms & AI ---
        diag_frame = tk.LabelFrame(self.root, text="Diagnosis & Reports", padx=10, pady=5, font=("Arial", 10, "bold"))
        diag_frame.pack(fill="both", expand=True, padx=15, pady=5)

        # Symptoms
        tk.Label(diag_frame, text="Current Symptoms (Describe in detail):").pack(anchor="w")
        self.txt_symptoms = scrolledtext.ScrolledText(diag_frame, height=4)
        self.txt_symptoms.pack(fill="x", pady=5)

        # Buttons
        btn_frame = tk.Frame(diag_frame)
        btn_frame.pack(pady=5)
        
        tk.Button(btn_frame, text="1. Analyze with AI", command=self.run_ai, bg="#673AB7", fg="white", font=("Arial", 11)).pack(side="left", padx=10)
        tk.Button(btn_frame, text="2. Save & Generate Report", command=self.save_data, bg="#009688", fg="white", font=("Arial", 11)).pack(side="left", padx=10)

        # AI Result
        tk.Label(diag_frame, text="AI Prediction:").pack(anchor="w")
        self.txt_result = scrolledtext.ScrolledText(diag_frame, height=8, bg="#f4f4f4")
        self.txt_result.pack(fill="both", expand=True, pady=5)

    def create_field(self, parent, label, r, col=0):
        tk.Label(parent, text=label).grid(row=r, column=col, sticky="w")
        entry = tk.Entry(parent, width=25)
        entry.grid(row=r, column=col+1, padx=5, pady=2)
        return entry

    def run_ai(self):
        symptoms = self.txt_symptoms.get("1.0", tk.END).strip()
        history = self.txt_history.get("1.0", tk.END).strip()
        allergies = self.entry_allergies.get()
        
        if len(symptoms) < 2:
            messagebox.showwarning("Input", "Please enter symptoms first.")
            return

        self.txt_result.delete("1.0", tk.END)
        self.txt_result.insert(tk.END, "Analyzing with Gemini AI...")
        self.root.update()
        
        prediction = get_ai_prediction(symptoms, history, allergies)
        self.txt_result.delete("1.0", tk.END)
        self.txt_result.insert(tk.END, prediction)

    def save_data(self):
        # Gather all data
        data = (
            self.entry_name.get(),
            self.entry_age.get(),
            self.combo_gender.get(),
            self.entry_phone.get(),
            self.entry_addr.get(),
            self.entry_date.get(),
            self.entry_ename.get(),
            self.entry_ephone.get(),
            self.entry_erel.get(),
            self.combo_blood.get(),
            self.txt_history.get("1.0", tk.END).strip(),
            self.entry_allergies.get(),
            self.txt_symptoms.get("1.0", tk.END).strip(),
            self.txt_result.get("1.0", tk.END).strip()
        )
        
        if not data[0]: # Check Name
            messagebox.showerror("Error", "Patient Name is mandatory.")
            return

        try:
            pid = self.db.insert_patient(data)
            
            # Fetch full record including the new ID to send to PDF
            full_record = (pid,) + data
            filename = self.pdf.generate(full_record)
            
            messagebox.showinfo("Success", f"Record Saved!\nPDF Report: {filename}")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = HospitalApp(root)
    root.mainloop()