"""
datafeeds/synthetic_generator.py
Generador de datos sintéticos realistas para modo demo
"""

import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict


class SyntheticDataGenerator:
    """Genera datos de velas sintéticas realistas"""
    
    def __init__(self, base_price: float = 2045.50, volatility: float = 0.005):
        """
        Inicializa el generador
        
        Args:
            base_price: Precio base (XAUUSD típicamente ~2045)
            volatility: Volatilidad (5% = 0.05)
        """
        self.base_price = base_price
        self.volatility = volatility
        self.current_price = base_price
    
    def generate_candles(self, count: int = 500, timeframe_minutes: int = 5) -> List[Dict]:
        """
        Genera velas sintéticas realistas
        
        Args:
            count: Número de velas a generar
            timeframe_minutes: Timeframe en minutos
        
        Returns:
            Lista de velas con estructura {'open', 'high', 'low', 'close', 'time', 'volume'}
        """
        candles = []
        current_time = datetime.now() - timedelta(minutes=timeframe_minutes * count)
        current_price = self.base_price
        
        for i in range(count):
            # Generar movimiento aleatorio
            daily_return = np.random.normal(0, self.volatility)
            
            # Generar OHLC
            open_price = current_price
            close_price = open_price * (1 + daily_return)
            
            # High y Low con volatilidad adicional
            high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, self.volatility/2)))
            low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, self.volatility/2)))
            
            # Generar volumen realista
            volume = int(np.random.normal(1000, 200))
            
            candle = {
                'open': round(open_price, 5),
                'high': round(high_price, 5),
                'low': round(low_price, 5),
                'close': round(close_price, 5),
                'time': int(current_time.timestamp()),
                'volume': max(volume, 100)
            }
            
            candles.append(candle)
            
            # Actualizar para siguiente vela
            current_price = close_price
            current_time += timedelta(minutes=timeframe_minutes)
        
        return candles
    
    def generate_trending_candles(self, count: int = 500, trend: str = 'UP', 
                                 strength: float = 0.002) -> List[Dict]:
        """
        Genera velas con tendencia
        
        Args:
            count: Número de velas
            trend: 'UP' o 'DOWN'
            strength: Fuerza de la tendencia (0.002 = 0.2% por vela)
        
        Returns:
            Lista de velas con tendencia
        """
        candles = []
        current_time = datetime.now() - timedelta(minutes=5 * count)
        current_price = self.base_price
        
        trend_direction = 1 if trend == 'UP' else -1
        
        for i in range(count):
            # Movimiento con tendencia
            trend_return = trend_direction * strength
            random_return = np.random.normal(0, self.volatility/2)
            daily_return = trend_return + random_return
            
            # OHLC
            open_price = current_price
            close_price = open_price * (1 + daily_return)
            high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, self.volatility/3)))
            low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, self.volatility/3)))
            
            volume = int(np.random.normal(1000, 200))
            
            candle = {
                'open': round(open_price, 5),
                'high': round(high_price, 5),
                'low': round(low_price, 5),
                'close': round(close_price, 5),
                'time': int(current_time.timestamp()),
                'volume': max(volume, 100)
            }
            
            candles.append(candle)
            current_price = close_price
            current_time += timedelta(minutes=5)
        
        return candles
    
    def generate_range_candles(self, count: int = 500, 
                              high_level: float = None,
                              low_level: float = None) -> List[Dict]:
        """
        Genera velas en rango (consolidación)
        
        Args:
            count: Número de velas
            high_level: Nivel superior del rango
            low_level: Nivel inferior del rango
        
        Returns:
            Lista de velas en rango
        """
        if not high_level:
            high_level = self.base_price * 1.01
        if not low_level:
            low_level = self.base_price * 0.99
        
        candles = []
        current_time = datetime.now() - timedelta(minutes=5 * count)
        
        for i in range(count):
            # Precio aleatorio dentro del rango
            close_price = np.random.uniform(low_level, high_level)
            open_price = np.random.uniform(low_level, high_level)
            high_price = max(open_price, close_price) + abs(np.random.normal(0, 0.001))
            low_price = min(open_price, close_price) - abs(np.random.normal(0, 0.001))
            
            volume = int(np.random.normal(800, 150))
            
            candle = {
                'open': round(open_price, 5),
                'high': round(high_price, 5),
                'low': round(low_price, 5),
                'close': round(close_price, 5),
                'time': int(current_time.timestamp()),
                'volume': max(volume, 100)
            }
            
            candles.append(candle)
            current_time += timedelta(minutes=5)
        
        return candles
    
    def generate_volatile_candles(self, count: int = 500, 
                                 volatility_multiplier: float = 2.0) -> List[Dict]:
        """
        Genera velas con volatilidad aumentada
        
        Args:
            count: Número de velas
            volatility_multiplier: Multiplicador de volatilidad
        
        Returns:
            Lista de velas volátiles
        """
        candles = []
        current_time = datetime.now() - timedelta(minutes=5 * count)
        current_price = self.base_price
        
        for i in range(count):
            # Mayor volatilidad
            daily_return = np.random.normal(0, self.volatility * volatility_multiplier)
            
            open_price = current_price
            close_price = open_price * (1 + daily_return)
            high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, self.volatility)))
            low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, self.volatility)))
            
            volume = int(np.random.normal(1500, 300))
            
            candle = {
                'open': round(open_price, 5),
                'high': round(high_price, 5),
                'low': round(low_price, 5),
                'close': round(close_price, 5),
                'time': int(current_time.timestamp()),
                'volume': max(volume, 100)
            }
            
            candles.append(candle)
            current_price = close_price
            current_time += timedelta(minutes=5)
        
        return candles


# Ejemplo de uso
if __name__ == '__main__':
    gen = SyntheticDataGenerator()
    
    # Generar diferentes tipos de datos
    normal_candles = gen.generate_candles(100)
    trending_up = gen.generate_trending_candles(100, trend='UP')
    ranging = gen.generate_range_candles(100)
    volatile = gen.generate_volatile_candles(100)
    
    print(f"Velas normales: {len(normal_candles)}")
    print(f"Tendencia alcista: {len(trending_up)}")
    print(f"Rango: {len(ranging)}")
    print(f"Volátiles: {len(volatile)}")
    
    # Mostrar primera vela
    print(f"\nPrimera vela normal:")
    print(normal_candles[0])
