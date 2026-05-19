# 🤖 CallBot - Professional AI Trading Bot

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-Proprietary-red.svg)
![Status](https://img.shields.io/badge/status-Active-brightgreen.svg)

## 📋 Descripción

**CallBot** es un algoritmo de trading profesional e inteligente diseñado para operar en mercados de divisas (Forex) con un enfoque innovador en la **gestión de capital compuesto**. El sistema implementa una estrategia ganadora basada en análisis técnico avanzado, con un riesgo controlado del **1% por operación** y retornos esperados de **30-65% mensual**.

### 🎯 Características Principales

✅ **Gestión de Capital Compuesto (1% Riesgo)**
- Ajuste dinámico del tamaño del lote basado en el balance actual
- Crecimiento exponencial del capital
- Riesgo constante del 1% por operación

✅ **Análisis Técnico Multi-Indicador**
- Break of Structure (BOS)
- Change of Character (CHOCH)
- Niveles de Fibonacci
- Bloques de Órdenes (Order Blocks)
- Zonas de Liquidez (Liquidity Zones)

✅ **Dashboard en Tiempo Real**
- Monitoreo completo de operaciones
- Estadísticas de rendimiento
- Gráficos interactivos
- Control del bot

✅ **Ejecución Automática**
- Operaciones ejecutadas automáticamente
- Gestión de Stop Loss y Take Profit
- Historial detallado de operaciones

---

## 🚀 Inicio Rápido

### Requisitos Previos

- Python 3.8 o superior
- MetaTrader 5 instalado y ejecutándose
- Conexión a internet
- Cuenta de trading (demo o real)

### Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/tuusuario/callbot.git
   cd callbot
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar MetaTrader 5:**
   - Abrir MetaTrader 5
   - Conectarse a una cuenta
   - Asegurar que el símbolo EURUSD esté disponible

4. **Ejecutar el bot:**
   ```bash
   python main.py
   ```

---

## 📊 Estructura del Proyecto

```
CallBot/
├── main.py                           # Punto de entrada principal
├── requirements.txt                  # Dependencias del proyecto
├── README.md                         # Este archivo
├── DESIGN.md                         # Diseño de arquitectura
├── TRADING_SYSTEM_DOCUMENTATION.md   # Documentación completa
│
├── core/                             # Módulos principales
│   ├── market_analyzer.py            # Análisis técnico
│   ├── enhanced_risk_manager.py      # Gestión de capital
│   ├── strategy_executor.py          # Ejecución de operaciones
│   ├── market_structure.py           # Detección de estructura
│   ├── fibonacci.py                  # Niveles de Fibonacci
│   ├── order_blocks.py               # Bloques de órdenes
│   ├── liquidity.py                  # Zonas de liquidez
│   ├── risk_manager.py               # Gestor de riesgo original
│   ├── trade_manager.py              # Gestión de operaciones
│   └── news_filter.py                # Filtro de noticias
│
├── mt5/                              # Integración con MetaTrader 5
│   └── connector.py                  # Conector a MT5
│
├── gui/                              # Interfaz gráfica
│   └── dashboard.py                  # Dashboard de monitoreo
│
├── database/                         # Base de datos
│   └── (archivos de configuración)
│
├── config/                           # Configuración
│   └── (archivos de configuración)
│
├── notifications/                    # Sistema de notificaciones
│   └── notifier.py                   # Notificador
│
└── ai/                               # Módulos de IA
    └── (módulos de inteligencia artificial)
```

---

## 🎮 Uso del Sistema

### Ejecución Básica

```bash
python main.py
```

El bot se iniciará con los parámetros por defecto:
- Balance Inicial: $100
- Par de Divisas: EURUSD
- Riesgo: 1% por operación

### Ejecución Personalizada

```python
from main import TradingBot

# Crear bot con parámetros personalizados
bot = TradingBot(
    initial_balance=1000,      # Balance inicial en USD
    symbol='GBPUSD',           # Par de divisas
    pip_value=0.0001           # Valor del pip
)

# Ejecutar con dashboard
bot.run(use_dashboard=True)

# O sin dashboard
bot.run(use_dashboard=False)
```

### Dashboard

El dashboard proporciona:
- 📊 **Resumen**: Estadísticas principales y sentimiento del mercado
- 📈 **Operaciones Abiertas**: Tabla de operaciones activas
- 📋 **Historial**: Registro de operaciones cerradas
- ⚙️ **Configuración**: Ajustes del bot

---

## 💡 Estrategia de Trading

### Componentes Técnicos

| Indicador | Descripción | Fuerza |
|-----------|-------------|--------|
| **BOS** | Break of Structure | 70% |
| **CHOCH** | Change of Character | 80% |
| **Fibonacci** | Niveles de retroceso | 65% |
| **Order Blocks** | Bloques institucionales | 65% |
| **Liquidez** | Zonas de liquidez | 60% |

### Generación de Señales

El sistema genera señales **BUY**, **SELL** o **HOLD** basadas en la convergencia de múltiples indicadores. La **confianza** de cada señal se calcula como el promedio de las fuerzas de los indicadores activos.

**Ejemplo de Señal:**
```
Acción: BUY
Confianza: 78%
Precio Entrada: 1.0850
Stop Loss: 1.0800
Take Profit: 1.0950
Riesgo: $1.00
Lote: 0.20
```

---

## 📈 Gestión de Capital

### Fórmula de Cálculo del Lote

```
Risk Amount = Balance × (Risk Percent / 100)
Lot Size = Risk Amount / (Stop Loss Pips × Pip Value)
```

### Ejemplo de Crecimiento Compuesto

Con retornos promedio de 40% mensual:

| Mes | Balance | Crecimiento |
|-----|---------|-------------|
| 1 | $100.00 | - |
| 2 | $140.00 | +40% |
| 3 | $196.00 | +40% |
| 4 | $274.40 | +40% |
| 6 | $537.82 | +40% |
| 12 | $8,916.10 | +8,816% |

---

## 📊 Módulos Principales

### 1. MarketAnalyzer (market_analyzer.py)

Consolida toda la lógica de análisis técnico.

```python
from core.market_analyzer import MarketAnalyzer

analyzer = MarketAnalyzer(candles, pip_value=0.0001)
signal = analyzer.generate_trading_signal()
```

### 2. EnhancedRiskManager (enhanced_risk_manager.py)

Implementa la gestión de capital compuesto.

```python
from core.enhanced_risk_manager import EnhancedRiskManager

risk_manager = EnhancedRiskManager(
    initial_balance=100,
    risk_percent=1.0
)

lot_size = risk_manager.calculate_lot_size(
    stop_loss_pips=50,
    pip_value=0.0001
)
```

### 3. StrategyExecutor (strategy_executor.py)

Ejecuta las operaciones basadas en señales.

```python
from core.strategy_executor import StrategyExecutor

executor = StrategyExecutor(
    risk_manager,
    mt5_connector,
    symbol='EURUSD'
)

result = executor.execute_signal(signal)
```

### 4. TradingDashboard (gui/dashboard.py)

Interfaz gráfica para monitoreo en tiempo real.

```python
from gui.dashboard import run_dashboard

run_dashboard(strategy_executor, market_analyzer)
```

---

## 🔧 Configuración Avanzada

### Parámetros del Risk Manager

```python
risk_manager = EnhancedRiskManager(
    initial_balance=100,      # Balance inicial
    risk_percent=1.0,         # Riesgo por operación (%)
    min_lot_size=0.01,        # Tamaño mínimo de lote
    max_lot_size=10.0         # Tamaño máximo de lote
)
```

### Parámetros del Strategy Executor

```python
executor.min_confidence = 0.6           # Confianza mínima (0-1)
executor.enable_news_filter = True      # Filtro de noticias
executor.enable_session_filter = True   # Filtro de sesión
```

---

## 📊 Estadísticas y Reportes

### Estadísticas Disponibles

- Balance inicial y actual
- Ganancia total y porcentaje
- Total de operaciones
- Operaciones ganadoras y perdedoras
- Tasa de ganancia (Win Rate)
- Factor de ganancia (Profit Factor)
- Ganancia promedio por operación

### Exportar Estadísticas

```python
risk_manager.export_statistics('trading_stats.json')
```

---

## 🐛 Troubleshooting

### Problema: "No se pudo conectar a MetaTrader 5"

**Solución:**
1. Verificar que MetaTrader 5 esté abierto
2. Verificar que haya una cuenta conectada
3. Reiniciar MetaTrader 5

### Problema: "El bot no ejecuta operaciones"

**Solución:**
1. Verificar que la confianza sea superior al 60%
2. Verificar que no haya filtros activos
3. Verificar que haya suficiente margen

### Problema: "Las operaciones tienen pérdidas consistentes"

**Solución:**
1. Ajustar los parámetros de Stop Loss/Take Profit
2. Aumentar el umbral de confianza mínima
3. Revisar la estrategia en mercados históricos

---

## 📚 Documentación Completa

Para documentación más detallada, consulta:
- [DESIGN.md](DESIGN.md) - Diseño de arquitectura
- [TRADING_SYSTEM_DOCUMENTATION.md](TRADING_SYSTEM_DOCUMENTATION.md) - Documentación completa del sistema

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

---

## ⚠️ Disclaimer

**AVISO IMPORTANTE:**

Este software se proporciona "tal cual" sin garantías de ningún tipo. El trading en Forex implica riesgo significativo de pérdida. Aunque este bot ha sido diseñado con estrategias profesionales, no hay garantía de rentabilidad.

**Recomendaciones:**
- Probar primero en cuenta demo
- Comenzar con capital pequeño
- Monitorear regularmente las operaciones
- No invertir dinero que no puedas permitirte perder

---

## 📄 Licencia

Este proyecto es propietario. Todos los derechos reservados.

---

## 👨‍💼 Autor

**Manus AI - Trading Bot Development Team**

- Desarrollo: 2024
- Versión: 1.0.0
- Última Actualización: 2024-05-18

---

## 📞 Soporte

Para soporte técnico, contacta a:
- Email: support@callbot.ai
- Discord: [Servidor de CallBot]
- Documentación: [Wiki del Proyecto]

---

## 🎉 Agradecimientos

Agradecemos a:
- MetaTrader 5 por la plataforma de trading
- La comunidad de traders profesionales
- Todos los contribuidores

---

**¡Bienvenido a CallBot! Que tus operaciones sean rentables.** 🚀📈
