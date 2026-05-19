"""
CallBot - Professional AI Trading Bot
Algoritmo de trading inteligente con gestión de capital compuesto (1% riesgo, 30-65% retorno)
"""

import sys
import time
from datetime import datetime

# Importar módulos del bot
from mt5.connector import MT5Connector
from core.market_analyzer import MarketAnalyzer
from core.enhanced_risk_manager import EnhancedRiskManager
from core.strategy_executor import StrategyExecutor
from gui.dashboard import run_dashboard


class TradingBot:
    """
    Bot de trading profesional que integra análisis técnico, gestión de riesgo y ejecución.
    """

    def __init__(self, initial_balance=100, symbol='EURUSD', pip_value=0.0001):
        """
        Inicializa el bot de trading.
        
        Args:
            initial_balance (float): Balance inicial (default: 100 USD)
            symbol (str): Par de divisas a operar (default: EURUSD)
            pip_value (float): Valor del pip (default: 0.0001)
        """
        self.initial_balance = initial_balance
        self.symbol = symbol
        self.pip_value = pip_value
        
        # Inicializar componentes
        self.mt5_connector = None
        self.risk_manager = EnhancedRiskManager(initial_balance)
        self.market_analyzer = None
        self.strategy_executor = None
        
        # Estado
        self.running = False
        self.trades_executed = 0
        
        print(f"""
╔════════════════════════════════════════════════════════════════╗
║            CALLBOT - Professional AI Trading Bot            ║
║                                                                ║
║  Algoritmo de Trading Inteligente con Gestión de Capital      ║
║  Riesgo: 1% por operación | Retorno Esperado: 30-65% mensual ║
║                                                                ║
║  Balance Inicial: ${initial_balance:.2f}                              ║
║  Par de Divisas: {symbol}                                    ║
║  Estado: Inicializando...                                      ║
╚════════════════════════════════════════════════════════════════╝
        """)

    def initialize(self, simulation_mode=False):
        """Inicializa la conexión con MT5 y los analizadores."""
        
        if simulation_mode:
            print("[!] Iniciando en MODO SIMULACIÓN (Sin conexión a MT5)...")
            from test_ui import MockMT5
            self.mt5_connector = MockMT5()
            candles = self.mt5_connector.get_symbol_data(self.symbol)
            self.market_analyzer = MarketAnalyzer(candles, self.pip_value)
            self.strategy_executor = StrategyExecutor(self.risk_manager, self.mt5_connector, self.symbol, self.pip_value)
            return True

        print("[*] Conectando a MetaTrader 5...")
        
        try:
            # Conectar a MT5
            self.mt5_connector = MT5Connector()
            
            if not self.mt5_connector.connect():
                print("[✗] Error: No se pudo conectar a MetaTrader 5")
                print("[!] Asegúrate de que MetaTrader 5 está abierto y ejecutándose")
                print("[*] ¿Deseas iniciar en modo simulación para ver la UI? (S/N): ")
                return False
            
            print("[✓] Conexión a MT5 establecida")
            
            # Obtener información de la cuenta
            account_info = self.mt5_connector.get_account_info()
            print(f"[✓] Información de cuenta obtenida")
            print(f"    - Balance: ${account_info.balance:.2f}")
            print(f"    - Equity: ${account_info.equity:.2f}")
            
            # Actualizar balance en el risk manager
            self.risk_manager.update_balance(account_info.balance)
            
            # Obtener datos de mercado
            print(f"[*] Obteniendo datos de mercado para {self.symbol}...")
            candles = self.mt5_connector.get_symbol_data(self.symbol)
            
            if not candles:
                print("[✗] Error: No se pudieron obtener datos de mercado")
                return False
            
            print(f"[✓] {len(candles)} velas obtenidas")
            
            # Inicializar analizadores
            self.market_analyzer = MarketAnalyzer(candles, self.pip_value)
            self.strategy_executor = StrategyExecutor(
                self.risk_manager,
                self.mt5_connector,
                self.symbol,
                self.pip_value
            )
            
            print("[✓] Analizadores inicializados")
            
            return True
        
        except Exception as e:
            print(f"[x] Error durante la inicialización: {str(e)}")
            return False

    def run(self, use_dashboard=True):
        """
        Ejecuta el bot de trading.
        
        Args:
            use_dashboard (bool): Si True, muestra el dashboard (default: True)
        """
        
        if not self.initialize():
            # Preguntar si desea modo simulación si falla MT5
            choice = input("¿Deseas iniciar en modo simulación para ver la UI? (S/N): ").lower()
            if choice == 's':
                if not self.initialize(simulation_mode=True):
                    print("[✗] No se pudo inicializar el modo simulación")
                    return
            else:
                print("[✗] No se pudo inicializar el bot")
                return
        
        self.running = True
        
        print("\n[✓] Bot listo para operar")
        print(f"[*] Riesgo por operación: {self.risk_manager.risk_percent}%")
        print(f"[*] Balance inicial: ${self.risk_manager.initial_balance:.2f}")
        
        # Mostrar dashboard si está habilitado
        if use_dashboard:
            print("[*] Iniciando dashboard...")
            try:
                run_dashboard(self.strategy_executor, self.market_analyzer)
            except Exception as e:
                print(f"[!] Error en el dashboard: {str(e)}")
                print("[*] Continuando sin dashboard...")
                self.run_trading_loop()
        else:
            self.run_trading_loop()

    def run_trading_loop(self):
        """Ejecuta el bucle principal de trading."""
        
        print("\n[*] Iniciando bucle de trading...")
        print("[*] Presiona Ctrl+C para detener\n")
        
        try:
            iteration = 0
            
            while self.running:
                iteration += 1
                
                try:
                    # Obtener datos actuales
                    candles = self.mt5_connector.get_symbol_data(self.symbol)
                    
                    if not candles:
                        print("[!] No se pudieron obtener datos de mercado")
                        time.sleep(5)
                        continue
                    
                    # Actualizar analizador
                    self.market_analyzer = MarketAnalyzer(candles, self.pip_value)
                    
                    # Generar señal
                    signal = self.market_analyzer.generate_trading_signal()
                    
                    # Mostrar información
                    print(f"\n[Iteración {iteration}] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"  Precio Actual: {candles[-1]['close']:.5f}")
                    print(f"  Acción: {signal['action']} (Confianza: {signal['confidence']:.2%})")
                    print(f"  Balance: ${self.risk_manager.current_balance:.2f}")
                    
                    # Ejecutar señal
                    if signal['action'] != 'HOLD':
                        result = self.strategy_executor.execute_signal(signal, self.market_analyzer)
                        
                        if result['executed']:
                            self.trades_executed += 1
                            print(f"  [✓] Operación ejecutada: {result['action']}")
                            print(f"      - Lote: {result['lot_size']:.2f}")
                            print(f"      - Riesgo: ${result['risk_amount']:.2f}")
                        else:
                            print(f"  [!] Operación no ejecutada: {result['reason']}")
                    
                    # Actualizar operaciones abiertas
                    current_prices = {self.symbol: candles[-1]['close']}
                    closed_trades = self.strategy_executor.update_open_trades(current_prices)
                    
                    if closed_trades:
                        for trade in closed_trades:
                            if trade['closed']:
                                print(f"  [✓] Operación cerrada: {trade['reason']}")
                                print(f"      - Ganancia/Pérdida: ${trade['profit_loss']:.2f}")
                    
                    # Mostrar estadísticas
                    stats = self.risk_manager.get_account_statistics()
                    print(f"  Estadísticas: {stats['total_trades']} ops, "
                          f"W/L: {stats['winning_trades']}/{stats['losing_trades']}, "
                          f"Retorno: {stats['return_percent']:.2f}%")
                    
                    # Esperar antes de la siguiente iteración
                    time.sleep(60)  # Esperar 1 minuto entre análisis
                
                except KeyboardInterrupt:
                    print("\n[!] Interrupción del usuario")
                    break
                
                except Exception as e:
                    print(f"[✗] Error en el bucle: {str(e)}")
                    time.sleep(5)
        
        finally:
            self.stop()

    def stop(self):
        """Detiene el bot de trading."""
        
        self.running = False
        
        print("\n[*] Deteniendo bot...")
        
        # Mostrar resumen final
        stats = self.risk_manager.get_account_statistics()
        
        print(f"""
╔════════════════════════════════════════════════════════════════╗
║                    RESUMEN FINAL DE OPERACIONES               ║
╠════════════════════════════════════════════════════════════════╣
║  Balance Inicial:        ${stats['initial_balance']:>40.2f}  ║
║  Balance Final:          ${stats['current_balance']:>40.2f}  ║
║  Ganancia Total:         ${stats['total_return']:>40.2f}  ║
║  Retorno Porcentual:     {stats['return_percent']:>40.2f}%  ║
║                                                                ║
║  Total de Operaciones:   {stats['total_trades']:>40}  ║
║  Operaciones Ganadoras:  {stats['winning_trades']:>40}  ║
║  Operaciones Perdedoras: {stats['losing_trades']:>40}  ║
║  Tasa de Ganancia:       {stats['win_rate']:>40.2f}%  ║
║  Factor de Ganancia:     {stats['profit_factor']:>40.2f}  ║
║  Ganancia Promedio:      ${stats['average_profit_per_trade']:>40.2f}  ║
╚════════════════════════════════════════════════════════════════╝
        """)
        
        # Exportar estadísticas
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = f"/mnt/desktop/CallBot/trading_stats_{timestamp}.json"
        
        try:
            self.risk_manager.export_statistics(filepath)
            print(f"[✓] Estadísticas exportadas a: {filepath}")
        except Exception as e:
            print(f"[!] Error al exportar estadísticas: {str(e)}")
        
        # Desconectar de MT5
        if self.mt5_connector:
            self.mt5_connector.disconnect()
            print("[✓] Desconectado de MetaTrader 5")
        
        print("[✓] Bot detenido")


def main():
    """Función principal."""
    
    # Crear bot
    bot = TradingBot(
        initial_balance=100,  # Comenzar con 100 USD
        symbol='EURUSD',
        pip_value=0.0001
    )
    
    # Ejecutar bot
    try:
        bot.run(use_dashboard=True)
    except KeyboardInterrupt:
        print("\n[!] Interrupción del usuario")
        bot.stop()
    except Exception as e:
        print(f"[✗] Error fatal: {str(e)}")
        bot.stop()


if __name__ == "__main__":
    main()
