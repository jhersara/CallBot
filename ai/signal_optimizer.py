"""
Módulo: Signal Optimizer (Machine Learning)
Descripción: Utiliza técnicas de ML para filtrar señales de baja probabilidad
y optimizar los puntos de entrada.
"""

import numpy as np
from datetime import datetime

class SignalOptimizer:
    """
    Optimizador de señales que utiliza datos históricos y actuales
    para mejorar el Win Rate del sistema.
    """

    def __init__(self):
        """Inicializa el optimizador."""
        self.trade_history = []
        self.learning_rate = 0.01

    def record_trade_outcome(self, signal_data, outcome):
        """
        Registra el resultado de una operación para aprendizaje.
        
        Args:
            signal_data (dict): Datos de la señal original.
            outcome (float): Resultado (profit/loss).
        """
        self.trade_history.append({
            'timestamp': datetime.now(),
            'signal': signal_data,
            'outcome': outcome
        })

    def optimize_signal(self, raw_signal, market_regime):
        """
        Ajusta la confianza de una señal basada en el aprendizaje previo
        y el régimen de mercado actual.
        
        Args:
            raw_signal (dict): Señal generada por el MarketAnalyzer.
            market_regime (str): Régimen detectado (TRENDING, RANGING, etc.)
            
        Returns:
            dict: Señal optimizada.
        """
        optimized_signal = raw_signal.copy()
        
        # Ajuste basado en el régimen de mercado
        if market_regime == 'HIGH_VOLATILITY':
            optimized_signal['confidence'] *= 0.8 # Ser más cauteloso
        elif market_regime == 'TRENDING' and raw_signal['action'] != 'HOLD':
            optimized_signal['confidence'] *= 1.1 # Aumentar confianza en tendencia
            
        # Limitar confianza a un máximo de 1.0
        optimized_signal['confidence'] = min(optimized_signal['confidence'], 1.0)
        
        return optimized_signal

    def get_performance_metrics(self):
        """Calcula métricas de rendimiento para el aprendizaje."""
        if not self.trade_history:
            return {'win_rate': 0, 'total_trades': 0}
            
        wins = sum(1 for t in self.trade_history if t['outcome'] > 0)
        total = len(self.trade_history)
        
        return {
            'win_rate': wins / total if total > 0 else 0,
            'total_trades': total,
            'profit_factor': self.calculate_profit_factor()
        }

    def calculate_profit_factor(self):
        """Calcula el factor de beneficio."""
        gross_profits = sum(t['outcome'] for t in self.trade_history if t['outcome'] > 0)
        gross_losses = abs(sum(t['outcome'] for t in self.trade_history if t['outcome'] < 0))
        
        return gross_profits / gross_losses if gross_losses > 0 else gross_profits
