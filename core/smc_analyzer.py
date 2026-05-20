# core/smc_analyzer.py
"""
Smart Money Concepts (SMC) Analyzer
Análisis avanzado de estructura de mercado: BOS, CHOCH, Order Blocks, FVG, Liquidez, Fibonacci
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
from enum import Enum


class SignalType(Enum):
    """Tipos de señales"""
    BOS_BULLISH = "BOS_BULLISH"
    BOS_BEARISH = "BOS_BEARISH"
    CHOCH_BULLISH = "CHOCH_BULLISH"
    CHOCH_BEARISH = "CHOCH_BEARISH"
    ORDER_BLOCK_BULLISH = "ORDER_BLOCK_BULLISH"
    ORDER_BLOCK_BEARISH = "ORDER_BLOCK_BEARISH"
    FVG_BULLISH = "FVG_BULLISH"
    FVG_BEARISH = "FVG_BEARISH"
    LIQUIDITY_ZONE = "LIQUIDITY_ZONE"
    FIBONACCI = "FIBONACCI"


@dataclass
class Signal:
    """Estructura de una señal de trading"""
    type: SignalType
    price: float
    confidence: float  # 0-1
    timestamp: int
    description: str
    strength: float  # 0-1
    
    def to_dict(self):
        return {
            'type': self.type.value,
            'price': self.price,
            'confidence': self.confidence,
            'timestamp': self.timestamp,
            'description': self.description,
            'strength': self.strength
        }


class SMCAnalyzer:
    """Analizador de Smart Money Concepts"""
    
    def __init__(self, pip_value: float = 0.0001):
        self.pip_value = pip_value
        self.signals: List[Signal] = []
        
    def analyze(self, candles: pd.DataFrame) -> Dict:
        """
        Análisis completo de SMC
        
        Args:
            candles: DataFrame con columnas [open, high, low, close, time]
        
        Returns:
            Dict con todos los análisis
        """
        if len(candles) < 50:
            return {'error': 'Necesita al menos 50 velas'}
        
        self.signals = []
        
        # Análisis individual
        bos_signals = self._detect_bos(candles)
        choch_signals = self._detect_choch(candles)
        ob_signals = self._detect_order_blocks(candles)
        fvg_signals = self._detect_fvg(candles)
        liquidity_zones = self._detect_liquidity_zones(candles)
        fibonacci_levels = self._calculate_fibonacci(candles)
        
        # Combinar señales
        self.signals.extend(bos_signals)
        self.signals.extend(choch_signals)
        self.signals.extend(ob_signals)
        self.signals.extend(fvg_signals)
        self.signals.extend(liquidity_zones)
        self.signals.extend(fibonacci_levels)
        
        # Generar señal consolidada
        consolidated_signal = self._consolidate_signals(candles)
        
        return {
            'bos': [s.to_dict() for s in bos_signals],
            'choch': [s.to_dict() for s in choch_signals],
            'order_blocks': [s.to_dict() for s in ob_signals],
            'fvg': [s.to_dict() for s in fvg_signals],
            'liquidity_zones': [s.to_dict() for s in liquidity_zones],
            'fibonacci': [s.to_dict() for s in fibonacci_levels],
            'consolidated_signal': consolidated_signal,
            'all_signals': [s.to_dict() for s in self.signals]
        }
    
    def _detect_bos(self, candles: pd.DataFrame) -> List[Signal]:
        """Detecta Break of Structure (BOS)"""
        signals = []
        
        if len(candles) < 3:
            return signals
        
        # Detectar máximos y mínimos locales
        for i in range(2, len(candles) - 1):
            prev_high = candles.iloc[i-2:i]['high'].max()
            prev_low = candles.iloc[i-2:i]['low'].min()
            current_close = candles.iloc[i]['close']
            current_high = candles.iloc[i]['high']
            current_low = candles.iloc[i]['low']
            
            # BOS Alcista: rompe máximo anterior
            if current_high > prev_high and current_close > prev_high:
                confidence = min(0.95, 0.7 + (current_high - prev_high) / (prev_high * 0.001))
                signals.append(Signal(
                    type=SignalType.BOS_BULLISH,
                    price=current_high,
                    confidence=confidence,
                    timestamp=int(candles.iloc[i]['time']),
                    description=f"BOS Alcista en {current_high:.5f}",
                    strength=confidence
                ))
            
            # BOS Bajista: rompe mínimo anterior
            if current_low < prev_low and current_close < prev_low:
                confidence = min(0.95, 0.7 + (prev_low - current_low) / (prev_low * 0.001))
                signals.append(Signal(
                    type=SignalType.BOS_BEARISH,
                    price=current_low,
                    confidence=confidence,
                    timestamp=int(candles.iloc[i]['time']),
                    description=f"BOS Bajista en {current_low:.5f}",
                    strength=confidence
                ))
        
        return signals
    
    def _detect_choch(self, candles: pd.DataFrame) -> List[Signal]:
        """Detecta Change of Character (CHOCH)"""
        signals = []
        
        if len(candles) < 10:
            return signals
        
        # Analizar cambio en patrón de velas
        for i in range(10, len(candles)):
            # Comparar últimas 5 velas con las 5 anteriores
            recent_range = candles.iloc[i-5:i]
            previous_range = candles.iloc[i-10:i-5]
            
            recent_volatility = recent_range['high'].max() - recent_range['low'].min()
            previous_volatility = previous_range['high'].max() - previous_range['low'].min()
            
            # Cambio significativo en volatilidad
            if recent_volatility < previous_volatility * 0.5:
                confidence = 0.75
                signals.append(Signal(
                    type=SignalType.CHOCH_BULLISH,
                    price=candles.iloc[i]['close'],
                    confidence=confidence,
                    timestamp=int(candles.iloc[i]['time']),
                    description=f"CHOCH detectado - Cambio de carácter",
                    strength=confidence
                ))
        
        return signals
    
    def _detect_order_blocks(self, candles: pd.DataFrame) -> List[Signal]:
        """Detecta Order Blocks (bloques institucionales)"""
        signals = []
        
        if len(candles) < 20:
            return signals
        
        # Buscar velas impulsivas grandes
        for i in range(5, len(candles) - 5):
            candle_range = candles.iloc[i]['high'] - candles.iloc[i]['low']
            avg_range = candles.iloc[i-5:i+5]['high'].subtract(candles.iloc[i-5:i+5]['low']).mean()
            
            # Vela impulsiva (rango > 1.5x promedio)
            if candle_range > avg_range * 1.5:
                # Order Block Alcista
                if candles.iloc[i]['close'] > candles.iloc[i]['open']:
                    signals.append(Signal(
                        type=SignalType.ORDER_BLOCK_BULLISH,
                        price=(candles.iloc[i]['high'] + candles.iloc[i]['low']) / 2,
                        confidence=0.80,
                        timestamp=int(candles.iloc[i]['time']),
                        description=f"Order Block Alcista en {candles.iloc[i]['high']:.5f}",
                        strength=0.80
                    ))
                
                # Order Block Bajista
                elif candles.iloc[i]['close'] < candles.iloc[i]['open']:
                    signals.append(Signal(
                        type=SignalType.ORDER_BLOCK_BEARISH,
                        price=(candles.iloc[i]['high'] + candles.iloc[i]['low']) / 2,
                        confidence=0.80,
                        timestamp=int(candles.iloc[i]['time']),
                        description=f"Order Block Bajista en {candles.iloc[i]['low']:.5f}",
                        strength=0.80
                    ))
        
        return signals
    
    def _detect_fvg(self, candles: pd.DataFrame) -> List[Signal]:
        """Detecta Fair Value Gaps (FVG)"""
        signals = []
        
        if len(candles) < 3:
            return signals
        
        # Buscar gaps entre velas
        for i in range(1, len(candles) - 1):
            prev_high = candles.iloc[i-1]['high']
            curr_low = candles.iloc[i]['low']
            curr_high = candles.iloc[i]['high']
            next_low = candles.iloc[i+1]['low']
            
            # FVG Alcista: low actual > high anterior
            if curr_low > prev_high:
                gap_size = curr_low - prev_high
                confidence = min(0.90, 0.65 + gap_size / prev_high)
                signals.append(Signal(
                    type=SignalType.FVG_BULLISH,
                    price=(prev_high + curr_low) / 2,
                    confidence=confidence,
                    timestamp=int(candles.iloc[i]['time']),
                    description=f"FVG Alcista: {gap_size:.5f}",
                    strength=confidence
                ))
            
            # FVG Bajista: high actual < low anterior
            if curr_high < next_low:
                gap_size = next_low - curr_high
                confidence = min(0.90, 0.65 + gap_size / next_low)
                signals.append(Signal(
                    type=SignalType.FVG_BEARISH,
                    price=(curr_high + next_low) / 2,
                    confidence=confidence,
                    timestamp=int(candles.iloc[i]['time']),
                    description=f"FVG Bajista: {gap_size:.5f}",
                    strength=confidence
                ))
        
        return signals
    
    def _detect_liquidity_zones(self, candles: pd.DataFrame) -> List[Signal]:
        """Detecta zonas de liquidez (acumulación de máximos/mínimos)"""
        signals = []
        
        if len(candles) < 20:
            return signals
        
        # Buscar máximos y mínimos agrupados
        highs = candles['high'].values
        lows = candles['low'].values
        
        # Detectar clusters de máximos
        for i in range(10, len(candles) - 10):
            window_highs = highs[i-10:i+10]
            window_lows = lows[i-10:i+10]
            
            max_high = window_highs.max()
            min_low = window_lows.min()
            
            # Zona de máximos
            high_cluster = np.sum(window_highs > max_high * 0.99)
            if high_cluster >= 3:
                signals.append(Signal(
                    type=SignalType.LIQUIDITY_ZONE,
                    price=max_high,
                    confidence=0.75,
                    timestamp=int(candles.iloc[i]['time']),
                    description=f"Zona de Liquidez (Máximos) en {max_high:.5f}",
                    strength=0.75
                ))
            
            # Zona de mínimos
            low_cluster = np.sum(window_lows < min_low * 1.01)
            if low_cluster >= 3:
                signals.append(Signal(
                    type=SignalType.LIQUIDITY_ZONE,
                    price=min_low,
                    confidence=0.75,
                    timestamp=int(candles.iloc[i]['time']),
                    description=f"Zona de Liquidez (Mínimos) en {min_low:.5f}",
                    strength=0.75
                ))
        
        return signals
    
    def _calculate_fibonacci(self, candles: pd.DataFrame) -> List[Signal]:
        """Calcula niveles de Fibonacci"""
        signals = []
        
        if len(candles) < 50:
            return signals
        
        # Encontrar máximo y mínimo en últimas 50 velas
        recent = candles.tail(50)
        high = recent['high'].max()
        low = recent['low'].min()
        
        # Niveles de Fibonacci
        fib_levels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]
        
        for level in fib_levels:
            fib_price = low + (high - low) * level
            signals.append(Signal(
                type=SignalType.FIBONACCI,
                price=fib_price,
                confidence=0.60,
                timestamp=int(candles.iloc[-1]['time']),
                description=f"Fibonacci {level*100:.1f}% en {fib_price:.5f}",
                strength=0.60
            ))
        
        return signals
    
    def _consolidate_signals(self, candles: pd.DataFrame) -> Dict:
        """Consolida todas las señales en una recomendación"""
        if not self.signals:
            return {
                'action': 'HOLD',
                'confidence': 0,
                'reasons': []
            }
        
        # Contar señales por tipo
        bullish_signals = sum(1 for s in self.signals if 'BULLISH' in s.type.value)
        bearish_signals = sum(1 for s in self.signals if 'BEARISH' in s.type.value)
        
        # Calcular confianza promedio
        avg_confidence = np.mean([s.confidence for s in self.signals[-10:]])  # Últimas 10
        
        # Determinar acción
        if bullish_signals > bearish_signals and avg_confidence > 0.70:
            action = 'BUY'
        elif bearish_signals > bullish_signals and avg_confidence > 0.70:
            action = 'SELL'
        else:
            action = 'HOLD'
        
        # Razones
        reasons = [s.description for s in self.signals[-5:]]  # Últimas 5 razones
        
        return {
            'action': action,
            'confidence': avg_confidence,
            'bullish_signals': bullish_signals,
            'bearish_signals': bearish_signals,
            'reasons': reasons
        }
