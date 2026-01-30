import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from database.db_manager import DatabaseManager
import datetime
import openpyxl 
from openpyxl.styles import Font
import os

class ExportView(ctk.CTkFrame):
    def __init__(self, master, back_callback):
        super().__init__(master)
        self.back_callback = back_callback
        self.db = DatabaseManager()

        self.pack(fill="both", expand=True)

        # Header
        self.header = ctk.CTkFrame(self, height=60, corner_radius=0)
        self.header.pack(fill="x")
        
        self.back_btn = ctk.CTkButton(self.header, text="← Menu", width=80, command=self.back_callback)
        self.back_btn.pack(side="left", padx=20, pady=10)

        self.title_label = ctk.CTkLabel(self.header, text="Reportistica", font=("Roboto", 24, "bold"))
        self.title_label.pack(side="left", padx=20)

        # Content
        self.content = ctk.CTkFrame(self)
        self.content.pack(fill="both", expand=True, padx=40, pady=40)

        ctk.CTkLabel(self.content, text="Esporta Certificati Consegnati", font=("Roboto", 20)).pack(pady=20)

        # Month Selection
        self.month_var = ctk.StringVar(value=datetime.datetime.now().strftime("%m"))
        ctk.CTkLabel(self.content, text="Mese (1-12):").pack()
        self.entry_month = ctk.CTkEntry(self.content, textvariable=self.month_var, width=100)
        self.entry_month.pack(pady=5)

        # Year Selection
        self.year_var = ctk.StringVar(value=datetime.datetime.now().strftime("%Y"))
        ctk.CTkLabel(self.content, text="Anno:").pack()
        self.entry_year = ctk.CTkEntry(self.content, textvariable=self.year_var, width=100)
        self.entry_year.pack(pady=5)

        # Career Filter (Optional)
        self.career_var = ctk.StringVar(value="Tutte")
        careers = ["Tutte", "Medicina", "Enfermería", "Instrumentación Quirúrgica", "Fonoaudiología"]
        ctk.CTkLabel(self.content, text="Carriera:").pack(pady=(20, 0))
        self.om_career = ctk.CTkOptionMenu(self.content, values=careers, variable=self.career_var)
        self.om_career.pack(pady=5)

        # Export Button
        self.btn_export = ctk.CTkButton(self.content, text="Scarica Excel", command=self.do_export, fg_color="#2196F3")
        self.btn_export.pack(pady=40)

    def do_export(self):
        month = self.entry_month.get()
        year = self.entry_year.get()
        career = self.career_var.get()
        
        c = career if career != "Tutte" else None
        
        try:
            data = self.db.get_delivered_certificates_by_month(month, year, c)
            if not data:
                messagebox.showinfo("Info", "Nessun dato trovato per il periodo selezionato.")
                return
            
            # Generate Excel
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = f"Report {month}-{year}"
            
            headers = ["Nome Studente", "Carriera", "N. Fattura", "Gestione", "Data Consegna"]
            ws.append(headers)
            for cell in ws[1]:
                cell.font = Font(bold=True)
                
            for row in data:
                # row: (nombre, carrera, factura, gestion, fecha)
                ws.append(row)
            
            filename = f"Report_Certificati_{year}_{month}.xlsx"
            # Get desktop path or save in current dir
            save_path = os.path.join(os.getcwd(), filename)
            
            wb.save(save_path)
            messagebox.showinfo("Successo", f"File salvato: {save_path}")
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante l'export: {e}")
