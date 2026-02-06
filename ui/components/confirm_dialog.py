import customtkinter as ctk

class ConfirmDialog(ctk.CTkToplevel):
    def __init__(self, master, title, message, theme_color, on_confirm, on_cancel=None, show_cancel=True):
        super().__init__(master)
        
        self.title(title)
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        
        # Window size and positioning
        width = 400
        height = 200
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)

        # Center the window relative to master
        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() // 2) - (width // 2)
        y = master.winfo_rooty() + (master.winfo_height() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")
        
        # Modal setup
        self.lift()
        self.attributes("-topmost", True)
        self.grab_set()
        
        # UI Elements
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Message
        self.label = ctk.CTkLabel(self.main_frame, text=message, font=("Roboto", 14), wraplength=350)
        self.label.pack(pady=(10, 20), expand=True)
        
        # Buttons Frame
        self.btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.btn_frame.pack(side="bottom", fill="x")
        
        if show_cancel:
            self.btn_cancel = ctk.CTkButton(
                self.btn_frame, 
                text="Cancelar", 
                fg_color="gray", 
                hover_color="#555555",
                command=self.cancel
            )
            self.btn_cancel.pack(side="left", padx=10, expand=True)
        
        confirm_text = "Confirmar" if show_cancel else "OK"
        self.btn_confirm = ctk.CTkButton(
            self.btn_frame, 
            text=confirm_text, 
            fg_color="#e74c3c" if "Eliminar" in title else "#27ae60",
            hover_color="#c0392b" if "Eliminar" in title else "#219150",
            command=self.confirm
        )
        self.btn_confirm.pack(side="right" if show_cancel else "bottom", padx=10, expand=True)
        
        # Bind enter key to confirm
        self.bind("<Return>", lambda e: self.confirm())
        self.bind("<Escape>", lambda e: self.cancel())

    def confirm(self):
        self.grab_release()
        self.destroy()
        if self.on_confirm:
            self.on_confirm()

    def cancel(self):
        self.grab_release()
        self.destroy()
        if self.on_cancel:
            self.on_cancel()
