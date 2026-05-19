"""
Script de Prueba: CallBot UI Demo
Descripción: Inicia la interfaz de usuario de CallBot en modo demostración (sin MT5).
"""

import tkinter as tk
from gui.dashboard import run_dashboard
from core.market_analyzer import MarketAnalyzer
from core.enhanced_risk_manager import EnhancedRiskManager
from core.strategy_executor import StrategyExecutor

class MockMT5:
    """Clase simulada para MT5 para propósitos de demostración."""
    def get_account_info(self):
        class Account:
            balance = 100.0
            equity = 100.0
        return Account()
    
    def get_symbol_data(self, symbol):
        # Generar 100 velas simuladas
        import random
        candles = []
        price = 1.0850
        for i in range(100):
            price += random.uniform(-0.0010, 0.0010)
            candles.append({
                'open': price,
                'high': price + 0.0005,
                'low': price - 0.0005,
                'close': price,
                'time': i,
                'volume': 100
            })
        return candles

def main():
    print("Iniciando CallBot UI en modo DEMOSTRACIÓN...")
    
    # Inicializar componentes simulados
    mock_mt5 = MockMT5()
    risk_manager = EnhancedRiskManager(initial_balance=100.0)
    
    # Generar datos simulados
    candles = mock_mt5.get_symbol_data("EURUSD")
    market_analyzer = MarketAnalyzer(candles)
    
    # Inicializar ejecutor
    strategy_executor = StrategyExecutor(
        risk_manager,
        mock_mt5,
        symbol="EURUSD"
    )
    
    # Iniciar Dashboard
    print("[✓] Dashboard cargado. Abriendo ventana...")
    run_dashboard(strategy_executor, market_analyzer)

if __name__ == "__main__":
    main()
