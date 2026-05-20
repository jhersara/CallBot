#!/usr/bin/env python3
"""
XAUUSD Quant Bot - Production Main
Punto de entrada unificado con integración MT5 real, FastAPI y WebSocket
"""

import asyncio
import logging
from datetime import datetime
import sys
import os

# Agregar ruta del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mt5.connector_improved import MT5ConnectorImproved
from core.market_analyzer import MarketAnalyzer
from core.enhanced_risk_manager import EnhancedRiskManager
from core.strategy_executor import StrategyExecutor
from database.crud import TradeCRUD
from api.fastapi_server import TradingBotAPI
from config.settings_advanced import (
    mt5_settings, trading_settings, api_settings, database_settings
)
from utils.logger import get_logger

# Configurar logging
logger = get_logger()


class TradingBotProduction:
    """
    Bot de trading profesional con integración MT5 real y FastAPI
    """
    
    def __init__(self):
        """Inicializa el bot de producción"""
        self.logger = logger
        self.running = False
        
        # Componentes
        self.mt5_connector = None
        self.risk_manager = None
        self.market_analyzer = None
        self.strategy_executor = None
        self.trade_crud = None
        self.api = None
        
        # Estado
        self.state = {
            'status': 'INITIALIZING',
            'balance': trading_settings.initial_balance,
            'equity': trading_settings.initial_balance,
            'open_trades': 0,
            'closed_trades': 0,
            'win_rate': 0.0,
            'profit_factor': 0.0,
            'last_signal': None,
            'mode': 'DEMO'
        }
        
        self.logger.info("=" * 70)
        self.logger.info("XAUUSD QUANT BOT - PRODUCTION MODE")
        self.logger.info("=" * 70)
        self.logger.info(f"Initial Balance: ${trading_settings.initial_balance:.2f}")
        self.logger.info(f"Risk per Trade: {trading_settings.risk_percent}%")
        self.logger.info(f"Symbol: XAUUSD | Timeframe: {trading_settings.timeframe}")
        self.logger.info("=" * 70)
    
    def initialize(self, demo_mode=False):
        """
        Inicializa todos los componentes del bot
        
        Args:
            demo_mode (bool): Si True, usa datos sintéticos sin MT5 real
        """
        try:
            self.logger.info("[*] Inicializando componentes...")
            
            # 1. Inicializar MT5 Connector
            self.logger.info("[*] Conectando a MetaTrader 5...")
            self.mt5_connector = MT5ConnectorImproved(config={
                'enable_auto_reconnect': True,
                'reconnect_attempts': 5,
                'reconnect_delay_seconds': 10
            })
            
            if demo_mode:
                self.logger.warning("[!] MODO DEMO ACTIVADO - Sin conexión MT5 real")
                self.state['mode'] = 'DEMO'
                # Usar datos sintéticos
                from datafeeds.synthetic_generator import SyntheticDataGenerator
                gen = SyntheticDataGenerator()
                candles = gen.generate_candles(500)
                self.state['balance'] = trading_settings.initial_balance
                self.state['equity'] = trading_settings.initial_balance
            else:
                # Conectar a MT5 real
                if not self.mt5_connector.connect(
                    login=mt5_settings.login,
                    password=mt5_settings.password,
                    server=mt5_settings.server
                ):
                    self.logger.error("[✗] Error conectando a MT5")
                    self.logger.error("[!] Iniciando en MODO DEMO...")
                    demo_mode = True
                    self.state['mode'] = 'DEMO'
                    from datafeeds.synthetic_generator import SyntheticDataGenerator
                    gen = SyntheticDataGenerator()
                    candles = gen.generate_candles(500)
                else:
                    self.logger.info("[✓] Conexión a MT5 establecida")
                    self.state['mode'] = 'REAL'
                    
                    # Obtener información de cuenta
                    account_info = self.mt5_connector.get_account_info()
                    if account_info:
                        self.state['balance'] = account_info.get('balance', trading_settings.initial_balance)
                        self.state['equity'] = account_info.get('equity', trading_settings.initial_balance)
                        self.logger.info(f"[✓] Balance: ${self.state['balance']:.2f}")
                        self.logger.info(f"[✓] Equity: ${self.state['equity']:.2f}")
                    
                    # Obtener datos de mercado
                    candles_data = self.mt5_connector.get_candles(
                        symbol='XAUUSD',
                        timeframe=5,  # M5
                        count=500
                    )
                    
                    if candles_data is not None:
                        candles = candles_data
                        self.logger.info(f"[✓] Obtenidas {len(candles)} velas de XAUUSD")
                    else:
                        self.logger.error("[✗] Error obteniendo datos de mercado")
                        return False
            
            # 2. Inicializar Risk Manager
            self.logger.info("[*] Inicializando gestor de riesgo...")
            self.risk_manager = EnhancedRiskManager(self.state['balance'])
            self.logger.info("[✓] Risk Manager inicializado")
            
            # 3. Inicializar Market Analyzer
            self.logger.info("[*] Inicializando analizador de mercado...")
            self.market_analyzer = MarketAnalyzer(candles, pip_value=0.01)  # XAUUSD pip
            self.logger.info("[✓] Market Analyzer inicializado")
            
            # 4. Inicializar Strategy Executor
            self.logger.info("[*] Inicializando ejecutor de estrategia...")
            self.strategy_executor = StrategyExecutor(
                risk_manager=self.risk_manager,
                mt5_connector=self.mt5_connector,
                symbol='XAUUSD',
                pip_value=0.01
            )
            self.logger.info("[✓] Strategy Executor inicializado")
            
            # 5. Inicializar Base de Datos
            self.logger.info("[*] Inicializando base de datos...")
            self.trade_crud = TradeCRUD(database_settings.url)
            self.trade_crud.create_tables()
            self.logger.info("[✓] Base de datos inicializada")
            
            # 6. Inicializar FastAPI
            self.logger.info("[*] Inicializando API FastAPI...")
            self.api = TradingBotAPI(self)
            self.logger.info("[✓] API FastAPI inicializada")
            
            self.state['status'] = 'READY'
            self.logger.info("[✓] Bot listo para operar")
            return True
        
        except Exception as e:
            self.logger.error(f"[✗] Error inicializando bot: {e}")
            self.state['status'] = 'ERROR'
            return False
    
    def analyze_and_execute(self):
        """Analiza mercado y ejecuta señales"""
        try:
            # Obtener datos actuales
            if self.state['mode'] == 'REAL':
                candles = self.mt5_connector.get_candles(
                    symbol='XAUUSD',
                    timeframe=5,
                    count=500
                )
                if candles is None:
                    self.logger.warning("[!] No se obtuvieron datos de mercado")
                    return
            else:
                # Modo demo: generar datos sintéticos
                from datafeeds.synthetic_generator import SyntheticDataGenerator
                gen = SyntheticDataGenerator()
                candles = gen.generate_candles(500)
            
            # Actualizar analizador
            self.market_analyzer.candles = candles
            
            # Generar señal consolidada
            signal = self.market_analyzer._consolidate_signals(candles)
            
            if signal['action'] != 'HOLD':
                self.logger.info(f"[📊] Señal: {signal['action']} | Confianza: {signal['confidence']:.2%}")
                
                # Preparar señal completa
                full_signal = {
                    'action': signal['action'],
                    'confidence': signal['confidence'],
                    'entry_price': candles[-1]['close'],
                    'stop_loss': candles[-1]['close'] - (50 * 0.01),  # 50 pips
                    'take_profit': candles[-1]['close'] + (150 * 0.01),  # 150 pips
                    'signals': signal['reasons']
                }
                
                # Ejecutar señal
                result = self.strategy_executor.execute_signal(full_signal, self.market_analyzer)
                
                if result['executed']:
                    self.logger.info(f"[✓] Operación ejecutada: {result['order_id']}")
                    self.state['last_signal'] = signal
                    self.state['open_trades'] = len(self.strategy_executor.open_trades)
                    
                    # Guardar en BD
                    self.trade_crud.insert_trade(
                        symbol='XAUUSD',
                        direction=full_signal['action'],
                        entry_price=full_signal['entry_price'],
                        stop_loss=full_signal['stop_loss'],
                        take_profit=full_signal['take_profit'],
                        lot_size=result.get('lot_size', 0),
                        order_id=result['order_id'],
                        confidence=full_signal['confidence']
                    )
                else:
                    self.logger.warning(f"[!] Operación no ejecutada: {result['reason']}")
            
            # Actualizar operaciones abiertas
            current_prices = {'XAUUSD': candles[-1]['close']}
            closed = self.strategy_executor.update_open_trades(current_prices)
            
            if closed:
                self.state['closed_trades'] += len(closed)
                for trade in closed:
                    if trade['closed']:
                        self.trade_crud.close_trade(
                            order_id=trade['trade_id'],
                            exit_price=trade['exit_price'],
                            profit_loss=trade['profit_loss'],
                            reason=trade['reason']
                        )
            
            # Actualizar estadísticas
            stats = self.risk_manager.get_statistics()
            self.state['win_rate'] = stats.get('win_rate', 0)
            self.state['profit_factor'] = stats.get('profit_factor', 0)
            self.state['equity'] = self.state['balance'] + sum(
                t.get('profit_loss', 0) for t in self.strategy_executor.open_trades
            )
        
        except Exception as e:
            self.logger.error(f"[✗] Error en análisis: {e}")
    
    async def run(self, demo_mode=False, update_interval=5):
        """
        Ejecuta el bot en loop
        
        Args:
            demo_mode (bool): Modo demo sin MT5 real
            update_interval (int): Intervalo de actualización en segundos
        """
        if not self.initialize(demo_mode=demo_mode):
            self.logger.error("[✗] No se pudo inicializar el bot")
            return
        
        self.running = True
        self.state['status'] = 'RUNNING'
        
        try:
            self.logger.info("[▶] Bot iniciado en loop de análisis")
            
            while self.running:
                try:
                    self.analyze_and_execute()
                    await asyncio.sleep(update_interval)
                
                except KeyboardInterrupt:
                    self.logger.info("[⏹] Deteniendo bot...")
                    self.running = False
                
                except Exception as e:
                    self.logger.error(f"[✗] Error en loop: {e}")
                    await asyncio.sleep(update_interval)
        
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Detiene el bot y libera recursos"""
        self.logger.info("[*] Deteniendo bot...")
        self.running = False
        self.state['status'] = 'STOPPED'
        
        if self.mt5_connector:
            self.mt5_connector.disconnect()
        
        if self.trade_crud:
            self.trade_crud.close()
        
        self.logger.info("[✓] Bot detenido")


async def main():
    """Punto de entrada principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='XAUUSD Quant Bot - Production')
    parser.add_argument('--demo', action='store_true', help='Ejecutar en modo demo')
    parser.add_argument('--api-only', action='store_true', help='Solo ejecutar API FastAPI')
    parser.add_argument('--interval', type=int, default=5, help='Intervalo de análisis (segundos)')
    
    args = parser.parse_args()
    
    # Crear bot
    bot = TradingBotProduction()
    
    if args.api_only:
        # Solo API
        if not bot.initialize(demo_mode=args.demo):
            logger.error("Error inicializando bot")
            return
        
        import uvicorn
        logger.info(f"[▶] Iniciando API en {api_settings.host}:{api_settings.port}")
        await asyncio.to_thread(
            uvicorn.run,
            bot.api.get_app(),
            host=api_settings.host,
            port=api_settings.port,
            log_level='info'
        )
    else:
        # Bot + API
        await bot.run(demo_mode=args.demo, update_interval=args.interval)


if __name__ == '__main__':
    asyncio.run(main())
