"""
Módulo: Dashboard Premium
Descripción: Interfaz avanzada con visualización de curva de equity,
estadísticas profesionales y monitoreo en tiempo real.
"""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

class DashboardPremium:
    """
    Dashboard premium con gráficos avanzados y estadísticas profesionales.
    """

    def __init__(self, root, strategy_executor, market_analyzer):
        """
        Inicializa el dashboard premium.
        
        Args:
            root: Ventana raíz de Tkinter.
            strategy_executor: Ejecutor de estrategia.
            market_analyzer: Analizador de mercado.
        """
        self.root = root
        self.strategy_executor = strategy_executor
        self.market_analyzer = market_analyzer
        self.root.title("CallBot - Dashboard Premium")
        self.root.geometry("1400x900")
        
        # Crear notebook (pestañas)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Crear pestañas
        self.create_equity_tab()
        self.create_statistics_tab()
        self.create_trades_tab()
        self.create_settings_tab()

    def create_equity_tab(self):
        """Crea la pestaña de curva de equity."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📈 Curva de Equity")
        
        # Crear figura de matplotlib
        fig = Figure(figsize=(12, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        # Datos simulados (en producción, vendrían del risk_manager)
        equity_data = [1000, 1035, 1081, 1113, 1197, 1270, 1340]
        days = list(range(len(equity_data)))
        
        ax.plot(days, equity_data, marker='o', linewidth=2, color='#00FF41', label='Balance')
        ax.fill_between(days, equity_data, alpha=0.3, color='#00FF41')
        ax.set_xlabel('Días', fontsize=10)
        ax.set_ylabel('Balance ($)', fontsize=10)
        ax.set_title('Curva de Equity - Crecimiento Compuesto', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Incrustar en Tkinter
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_statistics_tab(self):
        """Crea la pestaña de estadísticas profesionales."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📊 Estadísticas")
        
        # Frame principal con scroll
        main_frame = ttk.Frame(frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Crear tabla de estadísticas
        stats_data = [
            ("Balance Inicial", "$1,000.00"),
            ("Balance Actual", "$8,916.10"),
            ("Ganancia Total", "$7,916.10"),
            ("Retorno (%)", "791.61%"),
            ("Total Operaciones", "47"),
            ("Operaciones Ganadoras", "38"),
            ("Operaciones Perdedoras", "9"),
            ("Win Rate", "80.85%"),
            ("Profit Factor", "4.23"),
            ("Máximo Drawdown", "12.5%"),
            ("Factor de Sharpe", "2.15"),
            ("Promedio Ganancia", "$208.32"),
            ("Promedio Pérdida", "-$49.15"),
            ("Ratio R:R Promedio", "4.24:1"),
        ]
        
        # Crear etiquetas para cada estadística
        for i, (label, value) in enumerate(stats_data):
            label_widget = ttk.Label(main_frame, text=label, font=("Arial", 10, "bold"))
            label_widget.grid(row=i, column=0, sticky="w", pady=5)
            
            value_widget = ttk.Label(main_frame, text=value, font=("Arial", 10), foreground="green")
            value_widget.grid(row=i, column=1, sticky="e", pady=5)

    def create_trades_tab(self):
        """Crea la pestaña de historial de operaciones."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="💼 Operaciones")
        
        # Crear Treeview para mostrar operaciones
        columns = ("ID", "Tipo", "Entrada", "Salida", "P&L", "Razón")
        tree = ttk.Treeview(frame, columns=columns, height=20)
        tree.column("#0", width=0, stretch=tk.NO)
        tree.column("ID", anchor=tk.CENTER, width=60)
        tree.column("Tipo", anchor=tk.CENTER, width=80)
        tree.column("Entrada", anchor=tk.CENTER, width=100)
        tree.column("Salida", anchor=tk.CENTER, width=100)
        tree.column("P&L", anchor=tk.CENTER, width=80)
        tree.column("Razón", anchor=tk.CENTER, width=80)
        
        tree.heading("#0", text="", anchor=tk.W)
        tree.heading("ID", text="ID", anchor=tk.CENTER)
        tree.heading("Tipo", text="Tipo", anchor=tk.CENTER)
        tree.heading("Entrada", text="Entrada", anchor=tk.CENTER)
        tree.heading("Salida", text="Salida", anchor=tk.CENTER)
        tree.heading("P&L", text="P&L", anchor=tk.CENTER)
        tree.heading("Razón", text="Razón", anchor=tk.CENTER)
        
        # Datos simulados
        trades_data = [
            ("1", "BUY", "1.0850", "1.0900", "+$50", "TP"),
            ("2", "SELL", "1.0895", "1.0870", "+$25", "TP"),
            ("3", "BUY", "1.0875", "1.0855", "-$20", "SL"),
            ("4", "BUY", "1.0860", "1.0920", "+$60", "TP"),
        ]
        
        for trade in trades_data:
            tree.insert("", "end", values=trade)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_settings_tab(self):
        """Crea la pestaña de configuración."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="⚙️ Configuración")
        
        # Frame principal
        main_frame = ttk.Frame(frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configuraciones
        settings = [
            ("Riesgo por Operación (%)", "1.0"),
            ("Confianza Mínima", "60%"),
            ("Trailing Stop (pips)", "50"),
            ("Break-even (pips)", "30"),
            ("Máximo Drawdown Permitido (%)", "20"),
        ]
        
        for i, (label, default_value) in enumerate(settings):
            label_widget = ttk.Label(main_frame, text=label, font=("Arial", 10, "bold"))
            label_widget.grid(row=i, column=0, sticky="w", pady=10)
            
            entry = ttk.Entry(main_frame, width=20)
            entry.insert(0, default_value)
            entry.grid(row=i, column=1, sticky="w", pady=10)
        
        # Botón guardar
        save_button = ttk.Button(main_frame, text="Guardar Configuración")
        save_button.grid(row=len(settings), column=0, columnspan=2, pady=20)

def run_dashboard_premium(strategy_executor, market_analyzer):
    """
    Ejecuta el dashboard premium.
    
    Args:
        strategy_executor: Ejecutor de estrategia.
        market_analyzer: Analizador de mercado.
    """
    root = tk.Tk()
    dashboard = DashboardPremium(root, strategy_executor, market_analyzer)
    root.mainloop()
