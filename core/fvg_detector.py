"""
Módulo: FVG Detector
Descripción: Detecta Fair Value Gaps (FVG) y patrones de manipulación institucional.
"""

class FVGDetector:
    """
    Clase para detectar Fair Value Gaps (FVG) y patrones de manipulación institucional
    como Inducement y Sweep of Liquidity.
    """

    def __init__(self, candles):
        """
        Inicializa el detector de FVG.
        
        Args:
            candles (list): Lista de velas con estructura {
                'open', 'high', 'low', 'close', 'time', 'volume'
            }
        """
        self.candles = candles

    def detect_fvg(self):
        """
        Detecta Fair Value Gaps (FVG) en las velas.
        Un FVG alcista ocurre cuando el mínimo de la vela 3 es mayor que el máximo de la vela 1.
        Un FVG bajista ocurre cuando el máximo de la vela 3 es menor que el mínimo de la vela 1.
        
        Returns:
            list: Lista de diccionarios con los FVG detectados.
                  Cada diccionario contiene: {
                      'type': 'bullish'|'bearish',
                      'start_price': float,
                      'end_price': float,
                      'start_index': int,
                      'end_index': int
                  }
        """
        fvgs = []
        for i in range(2, len(self.candles)):
            candle1 = self.candles[i - 2]
            candle2 = self.candles[i - 1]
            candle3 = self.candles[i]

            # FVG Alcista (Bullish FVG)
            if candle3['low'] > candle1['high']:
                fvg_start = candle1['high']
                fvg_end = candle3['low']
                fvgs.append({
                    'type': 'bullish',
                    'start_price': fvg_start,
                    'end_price': fvg_end,
                    'start_index': i - 2,
                    'end_index': i
                })
            
            # FVG Bajista (Bearish FVG)
            elif candle3['high'] < candle1['low']:
                fvg_start = candle1['low']
                fvg_end = candle3['high']
                fvgs.append({
                    'type': 'bearish',
                    'start_price': fvg_start,
                    'end_price': fvg_end,
                    'start_index': i - 2,
                    'end_index': i
                })
        return fvgs

    def detect_inducement(self):
        """
        Detecta patrones de Inducement (atracción de liquidez).
        Esto es una simplificación: busca un pequeño retroceso que toma liquidez
        antes de un movimiento direccional más grande.
        
        Returns:
            dict: {
                'type': 'bullish'|'bearish'|None,
                'level': float,
                'strength': float
            }
        """
        if len(self.candles) < 5:
            return {'type': None, 'level': None, 'strength': 0}

        # Simplificación: buscar un mínimo/máximo local que es roto brevemente
        # antes de una reversión en la dirección opuesta.
        # Esto es un placeholder y necesita lógica más sofisticada.
        
        last_candle = self.candles[-1]
        prev_candle = self.candles[-2]
        
        # Ejemplo muy básico de Inducement alcista: un falso rompimiento bajista
        if last_candle['low'] < prev_candle['low'] and last_candle['close'] > prev_candle['close']:
            return {'type': 'bullish', 'level': prev_candle['low'], 'strength': 0.7}
        
        # Ejemplo muy básico de Inducement bajista: un falso rompimiento alcista
        if last_candle['high'] > prev_candle['high'] and last_candle['close'] < prev_candle['close']:
            return {'type': 'bearish', 'level': prev_candle['high'], 'strength': 0.7}
            
        return {'type': None, 'level': None, 'strength': 0}

    def detect_sweep_of_liquidity(self):
        """
        Detecta un Sweep of Liquidity (barrido de liquidez).
        Esto ocurre cuando una vela tiene una mecha larga que supera un máximo/mínimo anterior
        y luego el cuerpo de la vela cierra en la dirección opuesta.
        
        Returns:
            dict: {
                'type': 'bullish'|'bearish'|None,
                'level': float,
                'strength': float
            }
        """
        if len(self.candles) < 2:
            return {'type': None, 'level': None, 'strength': 0}

        last_candle = self.candles[-1]
        prev_candle = self.candles[-2]

        # Barrido de liquidez alcista (mecha larga hacia abajo, cierre alcista)
        if last_candle['low'] < prev_candle['low'] and last_candle['close'] > last_candle['open'] and \
           (last_candle['open'] - last_candle['low']) > (last_candle['high'] - last_candle['open']) * 2:
            return {'type': 'bullish', 'level': prev_candle['low'], 'strength': 0.8}

        # Barrido de liquidez bajista (mecha larga hacia arriba, cierre bajista)
        if last_candle['high'] > prev_candle['high'] and last_candle['close'] < last_candle['open'] and \
           (last_candle['high'] - last_candle['open']) > (last_candle['open'] - last_candle['low']) * 2:
            return {'type': 'bearish', 'level': prev_candle['high'], 'strength': 0.8}

        return {'type': None, 'level': None, 'strength': 0}
