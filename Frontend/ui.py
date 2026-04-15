import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime

from database.db import Database
from services.ai_service import AIService
from services.pdf_service import PDFService

class DiseasePredictionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Disease Prediction System")
        self.root.geometry("1200x750")

        self.db = Database()
        self.ai_service = AIService()
        self.pdf_service = PDFService()

        self.build_ui()

    def build_ui(self):
        main = tk.Frame(self.root, padx=20, pady=20)
        main.pack(fill="both", expand=True)

        tk.Label(
            main,
            text="Disease Prediction System",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", pady=(0, 15))

        form = tk.Frame(main)
        form.pack(fill="x")

        left = tk.Frame(form)
        left.pack(side="left", fill="both", expand=True, padx=(0, 20))

        right = tk.Frame(form)
        right.pack(side="left", fill="both", expand=True)

        self.name = self.add_entry(left, "Full Name")
        self.age = self.add_entry(left, "Age")
        self.phone = self.add_entry(left, "Phone")
        self.address = self.add_entry(left, "Address")

        tk.Label(left, text="Gender").pack(anchor="w", pady=(10, 0))
        self.gender = ttk.Combobox(left, values=["Male", "Female", "Other"], state="readonly")
        self.gender.pack(fill="x", pady=(0, 10))

        self.emer_name = self.add_entry(left, "Emergency Contact Name")
        self.emer_rel = self.add_entry(left, "Relationship")
        self.emer_phone = self.add_entry(left, "Emergency Phone")

        tk.Label(right, text="Medical History").pack(anchor="w")
        self.history = scrolledtext.ScrolledText(right, height=6)
        self.history.pack(fill="both", expand=False, pady=(0, 10))

        tk.Label(right, text="Symptoms").pack(anchor="w")
        self.symptoms = scrolledtext.ScrolledText(right, height=6)
        self.symptoms.pack(fill="both", expand=False, pady=(0, 10))

        btns = tk.Frame(main)
        btns.pack(fill="x", pady=15)

        tk.Button(
            btns, text="Run AI Analysis", command=self.run_ai,
            bg="#0078D7", fg="white", padx=15, pady=8
        ).pack(side="left", padx=5)

        tk.Button(
            btns, text="Save & Generate PDF", command=self.save_report,
            bg="#28a745", fg="white", padx=15, pady=8
        ).pack(side="left", padx=5)

        tk.Button(
            btns, text="Clear", command=self.clear_form,
            padx=15, pady=8
        ).pack(side="right", padx=5)

        tk.Label(main, text="AI Output", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.output = scrolledtext.ScrolledText(main, height=12)
        self.output.pack(fill="both", expand=True)

    def add_entry(self, parent, label):
        tk.Label(parent, text=label).pack(anchor="w", pady=(5, 0))
        entry = tk.Entry(parent)
        entry.pack(fill="x", pady=(0, 8))
        return entry

    def run_ai(self):
        symptoms = self.symptoms.get("1.0", tk.END).strip()
        if not symptoms:
            messagebox.showerror("Input Error", "Please enter symptoms first.")
            return

        result = self.ai_service.analyze(
            symptoms=symptoms,
            history=self.history.get("1.0", tk.END).strip(),
            age=self.age.get().strip(),
            gender=self.gender.get().strip()
        )

        self.output.delete("1.0", tk.END)
        text = (
            f"Provisional Diagnosis: {result.get('provisional_diagnosis', '')}\n\n"
            f"Differential Diagnosis: {result.get('differential_diagnosis', '')}\n\n"
            f"Recommended Tests: {result.get('recommended_tests', '')}\n\n"
            f"Treatment Plan: {result.get('treatment_plan', '')}\n\n"
            f"Medicine Suggestions: {result.get('medicine_suggestions', '')}\n\n"
            f"Notes: {result.get('notes', '')}"
        )
        self.output.insert(tk.END, text)

    def save_report(self):
        if not self.name.get().strip():
            messagebox.showerror("Input Error", "Patient name is required.")
            return

        diagnosis_text = self.output.get("1.0", tk.END).strip()

        record = (
            self.name.get().strip(),
            self.age.get().strip(),
            self.gender.get().strip(),
            self.phone.get().strip(),
            self.address.get().strip(),
            self.emer_name.get().strip(),
            self.emer_rel.get().strip(),
            self.emer_phone.get().strip(),
            self.history.get("1.0", tk.END).strip(),
            self.symptoms.get("1.0", tk.END).strip(),
            diagnosis_text,
            datetime.now().strftime("%Y-%m-%d %H:%M")
        )

        try:
            pid = self.db.save_patient(record)

            patient_data = {
                "id": pid,
                "name": record[0],
                "age": record[1],
                "gender": record[2],
                "phone": record[3],
                "address": record[4],
                "emer_name": record[5],
                "emer_rel": record[6],
                "emer_phone": record[7],
                "history": record[8],
                "symptoms": record[9]
            }

            ai_result = {
                "full_output": diagnosis_text
            }

            pdf_path = self.pdf_service.generate_report(patient_data, ai_result)

            messagebox.showinfo(
                "Success",
                f"Record saved successfully.\nPDF generated:\n{pdf_path}"
            )
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def clear_form(self):
        for entry in [self.name, self.age, self.phone, self.address, self.emer_name, self.emer_rel, self.emer_phone]:
            entry.delete(0, tk.END)
        self.gender.set("")
        self.history.delete("1.0", tk.END)
        self.symptoms.delete("1.0", tk.END)
        self.output.delete("1.0", tk.END)