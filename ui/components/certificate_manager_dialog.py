import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from database.db_manager import DatabaseManager
from ui.components.delivery_dialog import DeliveryDialog
from utils.date_util import DateUtil

class CertificateManagerDialog(ctk.CTkToplevel):
    def __init__(self, master, student_id, student_name, theme_color, on_close_callback=None):
        super().__init__(master)
        self.student_id = student_id
        self.student_name = student_name
        self.theme_color = theme_color
        self.on_close_callback = on_close_callback
        self.db = DatabaseManager()
        
        self.title(f"Certificados - {self.student_name}")
        self.geometry("600x400")
        
        # Center the window
        self.update_idletasks()
        width = 600
        height = 400
        x = master.winfo_x() + (master.winfo_width() // 2) - (width // 2)
        y = master.winfo_y() + (master.winfo_height() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # Modal
        self.lift()
        self.attributes("-topmost", True)
        self.after(10, self.grab_set)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Content
        self.frame = ctk.CTkFrame(self, fg_color="transparent")
        self.frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        
        # Treeview
        style = ttk.Style()
        style.theme_use("default")
        
        row_height = 28
        header_font_size = 10
        body_font_size = 10
        
        style.configure("Cert.Treeview", 
                        background="#2b2b2b", 
                        foreground="white", 
                        fieldbackground="#2b2b2b", 
                        rowheight=row_height,
                        font=("Roboto", body_font_size))
        style.map("Cert.Treeview", background=[("selected", self.theme_color)])
        style.configure("Cert.Treeview.Heading", font=("Roboto", header_font_size, "bold"))
        
        columns = ("id", "nombre", "fecha_entrega")
        self.tree = ttk.Treeview(self.frame, columns=columns, show="headings", selectmode="browse", style="Cert.Treeview")
        
        self.tree.heading("nombre", text="Certificado")
        self.tree.heading("fecha_entrega", text="Fecha Entrega")
        
        self.tree.column("id", width=0, stretch=False) # Hidden ID
        self.tree.column("nombre", width=300)
        self.tree.column("fecha_entrega", width=200)
        
        self.tree.grid(row=0, column=0, sticky="nsew", pady=(0, 20))
        
        self.tree.tag_configure("delivered", foreground="#00E676")
        
        # Buttons Frame
        self.btn_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.btn_frame.grid(row=1, column=0, sticky="ew")
        
        self.btn_deliver = ctk.CTkButton(self.btn_frame, text="Entregar", state="disabled", fg_color="gray", command=self.deliver_item)
        self.btn_deliver.pack(side="left", padx=5, expand=True, fill="x")
        
        self.btn_add = ctk.CTkButton(self.btn_frame, text="+ Nuevo Certificado", fg_color="#27ae60", hover_color="#219150", command=self.add_item)
        self.btn_add.pack(side="left", padx=5, expand=True, fill="x")

        self.btn_delete = ctk.CTkButton(self.btn_frame, text="Eliminar", state="disabled", fg_color="gray", command=self.delete_item)
        self.btn_delete.pack(side="left", padx=5, expand=True, fill="x")
        
        # Hint label
        self.hint_label = ctk.CTkLabel(self.frame, text="* Doble clic en el nombre per editarlo", font=("Roboto", 10, "italic"), text_color="gray")
        self.hint_label.grid(row=2, column=0, sticky="w", pady=(5, 0))

        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.bind("<Double-1>", self.on_double_click)
        
        # Context menu
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Entregar/Anular", command=self.deliver_item)
        self.menu.add_command(label="Editar Nombre", command=self.rename_item)
        self.menu.add_command(label="Eliminar", command=self.delete_item)
        
        self.tree.bind("<Button-2>" if self.tk.call('tk', 'windowingsystem') == 'aqua' else "<Button-3>", self.show_menu)

        
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.refresh_list()
        
    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        items = self.db.get_certificate_items(self.student_id)
        # items: (id, item_name, estado, fecha_entrega)
        
        for item in items:
            item_id, item_name, estado, fecha_entrega = item
            date_fmt = DateUtil.format_datetime(fecha_entrega) if fecha_entrega else "Pendiente"
            
            tags = ("delivered",) if estado == 1 else ()
            self.tree.insert("", "end", values=(item_id, item_name, date_fmt), tags=tags)
            
    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            tags = self.tree.item(selected[0])['tags']
            is_delivered = "delivered" in tags
            
            if is_delivered:
                self.btn_deliver.configure(text="Anular Entrega", state="normal", fg_color="#f39c12", hover_color="#d3840e", command=self.undo_delivery)
            else:
                self.btn_deliver.configure(text="Entregar", state="normal", fg_color="#9512f3", hover_color="#7d0fca", command=self.deliver_item)
            
            self.btn_delete.configure(state="normal", fg_color="#e74c3c", hover_color="#c0392b")
        else:
            self.btn_deliver.configure(text="Entregar", state="disabled", fg_color="gray")
            self.btn_delete.configure(state="disabled", fg_color="gray")

    def deliver_item(self):
        selected = self.tree.selection()
        if not selected: return
        
        vals = self.tree.item(selected[0])['values']
        item_id = vals[0]
        item_name = vals[1]
        
        def on_confirm(date):
            self.db.mark_item_delivered(item_id, date)
            self.refresh_list()
            
        DeliveryDialog(self, f"{self.student_name} - {item_name}", self.theme_color, on_confirm)

    def undo_delivery(self):
        selected = self.tree.selection()
        if not selected: return
        
        vals = self.tree.item(selected[0])['values']
        item_id = vals[0]
        item_name = vals[1]
        
        if messagebox.askyesno("Confirmar", f"¿Anular entrega de {item_name}?"):
            self.db.undo_item_delivery(item_id)
            self.refresh_list()

    def delete_item(self):
        selected = self.tree.selection()
        if not selected: return
        
        vals = self.tree.item(selected[0])['values']
        item_id = vals[0]
        item_name = vals[1]
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar certificado {item_name}?"):
            self.db.delete_certificate_item(item_id)
            self.refresh_list()
            
    def add_item(self):
        dialog = ctk.CTkInputDialog(text="Ingrese el nombre del certificado (es. I-24):", title="Nuevo Certificado")
        # Center dialog relative to this window
        input_value = dialog.get_input()
        if input_value and input_value.strip():
            self.db.add_certificate_item(self.student_id, input_value.strip())
            self.refresh_list()

    def rename_item(self):
        selected = self.tree.selection()
        if not selected: return
        
        vals = self.tree.item(selected[0])['values']
        item_id = vals[0]
        old_name = vals[1]
        
        dialog = ctk.CTkInputDialog(text="Editar nombre del certificado:", title="Editar Nombre")
        # Pre-fill is not natively supported by CTkInputDialog easily without hacks, 
        # but let's assume it's acceptable for now or user can just type new one.
        new_name = dialog.get_input()
        if new_name and new_name.strip() and new_name.strip() != old_name:
            self.db.update_item_name(item_id, new_name.strip())
            self.refresh_list()

    def on_double_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            if column == "#2": # Nombre
                self.rename_item()

    def show_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.menu.post(event.x_root, event.y_root)

    def on_close(self):
        if self.on_close_callback:
            self.on_close_callback()
        self.destroy()
