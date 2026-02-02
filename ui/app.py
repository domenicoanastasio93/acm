import customtkinter as ctk
from ui.views.dashboard import Dashboard
from ui.views.career_view import CareerView

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ACM - Academic Certificate Manager")
        self.geometry("1000x700")
        
        # Set default theme
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        self.show_dashboard()

    def show_dashboard(self):
        self.clear_container()
        dashboard = Dashboard(self.container, on_navigate=self.show_career_view)
        dashboard.pack(fill="both", expand=True)

    def show_career_view(self, career_name, theme_color):
        self.clear_container()
        view = CareerView(self.container, career_name, theme_color, back_callback=self.show_dashboard)
        view.pack(fill="both", expand=True)

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def start(self):
        self.mainloop()
