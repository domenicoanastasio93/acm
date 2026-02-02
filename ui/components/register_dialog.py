import customtkinter as ctk
from tkinter import messagebox
from ui.components.multi_select import MultiSelectDropdown

class RegisterDialog(ctk.CTkToplevel):
    def __init__(self, master, available_gestioni, theme_color, on_confirm):
        super().__init__(master)
        self.title("Nuevo Registro")
        self.geometry("400x550")
        self.theme_color = theme_color
        self.on_confirm = on_confirm
        self.available_gestioni = available_gestioni

        self.resizable(False, False)
        self.geometry("800x550")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure((0, 1), weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=0) # Button row

        # Left Column: Inputs
        self.left_col = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.left_col.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
        self.left_col.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.left_col, text="Datos del Estudiante", font=("Roboto", 20, "bold")).pack(pady=(0, 20))

        self.entry_numero = ctk.CTkEntry(self.left_col, placeholder_text="N. (Opcional)", height=40)
        self.entry_numero.pack(pady=10, fill="x")

        self.entry_name = ctk.CTkEntry(self.left_col, placeholder_text="Nombre Estudiante *", height=40)
        self.entry_name.pack(pady=10, fill="x")

        self.entry_factura = ctk.CTkEntry(self.left_col, placeholder_text="Número Factura", height=40)
        self.entry_factura.pack(pady=10, fill="x")

        self.entry_notas = ctk.CTkEntry(self.left_col, placeholder_text="Note (Opcional)", height=40)
        self.entry_notas.pack(pady=10, fill="x")

        # Right Column: Gestiones
        self.right_col = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.right_col.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        self.right_col.grid_columnconfigure(0, weight=1)
        self.right_col.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.right_col, text="Gestiones:", font=("Roboto", 16, "bold")).grid(row=0, column=0, pady=(0, 10), sticky="w")
        self.entry_gestion = MultiSelectDropdown(self.right_col, values=self.available_gestioni)
        self.entry_gestion.grid(row=1, column=0, sticky="nsew")

        # Bottom Row: Save Button
        self.btn_save = ctk.CTkButton(self.main_frame, text="Registrar Estudiante", 
                                      fg_color=self.theme_color, 
                                      hover_color="#219150" if self.theme_color == "#27ae60" else None, 
                                      width=300, height=50, font=("Roboto", 18, "bold"), 
                                      command=self.confirm)
        self.btn_save.grid(row=1, column=0, columnspan=2, pady=20)

    def confirm(self):
        numero = self.entry_numero.get()
        name = self.entry_name.get()
        factura = self.entry_factura.get()
        notas = self.entry_notas.get()
        gestion_str = self.entry_gestion.get()

        if name:
            self.on_confirm(numero, name, factura, gestion_str, notas)
            self.destroy()
        else:
            messagebox.showwarning("Atención", "El nombre del estudiante è obligatorio.")
