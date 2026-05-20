"""
Módulo: Strategy Executor
Descripción: Ejecuta las operaciones de trading basadas en señales del analizador de mercado.
Coordina entre el analizador, el gestor de riesgo y el conector de MT5.
"""

from core.market_analyzer import MarketAnalyzer
from core.enhanced_risk_manager import EnhancedRiskManager
from datetime import datetime


class StrategyExecutor:
    """
    Ejecutor de estrategia que coordina el flujo de trading.
    
    Flujo:
    1. Recibe señales del MarketAnalyzer
    2. Calcula el tamaño del lote con EnhancedRiskManager
    3. Ejecuta la orden a través del MT5Connector
    4. Registra la operación en el historial
    """

    def __init__(self, risk_manager, mt5_connector, symbol='EURUSD', pip_value=0.0001):
        """
        Inicializa el ejecutor de estrategia.
        
        Args:
            risk_manager (EnhancedRiskManager): Gestor de riesgo
            mt5_connector (MT5Connector): Conector a MetaTrader 5
            symbol (str): Par de divisas a operar
            pip_value (float): Valor del pip
        """
        self.risk_manager = risk_manager
        self.mt5_connector = mt5_connector
        self.symbol = symbol
        self.pip_value = pip_value
        
        # Operaciones abiertas
        self.open_trades = []
        
        # Configuración de confianza mínima para ejecutar
        self.min_confidence = 0.6
        
        # Configuración de filtros
        self.enable_news_filter = True
        self.enable_session_filter = True

    def execute_signal(self, signal, market_analyzer=None):
        """
        Ejecuta una operación basada en una señal de trading.
        
        Args:
            signal (dict): Señal del MarketAnalyzer con estructura:
                {
                    'action': 'BUY'|'SELL'|'HOLD',
                    'confidence': 0-1,
                    'entry_price': float,
                    'stop_loss': float,
                    'take_profit': float,
                    'signals': dict
                }
            market_analyzer (MarketAnalyzer): Analizador de mercado para validaciones adicionales
        
        Returns:
            dict: Resultado de la ejecución
        """
        # Validar confianza mínima
        if signal['confidence'] < self.min_confidence:
            return {
                'executed': False,
                'reason': f"Confianza insuficiente: {signal['confidence']:.2%} < {self.min_confidence:.2%}"
            }
        
        # Validar que no sea HOLD
        if signal['action'] == 'HOLD':
            return {
                'executed': False,
                'reason': 'Señal HOLD - No se ejecuta operación'
            }
        
        # Aplicar filtros
        if self.enable_news_filter and market_analyzer:
            if not self._check_news_filter(market_analyzer):
                return {
                    'executed': False,
                    'reason': 'Filtro de noticias activado - Evento económico próximo'
                }
        
        if self.enable_session_filter and market_analyzer:
            if not self._check_session_filter(market_analyzer):
                return {
                    'executed': False,
                    'reason': 'Filtro de sesión activado - Fuera de horario óptimo'
                }
        
        # Calcular tamaño de posición
        position_info = self.risk_manager.calculate_position_size(
            signal['entry_price'],
            signal['stop_loss'],
            self.pip_value
        )
        
        lot_size = position_info['lot_size']
        
        # Validar que el lote sea válido
        if lot_size <= 0:
            return {
                'executed': False,
                'reason': f'Tamaño de lote inválido: {lot_size}'
            }
        
        # Ejecutar orden en MT5
        try:
            order_result = self._execute_order(
                action=signal['action'],
                lot_size=lot_size,
                entry_price=signal['entry_price'],
                stop_loss=signal['stop_loss'],
                take_profit=signal['take_profit']
            )
            
            if order_result['success']:
                # Registrar operación abierta
                trade = {
                    'order_id': order_result.get('order_id'),
                    'symbol': self.symbol,
                    'action': signal['action'],
                    'entry_price': signal['entry_price'],
                    'lot_size': lot_size,
                    'stop_loss': signal['stop_loss'],
                    'take_profit': signal['take_profit'],
                    'entry_time': datetime.now(),
                    'confidence': signal['confidence'],
                    'signals': signal['signals']
                }
                
                self.open_trades.append(trade)
                
                return {
                    'executed': True,
                    'order_id': order_result.get('order_id'),
                    'action': signal['action'],
                    'lot_size': lot_size,
                    'entry_price': signal['entry_price'],
                    'stop_loss': signal['stop_loss'],
                    'take_profit': signal['take_profit'],
                    'risk_amount': position_info['risk_amount'],
                    'confidence': signal['confidence']
                }
            else:
                return {
                    'executed': False,
                    'reason': order_result.get('error', 'Error desconocido en MT5')
                }
        
        except Exception as e:
            return {
                'executed': False,
                'reason': f'Excepción en ejecución: {str(e)}'
            }

    def _execute_order(self, action, lot_size, entry_price, stop_loss, take_profit):
        """
        Ejecuta una orden en MT5.
        
        Args:
            action (str): 'BUY' o 'SELL'
            lot_size (float): Tamaño del lote
            entry_price (float): Precio de entrada
            stop_loss (float): Precio del stop loss
            take_profit (float): Precio del take profit
        
        Returns:
            dict: Resultado de la ejecución
        """
        try:
            # Ejecutar orden en MT5 real
            order_result = self.mt5_connector.send_order(
                symbol=self.symbol,
                action=action,
                lot_size=lot_size,
                stop_loss=stop_loss,
                take_profit=take_profit,
                comment=f"CallBot_{action}_{datetime.now().isoformat()}"
            )
            
            return order_result
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def close_trade(self, trade_id, exit_price, reason='MANUAL'):
        """
        Cierra una operación abierta.
        
        Args:
            trade_id (str): ID de la operación a cerrar
            exit_price (float): Precio de salida
            reason (str): Razón del cierre ('MANUAL', 'STOP_LOSS', 'TAKE_PROFIT')
        
        Returns:
            dict: Resultado del cierre
        """
        trade = None
        for t in self.open_trades:
            if t['order_id'] == trade_id:
                trade = t
                break
        
        if not trade:
            return {
                'closed': False,
                'reason': f'Operación no encontrada: {trade_id}'
            }
        
        # Calcular ganancia/pérdida
        if trade['action'] == 'BUY':
            pips = (exit_price - trade['entry_price']) / self.pip_value
            profit_loss = pips * trade['lot_size'] * self.pip_value * 10  # Aproximado
        else:  # SELL
            pips = (trade['entry_price'] - exit_price) / self.pip_value
            profit_loss = pips * trade['lot_size'] * self.pip_value * 10  # Aproximado
        
        # Registrar operación en historial
        self.risk_manager.record_trade(
            symbol=trade['symbol'],
            action=trade['action'],
            entry_price=trade['entry_price'],
            exit_price=exit_price,
            lot_size=trade['lot_size'],
            stop_loss=trade['stop_loss'],
            take_profit=trade['take_profit'],
            profit_loss=profit_loss,
            duration_minutes=int((datetime.now() - trade['entry_time']).total_seconds() / 60)
        )
        
        # Remover de operaciones abiertas
        self.open_trades.remove(trade)
        
        return {
            'closed': True,
            'trade_id': trade_id,
            'exit_price': exit_price,
            'profit_loss': profit_loss,
            'reason': reason
        }

    def update_open_trades(self, current_prices):
        """
        Actualiza el estado de las operaciones abiertas.
        
        Args:
            current_prices (dict): Precios actuales por símbolo
        
        Returns:
            list: Operaciones que alcanzaron stop loss o take profit
        """
        closed_trades = []
        
        for trade in self.open_trades[:]:
            current_price = current_prices.get(trade['symbol'])
            
            if not current_price:
                continue
            
            # Verificar stop loss
            if trade['action'] == 'BUY' and current_price <= trade['stop_loss']:
                result = self.close_trade(trade['order_id'], trade['stop_loss'], 'STOP_LOSS')
                closed_trades.append(result)
            
            elif trade['action'] == 'SELL' and current_price >= trade['stop_loss']:
                result = self.close_trade(trade['order_id'], trade['stop_loss'], 'STOP_LOSS')
                closed_trades.append(result)
            
            # Verificar take profit
            elif trade['action'] == 'BUY' and current_price >= trade['take_profit']:
                result = self.close_trade(trade['order_id'], trade['take_profit'], 'TAKE_PROFIT')
                closed_trades.append(result)
            
            elif trade['action'] == 'SELL' and current_price <= trade['take_profit']:
                result = self.close_trade(trade['order_id'], trade['take_profit'], 'TAKE_PROFIT')
                closed_trades.append(result)
        
        return closed_trades

    def _check_news_filter(self, market_analyzer):
        """
        Verifica si hay eventos económicos próximos.
        
        Args:
            market_analyzer (MarketAnalyzer): Analizador de mercado
        
        Returns:
            bool: True si es seguro operar, False si hay evento próximo
        """
        # TODO: Implementar verificación de calendario económico
        # Por ahora, siempre retorna True
        return True

    def _check_session_filter(self, market_analyzer):
        """
        Verifica si estamos en una sesión de trading óptima.
        
        Args:
            market_analyzer (MarketAnalyzer): Analizador de mercado
        
        Returns:
            bool: True si es sesión óptima, False si no
        """
        # TODO: Implementar verificación de sesiones (NY, Londres, Tokio, etc.)
        # Por ahora, siempre retorna True
        return True

    def get_open_trades(self):
        """
        Retorna las operaciones abiertas.
        
        Returns:
            list: Lista de operaciones abiertas
        """
        return self.open_trades

    def get_trade_statistics(self):
        """
        Retorna estadísticas de las operaciones abiertas.
        
        Returns:
            dict: Estadísticas de operaciones abiertas
        """
        total_open_trades = len(self.open_trades)
        total_risk = sum([
            self.risk_manager.calculate_risk_amount() 
            for _ in self.open_trades
        ])
        
        return {
            'total_open_trades': total_open_trades,
            'total_risk': total_risk,
            'account_statistics': self.risk_manager.get_account_statistics()
        }
