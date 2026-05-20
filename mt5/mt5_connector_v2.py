# mt5/mt5_connector_v2.py
"""
Conector MT5 mejorado con reconexión automática
Integración profesional con MetaTrader 5
"""

import MetaTrader5 as mt5
import pandas as pd
import logging
from typing import Optional, Tuple, List, Dict
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)


class MT5ConnectorV2:
    """Conector mejorado a MetaTrader 5"""
    
    def __init__(self, login: int, password: str, server: str, timeout: int = 5000):
        """
        Inicializar conector MT5
        
        Args:
            login: Número de cuenta
            password: Contraseña
            server: Servidor (ej: Exness-MT5)
            timeout: Timeout en ms
        """
        self.login = login
        self.password = password
        self.server = server
        self.timeout = timeout
        self.connected = False
        self.last_error = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        
    def connect(self) -> bool:
        """Conectar a MT5"""
        try:
            if not mt5.initialize(login=self.login, password=self.password, 
                                 server=self.server, timeout=self.timeout):
                self.last_error = f"Fallo al inicializar MT5: {mt5.last_error()}"
                logger.error(self.last_error)
                return False
            
            self.connected = True
            self.reconnect_attempts = 0
            logger.info(f"Conectado a MT5: {self.server}")
            return True
        
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error conectando a MT5: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Desconectar de MT5"""
        try:
            mt5.shutdown()
            self.connected = False
            logger.info("Desconectado de MT5")
            return True
        except Exception as e:
            logger.error(f"Error desconectando: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Verificar si está conectado"""
        try:
            if not self.connected:
                return False
            
            # Verificar conexión enviando un ping
            account_info = mt5.account_info()
            return account_info is not None
        
        except Exception as e:
            logger.warning(f"Conexión perdida: {e}")
            self.connected = False
            return False
    
    def reconnect(self) -> bool:
        """Reconectar automáticamente"""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            logger.error("Máximo de intentos de reconexión alcanzado")
            return False
        
        self.reconnect_attempts += 1
        logger.info(f"Intentando reconectar... ({self.reconnect_attempts}/{self.max_reconnect_attempts})")
        
        self.disconnect()
        time.sleep(2)  # Esperar 2 segundos antes de reconectar
        
        return self.connect()
    
    def get_account_info(self) -> Optional[Dict]:
        """Obtener información de la cuenta"""
        try:
            if not self.is_connected():
                if not self.reconnect():
                    return None
            
            account = mt5.account_info()
            if account is None:
                return None
            
            return {
                'login': account.login,
                'balance': account.balance,
                'equity': account.equity,
                'margin': account.margin,
                'margin_free': account.margin_free,
                'margin_level': account.margin_level,
                'currency': account.currency,
                'profit': account.profit,
                'leverage': account.leverage
            }
        
        except Exception as e:
            logger.error(f"Error obteniendo info de cuenta: {e}")
            return None
    
    def get_candles(self, symbol: str, timeframe: int, count: int = 100) -> Optional[pd.DataFrame]:
        """
        Obtener velas históricas
        
        Args:
            symbol: Símbolo (ej: XAUUSD)
            timeframe: Timeframe en minutos (1, 5, 15, 30, 60, 240, 1440)
            count: Número de velas
        
        Returns:
            DataFrame con velas
        """
        try:
            if not self.is_connected():
                if not self.reconnect():
                    return None
            
            # Convertir minutos a constante MT5
            tf_map = {
                1: mt5.TIMEFRAME_M1,
                5: mt5.TIMEFRAME_M5,
                15: mt5.TIMEFRAME_M15,
                30: mt5.TIMEFRAME_M30,
                60: mt5.TIMEFRAME_H1,
                240: mt5.TIMEFRAME_H4,
                1440: mt5.TIMEFRAME_D1
            }
            
            if timeframe not in tf_map:
                logger.error(f"Timeframe no soportado: {timeframe}")
                return None
            
            # Obtener velas
            rates = mt5.copy_rates_from_pos(symbol, tf_map[timeframe], 0, count)
            
            if rates is None or len(rates) == 0:
                logger.warning(f"No se obtuvieron velas para {symbol}")
                return None
            
            # Convertir a DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df = df[['time', 'open', 'high', 'low', 'close', 'tick_volume', 'real_volume']]
            
            return df
        
        except Exception as e:
            logger.error(f"Error obteniendo velas: {e}")
            return None
    
    def get_tick_data(self, symbol: str, count: int = 100) -> Optional[pd.DataFrame]:
        """Obtener datos de ticks"""
        try:
            if not self.is_connected():
                if not self.reconnect():
                    return None
            
            ticks = mt5.copy_ticks_from_pos(symbol, 0, count, mt5.COPY_TICKS_ALL)
            
            if ticks is None or len(ticks) == 0:
                return None
            
            df = pd.DataFrame(ticks)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            return df
        
        except Exception as e:
            logger.error(f"Error obteniendo ticks: {e}")
            return None
    
    def open_position(self, symbol: str, order_type: str, volume: float, 
                     price: float, sl: float, tp: float, comment: str = "") -> Optional[int]:
        """
        Abrir una posición
        
        Args:
            symbol: Símbolo
            order_type: 'BUY' o 'SELL'
            volume: Volumen/lotes
            price: Precio de entrada
            sl: Stop Loss
            tp: Take Profit
            comment: Comentario
        
        Returns:
            Ticket de la orden o None
        """
        try:
            if not self.is_connected():
                if not self.reconnect():
                    return None
            
            # Preparar orden
            order_type_map = {
                'BUY': mt5.ORDER_TYPE_BUY,
                'SELL': mt5.ORDER_TYPE_SELL
            }
            
            request = {
                'action': mt5.TRADE_ACTION_DEAL,
                'symbol': symbol,
                'volume': volume,
                'type': order_type_map.get(order_type),
                'price': price,
                'sl': sl,
                'tp': tp,
                'comment': comment,
                'type_time': mt5.ORDER_TIME_GTC,
                'type_filling': mt5.ORDER_FILLING_IOC
            }
            
            # Enviar orden
            result = mt5.order_send(request)
            
            if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"Error abriendo posición: {mt5.last_error()}")
                return None
            
            logger.info(f"Posición abierta: {result.order}")
            return result.order
        
        except Exception as e:
            logger.error(f"Error abriendo posición: {e}")
            return None
    
    def close_position(self, ticket: int, volume: Optional[float] = None) -> bool:
        """
        Cerrar una posición
        
        Args:
            ticket: Ticket de la posición
            volume: Volumen a cerrar (None = todo)
        
        Returns:
            True si se cerró correctamente
        """
        try:
            if not self.is_connected():
                if not self.reconnect():
                    return False
            
            # Obtener posición
            position = mt5.positions_get(ticket=ticket)
            
            if position is None or len(position) == 0:
                logger.error(f"Posición no encontrada: {ticket}")
                return False
            
            pos = position[0]
            
            # Preparar orden de cierre
            order_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
            close_volume = volume if volume else pos.volume
            
            request = {
                'action': mt5.TRADE_ACTION_DEAL,
                'symbol': pos.symbol,
                'volume': close_volume,
                'type': order_type,
                'position': ticket,
                'type_time': mt5.ORDER_TIME_GTC,
                'type_filling': mt5.ORDER_FILLING_IOC
            }
            
            # Enviar orden
            result = mt5.order_send(request)
            
            if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"Error cerrando posición: {mt5.last_error()}")
                return False
            
            logger.info(f"Posición cerrada: {ticket}")
            return True
        
        except Exception as e:
            logger.error(f"Error cerrando posición: {e}")
            return False
    
    def get_open_positions(self, symbol: Optional[str] = None) -> List[Dict]:
        """Obtener posiciones abiertas"""
        try:
            if not self.is_connected():
                if not self.reconnect():
                    return []
            
            if symbol:
                positions = mt5.positions_get(symbol=symbol)
            else:
                positions = mt5.positions_get()
            
            if positions is None:
                return []
            
            result = []
            for pos in positions:
                result.append({
                    'ticket': pos.ticket,
                    'symbol': pos.symbol,
                    'type': 'BUY' if pos.type == mt5.ORDER_TYPE_BUY else 'SELL',
                    'volume': pos.volume,
                    'price_open': pos.price_open,
                    'sl': pos.sl,
                    'tp': pos.tp,
                    'profit': pos.profit,
                    'time': datetime.fromtimestamp(pos.time),
                    'comment': pos.comment
                })
            
            return result
        
        except Exception as e:
            logger.error(f"Error obteniendo posiciones: {e}")
            return []
    
    def get_closed_deals(self, symbol: Optional[str] = None, count: int = 100) -> List[Dict]:
        """Obtener operaciones cerradas"""
        try:
            if not self.is_connected():
                if not self.reconnect():
                    return []
            
            if symbol:
                deals = mt5.history_deals_get(symbol=symbol)
            else:
                deals = mt5.history_deals_get()
            
            if deals is None:
                return []
            
            result = []
            for deal in deals[-count:]:
                result.append({
                    'ticket': deal.ticket,
                    'symbol': deal.symbol,
                    'type': 'BUY' if deal.type == mt5.DEAL_TYPE_BUY else 'SELL',
                    'volume': deal.volume,
                    'price': deal.price,
                    'profit': deal.profit,
                    'commission': deal.commission,
                    'time': datetime.fromtimestamp(deal.time),
                    'comment': deal.comment
                })
            
            return result
        
        except Exception as e:
            logger.error(f"Error obteniendo deals: {e}")
            return []
