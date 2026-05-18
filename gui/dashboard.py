import customtkinter as ctk

class Dashboard(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Professional AI Trading Bot")
        self.geometry("1200x700")

        self.balance_label = ctk.CTkLabel(self, text="Balance: $0")
        self.balance_label.pack(pady=10)

        self.status_label = ctk.CTkLabel(self, text="Estado: Desconectado")
        self.status_label.pack(pady=10)

        self.start_button = ctk.CTkButton(self, text="Iniciar Bot")
        self.start_button.pack(pady=10)

if __name__ == "__main__":
    app = Dashboard()
    app.mainloop()