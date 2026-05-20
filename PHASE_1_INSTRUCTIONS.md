# 🚀 FASE 1 - INSTRUCCIONES DE EJECUCIÓN

## ✅ Cambios Realizados

### 1. **strategy_executor.py** - ARREGLADO ✓
- ✅ Descomentado `_execute_order()`
- ✅ Ahora usa `mt5_connector.send_order()` real
- ✅ Ejecuta órdenes en MT5 real (no simuladas)

### 2. **main_production.py** - NUEVO ✓
- ✅ Punto de entrada unificado
- ✅ Integra TradingBot + StrategyExecutor + MT5ConnectorImproved
- ✅ Soporta modo DEMO y modo REAL
- ✅ Inyecta bot en FastAPI
- ✅ WebSocket para tiempo real

### 3. **database/crud.py** - NUEVO ✓
- ✅ CRUD completo para SQLite
- ✅ INSERT/SELECT/UPDATE trades
- ✅ Estadísticas consolidadas
- ✅ Exportación a CSV

### 4. **api/fastapi_server_v2.py** - MEJORADO ✓
- ✅ Inyecta instancia de TradingBot
- ✅ Endpoints conectados a datos reales
- ✅ WebSocket sincronizado
- ✅ Historial de trades desde BD

### 5. **datafeeds/synthetic_generator.py** - NUEVO ✓
- ✅ Generador de datos realistas
- ✅ Modo DEMO sin MT5
- ✅ Tendencias, rangos, volatilidad

---

## 🔧 INSTALACIÓN

### Paso 1: Instalar dependencias
```bash
cd CallBot
pip install -r requirements.txt
```

### Paso 2: Configurar variables de entorno
```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales MT5 (OPCIONAL - funciona sin ellas en DEMO)
# MT5_LOGIN=tu_numero_cuenta
# MT5_PASSWORD=tu_contraseña
# MT5_SERVER=Exness-MT5
```

---

## 🎮 EJECUCIÓN

### Opción A: MODO DEMO (Recomendado para testing)
```bash
# Terminal 1: Ejecutar bot en modo demo
python main_production.py --demo

# Terminal 2: Ejecutar API FastAPI
python main_production.py --demo --api-only
```

**Ventajas:**
- ✅ No necesita MT5 instalado
- ✅ Genera datos sintéticos realistas
- ✅ Perfecto para testing
- ✅ Rápido de probar

### Opción B: MODO REAL (Con MT5)
```bash
# Asegúrate de que MetaTrader 5 esté abierto

# Terminal 1: Ejecutar bot con MT5 real
python main_production.py

# Terminal 2: Ejecutar API FastAPI
python main_production.py --api-only
```

**Requisitos:**
- ✅ MetaTrader 5 instalado y ejecutándose
- ✅ Cuenta conectada (demo o real)
- ✅ Credenciales en `.env`

### Opción C: SOLO API (Sin bot de análisis)
```bash
# Solo ejecutar servidor API
python main_production.py --api-only
```

---

## 📊 VERIFICAR QUE FUNCIONA

### 1. Health Check
```bash
curl http://localhost:8000/health
```

**Respuesta esperada:**
```json
{
  "status": "OK",
  "timestamp": "2026-05-20T...",
  "bot_status": "RUNNING"
}
```

### 2. Obtener Métricas
```bash
curl http://localhost:8000/api/dashboard/metrics
```

**Respuesta esperada:**
```json
{
  "balance": 10000.00,
  "equity": 10000.00,
  "return_percent": 0.0,
  "open_trades": 0,
  "closed_trades": 0,
  "win_rate": 0.0,
  "profit_factor": 0.0,
  "status": "RUNNING",
  "mode": "DEMO"
}
```

### 3. Obtener Historial
```bash
curl http://localhost:8000/api/trades/history
```

### 4. WebSocket (Tiempo Real)
```bash
# Usar wscat o similar
wscat -c ws://localhost:8000/ws/trading
```

---

## 🔄 FLUJO DE EJECUCIÓN

