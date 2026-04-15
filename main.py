import tkinter as tk
from app.gui import HospitalApp

if __name__ == "__main__":
    root = tk.Tk()
    app = HospitalApp(root)
    root.mainloop()