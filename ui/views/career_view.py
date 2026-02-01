import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from database.db_manager import DatabaseManager
from utils.excel_util import get_unique_gestioni
from ui.components.multi_select import MultiSelectDropdown
from ui.components.delivery_dialog import DeliveryDialog
from utils.date_util import DateUtil


class CareerView(ctk.CTkFrame):
    def __init__(self, master, career_name, theme_color, back_callback):
        super().__init__(master)
        self.career_name = career_name
        self.theme_color = theme_color
        self.back_callback = back_callback
        self.db = DatabaseManager()
        self.available_gestioni = get_unique_gestioni()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Content area

        # --- Header ---
        self.header = ctk.CTkFrame(self, fg_color=self.theme_color, height=60, corner_radius=0)
        self.header.grid(row=0, column=0, sticky="ew")
        
        self.back_btn = ctk.CTkButton(self.header, text="← Menú", width=80, fg_color="white", text_color="black", hover_color="#eee", command=self.back_callback)
        self.back_btn.pack(side="left", padx=20, pady=10)

        self.title_label = ctk.CTkLabel(self.header, text=f"Gestión {self.career_name}", font=("Roboto", 24, "bold"), text_color="white")
        self.title_label.pack(side="left", padx=20)

        # --- Main Content Area (Split: Left Form, Right List) ---
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.content.grid_columnconfigure(1, weight=1) # List area expands

        # --- Left: Input Form ---
        self.form_frame = ctk.CTkFrame(self.content, width=300)
        self.form_frame.grid(row=0, column=0, sticky="ns", padx=(0, 20))
        
        ctk.CTkLabel(self.form_frame, text="Nuevo Registro", font=("Roboto", 16, "bold")).pack(pady=10)
        
        self.entry_numero = ctk.CTkEntry(self.form_frame, placeholder_text="N.")
        self.entry_numero.pack(pady=10, padx=20, fill="x")

        self.entry_name = ctk.CTkEntry(self.form_frame, placeholder_text="Nombre Estudiante")
        self.entry_name.pack(pady=10, padx=20, fill="x")

        self.entry_factura = ctk.CTkEntry(self.form_frame, placeholder_text="Número Factura")
        self.entry_factura.pack(pady=10, padx=20, fill="x")

        self.entry_gestion = MultiSelectDropdown(self.form_frame, values=self.available_gestioni)
        self.entry_gestion.pack(pady=10, padx=20, fill="x")

        self.btn_save = ctk.CTkButton(self.form_frame, text="Registrar", fg_color=self.theme_color, command=self.add_record)
        self.btn_save.pack(pady=20, padx=20, fill="x")

        # --- Right: Pending List ---
        self.list_frame = ctk.CTkFrame(self.content)
        self.list_frame.grid(row=0, column=1, sticky="nsew")
        self.list_frame.grid_rowconfigure(1, weight=1)
        self.list_frame.grid_columnconfigure(0, weight=1)

        # Search Bar & Count
        self.search_header = ctk.CTkFrame(self.list_frame, fg_color="transparent")
        self.search_header.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.search_header.grid_columnconfigure(0, weight=1)

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.filter_list)
        self.search_entry = ctk.CTkEntry(self.search_header, placeholder_text="Buscar por nombre...", textvariable=self.search_var)
        self.search_entry.grid(row=0, column=0, sticky="ew")

        self.count_label = ctk.CTkLabel(self.search_header, text="Total: 0", font=("Roboto", 12, "bold"))
        self.count_label.grid(row=0, column=1, padx=(10, 0))

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
        # We keep ID as the first column but label it "N." (or show the manual number there)
        # Actually, let's keep ID in a hidden column or at the end, and show "N." (manual) as the first.
        columns = ("db_id", "N.", "Nombre", "Factura", "Gestión", "Fecha")
        self.tree = ttk.Treeview(self.list_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("db_id", text="ID")
        self.tree.heading("N.", text="N.")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Factura", text="Factura")
        self.tree.heading("Gestión", text="Gestión")
        self.tree.heading("Fecha", text="Fecha de Inserción")
        
        self.tree.column("db_id", width=0, stretch=False) # Hide db_id
        self.tree.column("N.", width=50)
        self.tree.column("Nombre", width=150)
        self.tree.column("Factura", width=80)
        self.tree.column("Gestión", width=80)
        self.tree.column("Fecha", width=150)


        self.tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # Scrollbar for tree
        scrollbar = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky="ns", pady=(0, 10))

        # Action Buttons
        self.actions_frame = ctk.CTkFrame(self.list_frame, fg_color="transparent")
        self.actions_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.actions_frame.grid_columnconfigure((0, 1), weight=1)

        self.btn_deliver = ctk.CTkButton(self.actions_frame, text="Entregar Certificado", fg_color="gray", state="disabled", command=self.deliver_certificate)
        self.btn_deliver.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.btn_delete = ctk.CTkButton(self.actions_frame, text="Eliminar Estudiante", fg_color="gray", state="disabled", hover_color="#c0392b", command=self.delete_record)
        self.btn_delete.grid(row=0, column=1, padx=(5, 0), sticky="ew")

        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Context menu (Right click)
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Entregar Certificado", command=self.deliver_certificate)
        self.menu.add_command(label="Eliminar Estudiante", command=self.delete_record)
        self.tree.bind("<Button-2>" if self.tk.call('tk', 'windowingsystem') == 'aqua' else "<Button-3>", self.show_menu)

        self.refresh_data()

    def add_record(self):
        numero = self.entry_numero.get()
        name = self.entry_name.get()
        factura = self.entry_factura.get()
        gestiones = self.entry_gestion.get_selected_items()

        if name: # Solo il nome è obbligatorio
            if not gestiones:
                gestiones = [""]

            for gestion in gestiones:
                self.db.add_certificate(numero, name, self.career_name, factura, gestion)

            self.entry_numero.delete(0, "end")
            self.entry_name.delete(0, "end")
            self.entry_factura.delete(0, "end")
            self.entry_gestion.delete(0, "end")
            self.refresh_data()
        else:
            messagebox.showwarning("Atención", "El nombre del estudiante es obligatorio.")

    def refresh_data(self):
        # We just call filter_list as it already handles clearing, fetching and displaying
        self.filter_list()

    def filter_list(self, *args):
        query = self.search_var.get().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        records = self.db.get_pending_certificates(self.career_name)
        count = 0
        for r in records:
            # r: (id, numero, nombre, factura, gestion, fecha)
            if query in r[2].lower(): # r[2] is name
                count += 1
                formatted_record = list(r)
                formatted_record[5] = DateUtil.format_datetime(r[5])
                self.tree.insert("", "end", values=formatted_record)
        
        self.count_label.configure(text=f"Total: {count}")


    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.btn_deliver.configure(state="normal", fg_color=self.theme_color)
            self.btn_delete.configure(state="normal", fg_color="#e74c3c")
        else:
            self.btn_deliver.configure(state="disabled", fg_color="gray")
            self.btn_delete.configure(state="disabled", fg_color="gray")

    def show_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.menu.post(event.x_root, event.y_root)

    def deliver_certificate(self):
        selected = self.tree.selection()
        if not selected: return
        
        item_values = self.tree.item(selected[0])['values']
        cert_id, name = item_values[0], item_values[2] # 0 is db_id, 2 is name

        def on_confirm(custom_date):
            self.db.mark_as_delivered(cert_id, custom_date)
            self.refresh_data()
            self.btn_deliver.configure(state="disabled", fg_color="gray")
            self.btn_delete.configure(state="disabled", fg_color="gray")

        DeliveryDialog(self.master, name, self.theme_color, on_confirm)

    def delete_record(self):
        selected = self.tree.selection()
        if not selected: return
        
        item_values = self.tree.item(selected[0])['values']
        cert_id, name = item_values[0], item_values[2] # 0 is db_id, 2 is name

        if messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de que desea eliminar a {name}?\nEsta operación es irreversible."):
             self.db.delete_certificate(cert_id)
             self.refresh_data()
             self.btn_deliver.configure(state="disabled", fg_color="gray")
             self.btn_delete.configure(state="disabled", fg_color="gray")
