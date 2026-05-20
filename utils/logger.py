"""
Módulo: Advanced Logger
Descripción: Sistema de logging estructurado JSON con rotación automática
y múltiples niveles de severidad.
"""

import logging
import json
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path


class StructuredLogger:
    """
    Logger estructurado que guarda logs en formato JSON con rotación automática.
    
    Features:
    - Logging en formato JSON para análisis
    - Rotación automática de archivos
    - Niveles: DEBUG, INFO, WARNING, ERROR, CRITICAL
    - Contexto adicional (módulo, función, operación, etc.)
    - Separación de logs por severidad
    """

    def __init__(self, name="CallBot", log_dir="logs", max_bytes=10*1024*1024, backup_count=5):
        """
        Inicializa el logger estructurado.
        
        Args:
            name (str): Nombre del logger
            log_dir (str): Directorio para los archivos de log
            max_bytes (int): Tamaño máximo por archivo (default: 10MB)
            backup_count (int): Número de backups a mantener
        """
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Crear loggers separados por severidad
        self.loggers = {}
        self._setup_loggers(max_bytes, backup_count)

    def _setup_loggers(self, max_bytes, backup_count):
        """Configura los loggers para cada nivel de severidad."""
        
        levels = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL
        }
        
        for level_name, level_value in levels.items():
            logger = logging.getLogger(f"{self.name}_{level_name}")
            logger.setLevel(level_value)
            logger.handlers.clear()
            
            # Handler para archivo con rotación
            log_file = self.log_dir / f"{level_name}.log"
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count
            )
            file_handler.setLevel(level_value)
            
            # Handler para consola
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level_value)
            
            # Formato JSON
            formatter = logging.Formatter('%(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
            
            self.loggers[level_name] = logger

    def _format_message(self, level, message, **context):
        """
        Formatea el mensaje como JSON estructurado.
        
        Args:
            level (str): Nivel de log
            message (str): Mensaje principal
            **context: Contexto adicional
        
        Returns:
            str: Mensaje en formato JSON
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level.upper(),
            'logger': self.name,
            'message': message
        }
        
        # Añadir contexto adicional
        if context:
            log_entry['context'] = context
        
        return json.dumps(log_entry, ensure_ascii=False)

    def debug(self, message, **context):
        """Log nivel DEBUG."""
        formatted = self._format_message('debug', message, **context)
        self.loggers['debug'].debug(formatted)

    def info(self, message, **context):
        """Log nivel INFO."""
        formatted = self._format_message('info', message, **context)
        self.loggers['info'].info(formatted)

    def warning(self, message, **context):
        """Log nivel WARNING."""
        formatted = self._format_message('warning', message, **context)
        self.loggers['warning'].warning(formatted)

    def error(self, message, **context):
        """Log nivel ERROR."""
        formatted = self._format_message('error', message, **context)
        self.loggers['error'].error(formatted)

    def critical(self, message, **context):
        """Log nivel CRITICAL."""
        formatted = self._format_message('critical', message, **context)
        self.loggers['critical'].critical(formatted)

    def log_trade(self, action, symbol, entry_price, lot_size, stop_loss, take_profit, **additional):
        """
        Log especializado para operaciones de trading.
        
        Args:
            action (str): BUY/SELL
            symbol (str): Par de divisas
            entry_price (float): Precio de entrada
            lot_size (float): Tamaño del lote
            stop_loss (float): Stop loss
            take_profit (float): Take profit
            **additional: Datos adicionales
        """
        context = {
            'type': 'TRADE',
            'action': action,
            'symbol': symbol,
            'entry_price': entry_price,
            'lot_size': lot_size,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            **additional
        }
        self.info(f"Trade executed: {action} {symbol}", **context)

    def log_signal(self, action, confidence, signals, **additional):
        """
        Log especializado para señales de trading.
        
        Args:
            action (str): BUY/SELL/HOLD
            confidence (float): Confianza de la señal
            signals (dict): Señales individuales
            **additional: Datos adicionales
        """
        context = {
            'type': 'SIGNAL',
            'action': action,
            'confidence': confidence,
            'signals': signals,
            **additional
        }
        self.info(f"Signal generated: {action} (confidence: {confidence:.2%})", **context)

    def log_risk_event(self, event_type, description, **additional):
        """
        Log especializado para eventos de riesgo.
        
        Args:
            event_type (str): Tipo de evento (DRAWDOWN, STOP_OUT, etc.)
            description (str): Descripción del evento
            **additional: Datos adicionales
        """
        context = {
            'type': 'RISK_EVENT',
            'event_type': event_type,
            'description': description,
            **additional
        }
        self.warning(f"Risk event: {event_type}", **context)

    def log_performance(self, metrics, **additional):
        """
        Log especializado para métricas de rendimiento.
        
        Args:
            metrics (dict): Métricas de rendimiento
            **additional: Datos adicionales
        """
        context = {
            'type': 'PERFORMANCE',
            'metrics': metrics,
            **additional
        }
        self.info("Performance metrics updated", **context)

    def log_system_event(self, event_type, description, **additional):
        """
        Log especializado para eventos del sistema.
        
        Args:
            event_type (str): Tipo de evento (STARTUP, SHUTDOWN, ERROR, etc.)
            description (str): Descripción del evento
            **additional: Datos adicionales
        """
        context = {
            'type': 'SYSTEM_EVENT',
            'event_type': event_type,
            'description': description,
            **additional
        }
        
        if event_type in ['ERROR', 'CRITICAL']:
            self.error(f"System event: {event_type}", **context)
        else:
            self.info(f"System event: {event_type}", **context)


# Singleton global
_global_logger = None


def get_logger(name="CallBot"):
    """
    Obtiene el logger global (singleton).
    
    Args:
        name (str): Nombre del logger
    
    Returns:
        StructuredLogger: Instancia del logger
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = StructuredLogger(name)
    return _global_logger


# Funciones de conveniencia
def log_trade(action, symbol, entry_price, lot_size, stop_loss, take_profit, **kwargs):
    """Wrapper para log_trade."""
    get_logger().log_trade(action, symbol, entry_price, lot_size, stop_loss, take_profit, **kwargs)


def log_signal(action, confidence, signals, **kwargs):
    """Wrapper para log_signal."""
    get_logger().log_signal(action, confidence, signals, **kwargs)


def log_risk_event(event_type, description, **kwargs):
    """Wrapper para log_risk_event."""
    get_logger().log_risk_event(event_type, description, **kwargs)


def log_performance(metrics, **kwargs):
    """Wrapper para log_performance."""
    get_logger().log_performance(metrics, **kwargs)


def log_system_event(event_type, description, **kwargs):
    """Wrapper para log_system_event."""
    get_logger().log_system_event(event_type, description, **kwargs)
