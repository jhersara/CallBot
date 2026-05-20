# config/settings_advanced.py
"""
Configuración avanzada del XAUUSD Quant Bot
Incluye: MT5, Trading, API, IA, Notificaciones, Backtesting
"""

from dataclasses import dataclass
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class MT5Settings:
    """Configuración de MetaTrader 5"""
    login: int = int(os.getenv('MT5_LOGIN', 0))
    password: str = os.getenv('MT5_PASSWORD', '')
    server: str = os.getenv('MT5_SERVER', 'Exness-MT5')
    symbol: str = 'XAUUSD'
    timeout: int = 5000
    reconnect_attempts: int = 5
    reconnect_delay: int = 5


@dataclass
class TradingSettings:
    """Configuración de trading"""
    initial_balance: float = float(os.getenv('INITIAL_BALANCE', 10000))
    risk_percent: float = 1.0  # 1% por operación (fijo)
    max_daily_loss: float = 0.05  # 5% del balance
    max_drawdown: float = 0.20  # 20%
    timeframe: str = 'M5'  # M1, M5, M15, M30, H1, H4, D1
    
    # Parámetros SMC
    bos_threshold: float = 0.0002
    order_block_lookback: int = 50
    fvg_min_size: float = 0.0005
    liquidity_zone_size: float = 0.001
    
    # Filtros de sesión (UTC)
    london_start: int = 8
    london_end: int = 17
    ny_start: int = 13
    ny_end: int = 22
    tokyo_start: int = 0
    tokyo_end: int = 9
    
    # Confianza mínima para ejecutar
    min_confidence: float = 0.75


@dataclass
class APISettings:
    """Configuración de API FastAPI"""
    host: str = os.getenv('API_HOST', '0.0.0.0')
    port: int = int(os.getenv('API_PORT', 8000))
    debug: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    cors_origins: list = None
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ['http://localhost:3000', 'http://localhost:5173']


@dataclass
class DatabaseSettings:
    """Configuración de base de datos"""
    url: str = os.getenv('DATABASE_URL', 'sqlite:///./trading.db')
    echo: bool = os.getenv('DB_ECHO', 'False').lower() == 'true'


@dataclass
class AISettings:
    """Configuración de modelos IA"""
    xgboost_enabled: bool = True
    lstm_enabled: bool = True
    ensemble_enabled: bool = True
    model_update_interval: int = 3600  # segundos
    confidence_threshold: float = 0.75
    
    # Paths de modelos
    xgboost_model_path: str = 'models/xgboost_model.pkl'
    lstm_model_path: str = 'models/lstm_model.h5'
    scaler_path: str = 'models/scaler.pkl'


@dataclass
class NotificationSettings:
    """Configuración de notificaciones"""
    telegram_enabled: bool = os.getenv('TELEGRAM_ENABLED', 'False').lower() == 'true'
    telegram_token: str = os.getenv('TELEGRAM_TOKEN', '')
    telegram_chat_id: str = os.getenv('TELEGRAM_CHAT_ID', '')
    
    email_enabled: bool = False
    email_address: str = os.getenv('EMAIL_ADDRESS', '')
    
    webhook_enabled: bool = False
    webhook_url: str = os.getenv('WEBHOOK_URL', '')


@dataclass
class BacktestSettings:
    """Configuración de backtesting"""
    slippage: float = 0.5  # pips
    commission: float = 0.0001  # 0.01%
    monte_carlo_simulations: int = 5000
    walk_forward_periods: int = 12


# Instancias globales
mt5_settings = MT5Settings()
trading_settings = TradingSettings()
api_settings = APISettings()
database_settings = DatabaseSettings()
ai_settings = AISettings()
notification_settings = NotificationSettings()
backtest_settings = BacktestSettings()
