import os
import datetime
from fpdf import FPDF
from dotenv import load_dotenv

from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 20)
        self.cell(0, 10, "SK HOSPITAL", border=0, ln=1, align='C')
        self.set_font('Arial', '', 10)
        self.cell(0, 5, f"Report Date: {datetime.datetime.now().strftime('%Y-%m-%d')}",
                  border=0, ln=1, align='R')
        self.ln(5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(8)

def generate_pdf(data: tuple) -> str:
    pdf = PDFReport()
    pdf.add_page()

    # Unpack including the new email field
    (pid, name, age, gen, email, ph, addr,
     ename, erel, ephone,
     hist, sym, diag, visit_date) = data

    def section_header(title: str):
        pdf.set_font('Arial', 'B', 12)
        pdf.set_fill_color(220, 230, 241)
        pdf.cell(0, 8, f"  {title}", border=0, ln=1, align='L', fill=True)
        pdf.set_font('Arial', '', 11)
        pdf.ln(2)

    section_header("1. PATIENT IDENTITY")
    pdf.multi_cell(0, 6,
        f"Name    : {name}\n"
        f"Age     : {age}        Gender  : {gen}\n"
        f"Email   : {email}\n"
        f"Phone   : {ph}\n"
        f"Address : {addr}"
    )
    pdf.ln(5)

    section_header("2. EMERGENCY CONTACT")
    pdf.cell(0, 6, f"Name         : {ename}  ({erel})", ln=1)
    pdf.cell(0, 6, f"Phone        : {ephone}", ln=1)
    pdf.ln(5)

    section_header("3. CLINICAL PRESENTATION")
    pdf.multi_cell(0, 6, f"Medical History:\n{hist}\n\nPresenting Symptoms:\n{sym}")
    pdf.ln(5)

    section_header("4. ASSESSMENT & PLAN  (AI-Generated)")
    # Replace unsupported characters for FPDF standard fonts
    clean_diag = diag.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 6, clean_diag)

    pdf.ln(25)
    pdf.set_font('Arial', '', 10)
    
    # Check if signature exists in the root folder or an assets folder
    if os.path.exists("signature.png"):
        pdf.image("signature.png", x=140, w=40)
        
    sig_y = pdf.get_y()
    pdf.line(140, sig_y, 190, sig_y)
    pdf.set_xy(140, sig_y + 2)
    pdf.cell(50, 5, "Doctor's Signature", align='C')

    # Create reports directory if it doesn't exist
    if not os.path.exists("reports"):
        os.makedirs("reports")

    filename = f"reports/Report_{pid}_{name.replace(' ', '_')}.pdf"
    pdf.output(filename)
    return filename