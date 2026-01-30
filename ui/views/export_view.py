import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from database.db_manager import DatabaseManager
import datetime
import openpyxl 
from openpyxl.styles import Font
import os
from utils.date_util import DateUtil


COL_DATA_CONSEGNA = "Fecha de Entrega"

class ExportView(ctk.CTkFrame):
    def __init__(self, master, back_callback):
        super().__init__(master)
        self.back_callback = back_callback
        self.db = DatabaseManager()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        self.header = ctk.CTkFrame(self, height=60, corner_radius=0)
        self.header.grid(row=0, column=0, sticky="ew")
        
        self.back_btn = ctk.CTkButton(self.header, text="← Menú", width=80, command=self.back_callback)
        self.back_btn.pack(side="left", padx=20, pady=10)

        self.title_label = ctk.CTkLabel(self.header, text="Informes e Historial", font=("Roboto", 24, "bold"))
        self.title_label.pack(side="left", padx=20)

        # Content
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_columnconfigure(1, weight=2)
        self.content.grid_rowconfigure(0, weight=1)

        # --- Left: Export Controls ---
        self.export_frame = ctk.CTkFrame(self.content)
        self.export_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        ctk.CTkLabel(self.export_frame, text="Exportar Excel", font=("Roboto", 18, "bold")).pack(pady=15)

        # Month and Year Selection Lists
        self.months_list = ["Todos"] + [
            "Enero", "Febrero", "Marzo", "Abril",
            "Mayo", "Junio", "Julio", "Agosto",
            "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        
        current_date = datetime.datetime.now()
        current_month_idx = current_date.month # Shifted by 1 because of "Tutti"
        current_year = current_date.year
        
        self.years_list = ["Todos"] + [str(y) for y in range(current_year - 5, current_year + 5)]

        # Date Selection Container
        self.date_container = ctk.CTkFrame(self.export_frame, fg_color="transparent")
        self.date_container.pack(pady=10, fill="x", padx=20)
        self.date_container.grid_columnconfigure((0, 1), weight=1)

        # Month Selection
        self.month_var = ctk.StringVar(value=self.months_list[current_month_idx])
        ctk.CTkLabel(self.date_container, text="Mes:").grid(row=0, column=0, sticky="w", padx=5)
        self.om_month = ctk.CTkOptionMenu(self.date_container, values=self.months_list, variable=self.month_var)
        self.om_month.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="ew")

        # Year Selection
        self.year_var = ctk.StringVar(value=str(current_year))
        ctk.CTkLabel(self.date_container, text="Año:").grid(row=0, column=1, sticky="w", padx=5)
        self.om_year = ctk.CTkOptionMenu(self.date_container, values=self.years_list, variable=self.year_var)
        self.om_year.grid(row=1, column=1, padx=5, pady=(0, 5), sticky="ew")

        # Career Filter
        self.career_var = ctk.StringVar(value="Todas")
        # Auto-refresh on any change
        self.career_var.trace_add("write", lambda *args: self.refresh_history())
        self.month_var.trace_add("write", lambda *args: self.refresh_history())
        self.year_var.trace_add("write", lambda *args: self.refresh_history())

        careers = ["Todas", "Medicina", "Enfermería", "Instrumentación Quirúrgica", "Fonoaudiología"]
        ctk.CTkLabel(self.export_frame, text="Carrera:").pack(pady=(5, 0))
        self.om_career = ctk.CTkOptionMenu(self.export_frame, values=careers, variable=self.career_var, width=150)
        self.om_career.pack(pady=5)

        # Export Button
        self.btn_export = ctk.CTkButton(self.export_frame, text="Descargar Excel", command=self.do_export, fg_color="#2196F3")
        self.btn_export.pack(pady=30, padx=20, fill="x")

        # Clear History Button
        self.btn_clear_all = ctk.CTkButton(self.export_frame, text="Borrar Todo el Historial", 
                                           command=self.clear_all_history, fg_color="#e74c3c", hover_color="#c0392b")
        self.btn_clear_all.pack(pady=(20, 10), padx=20, fill="x")
        ctk.CTkLabel(self.export_frame, text="* Elimina permanentemente todos los datos entregados", 
                     font=("Roboto", 10, "italic"), text_color="gray").pack()

        # --- Right: History Management ---
        self.history_frame = ctk.CTkFrame(self.content)
        self.history_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self.history_frame.grid_columnconfigure(0, weight=1)
        self.history_frame.grid_rowconfigure(1, weight=1)

        # History Header
        self.history_header = ctk.CTkFrame(self.history_frame, fg_color="transparent")
        self.history_header.grid(row=0, column=0, pady=10, sticky="ew")
        self.history_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.history_header, text="Certificados Ya Entregados (Historial)", font=("Roboto", 18, "bold")).grid(row=0, column=0, padx=20, sticky="w")
        self.history_count_label = ctk.CTkLabel(self.history_header, text="Total: 0", font=("Roboto", 12, "bold"))
        self.history_count_label.grid(row=0, column=1, padx=20, sticky="e")

        # Treeview for History
        columns = ("db_id", "N.", "Nombre", "Carrera", "Factura", COL_DATA_CONSEGNA)
        self.tree = ttk.Treeview(self.history_frame, columns=columns, show="headings")
        
        self.tree.heading("db_id", text="ID")
        self.tree.heading("N.", text="N.")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Carrera", text="Carrera")
        self.tree.heading("Factura", text="Factura")
        self.tree.heading(COL_DATA_CONSEGNA, text=COL_DATA_CONSEGNA)
        
        self.tree.column("db_id", width=0, stretch=False) # Hide db_id
        self.tree.column("N.", width=50)
        self.tree.column("Nombre", width=150)
        self.tree.column("Carrera", width=120)
        self.tree.column("Factura", width=80)
        self.tree.column(COL_DATA_CONSEGNA, width=150)


        self.tree.grid(row=1, column=0, sticky="nsew", padx=15, pady=5)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.history_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky="ns", pady=5)

        # Actions for history
        self.history_actions = ctk.CTkFrame(self.history_frame, fg_color="transparent")
        self.history_actions.grid(row=2, column=0, pady=15, padx=15, sticky="ew")
        self.history_actions.grid_columnconfigure((0, 1), weight=1)

        self.btn_undo = ctk.CTkButton(self.history_actions, text="Anular Entrega (Restablecer)", 
                                      command=self.undo_selected, fg_color="orange")
        self.btn_undo.grid(row=0, column=0, padx=5, sticky="ew")

        self.btn_delete_one = ctk.CTkButton(self.history_actions, text="Eliminar Definitivamente", 
                                            command=self.delete_selected, fg_color="#e74c3c")
        self.btn_delete_one.grid(row=0, column=1, padx=5, sticky="ew")

        self.refresh_history()

    def refresh_history(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        selected_career = self.career_var.get()
        career_filter = selected_career if selected_career != "Todas" else None
        
        selected_month_name = self.month_var.get()
        selected_month = f"{self.months_list.index(selected_month_name):02d}" if selected_month_name != "Todos" else None
        selected_year = self.year_var.get()
        year_filter = selected_year if selected_year != "Todos" else None
        
        records = self.db.get_filtered_delivered_certificates(selected_month, year_filter, career_filter)
        for r in records:
            # r: (id, numero, nombre, carrera, num_factura, gestion, fecha_entrega)
            formatted_date = DateUtil.format_datetime(r[6])
            self.tree.insert("", "end", values=(r[0], r[1], r[2], r[3], r[4], formatted_date))
            
        self.history_count_label.configure(text=f"Total: {len(records)}")


    def undo_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Atención", "Seleccione un certificado para restablecer.")
            return
        
        item_values = self.tree.item(selected[0])['values']
        cert_id, name = item_values[0], item_values[2] # 0 is db_id, 2 is name

        if messagebox.askyesno("Confirmar Restablecimiento", f"¿Desea devolver a {name} a la lista de certificados para entregar?"):
            self.db.undo_delivery(cert_id)
            self.refresh_history()
            messagebox.showinfo("Éxito", f"{name} restablecido con éxito.")

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Atención", "Seleccione un certificado para eliminar.")
            return
        
        item_values = self.tree.item(selected[0])['values']
        cert_id, name = item_values[0], item_values[2] # 0 is db_id, 2 is name

        if messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de que desea eliminar permanentemente a {name} del historial?"):
            self.db.delete_certificate(cert_id)
            self.refresh_history()

    def clear_all_history(self):
        if messagebox.askyesno("Borrar Historial", "¿Está seguro de que desea ELIMINAR PERMANENTEMENTE todos los certificados entregados?\nEsta operación no se puede deshacer."):
            if messagebox.askyesno("Confirmación Final", "¿Está completamente seguro? Se perderán todos los datos del historial."):
                self.db.clear_delivered_certificates()
                self.refresh_history()
                messagebox.showinfo("Éxito", "Historial borrado con éxito.")

    def do_export(self):
        selected_month_name = self.month_var.get()
        month = f"{self.months_list.index(selected_month_name):02d}" if selected_month_name != "Todos" else None
        year = self.year_var.get() if self.year_var.get() != "Todos" else None
        career = self.career_var.get()
        
        c = career if career != "Todas" else None
        
        try:
            data = self.db.get_delivered_certificates_by_month(month, year, c)
            if not data:
                messagebox.showinfo("Información", "No se encontraron datos para el período seleccionado.")
                return
            
            # Generate Excel
            wb = openpyxl.Workbook()
            ws = wb.active
            
            period_str = f"{month or 'Siempre'}-{year or 'Siempre'}"
            ws.title = f"Report {period_str}"
            
            headers = ["N.", "Nombre Estudiante", "Carrera", "N. Factura", "Gestión", COL_DATA_CONSEGNA]
            ws.append(headers)
            for cell in ws[1]:
                cell.font = Font(bold=True)
                
            for row in data:
                # row: (numero, nombre, carrera, factura, gestion, fecha)
                formatted_row = list(row)
                formatted_row[5] = DateUtil.format_datetime(row[5])
                ws.append(formatted_row)

            
            filename_period = f"{year or 'Siempre'}" + (f"-{month}" if month else "")
            filename = f"Report_Certificati_{career}_{filename_period}.xlsx"
            # Get desktop path or save in current dir
            save_path = os.path.join("/Users/domenico/Downloads", filename)
            
            wb.save(save_path)
            messagebox.showinfo("Éxito", f"Archivo guardado: {save_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error durante la exportación: {e}")
