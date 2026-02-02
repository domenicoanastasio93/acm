import customtkinter as ctk
import datetime
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

        # --- Copyright Label ---
        try:
            scaling_factor = ctk.ScalingTracker.get_widget_scaling(self)
        except Exception:
            scaling_factor = 1.0
            
        current_year = datetime.datetime.now().year
        copyright_text = f"© {current_year} Domenico"
        
        # Add a footer row with weight 0 so it doesn't expand, but buttons do
        self.grid_rowconfigure(2, weight=0)
        self.copyright_label = ctk.CTkLabel(self, text=copyright_text, 
                                            font=("Roboto", int(10 * scaling_factor)), 
                                            text_color="gray")
        self.copyright_label.grid(row=2, column=1, sticky="se", padx=15, pady=(0, 10))

    def _adjust_color(self, hex_color):
        # Simply return a slightly darker or lighter version for hover if needed
        # For now, let CTK handle it or simple return the same
        return hex_color
