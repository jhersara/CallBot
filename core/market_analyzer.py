"""
Módulo: Market Analyzer
Descripción: Integra toda la lógica de análisis técnico para generar señales de trading.
Utiliza estructura de mercado, Fibonacci, bloques de órdenes y zonas de liquidez.
"""

from core.market_structure import MarketStructure
from core.fibonacci import Fibonacci
from core.order_blocks import OrderBlockDetector
from core.liquidity import LiquidityDetector
from core.fvg_detector import FVGDetector
from ai.market_classifier import MarketClassifier
from ai.signal_optimizer import SignalOptimizer


class MarketAnalyzer:
    """
    Analizador de mercado que consolida múltiples indicadores técnicos
    para generar señales de trading de alta probabilidad.
    """

    def __init__(self, candles, pip_value=0.0001):
        """
        Inicializa el analizador de mercado.
        
        Args:
            candles (list): Lista de velas con estructura {'open', 'high', 'low', 'close', 'time', 'volume'}
            pip_value (float): Valor del pip para el par de divisas (default: 0.0001 para pares mayor)
        """
        self.candles = candles
        self.pip_value = pip_value
        
        # Inicializar módulos de análisis
        self.market_structure = MarketStructure(candles)
        self.liquidity_detector = LiquidityDetector(candles)
        self.order_block_detector = OrderBlockDetector(candles)
        self.fvg_detector = FVGDetector(candles)
        self.market_classifier = MarketClassifier(candles)
        self.signal_optimizer = SignalOptimizer()
        
        # Calcular niveles de Fibonacci basados en el rango de las últimas 50 velas
        if len(candles) >= 50:
            recent_high = max([c['high'] for c in candles[-50:]])
            recent_low = min([c['low'] for c in candles[-50:]])
            self.fibonacci = Fibonacci(recent_high, recent_low)
        else:
            self.fibonacci = None

    def detect_bos_signal(self):
        """
        Detecta señales de Break of Structure (BOS).
        
        Returns:
            dict: {'signal': 'bullish_bos'|'bearish_bos'|None, 'strength': 0-1}
        """
        bos = self.market_structure.detect_bos()
        
        if bos == "bullish_bos":
            return {'signal': 'bullish_bos', 'strength': 0.7}
        elif bos == "bearish_bos":
            return {'signal': 'bearish_bos', 'strength': 0.7}
        
        return {'signal': None, 'strength': 0}

    def detect_choch_signal(self):
        """
        Detecta señales de Change of Character (CHOCH).
        
        Returns:
            dict: {'signal': 'bullish_choch'|'bearish_choch'|None, 'strength': 0-1}
        """
        choch = self.market_structure.detect_choch()
        
        if choch == "bearish_choch":
            return {'signal': 'bearish_choch', 'strength': 0.8}
        
        return {'signal': None, 'strength': 0}

    def detect_liquidity_signal(self):
        """
        Detecta zonas de liquidez (Liquidity Grab).
        Cuando el precio alcanza nuevos máximos, suele haber un retroceso.
        
        Returns:
            dict: {'signal': 'liquidity_grab'|None, 'strength': 0-1}
        """
        if self.liquidity_detector.detect_liquidity_grab():
            return {'signal': 'liquidity_grab', 'strength': 0.6}
        
        return {'signal': None, 'strength': 0}

    def detect_order_block_signal(self):
        """
        Detecta bloques de órdenes (Order Blocks).
        
        Returns:
            dict: {'signal': 'bullish_ob'|None, 'level': price, 'strength': 0-1}
        """
        bullish_ob = self.order_block_detector.detect_bullish_ob()
        
        if bullish_ob:
            return {
                'signal': 'bullish_ob',
                'level': bullish_ob['low'],
                'strength': 0.65
            }
        
        return {'signal': None, 'level': None, 'strength': 0}

    def detect_fibonacci_levels(self):
        """
        Calcula los niveles de Fibonacci para identificar zonas de soporte/resistencia.
        
        Returns:
            dict: Niveles de Fibonacci con sus precios
        """
        if self.fibonacci:
            return self.fibonacci.calculate_levels()
        
        return {}

    def identify_support_resistance(self):
        """
        Identifica niveles de soporte y resistencia basados en Fibonacci.
        
        Returns:
            dict: {'support': price, 'resistance': price}
        """
        fib_levels = self.detect_fibonacci_levels()
        
        if not fib_levels:
            return {'support': None, 'resistance': None}
        
        current_price = self.candles[-1]['close']
        
        # Encontrar soporte (nivel por debajo del precio actual)
        support = None
        resistance = None
        
        for level, price in fib_levels.items():
            if price < current_price and (support is None or price > support):
                support = price
            elif price > current_price and (resistance is None or price < resistance):
                resistance = price
        
        return {'support': support, 'resistance': resistance}

    def generate_trading_signal(self, use_ai=True):
        """
        Genera una señal de trading consolidada basada en múltiples indicadores.
        
        Returns:
            dict: {
                'action': 'BUY'|'SELL'|'HOLD',
                'confidence': 0-1,
                'entry_price': float,
                'stop_loss': float,
                'take_profit': float,
                'signals': dict (detalles de cada señal)
            }
        """
        current_price = self.candles[-1]['close']
        
        # Recopilar todas las señales
        bos_signal = self.detect_bos_signal()
        choch_signal = self.detect_choch_signal()
        liquidity_signal = self.detect_liquidity_signal()
        order_block_signal = self.detect_order_block_signal()
        support_resistance = self.identify_support_resistance()
        fvg_signals = self.detect_fvg_signals()
        inducement_signal = self.detect_inducement_signal()
        sweep_liquidity_signal = self.detect_sweep_of_liquidity_signal()
        
        # Calcular confianza basada en convergencia de señales
        buy_signals = 0
        sell_signals = 0
        total_confidence = 0
        
        # Evaluar BOS
        if bos_signal['signal'] == 'bullish_bos':
            buy_signals += 1
            total_confidence += bos_signal['strength']
        elif bos_signal['signal'] == 'bearish_bos':
            sell_signals += 1
            total_confidence += bos_signal['strength']
        
        # Evaluar CHOCH
        if choch_signal['signal'] == 'bullish_choch':
            buy_signals += 1
            total_confidence += choch_signal['strength']
        elif choch_signal['signal'] == 'bearish_choch':
            sell_signals += 1
            total_confidence += choch_signal['strength']
        
        # Evaluar Liquidity Grab
        if liquidity_signal['signal'] == 'liquidity_grab':
            # Liquidity grab típicamente precede a un retroceso (SELL)
            sell_signals += 1
            total_confidence += liquidity_signal['strength']
        
        # Evaluar Order Block
        if order_block_signal['signal'] == 'bullish_ob':
            buy_signals += 1
            total_confidence += order_block_signal['strength']
            
        # Evaluar FVG
        for fvg in fvg_signals:
            if fvg['type'] == 'bullish':
                buy_signals += 1
                total_confidence += 0.7
            elif fvg['type'] == 'bearish':
                sell_signals += 1
                total_confidence += 0.7
                
        # Evaluar Inducement
        if inducement_signal['type'] == 'bullish':
            buy_signals += 1
            total_confidence += inducement_signal['strength']
        elif inducement_signal['type'] == 'bearish':
            sell_signals += 1
            total_confidence += inducement_signal['strength']
            
        # Evaluar Sweep of Liquidity
        if sweep_liquidity_signal['type'] == 'bullish':
            buy_signals += 1
            total_confidence += sweep_liquidity_signal['strength']
        elif sweep_liquidity_signal['type'] == 'bearish':
            sell_signals += 1
            total_confidence += sweep_liquidity_signal['strength']
        
        # Determinar acción y calcular niveles
        action = 'HOLD'
        confidence = 0
        entry_price = current_price
        stop_loss = None
        take_profit = None
        
        if buy_signals > sell_signals and buy_signals > 0:
            action = 'BUY'
            confidence = min(total_confidence / buy_signals, 1.0) if buy_signals > 0 else 0
            
            # Stop loss: 50 pips por debajo del precio actual (ajustable)
            stop_loss = current_price - (50 * self.pip_value)
            
            # Take profit: 100 pips por encima del precio actual (ajustable)
            take_profit = current_price + (100 * self.pip_value)
            
            # Si hay soporte identificado, usar como stop loss más preciso
            if support_resistance['support']:
                stop_loss = support_resistance['support'] - (5 * self.pip_value)
            
            # Si hay resistencia, usar como take profit
            if support_resistance['resistance']:
                take_profit = support_resistance['resistance'] + (5 * self.pip_value)
        
        elif sell_signals > buy_signals and sell_signals > 0:
            action = 'SELL'
            confidence = min(total_confidence / sell_signals, 1.0) if sell_signals > 0 else 0
            
            # Stop loss: 50 pips por encima del precio actual
            stop_loss = current_price + (50 * self.pip_value)
            
            # Take profit: 100 pips por debajo del precio actual
            take_profit = current_price - (100 * self.pip_value)
            
            # Si hay resistencia identificada, usar como stop loss
            if support_resistance['resistance']:
                stop_loss = support_resistance['resistance'] + (5 * self.pip_value)
            
            # Si hay soporte, usar como take profit
            if support_resistance['support']:
                take_profit = support_resistance['support'] - (5 * self.pip_value)
        
        return {
            'action': action,
            'confidence': confidence,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'signals': {
                'bos': bos_signal,
                'choch': choch_signal,
                'liquidity': liquidity_signal,
                'order_block': order_block_signal,
                'support_resistance': support_resistance,
                'fvg': fvg_signals,
                'inducement': inducement_signal,
                'sweep_liquidity': sweep_liquidity_signal
            },
            'buy_signals': buy_signals,
            'sell_signals': sell_signals
        }
        
        # Aplicar IA Adaptativa si está habilitada
        if use_ai:
            regime_info = self.market_classifier.get_market_regime()
            signal = self.signal_optimizer.optimize_signal(signal, regime_info['regime'])
            signal['market_regime'] = regime_info
            
        return signal

    def get_market_sentiment(self):
        """
        Retorna el sentimiento general del mercado.
        
        Returns:
            str: 'BULLISH'|'BEARISH'|'NEUTRAL'
        """
        signal = self.generate_trading_signal()
        
        if signal['action'] == 'BUY':
            return 'BULLISH'
        elif signal['action'] == 'SELL':
            return 'BEARISH'
        else:
            return 'NEUTRAL'

    def detect_fvg_signals(self):
        """
        Detecta Fair Value Gaps.
        
        Returns:
            list: Lista de FVG detectados.
        """
        return self.fvg_detector.detect_fvg()

    def detect_inducement_signal(self):
        """
        Detecta señales de Inducement.
        
        Returns:
            dict: Señal de Inducement.
        """
        return self.fvg_detector.detect_inducement()

    def detect_sweep_of_liquidity_signal(self):
        """
        Detecta señales de Sweep of Liquidity.
        
        Returns:
            dict: Señal de Sweep of Liquidity.
        """
        return self.fvg_detector.detect_sweep_of_liquidity()
