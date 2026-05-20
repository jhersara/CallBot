"""
Módulo: Advanced Risk Manager
Descripción: Gestión profesional de riesgo con Trailing Stop, Break-even automático
y soporte para múltiples activos.
"""

class AdvancedRiskManager:
    """
    Gestor de riesgo avanzado con características institucionales.
    """

    def __init__(self, initial_balance=1000):
        """
        Inicializa el gestor de riesgo avanzado.
        
        Args:
            initial_balance (float): Balance inicial.
        """
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.open_trades = {}
        self.closed_trades = []
        self.risk_per_trade = 0.01  # 1% por operación

    def calculate_position_size(self, entry_price, stop_loss, symbol="EURUSD"):
        """
        Calcula el tamaño de la posición basado en el riesgo del 1%.
        
        Args:
            entry_price (float): Precio de entrada.
            stop_loss (float): Precio del stop loss.
            symbol (str): Símbolo del activo.
            
        Returns:
            float: Tamaño de la posición en lotes.
        """
        risk_amount = self.current_balance * self.risk_per_trade
        pips_at_risk = abs(entry_price - stop_loss) / 0.0001  # Para EURUSD
        
        # Ajustar para diferentes símbolos
        if symbol.endswith("JPY"):
            pips_at_risk = abs(entry_price - stop_loss) / 0.01
        
        position_size = risk_amount / (pips_at_risk * 10)  # 10 USD por pip por lote
        return max(position_size, 0.01)

    def set_trailing_stop(self, trade_id, entry_price, initial_stop_loss, trailing_distance=50):
        """
        Configura un Trailing Stop inteligente basado en la estructura del mercado.
        
        Args:
            trade_id (str): ID de la operación.
            entry_price (float): Precio de entrada.
            initial_stop_loss (float): Stop loss inicial.
            trailing_distance (int): Distancia del trailing en pips.
        """
        if trade_id in self.open_trades:
            self.open_trades[trade_id]['trailing_stop'] = {
                'enabled': True,
                'initial_sl': initial_stop_loss,
                'trailing_distance': trailing_distance,
                'highest_high': entry_price,
                'lowest_low': entry_price
            }

    def update_trailing_stop(self, trade_id, current_price, direction="BUY"):
        """
        Actualiza el Trailing Stop basado en el precio actual.
        
        Args:
            trade_id (str): ID de la operación.
            current_price (float): Precio actual.
            direction (str): Dirección de la operación (BUY o SELL).
            
        Returns:
            dict: Información del trailing stop actualizado.
        """
        if trade_id not in self.open_trades:
            return None
            
        trade = self.open_trades[trade_id]
        if not trade.get('trailing_stop', {}).get('enabled'):
            return None
            
        ts = trade['trailing_stop']
        
        if direction == "BUY":
            # Para compras, el trailing stop sube con nuevos máximos
            if current_price > ts['highest_high']:
                ts['highest_high'] = current_price
                new_sl = current_price - (ts['trailing_distance'] * 0.0001)
                ts['current_sl'] = max(new_sl, ts['initial_sl'])
        else:
            # Para ventas, el trailing stop baja con nuevos mínimos
            if current_price < ts['lowest_low']:
                ts['lowest_low'] = current_price
                new_sl = current_price + (ts['trailing_distance'] * 0.0001)
                ts['current_sl'] = min(new_sl, ts['initial_sl'])
                
        return ts

    def set_breakeven(self, trade_id, entry_price, first_target_pips=50):
        """
        Configura el Break-even automático.
        Una vez que la operación gana X pips, mueve el SL al punto de entrada.
        
        Args:
            trade_id (str): ID de la operación.
            entry_price (float): Precio de entrada.
            first_target_pips (int): Pips necesarios para activar BE.
        """
        if trade_id in self.open_trades:
            self.open_trades[trade_id]['breakeven'] = {
                'enabled': True,
                'entry_price': entry_price,
                'first_target_pips': first_target_pips,
                'activated': False
            }

    def check_breakeven_activation(self, trade_id, current_price, direction="BUY"):
        """
        Verifica si el Break-even debe activarse.
        
        Args:
            trade_id (str): ID de la operación.
            current_price (float): Precio actual.
            direction (str): Dirección de la operación.
            
        Returns:
            bool: True si BE fue activado.
        """
        if trade_id not in self.open_trades:
            return False
            
        trade = self.open_trades[trade_id]
        if not trade.get('breakeven', {}).get('enabled'):
            return False
            
        be = trade['breakeven']
        pips_gained = abs(current_price - be['entry_price']) / 0.0001
        
        if pips_gained >= be['first_target_pips'] and not be['activated']:
            be['activated'] = True
            trade['stop_loss'] = be['entry_price']
            return True
            
        return False

    def add_trade(self, trade_id, entry_price, stop_loss, take_profit, direction="BUY", symbol="EURUSD"):
        """
        Registra una nueva operación abierta.
        
        Args:
            trade_id (str): ID único de la operación.
            entry_price (float): Precio de entrada.
            stop_loss (float): Precio del stop loss.
            take_profit (float): Precio del take profit.
            direction (str): Dirección (BUY o SELL).
            symbol (str): Símbolo del activo.
        """
        self.open_trades[trade_id] = {
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'direction': direction,
            'symbol': symbol,
            'position_size': self.calculate_position_size(entry_price, stop_loss, symbol),
            'trailing_stop': None,
            'breakeven': None,
            'status': 'OPEN'
        }

    def close_trade(self, trade_id, close_price, reason="MANUAL"):
        """
        Cierra una operación y registra el resultado.
        
        Args:
            trade_id (str): ID de la operación.
            close_price (float): Precio de cierre.
            reason (str): Razón del cierre (SL, TP, MANUAL, etc.).
        """
        if trade_id not in self.open_trades:
            return None
            
        trade = self.open_trades[trade_id]
        
        # Calcular P&L
        if trade['direction'] == 'BUY':
            pnl = (close_price - trade['entry_price']) * trade['position_size'] * 10
        else:
            pnl = (trade['entry_price'] - close_price) * trade['position_size'] * 10
            
        trade['close_price'] = close_price
        trade['pnl'] = pnl
        trade['reason'] = reason
        trade['status'] = 'CLOSED'
        
        # Actualizar balance
        self.current_balance += pnl
        
        # Mover a historial
        self.closed_trades.append(trade)
        del self.open_trades[trade_id]
        
        return trade

    def get_portfolio_stats(self):
        """
        Retorna estadísticas del portafolio.
        
        Returns:
            dict: Estadísticas consolidadas.
        """
        if not self.closed_trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'total_pnl': 0,
                'open_trades': len(self.open_trades)
            }
            
        wins = sum(1 for t in self.closed_trades if t['pnl'] > 0)
        total = len(self.closed_trades)
        
        gross_profit = sum(t['pnl'] for t in self.closed_trades if t['pnl'] > 0)
        gross_loss = abs(sum(t['pnl'] for t in self.closed_trades if t['pnl'] < 0))
        
        return {
            'total_trades': total,
            'win_rate': wins / total if total > 0 else 0,
            'profit_factor': gross_profit / gross_loss if gross_loss > 0 else gross_profit,
            'total_pnl': sum(t['pnl'] for t in self.closed_trades),
            'open_trades': len(self.open_trades),
            'current_balance': self.current_balance
        }