```
main_production.py
    ↓
TradingBotProduction.__init__()
    ↓
TradingBotProduction.initialize()
    ├─ MT5ConnectorImproved.connect()  (Real o DEMO)
    ├─ EnhancedRiskManager()
    ├─ MarketAnalyzer()
    ├─ StrategyExecutor()
    ├─ TradeCRUD()
    └─ TradingBotAPI(bot)  ← Inyectar bot
    ↓
TradingBotProduction.run()
    ├─ Loop cada 5 segundos
    ├─ analyze_and_execute()
    │   ├─ Obtener velas
    │   ├─ Analizar SMC
    │   ├─ Generar señal
    │   ├─ Ejecutar orden (REAL)  ← ARREGLADO
    │   ├─ Guardar en BD
    │   └─ Actualizar estado
    └─ FastAPI sirve estado en tiempo real
```

---

## 🧪 TESTING RÁPIDO

### Test 1: Verificar que strategy_executor ejecuta órdenes reales
```python
# En Python REPL
from core.strategy_executor import StrategyExecutor
from mt5.connector_improved import MT5ConnectorImproved

connector = MT5ConnectorImproved()
executor = StrategyExecutor(None, connector, 'XAUUSD', 0.01)

# Ver que _execute_order ahora usa send_order()
print(executor._execute_order.__doc__)
```

### Test 2: Verificar que FastAPI recibe estado del bot
```python
from main_production import TradingBotProduction
from api.fastapi_server_v2 import TradingBotAPI

bot = TradingBotProduction()
api = TradingBotAPI(bot)

# Verificar que api.bot está inyectado
print(api.bot is not None)  # Debe ser True
```

### Test 3: Verificar CRUD
```python
from database.crud import TradeCRUD

crud = TradeCRUD()
crud.create_tables()

# Insertar trade de prueba
trade_id = crud.insert_trade(
    symbol='XAUUSD',
    direction='BUY',
    entry_price=2045.50,
    stop_loss=2040.00,
    take_profit=2055.00,
    lot_size=0.1,
    order_id='TEST_001',
    confidence=0.85
)

print(f"Trade insertado: {trade_id}")

# Obtener trade
trade = crud.get_trade('TEST_001')
print(trade)
```

---

## 🐛 TROUBLESHOOTING

### Error: "No se puede conectar a MT5"
**Solución**: Usar `--demo`
```bash
python main_production.py --demo
```

### Error: "Port 8000 already in use"
**Solución**: Cambiar puerto
```bash
# En api/fastapi_server_v2.py, cambiar:
# api_settings.port = 8001
```

### Error: "Base de datos locked"
**Solución**: Cerrar otras instancias
```bash
# Asegúrate de que solo hay una instancia del bot ejecutándose
```

### Error: "ImportError: No module named 'mt5'"
**Solución**: Instalar MetaTrader5
```bash
pip install MetaTrader5
```

---

## 📈 PRÓXIMOS PASOS (FASE 2)

Una vez que Fase 1 esté funcionando:

1. ✅ Conectar Frontend React a API
   - Dashboard consume `/api/dashboard/metrics`
   - Signals consume `/api/signals/current`
   - History consume `/api/trades/history`
   - WebSocket para tiempo real

2. ✅ Validar en modo DEMO primero
   - Generar señales
   - Ejecutar órdenes simuladas
   - Guardar en BD
   - Mostrar en dashboard

3. ✅ Probar en modo REAL con capital pequeño
   - Usar cuenta demo de MT5
   - Monitorear regularmente
   - Validar que órdenes se ejecutan

---

## ✨ CHECKLIST DE VALIDACIÓN

- [ ] `python main_production.py --demo` funciona sin errores
- [ ] `curl http://localhost:8000/health` retorna OK
- [ ] `/api/dashboard/metrics` retorna datos
- [ ] `/api/trades/history` retorna lista vacía (sin trades aún)
- [ ] WebSocket `/ws/trading` conecta y recibe actualizaciones
- [ ] Base de datos `trading.db` se crea automáticamente
- [ ] `strategy_executor._execute_order()` usa `send_order()` real
- [ ] CRUD inserta/obtiene trades correctamente
- [ ] FastAPI recibe instancia de TradingBot inyectada

---

## 📞 SOPORTE

Si algo no funciona:

1. Revisar logs en consola
2. Verificar que todas las dependencias están instaladas
3. Probar en modo DEMO primero
4. Revisar `AUDIT_REPORT.md` para más detalles

---

**¡Fase 1 lista para ejecutar!** 🚀
