import customtkinter as ctk
from utils.constants import CAREER_THEMES

class Dashboard(ctk.CTkFrame):
    def __init__(self, master, on_navigate):
        super().__init__(master)
        self.on_navigate = on_navigate

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        # Create buttons
        careers = list(CAREER_THEMES.keys())
        
        # Grid layout 2x2
        # 0: Medicina, 1: Enfermeria
        # 2: Instrumentacion, 3: Fonoaudiologia
        
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        
        for i, career in enumerate(careers):
            row, col = positions[i]
            color = CAREER_THEMES[career]
            
            btn = ctk.CTkButton(
                self, 
                text=career, 
                fg_color=color, 
                font=("Roboto", 24, "bold"),
                hover_color=self._adjust_color(color),
                command=lambda c=career, col=color: self.on_navigate(c, col)
            )
            # Make them big
            btn.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")

    def _adjust_color(self, hex_color):
        # Simply return a slightly darker or lighter version for hover if needed
        # For now, let CTK handle it or simple return the same
        return hex_color
