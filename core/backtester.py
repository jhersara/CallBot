"""
Módulo: Backtester
Descripción: Motor de backtesting profesional para validar la estrategia
en datos históricos.
"""

from core.market_analyzer import MarketAnalyzer
from core.advanced_risk_manager import AdvancedRiskManager

class Backtester:
    """
    Motor de backtesting que simula operaciones en datos históricos.
    """

    def __init__(self, historical_data, initial_balance=1000):
        """
        Inicializa el backtester.
        
        Args:
            historical_data (list): Lista de velas históricas.
            initial_balance (float): Balance inicial para el backtest.
        """
        self.historical_data = historical_data
        self.initial_balance = initial_balance
        self.risk_manager = AdvancedRiskManager(initial_balance)
        self.trades_executed = []
        self.equity_curve = [initial_balance]

    def run_backtest(self, window_size=100, min_confidence=0.6):
        """
        Ejecuta el backtest en los datos históricos.
        
        Args:
            window_size (int): Número de velas para el análisis.
            min_confidence (float): Confianza mínima para ejecutar operaciones.
            
        Returns:
            dict: Resultados del backtest.
        """
        for i in range(window_size, len(self.historical_data)):
            # Obtener ventana de datos
            window = self.historical_data[i-window_size:i]
            current_candle = self.historical_data[i]
            
            # Analizar mercado
            analyzer = MarketAnalyzer(window)
            signal = analyzer.generate_trading_signal()
            
            # Ejecutar si la confianza es suficiente
            if signal['confidence'] >= min_confidence and signal['action'] != 'HOLD':
                trade_id = f"BT_{i}"
                
                # Registrar operación
                self.risk_manager.add_trade(
                    trade_id,
                    signal['entry_price'],
                    signal['stop_loss'],
                    signal['take_profit'],
                    signal['action']
                )
                
                # Simular cierre en la siguiente vela (simplificado)
                if i + 1 < len(self.historical_data):
                    next_candle = self.historical_data[i + 1]
                    
                    # Verificar si se alcanzó SL o TP
                    if signal['action'] == 'BUY':
                        if next_candle['low'] <= signal['stop_loss']:
                            close_price = signal['stop_loss']
                            reason = 'SL'
                        elif next_candle['high'] >= signal['take_profit']:
                            close_price = signal['take_profit']
                            reason = 'TP'
                        else:
                            close_price = next_candle['close']
                            reason = 'CLOSE'
                    else:  # SELL
                        if next_candle['high'] >= signal['stop_loss']:
                            close_price = signal['stop_loss']
                            reason = 'SL'
                        elif next_candle['low'] <= signal['take_profit']:
                            close_price = signal['take_profit']
                            reason = 'TP'
                        else:
                            close_price = next_candle['close']
                            reason = 'CLOSE'
                    
                    # Cerrar operación
                    self.risk_manager.close_trade(trade_id, close_price, reason)
                    
                    # Registrar en historial
                    self.trades_executed.append({
                        'index': i,
                        'signal': signal['action'],
                        'confidence': signal['confidence'],
                        'reason': reason
                    })
                    
                    # Actualizar curva de equity
                    self.equity_curve.append(self.risk_manager.current_balance)

        return self.get_backtest_results()

    def get_backtest_results(self):
        """
        Retorna los resultados del backtest.
        
        Returns:
            dict: Resultados consolidados.
        """
        stats = self.risk_manager.get_portfolio_stats()
        
        return {
            'initial_balance': self.initial_balance,
            'final_balance': self.risk_manager.current_balance,
            'total_return': ((self.risk_manager.current_balance - self.initial_balance) / self.initial_balance) * 100,
            'total_trades': stats['total_trades'],
            'win_rate': stats['win_rate'],
            'profit_factor': stats['profit_factor'],
            'max_drawdown': self.calculate_max_drawdown(),
            'equity_curve': self.equity_curve
        }

    def calculate_max_drawdown(self):
        """
        Calcula el drawdown máximo durante el backtest.
        
        Returns:
            float: Drawdown máximo en porcentaje.
        """
        if not self.equity_curve:
            return 0
            
        peak = self.equity_curve[0]
        max_dd = 0
        
        for value in self.equity_curve:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            if dd > max_dd:
                max_dd = dd
                
        return max_dd * 100
