"""
Módulo: Enhanced Risk Manager
Descripción: Gestión de capital compuesto con riesgo del 1% y ajuste dinámico de lotes.
Implementa el sistema de gestión de capital del trader profesional.
"""

from datetime import datetime
import json
import os


class EnhancedRiskManager:
    """
    Gestor de riesgo mejorado que implementa la estrategia de gestión de capital compuesto.
    
    Características:
    - Riesgo fijo del 1% por operación
    - Ajuste dinámico del tamaño del lote basado en el balance actual
    - Seguimiento del historial de operaciones
    - Cálculo de métricas de rendimiento
    """

    def __init__(self, initial_balance, risk_percent=1.0, min_lot_size=0.01, max_lot_size=10.0):
        """
        Inicializa el gestor de riesgo mejorado.
        
        Args:
            initial_balance (float): Balance inicial de la cuenta (ej: 100 USD)
            risk_percent (float): Porcentaje de riesgo por operación (default: 1%)
            min_lot_size (float): Tamaño mínimo de lote permitido (default: 0.01)
            max_lot_size (float): Tamaño máximo de lote permitido (default: 10.0)
        """
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.risk_percent = risk_percent
        self.min_lot_size = min_lot_size
        self.max_lot_size = max_lot_size
        
        # Historial de operaciones
        self.trades_history = []
        self.monthly_returns = {}
        
        # Estadísticas
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_profit = 0
        self.total_loss = 0

    def calculate_risk_amount(self):
        """
        Calcula el monto de riesgo para la operación actual (1% del balance).
        
        Returns:
            float: Monto en USD a arriesgar en la operación
        """
        return self.current_balance * (self.risk_percent / 100)

    def calculate_lot_size(self, stop_loss_pips, pip_value=0.0001, account_currency_value=1.0):
        """
        Calcula el tamaño del lote dinámico basado en el riesgo del 1%.
        
        Fórmula: Lot Size = Risk Amount / (Stop Loss Pips * Pip Value * Account Currency Value)
        
        Args:
            stop_loss_pips (float): Distancia del stop loss en pips (ej: 50)
            pip_value (float): Valor del pip (default: 0.0001 para pares mayor)
            account_currency_value (float): Valor de la moneda de la cuenta (default: 1.0)
        
        Returns:
            float: Tamaño del lote ajustado al riesgo del 1%
        """
        if stop_loss_pips <= 0:
            return self.min_lot_size
        
        risk_amount = self.calculate_risk_amount()
        
        # Calcular tamaño del lote
        lot_size = risk_amount / (stop_loss_pips * pip_value * account_currency_value)
        
        # Aplicar límites
        lot_size = max(self.min_lot_size, min(lot_size, self.max_lot_size))
        
        # Redondear a 2 decimales
        return round(lot_size, 2)

    def calculate_position_size(self, entry_price, stop_loss_price, pip_value=0.0001):
        """
        Calcula el tamaño de la posición basado en la distancia entre entry y stop loss.
        
        Args:
            entry_price (float): Precio de entrada
            stop_loss_price (float): Precio del stop loss
            pip_value (float): Valor del pip
        
        Returns:
            dict: {
                'lot_size': float,
                'stop_loss_pips': float,
                'risk_amount': float
            }
        """
        stop_loss_pips = abs(entry_price - stop_loss_price) / pip_value
        lot_size = self.calculate_lot_size(stop_loss_pips, pip_value)
        risk_amount = self.calculate_risk_amount()
        
        return {
            'lot_size': lot_size,
            'stop_loss_pips': stop_loss_pips,
            'risk_amount': risk_amount
        }

    def record_trade(self, symbol, action, entry_price, exit_price, lot_size, 
                    stop_loss, take_profit, profit_loss, duration_minutes=None):
        """
        Registra una operación completada en el historial.
        
        Args:
            symbol (str): Par de divisas (ej: 'EURUSD')
            action (str): 'BUY' o 'SELL'
            entry_price (float): Precio de entrada
            exit_price (float): Precio de salida
            lot_size (float): Tamaño del lote utilizado
            stop_loss (float): Nivel de stop loss
            take_profit (float): Nivel de take profit
            profit_loss (float): Ganancia o pérdida en USD
            duration_minutes (int): Duración de la operación en minutos
        """
        trade = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'action': action,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'lot_size': lot_size,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'profit_loss': profit_loss,
            'duration_minutes': duration_minutes,
            'balance_before': self.current_balance - profit_loss,
            'balance_after': self.current_balance
        }
        
        self.trades_history.append(trade)
        
        # Actualizar balance
        self.current_balance += profit_loss
        
        # Actualizar estadísticas
        self.total_trades += 1
        if profit_loss > 0:
            self.winning_trades += 1
            self.total_profit += profit_loss
        else:
            self.losing_trades += 1
            self.total_loss += abs(profit_loss)
        
        # Registrar en historial mensual
        month_key = datetime.now().strftime('%Y-%m')
        if month_key not in self.monthly_returns:
            self.monthly_returns[month_key] = {
                'trades': 0,
                'profit': 0,
                'loss': 0,
                'return_percent': 0
            }
        
        self.monthly_returns[month_key]['trades'] += 1
        if profit_loss > 0:
            self.monthly_returns[month_key]['profit'] += profit_loss
        else:
            self.monthly_returns[month_key]['loss'] += abs(profit_loss)

    def update_balance(self, new_balance):
        """
        Actualiza el balance actual de la cuenta.
        
        Args:
            new_balance (float): Nuevo balance de la cuenta
        """
        self.current_balance = new_balance

    def get_account_statistics(self):
        """
        Retorna las estadísticas de la cuenta.
        
        Returns:
            dict: Estadísticas completas de trading
        """
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        total_return = self.current_balance - self.initial_balance
        return_percent = (total_return / self.initial_balance * 100) if self.initial_balance > 0 else 0
        profit_factor = (self.total_profit / self.total_loss) if self.total_loss > 0 else 0
        
        return {
            'initial_balance': self.initial_balance,
            'current_balance': self.current_balance,
            'total_return': total_return,
            'return_percent': return_percent,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': win_rate,
            'total_profit': self.total_profit,
            'total_loss': self.total_loss,
            'profit_factor': profit_factor,
            'average_profit_per_trade': (total_return / self.total_trades) if self.total_trades > 0 else 0
        }

    def get_monthly_statistics(self, month=None):
        """
        Retorna las estadísticas de un mes específico.
        
        Args:
            month (str): Mes en formato 'YYYY-MM' (default: mes actual)
        
        Returns:
            dict: Estadísticas del mes
        """
        if month is None:
            month = datetime.now().strftime('%Y-%m')
        
        if month not in self.monthly_returns:
            return None
        
        month_data = self.monthly_returns[month]
        month_profit = month_data['profit'] - month_data['loss']
        
        # Calcular balance inicial del mes (aproximado)
        # Buscar el balance antes de la primera operación del mes
        month_trades = [t for t in self.trades_history if t['timestamp'].startswith(month)]
        if month_trades:
            month_initial_balance = month_trades[0]['balance_before']
        else:
            month_initial_balance = self.current_balance
        
        month_return_percent = (month_profit / month_initial_balance * 100) if month_initial_balance > 0 else 0
        
        return {
            'month': month,
            'trades': month_data['trades'],
            'profit': month_data['profit'],
            'loss': month_data['loss'],
            'net_profit': month_profit,
            'return_percent': month_return_percent
        }

    def get_trades_history(self, limit=None):
        """
        Retorna el historial de operaciones.
        
        Args:
            limit (int): Número máximo de operaciones a retornar (default: todas)
        
        Returns:
            list: Historial de operaciones
        """
        if limit:
            return self.trades_history[-limit:]
        return self.trades_history

    def calculate_compound_growth(self, months=12):
        """
        Calcula el crecimiento compuesto proyectado basado en retornos históricos.
        
        Args:
            months (int): Número de meses a proyectar
        
        Returns:
            dict: Proyección de crecimiento
        """
        if not self.monthly_returns:
            return {
                'projected_balance': self.current_balance,
                'projected_growth': 0,
                'average_monthly_return': 0
            }
        
        # Calcular retorno promedio mensual
        total_return = 0
        valid_months = 0
        
        for month_data in self.monthly_returns.values():
            if month_data['trades'] > 0:
                month_profit = month_data['profit'] - month_data['loss']
                total_return += month_profit
                valid_months += 1
        
        average_monthly_return = total_return / valid_months if valid_months > 0 else 0
        
        # Proyectar crecimiento compuesto
        projected_balance = self.current_balance
        for _ in range(months):
            projected_balance += average_monthly_return
        
        projected_growth = ((projected_balance - self.current_balance) / self.current_balance * 100) if self.current_balance > 0 else 0
        
        return {
            'current_balance': self.current_balance,
            'projected_balance': projected_balance,
            'projected_growth': projected_growth,
            'average_monthly_return': average_monthly_return,
            'projection_months': months
        }

    def export_statistics(self, filepath):
        """
        Exporta las estadísticas a un archivo JSON.
        
        Args:
            filepath (str): Ruta del archivo para guardar
        """
        data = {
            'account_statistics': self.get_account_statistics(),
            'monthly_statistics': self.monthly_returns,
            'trades_history': self.trades_history,
            'compound_growth': self.calculate_compound_growth()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def reset_statistics(self):
        """
        Reinicia las estadísticas (mantiene el balance actual).
        """
        self.trades_history = []
        self.monthly_returns = {}
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_profit = 0
        self.total_loss = 0
