import customtkinter as ctk
from tkinter import ttk
import tkinter as tk
from database.db_manager import DatabaseManager
from datetime import datetime

class CareerView(ctk.CTkFrame):
    def __init__(self, master, career_name, theme_color, back_callback):
        super().__init__(master)
        self.career_name = career_name
        self.theme_color = theme_color
        self.back_callback = back_callback
        self.db = DatabaseManager()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Content area

        # --- Header ---
        self.header = ctk.CTkFrame(self, fg_color=self.theme_color, height=60, corner_radius=0)
        self.header.grid(row=0, column=0, sticky="ew")
        
        self.back_btn = ctk.CTkButton(self.header, text="← Menu", width=80, fg_color="white", text_color="black", hover_color="#eee", command=self.back_callback)
        self.back_btn.pack(side="left", padx=20, pady=10)

        self.title_label = ctk.CTkLabel(self.header, text=f"Gestione {self.career_name}", font=("Roboto", 24, "bold"), text_color="white")
        self.title_label.pack(side="left", padx=20)

        # --- Main Content Area (Split: Left Form, Right List) ---
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.content.grid_columnconfigure(1, weight=1) # List area expands

        # --- Left: Input Form ---
        self.form_frame = ctk.CTkFrame(self.content, width=300)
        self.form_frame.grid(row=0, column=0, sticky="ns", padx=(0, 20))
        
        ctk.CTkLabel(self.form_frame, text="Nuova Registrazione", font=("Roboto", 16, "bold")).pack(pady=10)
        
        self.entry_name = ctk.CTkEntry(self.form_frame, placeholder_text="Nome Studente")
        self.entry_name.pack(pady=10, padx=20, fill="x")

        self.entry_factura = ctk.CTkEntry(self.form_frame, placeholder_text="Numero Fattura")
        self.entry_factura.pack(pady=10, padx=20, fill="x")

        self.entry_gestion = ctk.CTkEntry(self.form_frame, placeholder_text="Gestione (es. II-25)")
        self.entry_gestion.pack(pady=10, padx=20, fill="x")

        self.btn_save = ctk.CTkButton(self.form_frame, text="Registra", fg_color=self.theme_color, command=self.add_record)
        self.btn_save.pack(pady=20, padx=20, fill="x")

        # --- Right: Pending List ---
        self.list_frame = ctk.CTkFrame(self.content)
        self.list_frame.grid(row=0, column=1, sticky="nsew")
        self.list_frame.grid_rowconfigure(1, weight=1)
        self.list_frame.grid_columnconfigure(0, weight=1)

        # Search Bar
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.filter_list)
        self.search_entry = ctk.CTkEntry(self.list_frame, placeholder_text="Cerca per nome...", textvariable=self.search_var)
        self.search_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Treeview Style
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#2b2b2b", 
                        foreground="white", 
                        fieldbackground="#2b2b2b", 
                        rowheight=30)
        style.map("Treeview", background=[("selected", self.theme_color)])
        style.configure("Treeview.Heading", font=("Roboto", 12, "bold"))
        
        # Treeview
        columns = ("ID", "Nome", "Fattura", "Gestione", "Data")
        self.tree = ttk.Treeview(self.list_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Fattura", text="Fattura")
        self.tree.heading("Gestione", text="Gestione")
        self.tree.heading("Data", text="Data Inserimento")
        
        self.tree.column("ID", width=30)
        self.tree.column("Nome", width=150)
        self.tree.column("Fattura", width=80)
        self.tree.column("Gestione", width=80)
        self.tree.column("Data", width=100)

        self.tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # Scrollbar for tree
        scrollbar = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky="ns", pady=(0, 10))

        # Deliver Button
        self.btn_deliver = ctk.CTkButton(self.list_frame, text="Consegnare Certificato", fg_color="gray", state="disabled", command=self.deliver_certificate)
        self.btn_deliver.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.refresh_data()

    def add_record(self):
        name = self.entry_name.get()
        factura = self.entry_factura.get()
        gestion = self.entry_gestion.get()

        if name and factura and gestion:
            self.db.add_certificate(name, self.career_name, factura, gestion)
            self.entry_name.delete(0, "end")
            self.entry_factura.delete(0, "end")
            self.entry_gestion.delete(0, "end")
            self.refresh_data()

    def refresh_data(self):
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        records = self.db.get_pending_certificates(self.career_name)
        for r in records:
            # r: (id, nombre, factura, gestion, fecha)
            self.tree.insert("", "end", values=r)
        
        self.filter_list()

    def filter_list(self, *args):
        query = self.search_var.get().lower()
        # This is a basic client-side filter for now since we just fetched all pending
        # If dataset grows, move filter to DB query
        
        # We need to reload all to filter correctly if we are typing backspace
        # A bit inefficient to fetch from DB every keystroke, so let's just 
        # rebuild from DB if query is empty, or filter current items?
        # Simpler: just reload from DB if query is empty, else filter what we have? 
        # No, "get_children" only gives us what's there. 
        # Easiest: Reload all, then detach those that don't match.
        
        # Let's just re-fetch all for simplicity in this prototype phase
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        records = self.db.get_pending_certificates(self.career_name)
        for r in records:
            if query in r[1].lower(): # r[1] is name
                self.tree.insert("", "end", values=r)

    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.btn_deliver.configure(state="normal", fg_color=self.theme_color)
        else:
            self.btn_deliver.configure(state="disabled", fg_color="gray")

    def deliver_certificate(self):
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        # item['values'] = [ID, Name, ...]
        cert_id = item['values'][0]
        name = item['values'][1]

        # Confirm Dialog
        if tk.messagebox.askyesno("Conferma", f"Confermare consegna per {name}?"):
             self.db.mark_as_delivered(cert_id)
             self.refresh_data()
             self.btn_deliver.configure(state="disabled", fg_color="gray")
