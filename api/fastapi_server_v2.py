# api/fastapi_server_v2.py
"""
Servidor FastAPI mejorado con inyección de TradingBot real
"""

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import json
from typing import Dict, List, Optional
from datetime import datetime
import logging

from config.settings_advanced import api_settings

logger = logging.getLogger(__name__)


class TradingBotAPI:
    """API del bot de trading con TradingBot inyectado"""
    
    def __init__(self, bot=None):
        """
        Inicializa la API
        
        Args:
            bot: Instancia de TradingBotProduction (opcional)
        """
        self.app = FastAPI(
            title="XAUUSD Quant Bot API",
            version="1.0.0",
            description="API profesional para trading algorítmico"
        )
        self.bot = bot  # Inyectar instancia real
        self.setup_middleware()
        self.setup_routes()
        self.active_connections: List[WebSocket] = []
    
    def setup_middleware(self):
        """Configurar CORS y middlewares"""
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
                'bot_status': self.bot.state['status'] if self.bot else 'NO_BOT'
            }
        
        # Dashboard - Métricas principales
        @self.app.get("/api/dashboard/metrics")
        async def get_dashboard_metrics():
            if not self.bot:
                raise HTTPException(status_code=503, detail="Bot no inicializado")
            
            return {
                'balance': self.bot.state['balance'],
                'equity': self.bot.state['equity'],
                'return_percent': ((self.bot.state['equity'] - self.bot.state['balance']) / self.bot.state['balance'] * 100) if self.bot.state['balance'] > 0 else 0,
                'open_trades': self.bot.state['open_trades'],
                'closed_trades': self.bot.state['closed_trades'],
                'win_rate': self.bot.state['win_rate'],
                'profit_factor': self.bot.state['profit_factor'],
                'status': self.bot.state['status'],
                'mode': self.bot.state['mode'],
                'timestamp': datetime.now().isoformat()
            }
        
        # Historial de operaciones
        @self.app.get("/api/trades/history")
        async def get_trade_history(limit: int = 50, status: str = None):
            if not self.bot or not self.bot.trade_crud:
                raise HTTPException(status_code=503, detail="BD no inicializada")
            
            try:
                if status:
                    trades = self.bot.trade_crud.get_all_trades(status=status, limit=limit)
                else:
                    trades = self.bot.trade_crud.get_all_trades(limit=limit)
                
                return {
                    'trades': trades,
                    'total': len(trades),
                    'limit': limit,
                    'timestamp': datetime.now().isoformat()
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Operaciones abiertas
        @self.app.get("/api/trades/open")
        async def get_open_trades():
            if not self.bot or not self.bot.trade_crud:
                raise HTTPException(status_code=503, detail="BD no inicializada")
            
            try:
                trades = self.bot.trade_crud.get_open_trades()
                return {
                    'trades': trades,
                    'total': len(trades),
                    'timestamp': datetime.now().isoformat()
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Señales actuales
        @self.app.get("/api/signals/current")
        async def get_current_signals():
            if not self.bot:
                raise HTTPException(status_code=503, detail="Bot no inicializado")
            
            return {
                'signal': self.bot.state.get('last_signal', {}),
                'timestamp': datetime.now().isoformat()
            }
        
        # Configuración del bot
        @self.app.get("/api/config")
        async def get_config():
            if not self.bot:
                raise HTTPException(status_code=503, detail="Bot no inicializado")
            
            return {
                'symbol': 'XAUUSD',
                'timeframe': 'M5',
                'risk_percent': 1.0,
                'initial_balance': self.bot.state['balance'],
                'mode': self.bot.state['mode'],
                'status': self.bot.state['status']
            }
        
        @self.app.post("/api/config/update")
        async def update_config(config: Dict):
            """Actualizar configuración del bot"""
            if not self.bot:
                raise HTTPException(status_code=503, detail="Bot no inicializado")
            
            try:
                if 'mode' in config:
                    self.bot.state['mode'] = config['mode']
                
                return {
                    'status': 'OK',
                    'message': 'Configuración actualizada',
                    'config': config
                }
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        # Control del bot
        @self.app.post("/api/bot/start")
        async def start_bot():
            if not self.bot:
                raise HTTPException(status_code=503, detail="Bot no inicializado")
            
            self.bot.running = True
            self.bot.state['status'] = 'RUNNING'
            logger.info("Bot iniciado")
            return {'status': 'OK', 'message': 'Bot iniciado'}
        
        @self.app.post("/api/bot/stop")
        async def stop_bot():
            if not self.bot:
                raise HTTPException(status_code=503, detail="Bot no inicializado")
            
            self.bot.running = False
            self.bot.state['status'] = 'STOPPED'
            logger.info("Bot detenido")
            return {'status': 'OK', 'message': 'Bot detenido'}
        
        # Estadísticas
        @self.app.get("/api/statistics")
        async def get_statistics(days: int = 30):
            if not self.bot or not self.bot.trade_crud:
                raise HTTPException(status_code=503, detail="BD no inicializada")
            
            try:
                stats = self.bot.trade_crud.get_statistics(days=days)
                return {
                    'statistics': stats,
                    'period_days': days,
                    'timestamp': datetime.now().isoformat()
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # WebSocket para datos en tiempo real
        @self.app.websocket("/ws/trading")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.active_connections.append(websocket)
            logger.info(f"Cliente WebSocket conectado. Total: {len(self.active_connections)}")
            
            try:
                while True:
                    if self.bot:
                        # Enviar estado cada segundo
                        await websocket.send_json({
                            'type': 'state_update',
                            'data': self.bot.state,
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
        """Enviar actualización de operación"""
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


if __name__ == "__main__":
    import uvicorn
    
    # Crear API sin bot (para testing)
    api = TradingBotAPI()
    
    uvicorn.run(
        api.get_app(),
        host=api_settings.host,
        port=api_settings.port,
        log_level="info"
    )
