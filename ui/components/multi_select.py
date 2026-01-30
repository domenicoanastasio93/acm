import customtkinter as ctk

class MultiSelectDropdown(ctk.CTkFrame):
    def __init__(self, master, values, placeholder="Seleccionar Gestiones", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.values = values
        self.placeholder = placeholder
        self.selections = dict.fromkeys(self.values, 0) # val: quantity
        
        # Header showing summary (non-clickable, non-hoverable)
        self.button = ctk.CTkButton(self, text=self.placeholder, 
                                    fg_color="#3B3B3B", hover=False,
                                    height=35, font=("Roboto", 13, "bold"))
        self.button.pack(fill="x")
        
        # Scrollable frame for the list of items with counters
        # Always visible
        self.dropdown_frame = ctk.CTkScrollableFrame(self, height=250, fg_color="#2B2B2B",
                                                     border_width=1, border_color="#444")
        self.dropdown_frame.pack(fill="x", pady=(5, 0))
        self.is_open = True
        
        self.rows = []
        for val in self.values:
            row = ctk.CTkFrame(self.dropdown_frame, fg_color="transparent")
            row.pack(fill="x", padx=5, pady=4)
            
            lbl = ctk.CTkLabel(row, text=val, font=("Roboto", 13), anchor="w")
            lbl.pack(side="left", padx=(10, 5), expand=True, fill="x")
            
            # Counter Container
            counter_frame = ctk.CTkFrame(row, fg_color="#1E1E1E", corner_radius=6)
            counter_frame.pack(side="right", padx=10)
            
            minus_btn = ctk.CTkButton(counter_frame, text="-", width=28, height=28, 
                                      fg_color="transparent", hover_color="#333",
                                      font=("Roboto", 16, "bold"),
                                      command=lambda v=val: self.change_qty(v, -1))
            minus_btn.pack(side="left")
            
            qty_lbl = ctk.CTkLabel(counter_frame, text="0", width=30, font=("Roboto", 12, "bold"))
            qty_lbl.pack(side="left")
            
            plus_btn = ctk.CTkButton(counter_frame, text="+", width=28, height=28,
                                     fg_color="transparent", hover_color="#333",
                                     font=("Roboto", 16, "bold"),
                                     command=lambda v=val: self.change_qty(v, 1))
            plus_btn.pack(side="left")
            
            self.rows.append({"val": val, "qty_lbl": qty_lbl})
            
    def change_qty(self, val, delta):
        new_qty = max(0, self.selections[val] + delta)
        self.selections[val] = new_qty
        for item in self.rows:
            if item["val"] == val:
                item["qty_lbl"].configure(text=str(new_qty))
        self.update_button_text()
            
    def toggle_dropdown(self):
        # Always open, so toggle is disabled
        pass
            
    def update_button_text(self):
        selected_summaries = []
        for val, qty in self.selections.items():
            if qty > 0:
                if qty == 1:
                    selected_summaries.append(val)
                else:
                    selected_summaries.append(f"{val} (X{qty})")
                    
        if not selected_summaries:
            self.button.configure(text=self.placeholder)
        else:
            text = ", ".join(selected_summaries)
            if len(text) > 30:
                total_qty = sum(self.selections.values())
                text = f"{total_qty} Gestiones seleccionadas"
            self.button.configure(text=text)
            
    def get(self):
        # Format for DB: space separated, with (Xn) for quantities > 1
        result_parts = []
        for val, qty in self.selections.items():
            if qty > 0:
                if qty == 1:
                    result_parts.append(val)
                else:
                    result_parts.append(f"{val} (X{qty})")
        return " ".join(result_parts)
        
    def delete(self, start, end):
        # Reset all quantities (Compatibility with CTkEntry.delete)
        for val in self.selections:
            self.selections[val] = 0
        for item in self.rows:
            item["qty_lbl"].configure(text="0")
        self.update_button_text()
