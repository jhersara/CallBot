"""
Módulo: Trading Dashboard
Descripción: Dashboard de monitoreo en tiempo real del bot de trading.
Muestra estadísticas, operaciones abiertas, gráficos de rendimiento y control del bot.
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime
import json


class TradingDashboard(ctk.CTk):
    """
    Dashboard interactivo para monitoreo del bot de trading.
    
    Características:
    - Visualización de balance y retorno
    - Estadísticas de trading
    - Operaciones abiertas
    - Gráficos de rendimiento
    - Control del bot (iniciar/detener)
    """

    def __init__(self, strategy_executor, market_analyzer):
        """
        Inicializa el dashboard.
        
        Args:
            strategy_executor (StrategyExecutor): Ejecutor de estrategia
            market_analyzer (MarketAnalyzer): Analizador de mercado
        """
        super().__init__()
        
        self.strategy_executor = strategy_executor
        self.market_analyzer = market_analyzer
        self.risk_manager = strategy_executor.risk_manager
        
        self.title("🤖 Trading Bot Dashboard - CallBot")
        self.geometry("1400x900")
        
        # Estado del bot
        self.bot_running = False
        
        # Crear interfaz
        self._create_widgets()
        
        # Actualizar datos cada segundo
        self.update_dashboard()

    def _create_widgets(self):
        """Crea los widgets del dashboard."""
        
        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # ========== HEADER ==========
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill="x", pady=(0, 10))
        
        title_label = ctk.CTkLabel(header_frame, text="🤖 Trading Bot Dashboard", 
                                   font=("Arial", 24, "bold"))
        title_label.pack(side="left")
        
        # Botones de control
        control_frame = ctk.CTkFrame(header_frame)
        control_frame.pack(side="right")
        
        self.start_button = ctk.CTkButton(control_frame, text="▶ Iniciar Bot", 
                                          command=self.start_bot, width=120)
        self.start_button.pack(side="left", padx=5)
        
        self.stop_button = ctk.CTkButton(control_frame, text="⏹ Detener Bot", 
                                         command=self.stop_bot, width=120, state="disabled")
        self.stop_button.pack(side="left", padx=5)
        
        # ========== NOTEBOOK (Pestañas) ==========
        notebook = ctk.CTkTabview(main_frame)
        notebook.pack(fill="both", expand=True)
        
        # Pestaña 1: Resumen
        summary_frame = notebook.add("📊 Resumen")
        self._create_summary_tab(summary_frame)
        
        # Pestaña 2: Operaciones Abiertas
        trades_frame = notebook.add("📈 Operaciones Abiertas")
        self._create_trades_tab(trades_frame)
        
        # Pestaña 3: Historial
        history_frame = notebook.add("📋 Historial")
        self._create_history_tab(history_frame)
        
        # Pestaña 4: Configuración
        config_frame = notebook.add("⚙️ Configuración")
        self._create_config_tab(config_frame)

    def _create_summary_tab(self, parent):
        """Crea la pestaña de resumen."""
        
        # Frame superior: Estadísticas principales
        stats_frame = ctk.CTkFrame(parent)
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        stats_label = ctk.CTkLabel(stats_frame, text="Estadísticas Principales", 
                                   font=("Arial", 14, "bold"))
        stats_label.pack()
        
        # Grid de estadísticas
        stats_data = [
            ("Balance Inicial:", "initial_balance", "USD"),
            ("Balance Actual:", "current_balance", "USD"),
            ("Ganancia Total:", "total_return", "USD"),
            ("Retorno %:", "return_percent", "%"),
            ("Total Operaciones:", "total_trades", ""),
            ("Operaciones Ganadoras:", "winning_trades", ""),
            ("Operaciones Perdedoras:", "losing_trades", ""),
            ("Tasa de Ganancia:", "win_rate", "%"),
            ("Factor de Ganancia:", "profit_factor", ""),
            ("Ganancia Promedio:", "average_profit_per_trade", "USD"),
        ]
        
        self.stats_labels = {}
        
        grid_frame = ctk.CTkFrame(stats_frame)
        grid_frame.pack(fill="x", padx=20, pady=10)
        
        for idx, (label, key, unit) in enumerate(stats_data):
            row = idx // 2
            col = idx % 2
            
            label_widget = ctk.CTkLabel(grid_frame, text=label, font=("Arial", 10, "bold"))
            label_widget.grid(row=row, column=col*2, sticky="w", padx=5, pady=5)
            
            value_widget = ctk.CTkLabel(grid_frame, text="0 " + unit, 
                                       font=("Arial", 10), text_color="green")
            value_widget.grid(row=row, column=col*2+1, sticky="w", padx=5, pady=5)
            
            self.stats_labels[key] = (value_widget, unit)
        
        # Frame inferior: Sentimiento del mercado
        sentiment_frame = ctk.CTkFrame(parent)
        sentiment_frame.pack(fill="x", padx=10, pady=10)
        
        sentiment_title = ctk.CTkLabel(sentiment_frame, text="Sentimiento del Mercado", 
                                       font=("Arial", 14, "bold"))
        sentiment_title.pack()
        
        self.sentiment_label = ctk.CTkLabel(sentiment_frame, text="NEUTRAL", 
                                           font=("Arial", 16, "bold"), text_color="blue")
        self.sentiment_label.pack(pady=10)
        
        # Frame: Información de señales
        signals_frame = ctk.CTkFrame(parent)
        signals_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        signals_title = ctk.CTkLabel(signals_frame, text="Señales Actuales", 
                                    font=("Arial", 14, "bold"))
        signals_title.pack()
        
        self.signals_text = ctk.CTkTextbox(signals_frame, height=200)
        self.signals_text.pack(fill="both", expand=True, padx=5, pady=5)

    def _create_trades_tab(self, parent):
        """Crea la pestaña de operaciones abiertas."""
        
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        title = ctk.CTkLabel(frame, text="Operaciones Abiertas", font=("Arial", 14, "bold"))
        title.pack()
        
        # Crear tabla
        columns = ("ID", "Símbolo", "Acción", "Entrada", "Stop Loss", "Take Profit", 
                  "Lote", "Confianza", "Tiempo")
        
        self.trades_tree = ttk.Treeview(frame, columns=columns, height=15)
        self.trades_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Definir columnas
        self.trades_tree.column("#0", width=0, stretch=False)
        self.trades_tree.column("ID", anchor="center", width=80)
        self.trades_tree.column("Símbolo", anchor="center", width=80)
        self.trades_tree.column("Acción", anchor="center", width=60)
        self.trades_tree.column("Entrada", anchor="center", width=90)
        self.trades_tree.column("Stop Loss", anchor="center", width=90)
        self.trades_tree.column("Take Profit", anchor="center", width=90)
        self.trades_tree.column("Lote", anchor="center", width=60)
        self.trades_tree.column("Confianza", anchor="center", width=80)
        self.trades_tree.column("Tiempo", anchor="center", width=100)
        
        # Definir encabezados
        self.trades_tree.heading("#0", text="")
        self.trades_tree.heading("ID", text="ID")
        self.trades_tree.heading("Símbolo", text="Símbolo")
        self.trades_tree.heading("Acción", text="Acción")
        self.trades_tree.heading("Entrada", text="Entrada")
        self.trades_tree.heading("Stop Loss", text="Stop Loss")
        self.trades_tree.heading("Take Profit", text="Take Profit")
        self.trades_tree.heading("Lote", text="Lote")
        self.trades_tree.heading("Confianza", text="Confianza")
        self.trades_tree.heading("Tiempo", text="Tiempo")

    def _create_history_tab(self, parent):
        """Crea la pestaña de historial."""
        
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        title = ctk.CTkLabel(frame, text="Historial de Operaciones", font=("Arial", 14, "bold"))
        title.pack()
        
        # Crear tabla
        columns = ("Fecha", "Símbolo", "Acción", "Entrada", "Salida", "Lote", 
                  "Ganancia/Pérdida", "Duración")
        
        self.history_tree = ttk.Treeview(frame, columns=columns, height=15)
        self.history_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Definir columnas
        self.history_tree.column("#0", width=0, stretch=False)
        self.history_tree.column("Fecha", anchor="center", width=150)
        self.history_tree.column("Símbolo", anchor="center", width=80)
        self.history_tree.column("Acción", anchor="center", width=60)
        self.history_tree.column("Entrada", anchor="center", width=90)
        self.history_tree.column("Salida", anchor="center", width=90)
        self.history_tree.column("Lote", anchor="center", width=60)
        self.history_tree.column("Ganancia/Pérdida", anchor="center", width=120)
        self.history_tree.column("Duración", anchor="center", width=100)
        
        # Definir encabezados
        self.history_tree.heading("#0", text="")
        self.history_tree.heading("Fecha", text="Fecha")
        self.history_tree.heading("Símbolo", text="Símbolo")
        self.history_tree.heading("Acción", text="Acción")
        self.history_tree.heading("Entrada", text="Entrada")
        self.history_tree.heading("Salida", text="Salida")
        self.history_tree.heading("Lote", text="Lote")
        self.history_tree.heading("Ganancia/Pérdida", text="Ganancia/Pérdida")
        self.history_tree.heading("Duración", text="Duración")

    def _create_config_tab(self, parent):
        """Crea la pestaña de configuración."""
        
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        title = ctk.CTkLabel(frame, text="Configuración del Bot", font=("Arial", 14, "bold"))
        title.pack(pady=10)
        
        # Riesgo
        risk_label = ctk.CTkLabel(frame, text="Porcentaje de Riesgo (%):", font=("Arial", 12))
        risk_label.pack()
        
        self.risk_spinbox = ctk.CTkEntry(frame, width=100)
        self.risk_spinbox.insert(0, "1.0")
        self.risk_spinbox.pack(pady=5)
        
        # Confianza mínima
        confidence_label = ctk.CTkLabel(frame, text="Confianza Mínima (0-1):", font=("Arial", 12))
        confidence_label.pack(pady=(20, 0))
        
        self.confidence_spinbox = ctk.CTkEntry(frame, width=100)
        self.confidence_spinbox.insert(0, "0.6")
        self.confidence_spinbox.pack(pady=5)
        
        # Filtro de noticias
        self.news_filter_var = ctk.BooleanVar(value=True)
        news_check = ctk.CTkCheckBox(frame, text="Filtro de Noticias Económicas", 
                                     variable=self.news_filter_var)
        news_check.pack(pady=10)
        
        # Filtro de sesión
        self.session_filter_var = ctk.BooleanVar(value=True)
        session_check = ctk.CTkCheckBox(frame, text="Filtro de Sesión de Trading", 
                                        variable=self.session_filter_var)
        session_check.pack(pady=10)
        
        # Botón guardar configuración
        save_button = ctk.CTkButton(frame, text=" Guardar Configuración", 
                                   command=self.save_config, width=200)
        save_button.pack(pady=20)
        
        # Botón exportar estadísticas
        export_button = ctk.CTkButton(frame, text=" Exportar Estadísticas", 
                                     command=self.export_statistics, width=200)
        export_button.pack(pady=5)

    def update_dashboard(self):
        """Actualiza los datos del dashboard."""
        
        if self.bot_running:
            # Actualizar estadísticas
            stats = self.risk_manager.get_account_statistics()
            
            for key, (widget, unit) in self.stats_labels.items():
                if key in stats:
                    value = stats[key]
                    if isinstance(value, float):
                        text = f"{value:.2f} {unit}"
                    else:
                        text = f"{value} {unit}"
                    widget.configure(text=text)
            
            # Actualizar sentimiento
            sentiment = self.market_analyzer.get_market_sentiment()
            colors = {'BULLISH': 'green', 'BEARISH': 'red', 'NEUTRAL': 'blue'}
            self.sentiment_label.configure(text=sentiment, text_color=colors.get(sentiment, 'blue'))
            
            # Actualizar señales
            signal = self.market_analyzer.generate_trading_signal()
            signals_text = f"""
