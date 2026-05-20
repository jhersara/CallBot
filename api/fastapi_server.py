# api/fastapi_server.py
"""
Servidor FastAPI con WebSocket para XAUUSD Quant Bot
Proporciona APIs REST y WebSocket para el frontend
"""

from fastapi import FastAPI, WebSocket, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

from config.settings_advanced import (
    api_settings, mt5_settings, trading_settings, ai_settings
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TradingBotAPI:
    """API del bot de trading"""
    
    def __init__(self):
        self.app = FastAPI(title="XAUUSD Quant Bot API", version="1.0.0")
        self.setup_middleware()
        self.setup_routes()
        self.active_connections: List[WebSocket] = []
        self.bot_state = {
            'status': 'STOPPED',
            'balance': trading_settings.initial_balance,
            'equity': trading_settings.initial_balance,
            'open_trades': 0,
            'closed_trades': 0,
            'win_rate': 0.0,
            'profit_factor': 0.0,
            'last_signal': None,
            'mode': 'DEMO'
        }
    
    def setup_middleware(self):
        """Configurar CORS y otros middlewares"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=api_settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def setup_routes(self):
        """Configurar rutas de la API"""
        
        # Health check
        @self.app.get("/health")
        async def health():
            return {
                'status': 'OK',
                'timestamp': datetime.now().isoformat(),
                'bot_state': self.bot_state
            }
        
        # Dashboard - Métricas principales
        @self.app.get("/api/dashboard/metrics")
        async def get_dashboard_metrics():
            return {
                'balance': self.bot_state['balance'],
                'equity': self.bot_state['equity'],
                'return_percent': ((self.bot_state['equity'] - trading_settings.initial_balance) / trading_settings.initial_balance) * 100,
                'open_trades': self.bot_state['open_trades'],
                'closed_trades': self.bot_state['closed_trades'],
                'win_rate': self.bot_state['win_rate'],
                'profit_factor': self.bot_state['profit_factor'],
                'status': self.bot_state['status'],
                'mode': self.bot_state['mode']
            }
        
        # Historial de operaciones
        @self.app.get("/api/trades/history")
        async def get_trade_history(limit: int = 50):
            # TODO: Conectar a base de datos
            return {
                'trades': [],
                'total': 0,
                'limit': limit
            }
        
        # Señales actuales
        @self.app.get("/api/signals/current")
        async def get_current_signals():
            return {
                'signals': self.bot_state.get('last_signal', {}),
                'timestamp': datetime.now().isoformat()
            }
        
        # Configuración del bot
        @self.app.get("/api/config")
        async def get_config():
            return {
                'symbol': trading_settings.symbol if hasattr(trading_settings, 'symbol') else 'XAUUSD',
                'timeframe': trading_settings.timeframe,
                'risk_percent': trading_settings.risk_percent,
                'initial_balance': trading_settings.initial_balance,
                'min_confidence': trading_settings.min_confidence,
                'mode': self.bot_state['mode']
            }
        
        @self.app.post("/api/config/update")
        async def update_config(config: Dict):
            """Actualizar configuración del bot"""
            try:
                if 'mode' in config:
                    self.bot_state['mode'] = config['mode']
                if 'risk_percent' in config:
                    trading_settings.risk_percent = config['risk_percent']
                if 'min_confidence' in config:
                    trading_settings.min_confidence = config['min_confidence']
                
                return {'status': 'OK', 'message': 'Configuración actualizada'}
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        # Control del bot
        @self.app.post("/api/bot/start")
        async def start_bot():
            self.bot_state['status'] = 'RUNNING'
            logger.info("Bot iniciado")
            return {'status': 'OK', 'message': 'Bot iniciado'}
        
        @self.app.post("/api/bot/stop")
        async def stop_bot():
            self.bot_state['status'] = 'STOPPED'
            logger.info("Bot detenido")
            return {'status': 'OK', 'message': 'Bot detenido'}
        
        # WebSocket para datos en tiempo real
        @self.app.websocket("/ws/trading")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.active_connections.append(websocket)
            logger.info(f"Cliente conectado. Total: {len(self.active_connections)}")
            
            try:
                while True:
                    # Enviar estado cada segundo
                    await websocket.send_json({
                        'type': 'state_update',
                        'data': self.bot_state,
                        'timestamp': datetime.now().isoformat()
                    })
                    await asyncio.sleep(1)
            
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
            
            finally:
                self.active_connections.remove(websocket)
                logger.info(f"Cliente desconectado. Total: {len(self.active_connections)}")
    
    async def broadcast_signal(self, signal: Dict):
        """Enviar señal a todos los clientes conectados"""
        message = {
            'type': 'signal',
            'data': signal,
            'timestamp': datetime.now().isoformat()
        }
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error enviando señal: {e}")
    
    async def broadcast_trade_update(self, trade: Dict):
        """Enviar actualización de operación a todos los clientes"""
        message = {
            'type': 'trade_update',
            'data': trade,
            'timestamp': datetime.now().isoformat()
        }
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error enviando actualización: {e}")
    
    def get_app(self):
        """Retornar la aplicación FastAPI"""
        return self.app


# Instancia global
api = TradingBotAPI()
app = api.get_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=api_settings.host,
        port=api_settings.port,
        log_level="info"
    )
