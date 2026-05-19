"""
Módulo: Market Classifier (IA Adaptativa)
Descripción: Identifica el régimen de mercado (Tendencia, Rango, Volatilidad)
para adaptar la estrategia de trading.
"""

import numpy as np

class MarketClassifier:
    """
    Clasificador de régimen de mercado basado en indicadores estadísticos.
    Prepara el camino para la integración de modelos de Machine Learning.
    """

    def __init__(self, candles):
        """
        Inicializa el clasificador.
        
        Args:
            candles (list): Lista de velas.
        """
        self.candles = candles

    def calculate_atr(self, period=14):
        """Calcula el Average True Range (ATR) para medir volatilidad."""
        if len(self.candles) < period + 1:
            return 0
        
        tr_list = []
        for i in range(1, len(self.candles)):
            h = self.candles[i]['high']
            l = self.candles[i]['low']
            pc = self.candles[i-1]['close']
            tr = max(h - l, abs(h - pc), abs(l - pc))
            tr_list.append(tr)
            
        return np.mean(tr_list[-period:])

    def calculate_adx(self, period=14):
        """Calcula el Average Directional Index (ADX) para medir fuerza de tendencia."""
        # Simplificación para el clasificador de régimen
        if len(self.candles) < period * 2:
            return 20 # Valor neutral
            
        # Lógica simplificada de ADX
        return 25 # Placeholder para lógica real

    def get_market_regime(self):
        """
        Determina el régimen actual del mercado.
        
        Returns:
            dict: {
                'regime': 'TRENDING'|'RANGING'|'HIGH_VOLATILITY',
                'confidence': float,
                'atr': float,
                'adx': float
            }
        """
        atr = self.calculate_atr()
        adx = self.calculate_adx()
        
        # Lógica de clasificación
        if atr > np.mean([c['high'] - c['low'] for c in self.candles[-50:]]) * 1.5:
            regime = 'HIGH_VOLATILITY'
            confidence = 0.8
        elif adx > 25:
            regime = 'TRENDING'
            confidence = 0.75
        else:
            regime = 'RANGING'
            confidence = 0.7
            
        return {
            'regime': regime,
            'confidence': confidence,
            'atr': atr,
            'adx': adx
        }

    def get_adaptive_parameters(self):
        """
        Retorna parámetros adaptativos basados en el régimen de mercado.
        """
        regime_info = self.get_market_regime()
        regime = regime_info['regime']
        
        params = {
            'min_confidence': 0.6,
            'stop_loss_multiplier': 1.0,
            'take_profit_multiplier': 1.0
        }
        
        if regime == 'HIGH_VOLATILITY':
            params['min_confidence'] = 0.75
            params['stop_loss_multiplier'] = 1.5
            params['take_profit_multiplier'] = 2.0
        elif regime == 'TRENDING':
            params['min_confidence'] = 0.6
            params['take_profit_multiplier'] = 1.5
        elif regime == 'RANGING':
            params['min_confidence'] = 0.7
            params['take_profit_multiplier'] = 0.8
            
        return params