Acción: {signal['action']}
Confianza: {signal['confidence']:.2%}
Precio Entrada: {signal['entry_price']:.5f}
Stop Loss: {signal['stop_loss']:.5f}
Take Profit: {signal['take_profit']:.5f}

Señales Activas:
- BOS: {signal['signals']['bos']['signal']} (Fuerza: {signal['signals']['bos']['strength']:.2f})
- CHOCH: {signal['signals']['choch']['signal']} (Fuerza: {signal['signals']['choch']['strength']:.2f})
- Liquidez: {signal['signals']['liquidity']['signal']} (Fuerza: {signal['signals']['liquidity']['strength']:.2f})
- Bloque de Órdenes: {signal['signals']['order_block']['signal']} (Fuerza: {signal['signals']['order_block']['strength']:.2f})

Soporte: {signal['signals']['support_resistance']['support']:.5f}
Resistencia: {signal['signals']['support_resistance']['resistance']:.5f}
            """
            
            self.signals_text.delete("1.0", "end")
            self.signals_text.insert("1.0", signals_text)
            
            # Actualizar operaciones abiertas
            self._update_trades_tree()
            
            # Actualizar historial
            self._update_history_tree()
        
        # Programar siguiente actualización
        self.after(1000, self.update_dashboard)

    def _update_trades_tree(self):
        """Actualiza la tabla de operaciones abiertas."""
        
        # Limpiar tabla
        for item in self.trades_tree.get_children():
            self.trades_tree.delete(item)
        
        # Agregar operaciones abiertas
        open_trades = self.strategy_executor.get_open_trades()
        
        for trade in open_trades:
            duration = (datetime.now() - trade['entry_time']).total_seconds() / 60
            
            self.trades_tree.insert("", "end", values=(
                trade['order_id'][:10],
                trade['symbol'],
                trade['action'],
                f"{trade['entry_price']:.5f}",
                f"{trade['stop_loss']:.5f}",
                f"{trade['take_profit']:.5f}",
                f"{trade['lot_size']:.2f}",
                f"{trade['confidence']:.2%}",
                f"{int(duration)} min"
            ))

    def _update_history_tree(self):
        """Actualiza la tabla de historial."""
        
        # Limpiar tabla
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Agregar últimas 20 operaciones
        trades_history = self.risk_manager.get_trades_history(limit=20)
        
        for trade in reversed(trades_history):
            self.history_tree.insert("", "end", values=(
                trade['timestamp'][:19],
                trade['symbol'],
                trade['action'],
                f"{trade['entry_price']:.5f}",
                f"{trade['exit_price']:.5f}",
                f"{trade['lot_size']:.2f}",
                f"{trade['profit_loss']:.2f}",
                f"{trade['duration_minutes']} min"
            ))

    def start_bot(self):
        """Inicia el bot de trading."""
        self.bot_running = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        messagebox.showinfo("Bot Iniciado", "El bot de trading ha sido iniciado.")

    def stop_bot(self):
        """Detiene el bot de trading."""
        self.bot_running = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        messagebox.showinfo("Bot Detenido", "El bot de trading ha sido detenido.")

    def save_config(self):
        """Guarda la configuración."""
        try:
            self.strategy_executor.risk_manager.risk_percent = float(self.risk_spinbox.get())
            self.strategy_executor.min_confidence = float(self.confidence_spinbox.get())
            self.strategy_executor.enable_news_filter = self.news_filter_var.get()
            self.strategy_executor.enable_session_filter = self.session_filter_var.get()
            
            messagebox.showinfo("Configuración Guardada", "La configuración ha sido actualizada.")
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese valores válidos.")

    def export_statistics(self):
        """Exporta las estadísticas a un archivo."""
        filepath = f"/mnt/desktop/CallBot/trading_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.risk_manager.export_statistics(filepath)
        messagebox.showinfo("Exportado", f"Estadísticas exportadas a:\n{filepath}")


def run_dashboard(strategy_executor, market_analyzer):
    """
    Ejecuta el dashboard.
    
    Args:
        strategy_executor (StrategyExecutor): Ejecutor de estrategia
        market_analyzer (MarketAnalyzer): Analizador de mercado
    """
    dashboard = TradingDashboard(strategy_executor, market_analyzer)
    dashboard.mainloop()
