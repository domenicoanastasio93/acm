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
        
        # Scrollable frame for the list of items
        self.dropdown_frame = ctk.CTkScrollableFrame(self, height=250, fg_color="#2B2B2B",
                                                     border_width=1, border_color="#444")
        self.dropdown_frame.pack(fill="x", pady=(5, 0))
        
        self.year_sections = {} # {year_suffix: {'frame': scrollable_frame, 'content': list_frame, 'is_open': bool, 'btn': button}}
        self.rows = []
        
        self._initialize_sections()

    def _initialize_sections(self):
        # Group values by year
        grouped = {}
        for val in self.values:
            if "-" in val:
                year_suffix = val.split("-")[-1]
                if year_suffix not in grouped:
                    grouped[year_suffix] = []
                grouped[year_suffix].append(val)
        
        # Create sections in the order they appear in self.values (already reversed)
        for year_suffix, vals in grouped.items():
            full_year = f"20{year_suffix}"
            
            # Year Toggle Button
            btn = ctk.CTkButton(self.dropdown_frame, text=f"▶ {full_year}", 
                                anchor="w", fg_color="#3D3D3D", hover_color="#4D4D4D",
                                height=30, font=("Roboto", 13, "bold"),
                                command=lambda y=year_suffix: self.toggle_section(y))
            btn.pack(fill="x", padx=5, pady=(5, 2))
            
            # Container for the year's items (not packed initially)
            content_frame = ctk.CTkFrame(self.dropdown_frame, fg_color="transparent")
            
            self.year_sections[year_suffix] = {
                'btn': btn,
                'content': content_frame,
                'is_open': False,
                'year_text': full_year
            }
            
            for v in vals:
                self._create_row(content_frame, v)

    def _create_row(self, parent, val):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=5, pady=2)
        
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

    def toggle_section(self, year_suffix):
        section = self.year_sections[year_suffix]
        if section['is_open']:
            section['content'].pack_forget()
            section['btn'].configure(text=f"▶ {section['year_text']}")
            section['is_open'] = False
        else:
            # To maintain order, we would need to complexify, 
            # but since they ARE the only things in dropdown_frame, 
            # we can just pack it again. Actually, pack_forget removes it from layout.
            # A better way is to always have it packed but hide/show.
            # But in tkinter, pack_forget is standard. 
            # To keep order, we'll re-pack everything (simple enough here)
            section['is_open'] = True
            section['btn'].configure(text=f"▼ {section['year_text']}")
            self._repack_all()

    def _repack_all(self):
        # This ensures the order is preserved when a section is re-opened
        for y_suffix in self.year_sections: # Dictionary iterates in insertion order (Py 3.7+)
            section = self.year_sections[y_suffix]
            section['btn'].pack_forget()
            section['content'].pack_forget()
            
            section['btn'].pack(fill="x", padx=5, pady=(5, 2))
            if section['is_open']:
                section['content'].pack(fill="x", padx=5)

    def change_qty(self, val, delta):
        new_qty = max(0, self.selections[val] + delta)
        self.selections[val] = new_qty
        for item in self.rows:
            if item["val"] == val:
                item["qty_lbl"].configure(text=str(new_qty))
        self.update_button_text()

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
        result_parts = []
        for val, qty in self.selections.items():
            if qty > 0:
                if qty == 1:
                    result_parts.append(val)
                else:
                    result_parts.append(f"{val} (X{qty})")
        return " ".join(result_parts)

    def get_selected_items(self):
        items = []
        for val, qty in self.selections.items():
            for _ in range(qty):
                items.append(val)
        return items
        
    def delete(self, start, end):
        for val in self.selections:
            self.selections[val] = 0
        for item in self.rows:
            item["qty_lbl"].configure(text="0")
        self.update_button_text()
