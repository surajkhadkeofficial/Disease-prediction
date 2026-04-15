import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import datetime
import os

from app.database import Database
from app.api import get_ai_analysis
from app.pdf_generator import generate_pdf

class HospitalApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.hospital_name = os.getenv("HOSPITAL_NAME", "CITY GENERAL HOSPITAL")
        self.root.title(f"{self.hospital_name} — AI Prediction System")

        try:
            self.root.state('zoomed')
        except Exception:
            self.root.attributes('-zoomed', True)

        self.db = Database()
        self._setup_ui()

    def _setup_ui(self):
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        tk.Label(main_frame, text="🏥 Patient Intake Form", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 15))

        form_frame = tk.Frame(main_frame)
        form_frame.pack(fill="both", expand=True)

        # LEFT COLUMN
        tk.Label(form_frame, text="1. Patient Information", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        self.ent_name  = self._input_row(form_frame, "Full Name:", 1, 0)
        self.ent_age   = self._input_row(form_frame, "Age:", 2, 0)
        
        tk.Label(form_frame, text="Gender:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.combo_gender = ttk.Combobox(form_frame, values=["Male", "Female", "Other"], width=27)
        self.combo_gender.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        
        self.ent_email = self._input_row(form_frame, "Email:", 4, 0)
        self.ent_phone = self._input_row(form_frame, "Phone:", 5, 0)
        self.ent_addr  = self._input_row(form_frame, "Address:", 6, 0)

        # LEFT COLUMN (Emergency)
        tk.Label(form_frame, text="2. Emergency Contact", font=("Segoe UI", 11, "bold")).grid(row=7, column=0, columnspan=2, sticky="w", pady=(18, 8))
        self.ent_ename  = self._input_row(form_frame, "Contact Name:", 8, 0)
        self.ent_erel   = self._input_row(form_frame, "Relationship:", 9, 0)
        self.ent_ephone = self._input_row(form_frame, "Emergency Phone:", 10, 0)

        # RIGHT COLUMN
        tk.Label(form_frame, text="3. Clinical Data", font=("Segoe UI", 11, "bold")).grid(row=0, column=2, columnspan=2, sticky="w", pady=(0, 8), padx=(50, 0))

        tk.Label(form_frame, text="Medical History:").grid(row=1, column=2, sticky="nw", padx=(50, 5), pady=5)
        self.txt_hist = tk.Text(form_frame, height=5, width=45, font=("Segoe UI", 10))
        self.txt_hist.grid(row=1, column=3, rowspan=3, sticky="w", padx=5, pady=5)

        tk.Label(form_frame, text="Symptoms:").grid(row=4, column=2, sticky="nw", padx=(50, 5), pady=5)
        self.txt_sym = scrolledtext.ScrolledText(form_frame, height=5, width=45, font=("Segoe UI", 10))
        self.txt_sym.grid(row=4, column=3, rowspan=3, sticky="w", padx=5, pady=5)

        # Buttons
        btn_frame = tk.Frame(main_frame, pady=15)
        btn_frame.pack(fill="x")

        tk.Button(btn_frame, text="🔍 Run AI Analysis", command=self.run_ai, bg="#0078D7", fg="white", font=("Segoe UI", 10, "bold"), width=22).pack(side="left", padx=5)
        tk.Button(btn_frame, text="💾 Save & Generate PDF", command=self.save, bg="#28a745", fg="white", font=("Segoe UI", 10, "bold"), width=22).pack(side="left", padx=5)
        tk.Button(btn_frame, text="🗑 Clear Form", command=self.clear, font=("Segoe UI", 10), width=15).pack(side="right", padx=5)

        # AI Output
        tk.Label(main_frame, text="AI Analysis Output:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.txt_result = scrolledtext.ScrolledText(main_frame, height=10, font=("Segoe UI", 10), bg="#f4f4f4")
        self.txt_result.pack(fill="both", expand=True, pady=(4, 10))

    def _input_row(self, parent, label: str, row: int, col: int) -> tk.Entry:
        tk.Label(parent, text=label).grid(row=row, column=col, sticky="w", padx=5, pady=5)
        entry = tk.Entry(parent, width=30, font=("Segoe UI", 10))
        entry.grid(row=row, column=col + 1, sticky="w", padx=5, pady=5)
        return entry

    def run_ai(self):
        sym = self.txt_sym.get("1.0", tk.END).strip()
        if not sym:
            messagebox.showerror("Input Error", "Please enter the patient's symptoms.")
            return

        self.txt_result.delete("1.0", tk.END)
        self.txt_result.insert(tk.END, "⏳ Analyzing with Gemini AI — please wait...")
        self.root.update()

        result = get_ai_analysis(
            symptoms=sym,
            history=self.txt_hist.get("1.0", tk.END).strip(),
            age=self.ent_age.get(),
            gender=self.combo_gender.get()
        )
        self.txt_result.delete("1.0", tk.END)
        self.txt_result.insert(tk.END, result)

    def save(self):
        if not self.ent_name.get().strip():
            messagebox.showerror("Input Error", "Patient name is required.")
            return

        diagnosis = self.txt_result.get("1.0", tk.END).strip()
        if not diagnosis:
            messagebox.showwarning("No Diagnosis", "No AI analysis found. Please run AI Analysis first.")

        record = (
            self.ent_name.get().strip(),
            self.ent_age.get().strip(),
            self.combo_gender.get(),
            self.ent_email.get().strip(),
            self.ent_phone.get().strip(),
            self.ent_addr.get().strip(),
            self.ent_ename.get().strip(),
            self.ent_erel.get().strip(),
            self.ent_ephone.get().strip(),
            self.txt_hist.get("1.0", tk.END).strip(),
            self.txt_sym.get("1.0", tk.END).strip(),
            diagnosis,
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        )

        try:
            pid = self.db.save(record)
            pdf_file = generate_pdf((pid,) + record)
            messagebox.showinfo("Success", f"✅ Record saved to database (ID: {pid})\n📄 PDF created: {pdf_file}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def clear(self):
        for entry in (self.ent_name, self.ent_age, self.ent_email, self.ent_phone, self.ent_addr, self.ent_ename, self.ent_erel, self.ent_ephone):
            entry.delete(0, tk.END)
        self.combo_gender.set('')
        self.txt_hist.delete("1.0", tk.END)
        self.txt_sym.delete("1.0", tk.END)
        self.txt_result.delete("1.0", tk.END)