"""
Módulo: MT5 Connector Improved
Descripción: Conector mejorado a MetaTrader 5 con manejo robusto de errores,
reconexión automática y validaciones completas.
"""

import MetaTrader5 as mt5
import time
from datetime import datetime
from typing import Optional, Dict, List, Any
from utils.logger import get_logger


class MT5ConnectorImproved:
    """
    Conector mejorado a MetaTrader 5 con características profesionales:
    - Reconexión automática
    - Manejo robusto de errores
    - Validaciones completas
    - Logging estructurado
    - Timeout handling
    """

    def __init__(self, config=None):
        """
        Inicializa el conector mejorado.
        
        Args:
            config: Configuración del conector (opcional)
        """
        self.logger = get_logger()
        self.connected = False
        self.account_info = None
        
        # Configuración
        self.config = config or {}
        self.enable_auto_reconnect = self.config.get('enable_auto_reconnect', True)
        self.reconnect_attempts = self.config.get('reconnect_attempts', 5)
        self.reconnect_delay = self.config.get('reconnect_delay_seconds', 10)
        self.connection_timeout = self.config.get('connection_timeout', 30)
        
        self.logger.info("MT5 Connector initialized", 
                        auto_reconnect=self.enable_auto_reconnect,
                        max_attempts=self.reconnect_attempts)

    def connect(self, path: Optional[str] = None, login: Optional[int] = None, 
                password: Optional[str] = None, server: Optional[str] = None) -> bool:
        """
        Conecta a MetaTrader 5.
        
        Args:
            path (str): Ruta de instalación de MT5
            login (int): Número de cuenta
            password (str): Contraseña
            server (str): Servidor de trading
        
        Returns:
            bool: True si la conexión fue exitosa
        """
        try:
            self.logger.info("Attempting to connect to MT5")
            
            # Inicializar MT5
            if path:
                if not mt5.initialize(path=path, login=login, password=password, server=server):
                    error = mt5.last_error()
                    self.logger.error("Failed to initialize MT5", error=error)
                    return False
            else:
                if not mt5.initialize():
                    error = mt5.last_error()
                    self.logger.error("Failed to initialize MT5", error=error)
                    return False
            
            # Verificar conexión
            account_info = mt5.account_info()
            if account_info is None:
                self.logger.error("Failed to get account info")
                return False
            
            self.connected = True
            self.account_info = account_info
            
            self.logger.info("MT5 connection established", 
                           login=account_info.login,
                           server=account_info.server,
                           balance=account_info.balance,
                           leverage=account_info.leverage)
            
            return True
        
        except Exception as e:
            self.logger.error("Exception during MT5 connection", exception=str(e))
            return False

    def disconnect(self):
        """Desconecta de MetaTrader 5."""
        try:
            if self.connected:
                mt5.shutdown()
                self.connected = False
                self.logger.info("MT5 disconnected")
        except Exception as e:
            self.logger.error("Error during MT5 disconnection", exception=str(e))

    def ensure_connection(self) -> bool:
        """
        Asegura que la conexión esté activa. Reintenta si es necesario.
        
        Returns:
            bool: True si la conexión está activa
        """
        if self.connected and self._check_connection():
            return True
        
        if not self.enable_auto_reconnect:
            return False
        
        self.logger.warning("MT5 connection lost, attempting to reconnect")
        
        for attempt in range(1, self.reconnect_attempts + 1):
            self.logger.info(f"Reconnection attempt {attempt}/{self.reconnect_attempts}")
            
            if self.connect():
                self.logger.info("Reconnection successful")
                return True
            
            if attempt < self.reconnect_attempts:
                time.sleep(self.reconnect_delay)
        
        self.logger.error("Failed to reconnect after all attempts")
        return False

    def _check_connection(self) -> bool:
        """
        Verifica si la conexión está activa.
        
        Returns:
            bool: True si la conexión está activa
        """
        try:
            account_info = mt5.account_info()
            return account_info is not None
        except:
            return False

    def get_account_info(self) -> Optional[Any]:
        """
        Obtiene información de la cuenta.
        
        Returns:
            AccountInfo: Información de la cuenta o None
        """
        if not self.ensure_connection():
            return None
        
        try:
            account_info = mt5.account_info()
            if account_info is None:
                error = mt5.last_error()
                self.logger.error("Failed to get account info", error=error)
                return None
            
            self.account_info = account_info
            return account_info
        
        except Exception as e:
            self.logger.error("Exception getting account info", exception=str(e))
            return None

    def get_symbol_data(self, symbol: str = "EURUSD", timeframe: int = mt5.TIMEFRAME_M1, 
                       bars: int = 500) -> Optional[List[Dict]]:
        """
        Obtiene datos de mercado (velas).
        
        Args:
            symbol (str): Símbolo del par de divisas
            timeframe (int): Timeframe (mt5.TIMEFRAME_M1, etc.)
            bars (int): Número de barras a obtener
        
        Returns:
            list: Lista de velas o None
        """
        if not self.ensure_connection():
            return None
        
        try:
            # Verificar que el símbolo esté disponible
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                self.logger.error("Symbol not found", symbol=symbol)
                return None
            
            if not symbol_info.visible:
                # Intentar hacer visible el símbolo
                if not mt5.symbol_select(symbol, True):
                    self.logger.error("Failed to select symbol", symbol=symbol)
                    return None
            
            # Obtener datos
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
            
            if rates is None:
                error = mt5.last_error()
                self.logger.error("Failed to get rates", symbol=symbol, error=error)
                return None
            
            if len(rates) == 0:
                self.logger.warning("No rates returned", symbol=symbol)
                return None
            
            # Convertir a formato estándar
            candles = []
            for rate in rates:
                candles.append({
                    'time': datetime.fromtimestamp(rate['time']),
                    'open': rate['open'],
                    'high': rate['high'],
                    'low': rate['low'],
                    'close': rate['close'],
                    'volume': rate['tick_volume']
                })
            
            self.logger.debug(f"Retrieved {len(candles)} candles", 
                            symbol=symbol, 
                            timeframe=timeframe,
                            bars=bars)
            
            return candles
        
        except Exception as e:
            self.logger.error("Exception getting symbol data", 
                            symbol=symbol, 
                            exception=str(e))
            return None

    def send_order(self, symbol: str, action: str, lot_size: float, 
                  stop_loss: Optional[float] = None, 
                  take_profit: Optional[float] = None,
                  comment: str = "CallBot") -> Dict:
        """
        Envía una orden al broker.
        
        Args:
            symbol (str): Símbolo del par
            action (str): 'BUY' o 'SELL'
            lot_size (float): Tamaño del lote
            stop_loss (float): Nivel de stop loss (opcional)
            take_profit (float): Nivel de take profit (opcional)
            comment (str): Comentario de la orden
        
        Returns:
            dict: Resultado de la operación
        """
        if not self.ensure_connection():
            return {'success': False, 'error': 'Not connected to MT5'}
        
        try:
            # Validar símbolo
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                return {'success': False, 'error': f'Symbol {symbol} not found'}
            
            # Obtener precio actual
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                return {'success': False, 'error': 'Failed to get current price'}
            
            # Determinar tipo de orden y precio
            if action == 'BUY':
                order_type = mt5.ORDER_TYPE_BUY
                price = tick.ask
            elif action == 'SELL':
                order_type = mt5.ORDER_TYPE_SELL
                price = tick.bid
            else:
                return {'success': False, 'error': f'Invalid action: {action}'}
            
            # Preparar request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot_size,
                "type": order_type,
                "price": price,
                "deviation": 20,
                "magic": 234000,
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Añadir SL y TP si se proporcionan
            if stop_loss is not None:
                request["sl"] = stop_loss
            if take_profit is not None:
                request["tp"] = take_profit
            
            # Enviar orden
            result = mt5.order_send(request)
            
            if result is None:
                error = mt5.last_error()
                self.logger.error("Failed to send order", error=error)
                return {'success': False, 'error': f'MT5 error: {error}'}
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                self.logger.warning("Order not executed", retcode=result.retcode, comment=result.comment)
                return {
                    'success': False, 
                    'error': f'Order failed: {result.comment}',
                    'retcode': result.retcode
                }
            
            # Orden exitosa
            self.logger.log_trade(
                action=action,
                symbol=symbol,
                entry_price=result.price,
                lot_size=lot_size,
                stop_loss=stop_loss,
                take_profit=take_profit,
                order_id=result.order,
                deal_id=result.deal
            )
            
            return {
                'success': True,
                'order_id': result.order,
                'deal_id': result.deal,
                'price': result.price,
                'volume': result.volume,
                'comment': result.comment
            }
        
        except Exception as e:
            self.logger.error("Exception sending order", exception=str(e))
            return {'success': False, 'error': f'Exception: {str(e)}'}

    def close_position(self, ticket: int) -> Dict:
        """
        Cierra una posición abierta.
        
        Args:
            ticket (int): Ticket de la posición
        
        Returns:
            dict: Resultado de la operación
        """
        if not self.ensure_connection():
            return {'success': False, 'error': 'Not connected to MT5'}
        
        try:
            # Obtener información de la posición
            position = mt5.positions_get(ticket=ticket)
            
            if position is None or len(position) == 0:
                return {'success': False, 'error': f'Position {ticket} not found'}
            
            position = position[0]
            
            # Determinar tipo de orden de cierre
            if position.type == mt5.POSITION_TYPE_BUY:
                order_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(position.symbol).bid
            else:
                order_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(position.symbol).ask
            
            # Preparar request de cierre
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": order_type,
                "position": ticket,
                "price": price,
                "deviation": 20,
                "magic": 234000,
                "comment": "CallBot close",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Enviar orden de cierre
            result = mt5.order_send(request)
            
            if result is None:
                error = mt5.last_error()
                return {'success': False, 'error': f'MT5 error: {error}'}
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                return {
                    'success': False,
                    'error': f'Close failed: {result.comment}',
                    'retcode': result.retcode
                }
            
            self.logger.info("Position closed", 
                           ticket=ticket, 
                           price=result.price,
                           profit=position.profit)
            
            return {
                'success': True,
                'ticket': ticket,
                'close_price': result.price,
                'profit': position.profit
            }
        
        except Exception as e:
            self.logger.error("Exception closing position", exception=str(e))
            return {'success': False, 'error': f'Exception: {str(e)}'}

    def get_open_positions(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        Obtiene las posiciones abiertas.
        
        Args:
            symbol (str): Filtrar por símbolo (opcional)
        
        Returns:
            list: Lista de posiciones abiertas
        """
        if not self.ensure_connection():
            return []
        
        try:
            if symbol:
                positions = mt5.positions_get(symbol=symbol)
            else:
                positions = mt5.positions_get()
            
            if positions is None:
                return []
            
            positions_list = []
            for pos in positions:
                positions_list.append({
                    'ticket': pos.ticket,
                    'symbol': pos.symbol,
                    'type': 'BUY' if pos.type == mt5.POSITION_TYPE_BUY else 'SELL',
                    'volume': pos.volume,
                    'price_open': pos.price_open,
                    'price_current': pos.price_current,
                    'sl': pos.sl,
                    'tp': pos.tp,
                    'profit': pos.profit,
                    'comment': pos.comment,
                    'time': datetime.fromtimestamp(pos.time)
                })
            
            return positions_list
        
        except Exception as e:
            self.logger.error("Exception getting positions", exception=str(e))
            return []

    def get_history_deals(self, from_date: datetime, to_date: datetime) -> List[Dict]:
        """
        Obtiene el historial de deals.
        
        Args:
            from_date (datetime): Fecha inicial
            to_date (datetime): Fecha final
        
        Returns:
            list: Lista de deals
        """
        if not self.ensure_connection():
            return []
        
        try:
            deals = mt5.history_deals_get(from_date, to_date)
            
            if deals is None:
                return []
            
            deals_list = []
            for deal in deals:
                deals_list.append({
                    'ticket': deal.ticket,
                    'order': deal.order,
                    'symbol': deal.symbol,
                    'type': deal.type,
                    'volume': deal.volume,
                    'price': deal.price,
                    'profit': deal.profit,
                    'commission': deal.commission,
                    'swap': deal.swap,
                    'comment': deal.comment,
                    'time': datetime.fromtimestamp(deal.time)
                })
            
            return deals_list
        
        except Exception as e:
            self.logger.error("Exception getting history", exception=str(e))
            return []
