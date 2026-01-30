import customtkinter as ctk
from utils.date_util import DateUtil

class DeliveryDialog(ctk.CTkToplevel):
    def __init__(self, master, student_name, theme_color, callback):
        super().__init__(master)
        
        self.title("Conferma Consegna")
        self.geometry("400x300")
        self.callback = callback
        
        # Make it modal
        self.lift()
        self.attributes("-topmost", True)
        self.grab_set()
        
        # Center the window
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() // 2) - (400 // 2)
        y = master.winfo_y() + (master.winfo_height() // 2) - (300 // 2)
        self.geometry(f"+{x}+{y}")

        self.grid_columnconfigure(0, weight=1)
        
        # Title
        self.label = ctk.CTkLabel(self, text="Conferma Consegna", font=("Roboto", 20, "bold"), text_color=theme_color)
        self.label.pack(pady=(20, 10))
        
        # Student Info
        self.info_label = ctk.CTkLabel(self, text=f"Studente: {student_name}", font=("Roboto", 14))
        self.info_label.pack(pady=5)
        
        # Date Input
        ctk.CTkLabel(self, text="Data di Consegna (GG/MM/AAAA):", font=("Roboto", 12)).pack(pady=(15, 0))
        
        self.date_entry = ctk.CTkEntry(self, width=200, justify="center")
        self.date_entry.insert(0, DateUtil.get_current_date_italy())
        self.date_entry.pack(pady=10)
        
        # Buttons Frame
        self.buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.buttons_frame.pack(pady=20, fill="x", padx=40)
        self.buttons_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.btn_cancel = ctk.CTkButton(self.buttons_frame, text="Annulla", fg_color="gray", command=self.destroy)
        self.btn_cancel.grid(row=0, column=0, padx=5)
        
        self.btn_confirm = ctk.CTkButton(self.buttons_frame, text="Conferma", fg_color=theme_color, command=self.confirm)
        self.btn_confirm.grid(row=0, column=1, padx=5)

    def confirm(self):
        entered_date = self.date_entry.get()
        db_date = DateUtil.parse_to_db_format(entered_date)
        
        if db_date:
            self.callback(db_date)
            self.destroy()
        else:
            from tkinter import messagebox
            messagebox.showerror("Errore", "Formato data non valido. Usa GG/MM/AAAA")
