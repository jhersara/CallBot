"""
Módulo: Config Manager
Descripción: Sistema de configuración centralizado con validación y soporte
para múltiples entornos (desarrollo, producción).
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict, field


@dataclass
class TradingConfig:
    """Configuración de parámetros de trading."""
    initial_balance: float = 100.0
    risk_percent: float = 1.0
    min_confidence: float = 0.6
    min_lot_size: float = 0.01
    max_lot_size: float = 10.0
    
    # Stop Loss y Take Profit (en pips)
    default_stop_loss_pips: int = 50
    default_take_profit_pips: int = 100
    
    # Trailing Stop
    enable_trailing_stop: bool = True
    trailing_stop_pips: int = 30
    breakeven_pips: int = 20
    
    # Filtros
    enable_news_filter: bool = True
    enable_session_filter: bool = True
    enable_spread_filter: bool = True
    max_spread_pips: int = 3


@dataclass
class MT5Config:
    """Configuración de MetaTrader 5."""
    symbol: str = 'EURUSD'
    timeframe: str = 'M1'  # M1, M5, M15, H1, H4, D1
    pip_value: float = 0.0001
    bars_to_load: int = 500
    
    # Reconexión automática
    enable_auto_reconnect: bool = True
    reconnect_attempts: int = 5
    reconnect_delay_seconds: int = 10
    
    # Timeout
    connection_timeout: int = 30
    order_timeout: int = 60


@dataclass
class RiskConfig:
    """Configuración de gestión de riesgo."""
    max_daily_loss_percent: float = 5.0
    max_drawdown_percent: float = 20.0
    max_concurrent_trades: int = 3
    max_correlation_exposure: float = 0.7
    
    # Circuit breaker
    enable_circuit_breaker: bool = True
    circuit_breaker_loss_percent: float = 10.0
    
    # Position sizing
    use_kelly_criterion: bool = False
    kelly_fraction: float = 0.25


@dataclass
class AIConfig:
    """Configuración de IA y Machine Learning."""
    enable_ai: bool = True
    enable_market_classifier: bool = True
    enable_signal_optimizer: bool = True
    
    # Modelos
    retrain_frequency_days: int = 30
    min_training_samples: int = 1000
    
    # Feature engineering
    lookback_periods: list = field(default_factory=lambda: [10, 20, 50, 100])
    
    # Regímenes de mercado
    regime_adaptation: bool = True


@dataclass
class DashboardConfig:
    """Configuración del dashboard."""
    enable_web_dashboard: bool = True
    dashboard_host: str = 'localhost'
    dashboard_port: int = 8501
    
    # API
    api_host: str = 'localhost'
    api_port: int = 8000
    
    # WebSocket
    websocket_port: int = 8765
    enable_websocket: bool = True
    
    # Actualización
    update_interval_seconds: int = 1


@dataclass
class LoggingConfig:
    """Configuración de logging."""
    log_level: str = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_dir: str = 'logs'
    max_log_size_mb: int = 10
    backup_count: int = 5
    
    # Logging especializado
    log_trades: bool = True
    log_signals: bool = True
    log_performance: bool = True
    log_risk_events: bool = True


@dataclass
class NotificationConfig:
    """Configuración de notificaciones."""
    enable_telegram: bool = False
    telegram_bot_token: str = ''
    telegram_chat_id: str = ''
    
    # Alertas
    notify_on_trade: bool = True
    notify_on_risk_event: bool = True
    notify_on_daily_summary: bool = True


class ConfigManager:
    """
    Gestor centralizado de configuración con validación y soporte para
    múltiples entornos.
    """

    def __init__(self, config_file: Optional[str] = None, env: str = 'development'):
        """
        Inicializa el gestor de configuración.
        
        Args:
            config_file (str): Ruta al archivo de configuración JSON
            env (str): Entorno (development, production)
        """
        self.env = env
        self.config_file = config_file or f'config/config_{env}.json'
        
        # Inicializar configuraciones con valores por defecto
        self.trading = TradingConfig()
        self.mt5 = MT5Config()
        self.risk = RiskConfig()
        self.ai = AIConfig()
        self.dashboard = DashboardConfig()
        self.logging = LoggingConfig()
        self.notification = NotificationConfig()
        
        # Cargar configuración desde archivo si existe
        self._load_config()
        
        # Cargar variables de entorno (sobrescriben archivo)
        self._load_env_variables()
        
        # Validar configuración
        self._validate_config()

    def _load_config(self):
        """Carga la configuración desde archivo JSON."""
        config_path = Path(self.config_file)
        
        if not config_path.exists():
            return
        
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
            
            # Cargar cada sección
            if 'trading' in data:
                self.trading = TradingConfig(**data['trading'])
            if 'mt5' in data:
                self.mt5 = MT5Config(**data['mt5'])
            if 'risk' in data:
                self.risk = RiskConfig(**data['risk'])
            if 'ai' in data:
                self.ai = AIConfig(**data['ai'])
            if 'dashboard' in data:
                self.dashboard = DashboardConfig(**data['dashboard'])
            if 'logging' in data:
                self.logging = LoggingConfig(**data['logging'])
            if 'notification' in data:
                self.notification = NotificationConfig(**data['notification'])
        
        except Exception as e:
            print(f"[!] Error loading config file: {str(e)}")

    def _load_env_variables(self):
        """Carga variables de entorno (sobrescriben archivo)."""
        
        # Trading
        if os.getenv('INITIAL_BALANCE'):
            self.trading.initial_balance = float(os.getenv('INITIAL_BALANCE'))
        if os.getenv('RISK_PERCENT'):
            self.trading.risk_percent = float(os.getenv('RISK_PERCENT'))
        if os.getenv('MIN_CONFIDENCE'):
            self.trading.min_confidence = float(os.getenv('MIN_CONFIDENCE'))
        
        # MT5
        if os.getenv('MT5_SYMBOL'):
            self.mt5.symbol = os.getenv('MT5_SYMBOL')
        if os.getenv('MT5_TIMEFRAME'):
            self.mt5.timeframe = os.getenv('MT5_TIMEFRAME')
        
        # Dashboard
        if os.getenv('DASHBOARD_PORT'):
            self.dashboard.dashboard_port = int(os.getenv('DASHBOARD_PORT'))
        
        # Telegram
        if os.getenv('TELEGRAM_BOT_TOKEN'):
            self.notification.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
            self.notification.enable_telegram = True
        if os.getenv('TELEGRAM_CHAT_ID'):
            self.notification.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')

    def _validate_config(self):
        """Valida la configuración."""
        
        # Validar trading
        assert 0 < self.trading.risk_percent <= 5, "Risk percent debe estar entre 0 y 5%"
        assert 0 <= self.trading.min_confidence <= 1, "Min confidence debe estar entre 0 y 1"
        assert self.trading.min_lot_size > 0, "Min lot size debe ser positivo"
        assert self.trading.max_lot_size >= self.trading.min_lot_size, "Max lot >= Min lot"
        
        # Validar risk
        assert 0 < self.risk.max_daily_loss_percent <= 100, "Max daily loss debe estar entre 0 y 100%"
        assert 0 < self.risk.max_drawdown_percent <= 100, "Max drawdown debe estar entre 0 y 100%"
        assert self.risk.max_concurrent_trades > 0, "Max concurrent trades debe ser positivo"
        
        # Validar MT5
        assert self.mt5.pip_value > 0, "Pip value debe ser positivo"
        assert self.mt5.bars_to_load > 0, "Bars to load debe ser positivo"

    def save_config(self, filepath: Optional[str] = None):
        """
        Guarda la configuración actual en archivo JSON.
        
        Args:
            filepath (str): Ruta del archivo (default: self.config_file)
        """
        filepath = filepath or self.config_file
        config_path = Path(filepath)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'trading': asdict(self.trading),
            'mt5': asdict(self.mt5),
            'risk': asdict(self.risk),
            'ai': asdict(self.ai),
            'dashboard': asdict(self.dashboard),
            'logging': asdict(self.logging),
            'notification': asdict(self.notification)
        }
        
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=2)

    def get_all_config(self) -> Dict[str, Any]:
        """
        Retorna toda la configuración como diccionario.
        
        Returns:
            dict: Configuración completa
        """
        return {
            'trading': asdict(self.trading),
            'mt5': asdict(self.mt5),
            'risk': asdict(self.risk),
            'ai': asdict(self.ai),
            'dashboard': asdict(self.dashboard),
            'logging': asdict(self.logging),
            'notification': asdict(self.notification),
            'environment': self.env
        }

    def update_config(self, section: str, **kwargs):
        """
        Actualiza la configuración de una sección específica.
        
        Args:
            section (str): Sección a actualizar (trading, mt5, risk, etc.)
            **kwargs: Parámetros a actualizar
        """
        config_obj = getattr(self, section, None)
        
        if config_obj is None:
            raise ValueError(f"Sección de configuración inválida: {section}")
        
        for key, value in kwargs.items():
            if hasattr(config_obj, key):
                setattr(config_obj, key, value)
            else:
                raise ValueError(f"Parámetro inválido: {key} en sección {section}")
        
        # Revalidar después de actualizar
        self._validate_config()


# Singleton global
_global_config = None


def get_config(env: str = 'development') -> ConfigManager:
    """
    Obtiene la configuración global (singleton).
    
    Args:
        env (str): Entorno (development, production)
    
    Returns:
        ConfigManager: Instancia del gestor de configuración
    """
    global _global_config
    if _global_config is None:
        _global_config = ConfigManager(env=env)
    return _global_config


def reload_config(env: Optional[str] = None):
    """
    Recarga la configuración.
    
    Args:
        env (str): Nuevo entorno (opcional)
    """
    global _global_config
    _global_config = ConfigManager(env=env or 'development')
