import customtkinter as ctk
from tkinter import messagebox
from ui.components.multi_select import MultiSelectDropdown

class AddCertificatesDialog(ctk.CTkToplevel):
    def __init__(self, master, available_gestioni, theme_color, on_confirm):
        super().__init__(master)
        self.title("Añadir Certificados")
        self.theme_color = theme_color
        self.on_confirm = on_confirm
        self.available_gestioni = available_gestioni

        self.resizable(False, False)
        
        # Center the window
        self.update_idletasks()
        width = 400
        height = 500
        x = master.winfo_x() + (master.winfo_width() // 2) - (width // 2)
        y = master.winfo_y() + (master.winfo_height() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        # Modal setup
        self.lift()
        self.attributes("-topmost", True)
        self.after(10, self.grab_set)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=0)

        ctk.CTkLabel(self.main_frame, text="Seleccionar Certificados", font=("Roboto", 20, "bold")).grid(row=0, column=0, pady=(10, 20))

        # Gestiones MultiSelect
        self.entry_gestion = MultiSelectDropdown(self.main_frame, values=self.available_gestioni)
        self.entry_gestion.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))

        # Bottom Row: Save Button
        self.btn_save = ctk.CTkButton(self.main_frame, text="Añadir Certificados", 
                                      fg_color="#27ae60", 
                                      hover_color="#219150", 
                                      height=45, font=("Roboto", 16, "bold"), 
                                      command=self.confirm)
        self.btn_save.grid(row=2, column=0, pady=20, padx=20, sticky="ew")

    def confirm(self):
        selected_items = self.entry_gestion.get_selected_items()
        if selected_items:
            self.on_confirm(selected_items)
            self.destroy()
        else:
            messagebox.showwarning("Atención", "Debe seleccionar al menos un certificado.")
