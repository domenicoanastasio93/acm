import customtkinter as ctk
from utils.date_util import DateUtil

class DeliveryDialog(ctk.CTkToplevel):
    def __init__(self, master, student_name, theme_color, callback):
        super().__init__(master)
        
        self.title("Confirmar Entrega")
        self.geometry("400x300")
        self.callback = callback
        
        self.resizable(False, False)

        # Center the window
        self.update_idletasks()
        width = 400
        height = 300
        x = master.winfo_x() + (master.winfo_width() // 2) - (width // 2)
        y = master.winfo_y() + (master.winfo_height() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # Safe modal setup for Windows
        self.lift()
        self.attributes("-topmost", True)
        self.after(10, self.grab_set)

        self.grid_columnconfigure(0, weight=1)
        
        # Title
        self.label = ctk.CTkLabel(self, text="Confirmar Entrega", font=("Roboto", 20, "bold"), text_color=theme_color)
        self.label.pack(pady=(20, 10))
        
        # Student Info
        self.info_label = ctk.CTkLabel(self, text=f"Estudiante: {student_name}", font=("Roboto", 14))
        self.info_label.pack(pady=5)
        
        # Date Input
        ctk.CTkLabel(self, text="Fecha de Entrega (DD/MM/AAAA):", font=("Roboto", 12)).pack(pady=(15, 0))
        
        self.date_entry = ctk.CTkEntry(self, width=200, justify="center")
        self.date_entry.insert(0, DateUtil.get_current_date_italy())
        self.date_entry.pack(pady=10)
        
        # Buttons Frame
        self.buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.buttons_frame.pack(pady=20, fill="x", padx=40)
        self.buttons_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.btn_cancel = ctk.CTkButton(self.buttons_frame, text="Anular", fg_color="gray", hover_color="#6d7370", command=self.destroy)
        self.btn_cancel.grid(row=0, column=0, padx=5)
        
        self.btn_confirm = ctk.CTkButton(self.buttons_frame, text="Confirmar", fg_color="#27ae60", hover_color="#219150", command=self.confirm)
        self.btn_confirm.grid(row=0, column=1, padx=5)

    def confirm(self):
        entered_date = self.date_entry.get()
        db_date = DateUtil.parse_to_db_format(entered_date)
        
        if db_date:
            self.callback(db_date)
            self.destroy()
        else:
            from tkinter import messagebox
            messagebox.showerror("Error", "Formato de fecha no válido. Use DD/MM/AAAA")
