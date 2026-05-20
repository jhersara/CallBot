"""
database/crud.py
CRUD completo para persistencia de trades en SQLite
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import json
import logging


class TradeCRUD:
    """CRUD para operaciones de trading"""
    
    def __init__(self, db_url: str = 'sqlite:///./trading.db'):
        """
        Inicializa el CRUD
        
        Args:
            db_url: URL de la base de datos (ej: sqlite:///./trading.db)
        """
        # Extraer ruta del archivo
        self.db_path = db_url.replace('sqlite:///', '').replace('sqlite:///', '')
        if not self.db_path:
            self.db_path = './trading.db'
        
        self.logger = logging.getLogger(__name__)
        self.connection = None
        self.connect()
    
    def connect(self):
        """Conectar a la base de datos"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            self.logger.info(f"Conectado a BD: {self.db_path}")
        except Exception as e:
            self.logger.error(f"Error conectando a BD: {e}")
            raise
    
    def close(self):
        """Cerrar conexión"""
        if self.connection:
            self.connection.close()
            self.logger.info("Conexión cerrada")
    
    def create_tables(self):
        """Crear tablas si no existen"""
        try:
            cursor = self.connection.cursor()
            
            # Tabla de trades
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT UNIQUE NOT NULL,
                    symbol TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    exit_price REAL,
                    stop_loss REAL NOT NULL,
                    take_profit REAL NOT NULL,
                    lot_size REAL NOT NULL,
                    profit_loss REAL,
                    confidence REAL,
                    entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    exit_time TIMESTAMP,
                    status TEXT DEFAULT 'OPEN',
                    reason_close TEXT,
                    signals TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de estadísticas diarias
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE UNIQUE NOT NULL,
                    total_trades INTEGER DEFAULT 0,
                    winning_trades INTEGER DEFAULT 0,
                    losing_trades INTEGER DEFAULT 0,
                    total_profit_loss REAL DEFAULT 0,
                    win_rate REAL DEFAULT 0,
                    profit_factor REAL DEFAULT 0,
                    max_drawdown REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de configuración
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.connection.commit()
            self.logger.info("Tablas creadas/verificadas")
        
        except Exception as e:
            self.logger.error(f"Error creando tablas: {e}")
            raise
    
    # ============ TRADES CRUD ============
    
    def insert_trade(self, symbol: str, direction: str, entry_price: float,
                    stop_loss: float, take_profit: float, lot_size: float,
                    order_id: str, confidence: float = 0.0, signals: List = None) -> int:
        """
        Insertar un nuevo trade
        
        Returns:
            ID del trade insertado
        """
        try:
            cursor = self.connection.cursor()
            
            signals_json = json.dumps(signals) if signals else None
            
            cursor.execute('''
                INSERT INTO trades (
                    order_id, symbol, direction, entry_price, stop_loss, take_profit,
                    lot_size, confidence, signals, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                order_id, symbol, direction, entry_price, stop_loss, take_profit,
                lot_size, confidence, signals_json, 'OPEN'
            ))
            
            self.connection.commit()
            trade_id = cursor.lastrowid
            self.logger.info(f"Trade insertado: {order_id}")
            return trade_id
        
        except Exception as e:
            self.logger.error(f"Error insertando trade: {e}")
            raise
    
    def close_trade(self, order_id: str, exit_price: float, profit_loss: float,
                   reason: str = 'MANUAL') -> bool:
        """
        Cerrar un trade
        
        Returns:
            True si se cerró correctamente
        """
        try:
            cursor = self.connection.cursor()
            
            cursor.execute('''
                UPDATE trades SET
                    exit_price = ?,
                    profit_loss = ?,
                    status = 'CLOSED',
                    reason_close = ?,
                    exit_time = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE order_id = ?
            ''', (exit_price, profit_loss, reason, order_id))
            
            self.connection.commit()
            self.logger.info(f"Trade cerrado: {order_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error cerrando trade: {e}")
            return False
    
    def get_trade(self, order_id: str) -> Optional[Dict]:
        """Obtener un trade por order_id"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT * FROM trades WHERE order_id = ?', (order_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
        
        except Exception as e:
            self.logger.error(f"Error obteniendo trade: {e}")
            return None
    
    def get_all_trades(self, status: str = None, limit: int = 100) -> List[Dict]:
        """
        Obtener todos los trades
        
        Args:
            status: Filtrar por estado ('OPEN', 'CLOSED')
            limit: Límite de resultados
        """
        try:
            cursor = self.connection.cursor()
            
            if status:
                cursor.execute('''
                    SELECT * FROM trades WHERE status = ?
                    ORDER BY created_at DESC LIMIT ?
                ''', (status, limit))
            else:
                cursor.execute('''
                    SELECT * FROM trades
                    ORDER BY created_at DESC LIMIT ?
                ''', (limit,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        
        except Exception as e:
            self.logger.error(f"Error obteniendo trades: {e}")
            return []
    
    def get_open_trades(self) -> List[Dict]:
        """Obtener todos los trades abiertos"""
        return self.get_all_trades(status='OPEN')
    
    def get_closed_trades(self, limit: int = 100) -> List[Dict]:
        """Obtener todos los trades cerrados"""
        return self.get_all_trades(status='CLOSED', limit=limit)
    
    def get_trades_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Obtener trades en un rango de fechas
        
        Args:
            start_date: Fecha inicio (YYYY-MM-DD)
            end_date: Fecha fin (YYYY-MM-DD)
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT * FROM trades
                WHERE DATE(entry_time) BETWEEN ? AND ?
                ORDER BY entry_time DESC
            ''', (start_date, end_date))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        
        except Exception as e:
            self.logger.error(f"Error obteniendo trades por fecha: {e}")
            return []
    
    def get_trades_by_symbol(self, symbol: str) -> List[Dict]:
        """Obtener trades de un símbolo específico"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT * FROM trades WHERE symbol = ?
                ORDER BY created_at DESC
            ''', (symbol,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        
        except Exception as e:
            self.logger.error(f"Error obteniendo trades por símbolo: {e}")
            return []
    
    # ============ ESTADÍSTICAS ============
    
    def calculate_daily_stats(self, date: str = None) -> Dict:
        """
        Calcular estadísticas diarias
        
        Args:
            date: Fecha (YYYY-MM-DD), si no se proporciona usa hoy
        """
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            cursor = self.connection.cursor()
            
            # Obtener trades del día
            cursor.execute('''
                SELECT * FROM trades
                WHERE DATE(entry_time) = ? AND status = 'CLOSED'
            ''', (date,))
            
            trades = [dict(row) for row in cursor.fetchall()]
            
            if not trades:
                return {
                    'date': date,
                    'total_trades': 0,
                    'winning_trades': 0,
                    'losing_trades': 0,
                    'total_profit_loss': 0,
                    'win_rate': 0,
                    'profit_factor': 0
                }
            
            # Calcular métricas
            total_trades = len(trades)
            winning_trades = sum(1 for t in trades if t['profit_loss'] > 0)
            losing_trades = sum(1 for t in trades if t['profit_loss'] < 0)
            total_profit_loss = sum(t['profit_loss'] for t in trades)
            
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            # Profit Factor
            gross_profit = sum(t['profit_loss'] for t in trades if t['profit_loss'] > 0)
            gross_loss = abs(sum(t['profit_loss'] for t in trades if t['profit_loss'] < 0))
            profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 0
            
            stats = {
                'date': date,
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'total_profit_loss': total_profit_loss,
                'win_rate': win_rate,
                'profit_factor': profit_factor
            }
            
            # Guardar en BD
            cursor.execute('''
                INSERT OR REPLACE INTO daily_stats (
                    date, total_trades, winning_trades, losing_trades,
                    total_profit_loss, win_rate, profit_factor
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                date, total_trades, winning_trades, losing_trades,
                total_profit_loss, win_rate, profit_factor
            ))
            
            self.connection.commit()
            return stats
        
        except Exception as e:
            self.logger.error(f"Error calculando estadísticas: {e}")
            return {}
    
    def get_statistics(self, days: int = 30) -> Dict:
        """
        Obtener estadísticas consolidadas
        
        Args:
            days: Últimos N días
        """
        try:
            cursor = self.connection.cursor()
            
            # Obtener trades cerrados
            cursor.execute('''
                SELECT * FROM trades
                WHERE status = 'CLOSED'
                AND DATE(exit_time) >= DATE('now', '-' || ? || ' days')
                ORDER BY exit_time DESC
            ''', (days,))
            
            trades = [dict(row) for row in cursor.fetchall()]
            
            if not trades:
                return {
                    'total_trades': 0,
                    'winning_trades': 0,
                    'losing_trades': 0,
                    'total_profit_loss': 0,
                    'win_rate': 0,
                    'profit_factor': 0,
                    'avg_profit_loss': 0
                }
            
            # Calcular métricas
            total_trades = len(trades)
            winning_trades = sum(1 for t in trades if t['profit_loss'] > 0)
            losing_trades = sum(1 for t in trades if t['profit_loss'] < 0)
            total_profit_loss = sum(t['profit_loss'] for t in trades)
            
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            avg_profit_loss = total_profit_loss / total_trades if total_trades > 0 else 0
            
            # Profit Factor
            gross_profit = sum(t['profit_loss'] for t in trades if t['profit_loss'] > 0)
            gross_loss = abs(sum(t['profit_loss'] for t in trades if t['profit_loss'] < 0))
            profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 0
            
            return {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'total_profit_loss': total_profit_loss,
                'win_rate': win_rate,
                'profit_factor': profit_factor,
                'avg_profit_loss': avg_profit_loss,
                'period_days': days
            }
        
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    # ============ CONFIGURACIÓN ============
    
    def set_config(self, key: str, value: str):
        """Guardar configuración"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO config (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (key, value))
            self.connection.commit()
        except Exception as e:
            self.logger.error(f"Error guardando config: {e}")
    
    def get_config(self, key: str) -> Optional[str]:
        """Obtener configuración"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT value FROM config WHERE key = ?', (key,))
            row = cursor.fetchone()
            return row[0] if row else None
        except Exception as e:
            self.logger.error(f"Error obteniendo config: {e}")
            return None
    
    def export_trades_csv(self, filename: str = 'trades_export.csv'):
        """Exportar trades a CSV"""
        try:
            import csv
            
            trades = self.get_all_trades(limit=10000)
            
            if not trades:
                self.logger.warning("No hay trades para exportar")
                return
            
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=trades[0].keys())
                writer.writeheader()
                writer.writerows(trades)
            
            self.logger.info(f"Trades exportados a {filename}")
        
        except Exception as e:
            self.logger.error(f"Error exportando trades: {e}")
